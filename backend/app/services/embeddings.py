from langchain_huggingface import HuggingFaceEmbeddings
from app.core.config import get_settings

settings = get_settings()

def get_embedding_model() -> HuggingFaceEmbeddings:

    return HuggingFaceEmbeddings(
        model_name = settings.huggingface_embed_model,
        encode_kwargs={"normalize_embeddings": True},
    )