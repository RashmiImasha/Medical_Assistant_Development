from langchain_voyageai import VoyageAIEmbeddings
from app.core.config import get_settings

settings = get_settings()

def get_embedding_model() -> VoyageAIEmbeddings:

    return VoyageAIEmbeddings(
        model = settings.voyage_embedding_model,
        voyage_api_key = settings.voyage_api_key,
    )