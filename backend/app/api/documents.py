import uuid, shutil
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.database import SessionLocal, get_db
from app.db.models import Document
from app.models.schemas import DocumentResponse, DocumentUploadResponse
from app.services.ingestion import ingest_pdf

router = APIRouter(prefix="/documents", tags=["documents"])
logger = get_logger(__name__)

RAW_PDF_DIR =Path("data/raw_pdfs")
RAW_PDF_DIR.mkdir(parents=True, exist_ok=True)

def _run_ingestion(doc_id:str, pdf_path:str, namespace:str) -> None:

    db =SessionLocal()
    try:
        document = db.query(Document).filter(Document.id == doc_id).first()
        if document is None:
            logger.error(f"Document id {doc_id} vanished before ingestion could run")
            return
        
        document.status = "processing"
        db.commit()

        chunk_count = ingest_pdf(pdf_path=pdf_path, namespace=namespace)

        document.status = "ready"
        db.commit()
        logger.info(f"Document id {doc_id} is ready with {chunk_count} chunks")

    except Exception:
        logger.exception(f"Ingestion is failed for document id {doc_id}")
        db.query(Document).filter(Document.id == doc_id).update({"status": "failed"})
        db.commit()
    
    finally:
        db.close()

@router.post("/upload", response_model=DocumentUploadResponse, status_code=202)
def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Accepts a PDF upload, saves it to disk, creates a pending Document row,
    then kicks off ingestion (PDF -> Markdown -> chunks -> Pinecone) as a
    background task so the client isn't blocked waiting for embeddings.
    Poll GET /documents/{id} to check when status flips to "ready".
    """

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only pdf files are supported")
    
    document_id = str(uuid.uuid4())
    namespace = document_id     # one Pinecone namespace per document
    pdf_path = RAW_PDF_DIR / f"{document_id}_{file.filename}"

    with pdf_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    document = Document(
        id=document_id,
        filename=file.filename,
        pinecone_namespace=namespace,
        status="pending",
    )
    db.add(document)
    db.commit()

    background_tasks.add_task(_run_ingestion, document_id, str(pdf_path), namespace)

    return DocumentUploadResponse(
        id=document_id,
        filename=file.filename,
        status="pending",
        message="Upload received. Ingestion is running in the background.",
    )


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id:str, 
    db: Session = Depends(get_db)
):
    """Check ingestion status for a single document (pending/processing/ready/failed)."""

    document = db.query(Document).filter(Document.id == document_id).first()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.get("", response_model=list[DocumentResponse])
def list_documents(
    db: Session = Depends(get_db)
):
    """List all uploaded documents, most recent first."""
    all_documents = db.query(Document).order_by(Document.uploaded_at.desc()).all()
    return all_documents