import uuid, shutil
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.schemas import DocumentUploadResponse
from app.services.ingestion import ingest_pdf

router = APIRouter(prefix="/documents", tags=["documents"])
logger = get_logger(__name__)

RAW_PDF_DIR =Path("data/raw_pdfs")
RAW_PDF_DIR.mkdir(parents=True, exist_ok=True)

# @router.post("/upload", response_model=DocumentUploadResponse, status_code=200)
# def upload_document(
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db),
# ):
#     """
#     Accepts a PDF upload, saves it to disk, creates a Document row,
#     then run ingestion (PDF -> Markdown -> chunks -> Pinecone) sinchronously 
    
#     """

#     if not file.filename.lower().endswith(".pdf"):
#         raise HTTPException(status_code=400, detail="Only pdf files are supported")
    
#     document_id = str(uuid.uuid4())
#     namespace = document_id     # one Pinecone namespace per document
#     pdf_path = RAW_PDF_DIR / f"{file.filename}"

#     with pdf_path.open("wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)   

#     try:
#         chunk_count = ingest_pdf(pdf_path=str(pdf_path), namespace=namespace)

#         document = Document(
#         id=document_id,
#         filename=file.filename,
#         pinecone_namespace=namespace,
#         )

#         db.add(document)
#         db.commit()
        
#         message = f"Successfully uploaded file : {document_id} with {chunk_count} chunks"
#         logger.info(message)
#         print(message)
    
#     except Exception:
#         logger.exception(f"Ingestion is failed for document id {document_id}")        
#         raise HTTPException(status_code=500, detail="Ingestion failed — check server logs for details.")


#     return DocumentUploadResponse(
#         id=document_id,
#         filename=file.filename,
#         message=message,
#     )

@router.post("/upload", response_model=DocumentUploadResponse, status_code=200)
def upload_document(
    file: UploadFile = File(...),
):
    """
    Accepts a PDF upload, saves it to disk, creates a Document row,
    then run ingestion (PDF -> Markdown -> chunks -> Pinecone) sinchronously 
    
    """

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only pdf files are supported")
    
    document_id = str(uuid.uuid4())
    namespace = document_id     # one Pinecone namespace per document
    pdf_path = RAW_PDF_DIR / f"{file.filename}"

    with pdf_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)   

    try:
        chunk_count = ingest_pdf(pdf_path=str(pdf_path), namespace=namespace)

        message = f"Successfully ingest file : {document_id} with {chunk_count} chunks to Pinecone"
        logger.info(message)
        print(message)
    
    except Exception:
        logger.exception(f"Ingestion is failed for document id {document_id}")        
        raise HTTPException(status_code=500, detail="Ingestion failed — check server logs for details.")


    return DocumentUploadResponse(
        id=document_id,
        filename=file.filename,
        message=message,
    )




# @router.get("/{document_id}", response_model=DocumentResponse)
# def get_document(
#     document_id:str, 
#     db: Session = Depends(get_db)
# ):

#     document = db.query(Document).filter(Document.id == document_id).first()

#     if document is None:
#         raise HTTPException(status_code=404, detail="Document not found")
    
#     return document

# @router.get("", response_model=list[DocumentResponse])
# def list_documents(
#     db: Session = Depends(get_db)
# ):
#     """List all uploaded documents, most recent first."""
#     all_documents = db.query(Document).order_by(Document.uploaded_at.desc()).all()
#     return all_documents