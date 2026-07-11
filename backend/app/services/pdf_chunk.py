from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

def read_markdown(markdown_file: str) -> str:

    """
    Read markdown content.
 
    Args:
        markdown_file: Markdown file path.
 
    Returns:
        Markdown content.
    """
    return Path(markdown_file).read_text(encoding="utf-8")

def chunk_markdown(markdown_file: str, chunk_size:int =500, chunk_overlap: int = 150) -> list[Document]:

    """
    Generate semantic chunks from markdown.
 
    Args:
        markdown_file: Markdown file path.
        embeddings: Any LangChain-compatible embeddings object — here, our
            Gemini embeddings from services/embeddings.py. SemanticChunker
            uses embedding distance between sentences to decide chunk
            boundaries, so it needs a live embeddings model, not just text.
 
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

