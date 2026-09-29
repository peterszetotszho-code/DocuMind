from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableLambda

from rag_dialogue.rag_service import RAGService, is_list_question


class FakeLLM(RunnableLambda):
    """A chat model double that records the prompt it received."""

    def __init__(self, answer: str = "fake answer") -> None:
        self.answer = answer
        self.last_messages = None
        super().__init__(self._invoke)

    def _invoke(self, messages):
        self.last_messages = (
            messages.messages if hasattr(messages, "messages") else messages
        )
        return AIMessage(content=self.answer)


def test_answer_returns_answer_and_sources():
    llm = FakeLLM("synthesized answer")
    retriever = lambda _question: [
        Document(page_content="fact a", metadata={"source": "a.pdf"}),
        Document(page_content="fact b", metadata={"source": "b.pdf"}),
    ]
    service = RAGService(llm=llm, retriever=retriever)

    result = service.answer("question?")

    assert result.answer == "synthesized answer"
    assert result.sources == ["a.pdf", "b.pdf"]
    system_message = llm.last_messages[0]
    assert "fact a" in system_message.content
    assert "fact b" in system_message.content


def test_answer_with_history_includes_prior_turns():
    llm = FakeLLM()
    service = RAGService(
        llm=llm,
        retriever=lambda _question: [Document(page_content="ctx")],
    )
    history = [HumanMessage(content="before?"), AIMessage(content="answer")]

    service.answer("now?", history=history)

    role_names = [type(message).__name__ for message in llm.last_messages]
    assert role_names.count("HumanMessage") == 2  # history turn + current question
    assert role_names.count("AIMessage") == 1


def test_is_list_question_detects_enumeration():
    assert is_list_question("資料中有哪些保險產品")
    assert is_list_question("列出所有保障計劃")
    assert is_list_question("list all products")
    assert is_list_question("這三份產品分別有什麼用")
    assert not is_list_question("vhis有什麼特點")
    assert not is_list_question("什麼人適合買")
