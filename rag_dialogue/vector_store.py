"""Vector store wrapper backed by a local Chroma database."""

from langchain_chroma import Chroma
from langchain_core.documents import Document

from rag_dialogue.config import settings
from rag_dialogue.embeddings import get_embeddings


def get_vector_store() -> Chroma:
    """Return a Chroma store persisted under the configured directory."""
    settings.chroma_dir.mkdir(parents=True, exist_ok=True)
    return Chroma(
        persist_directory=str(settings.chroma_dir),
        embedding_function=get_embeddings(),
    )


def add_documents(documents: list[Document]) -> None:
    """Embed and persist documents into the vector store."""
    if not documents:
        return
    get_vector_store().add_documents(documents)


def retrieve(query: str, k: int | None = None) -> list[Document]:
    """Retrieve the most relevant document chunks for a query."""
    store = get_vector_store()
    return store.similarity_search(query, k=k or settings.top_k)
