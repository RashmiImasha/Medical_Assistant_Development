from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_env: str = "development"
    app_name: str = "Investor Platform API"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:5173"

    # PostgreSQL
    database_url: str
 
    # Gemini (embeddings)
    voyage_api_key: str
    voyage_embedding_model: str = "voyage-4-large"
 
    # Pinecone (vector store)
    pinecone_api_key: str
    pinecone_index_name: str = "investor-platform"
    pinecone_cloud: str = "aws"
    pinecone_region: str = "us-east-1"
 
    # Groq (LLM)
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"
 
    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

@lru_cache
def get_settings() -> Settings:

    """
    Cached settings accessor. FastAPI route handlers and service modules
    call get_settings() rather than instantiating Settings() directly, so
    the .env file is only parsed once per process.
    """
     
    return Settings()
    

 