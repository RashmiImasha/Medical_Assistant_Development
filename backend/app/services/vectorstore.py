from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore

from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger()

_pinecone_client = Pinecone(api_key=settings.pinecone_api_key)

def ensure_db_exists() -> None:

    existing_indexes = [index["name"] for index in _pinecone_client.list_indexes()]

    if settings.pinecone_index_name not in existing_indexes:

        logger.info("Creating Pinecone index: %s", settings.pinecone_index_name)
        _pinecone_client.create_index(
            name=settings.pinecone_index_name,
            dimension=1024,
            metric="cosine",
            spec=ServerlessSpec(cloud=settings.pinecone_cloud, region=settings.pinecone_region)
        )

def get_vector_db(embeddings) -> PineconeVectorStore:

    ensure_db_exists()
    index = _pinecone_client.Index(settings.pinecone_index_name)
    
    return PineconeVectorStore(index=index, embedding=embeddings)
