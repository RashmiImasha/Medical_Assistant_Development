from pathlib import Path
import pymupdf4llm
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

def convert_pdf_to_markdown(pdf_path:str, output_dir:str) -> str:
    """
        pdf_path: Source PDF path.
        output_dir: Output markdown directory.

    Returns:
        Generated markdown file path.
    """

    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        raise FileNotFoundError(f"PDF File not found: {pdf_path}")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    markdown_content = pymupdf4llm.to_markdown(str(pdf_file))

    markdown_file = output_path / f"{pdf_file.stem}.md"
    markdown_file.write_text(markdown_content, encoding="utf-8")

    return str(markdown_file)


def read_markdown(markdown_file: str) -> str:

    """
    Read markdown content.
 
    Args:
        markdown_file: Markdown file path.
 
    Returns:
        Markdown content.
    """
    return Path(markdown_file).read_text(encoding="utf-8")

def chunk_markdown(markdown_file: str, chunk_size:int =300, chunk_overlap: int = 80) -> list[Document]:

    """
    Generate semantic chunks from markdown.
 
    Args:
        markdown_file: Markdown file path.        
 
    Returns:
        List of semantic chunks as LangChain Documents.
    """

    markdown_content = read_markdown(markdown_file)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""],
    )

    return splitter.create_documents([markdown_content])

