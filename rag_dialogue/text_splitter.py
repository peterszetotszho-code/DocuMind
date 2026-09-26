"""Text splitting utilities for chunking documents before indexing."""

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag_dialogue.config import settings


def get_splitter() -> RecursiveCharacterTextSplitter:
    """Build a recursive character text splitter from the configured settings."""
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )


def split_documents(documents: list[Document]) -> list[Document]:
    """Split a list of documents into smaller overlapping chunks."""
    return get_splitter().split_documents(documents)
