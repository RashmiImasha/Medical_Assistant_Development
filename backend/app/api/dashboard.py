from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pinecone import Pinecone

from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.database import get_db
from app.db.models import Document
from app.models.schemas import ExtractMetricsResponse, FinancialMetrics
from app.services.metrics_retrieval import Retriever, extract_financial_metrics
from app.services.ingestion import get_pinecone_client
from app.services.ingestion import get_embedding_model

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
logger = get_logger(__name__)
settings = get_settings()


def get_namespace_metadata(namespace: str):

    pinecone_client = get_pinecone_client()

    index = pinecone_client.Index(
        settings.pinecone_index_name
    )

    ids = next(index.list(namespace=namespace))

    if not ids:
        raise ValueError(
            f"No vectors found in namespace: {namespace}"
        )

    first_id = ids[0]

    result = index.fetch(
        ids=[first_id],
        namespace=namespace
    )

    vector = result.vectors[first_id]
    metadata = vector.metadata

    return {
        "company": metadata.get("company"),
        "year": metadata.get("year"),
        "source_file": metadata.get("source_file")
    }


@router.post("/extract", response_model=ExtractMetricsResponse, status_code=200)
def extract_and_save_metrics(
    document_id: str,    
    db: Session = Depends(get_db)
):
    
    pinecone_namespace = document_id

    try:         

        if pinecone_namespace:

            print(f"found pinecone namespace with document id {document_id}")

            metadata = get_namespace_metadata(
                namespace=pinecone_namespace
            )

            company = metadata["company"]
            year = metadata["year"]
            file_name = metadata["source_file"]
            print(f"Extracted from document: {file_name} - company: {company} | year: {year}")

            pinecone_client = get_pinecone_client()

            index = pinecone_client.Index(
                settings.pinecone_index_name
            )

            embedding_model = get_embedding_model()

            retriever = Retriever(
                index=index,
                embeddings=embedding_model,
                namespace=pinecone_namespace
            )

            metrics = extract_financial_metrics(
                retriever=retriever,
                company=company,
                year=year
            )

            document = Document(
                id = document_id,            
                file_name=file_name,
                company=company,
                year=year,
                pinecone_namespace=pinecone_namespace,
                financial_metrics=metrics.dict()
            )

            db.add(document)
            db.commit()

            message = f"Successfully uploaded file : {document_id} to postgresql database"
            logger.info(message)
            print(message)
            
        else:
            print(f"Pinecone namespace is not exist for this document: {document_id}")

    except Exception as e:
 
        logger.exception(
            "Metric extraction failed for document=%s",
            document_id
        )
        raise

    return ExtractMetricsResponse(
        id=document_id,
        filename=file_name,
        metrics=metrics
    )
