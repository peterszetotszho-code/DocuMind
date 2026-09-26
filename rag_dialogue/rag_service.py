"""Core RAG service that combines retrieval and generation."""

from collections.abc import Callable

from langchain_core.documents import Document

from rag_dialogue.config import settings
from rag_dialogue.llm import get_llm
from rag_dialogue.prompts import build_messages
from rag_dialogue.vector_store import retrieve as vector_retrieve


class RAGService:
    """Answer questions using retrieval-augmented generation."""

    def __init__(
        self,
        llm=None,
        retriever: Callable[[str], list[Document]] | None = None,
        top_k: int | None = None,
    ) -> None:
        self._llm = llm
        self._retriever = retriever
        self.top_k = top_k or settings.top_k

    @property
    def llm(self):
        """Lazily build the chat model on first use."""
        if self._llm is None:
            self._llm = get_llm()
        return self._llm

    def retrieve(self, question: str) -> list[Document]:
        """Return the document chunks most relevant to the question."""
        if self._retriever is not None:
            return self._retriever(question)
        return vector_retrieve(question, k=self.top_k)

    @staticmethod
    def build_context(documents: list[Document]) -> str:
        """Join retrieved chunks into a single context string."""
        return "\n\n".join(document.page_content for document in documents)

    def answer(
        self,
        question: str,
        history: list[tuple[str, str]] | None = None,
    ) -> str:
        """Retrieve relevant chunks and generate an answer with context."""
        documents = self.retrieve(question)
        context = self.build_context(documents)
        messages = build_messages(context=context, question=question, history=history)
        response = self.llm.invoke(messages)
        return response.content
