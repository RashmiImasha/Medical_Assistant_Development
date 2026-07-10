from pathlib import Path
from langchain_core.documents import Document
from langchain_experimental.text_splitter import SemanticChunker

def read_markdown(markdown_file: str) -> str:

    """
    Read markdown content.
 
    Args:
        markdown_file: Markdown file path.
 
    Returns:
        Markdown content.
    """
    return Path(markdown_file).read_text(encoding="utf-8")

def chunk_markdown(markdown_file: str, embeddings) -> list[Document]:

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
    splitter = SemanticChunker(embeddings=embeddings, breakpoint_threshold_type="percentile")

    return splitter.create_documents([markdown_content])

