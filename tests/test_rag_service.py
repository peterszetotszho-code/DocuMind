from types import SimpleNamespace

from langchain_core.documents import Document

from rag_dialogue.rag_service import RAGService


class FakeLLM:
    """A chat model double that records the messages it received."""

    def __init__(self, answer: str = "fake answer") -> None:
        self.answer = answer
        self.last_messages = None

    def invoke(self, messages):
        self.last_messages = messages
        return SimpleNamespace(content=self.answer)


def test_answer_builds_context_and_prompt():
    llm = FakeLLM("synthesized answer")
    retriever = lambda _question: [
        Document(page_content="fact a"),
        Document(page_content="fact b"),
    ]
    service = RAGService(llm=llm, retriever=retriever)

    result = service.answer("question?")

    assert result == "synthesized answer"
    system_message = llm.last_messages[0]
    assert "fact a" in system_message.content
    assert "fact b" in system_message.content
    assert llm.last_messages[-1].content == "question?"


def test_answer_with_history_includes_prior_turns():
    llm = FakeLLM()
    service = RAGService(
        llm=llm,
        retriever=lambda _question: [Document(page_content="ctx")],
    )
    history = [("human", "who wrote it?"), ("ai", "someone")]

    service.answer("when?", history=history)

    role_names = [type(message).__name__ for message in llm.last_messages]
    assert role_names.count("HumanMessage") == 2  # history turn + current question
    assert role_names.count("AIMessage") == 1


def test_build_context_joins_documents():
    documents = [Document(page_content="one"), Document(page_content="two")]
    assert RAGService.build_context(documents) == "one\n\ntwo"
