from pathlib import Path

from app.core.logging import get_logger
from app.services.pdf_to_markdown import PDFToMarkdownConverter
from app.services.pdf_chunk import chunk_markdown
from app.services.embeddings import get_embedding_model
from app.services.vectorstore import get_vector_db

logger = get_logger(__name__)
MARKDOWN_OUTPUT_DIR = "data/markdown"

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
    logger.info(f"Ingesting {company}, {year} for {pdf_file}")

    converter = PDFToMarkdownConverter()
    markdown_file = converter.convert_pdf(pdf_path=pdf_path, output_dir=MARKDOWN_OUTPUT_DIR)

    embeddings = get_embedding_model()
    chunks = chunk_markdown(markdown_file=markdown_file, embeddings=embeddings)

    for chunk in chunks:
        chunk.metadata.update({"company":company, "year":year, "source_file":pdf_file.name})
    
    vectore_db = get_vector_db(embeddings)
    vectore_db.add_documents(documents=chunks, namespace=namespace)

    logger.info(f"Ingested {len(chunks)} for {pdf_file.name} into {namespace} namespace in Pinecone")

    return len(chunks)




