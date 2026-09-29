"""Core RAG service that combines retrieval and generation via LCEL."""

import os
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from operator import itemgetter

from langchain_core.documents import Document
from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable, RunnableLambda

from rag_dialogue.config import settings
from rag_dialogue.llm import get_llm
from rag_dialogue.prompts import RAG_PROMPT
from rag_dialogue.vector_store import get_retriever

# Keywords that suggest the user wants a full enumeration rather than a
# single fact, so we retrieve a larger context window.
_LIST_KEYWORDS = (
    "哪些", "列出", "所有", "全部", "有幾", "種類", "多少", "幾個",
    "list", "what are", "enumerate", "how many",
)


def is_list_question(question: str) -> bool:
    """Return True if the question asks for a list or enumeration."""
    lowered = question.lower()
    return any(keyword in lowered for keyword in _LIST_KEYWORDS)


def _format_docs(documents: list[Document]) -> str:
    """Join retrieved chunks into a single context string."""
    return "\n\n".join(document.page_content for document in documents)


@dataclass
class RAGAnswer:
    """The generated answer plus the source files it was grounded in."""

    answer: str
    sources: list[str]


class RAGService:
    """Answer questions using retrieval-augmented generation, assembled with LCEL."""

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

    def _retrieval_k(self, question: str) -> int:
        """Choose how many chunks to retrieve (larger for list questions)."""
        if is_list_question(question):
            return max(self.top_k, settings.list_top_k)
        return self.top_k

    def _retrieve(self, question: str) -> list[Document]:
        """Retrieve the chunks most relevant to the question."""
        if self._retriever is not None:
            return self._retriever(question)
        return get_retriever(k=self._retrieval_k(question)).invoke(question)

    def _retriever_runnable(self, question: str) -> Runnable:
        """Return a runnable retriever (wrapping an injected callable)."""
        if self._retriever is not None:
            return RunnableLambda(self._retriever)
        return get_retriever(k=self._retrieval_k(question))

    def _chain(self, question: str) -> Runnable:
        """Build the LCEL chain: retriever | prompt | llm | StrOutputParser."""
        return (
            {
                "context": itemgetter("question") | self._retriever_runnable(question) | _format_docs,
                "question": itemgetter("question"),
                "history": itemgetter("history"),
            }
            | RAG_PROMPT
            | self.llm
            | StrOutputParser()
        )

    def answer(
        self,
        question: str,
        history: list[BaseMessage] | None = None,
    ) -> RAGAnswer:
        """Retrieve, generate an answer, and return it with its sources."""
        documents = self._retrieve(question)
        answer = self._chain(question).invoke(
            {"question": question, "history": history or []}
        )
        sources = sorted(
            {os.path.basename(doc.metadata.get("source", "?")) for doc in documents}
        )
        return RAGAnswer(answer=answer, sources=sources)

    def stream(
        self,
        question: str,
        history: list[BaseMessage] | None = None,
    ) -> Iterator[str]:
        """Yield the answer token by token for a streaming UI."""
        yield from self._chain(question).stream(
            {"question": question, "history": history or []}
        )
