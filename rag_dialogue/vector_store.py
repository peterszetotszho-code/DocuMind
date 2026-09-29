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


def get_retriever(k: int | None = None):
    """Return a similarity-search retriever backed by the Chroma store."""
    return get_vector_store().as_retriever(
        search_kwargs={"k": k or settings.top_k}
    )


def add_documents(documents: list[Document]) -> None:
    """Embed and persist documents into the vector store."""
    if not documents:
        return
    get_vector_store().add_documents(documents)


def delete_by_source(source: str) -> None:
    """Remove all chunks whose ``source`` metadata matches the given path."""
    get_vector_store().delete(where={"source": source})


def retrieve(query: str, k: int | None = None) -> list[Document]:
    """Retrieve the most relevant document chunks for a query."""
    store = get_vector_store()
    return store.similarity_search(query, k=k or settings.top_k)
