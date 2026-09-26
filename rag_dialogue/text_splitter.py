"""Text splitting utilities for chunking documents before indexing."""

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag_dialogue.config import settings

# Ordered from largest to smallest boundary. Chinese sentence punctuation is
# included so Chinese documents are chunked at sentence boundaries rather than
# at arbitrary character counts.
SEPARATORS = ["\n\n", "\n", "。", "！", "？", "；", "，", "、", " ", ""]


def get_splitter() -> RecursiveCharacterTextSplitter:
    """Build a recursive character text splitter from the configured settings."""
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=SEPARATORS,
    )


def split_documents(documents: list[Document]) -> list[Document]:
    """Split a list of documents into smaller overlapping chunks."""
    return get_splitter().split_documents(documents)
