"""Factory for the local Ollama embedding model."""

from langchain_ollama import OllamaEmbeddings

from rag_dialogue.config import settings


def get_embeddings() -> OllamaEmbeddings:
    """Build an embedding model backed by a locally running Ollama instance."""
    return OllamaEmbeddings(
        base_url=settings.ollama_base_url,
        model=settings.embedding_model,
    )
