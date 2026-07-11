from pathlib import Path
from functools import lru_cache
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_community.embeddings import FastEmbedEmbeddings

from app.core.logging import get_logger
from app.core.config import get_settings
from app.services.pdf_chunk import chunk_markdown, convert_pdf_to_markdown

settings = get_settings()
logger = get_logger(__name__)
MARKDOWN_OUTPUT_DIR = "data/markdown"

_pinecone_client = Pinecone(api_key=settings.pinecone_api_key)

def ensure_db_exists() -> None:

    existing_indexes = [index["name"] for index in _pinecone_client.list_indexes()]

    if settings.pinecone_index_name not in existing_indexes:

        logger.info(f"Creating Pinecone index: {settings.pinecone_index_name} ")
        _pinecone_client.create_index(
            name=settings.pinecone_index_name,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(cloud=settings.pinecone_cloud, region=settings.pinecone_region)
        )

def get_vector_db(embeddings) -> PineconeVectorStore:

    ensure_db_exists()
    index = _pinecone_client.Index(settings.pinecone_index_name)
    
    return PineconeVectorStore(index=index, embedding=embeddings)

@lru_cache
def get_embedding_model() -> FastEmbedEmbeddings:

    return FastEmbedEmbeddings(
        model_name = settings.huggingface_embed_model,
        threads=None,        
    )


def parse_company_year(pdf_file:Path) -> tuple[str, str]:

    """
    Parse company and year from a PDF filename.
    Supports names like `2024_Apple.pdf` and `2024_AnnualReport_Apple.pdf`.
    """
    stem = pdf_file.stem
    parts = stem.split("_")

    if parts and parts[0].isdigit():
        year = parts[0]
        company = parts[-1]
    elif len(parts) >= 2:        
        company = parts[0]
        year = parts[1]
    else:
        company = stem
        year = ""
    return company, year


def ingest_pdf(pdf_path:str, namespace:str) -> int:

    """
    Runs the full ingestion pipeline for a single PDF:
    PDF -> Markdown -> semantic chunks -> Voyage embeddings -> Pinecone upsert.
 
    Args:
        pdf_path: Path to the PDF file on disk.
        namespace: Pinecone namespace 
 
    Returns:
        Number of chunks ingested.
    """

    pdf_file = Path(pdf_path)
    company,year = parse_company_year(pdf_file)
    
    print(f"Ingesting {company}, {year} for {pdf_file}")

    markdown_file = convert_pdf_to_markdown(pdf_path=pdf_path, output_dir=MARKDOWN_OUTPUT_DIR)

    chunks = chunk_markdown(markdown_file=markdown_file)    
    print(f"Generated {len(chunks)} chunks for {pdf_file.name}")

    for chunk in chunks:
        chunk.metadata.update({"company":company, "year":year, "source_file":pdf_file.name})
        
    embeddings = get_embedding_model()

    
    print(f"Generated embeddings for {len(chunks)} chunks")
    vectore_db = get_vector_db(embeddings)
    vectore_db.add_documents(documents=chunks, namespace=namespace)

    ingest_msg = f"Ingested {len(chunks)} for {pdf_file.name} into {namespace} namespace in Pinecone"
    logger.info(ingest_msg)
    print(ingest_msg)

    return len(chunks)




