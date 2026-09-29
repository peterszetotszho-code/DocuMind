"""ReAct agent with knowledge-base tools, streaming, and call interception."""

from collections.abc import Iterator

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

from rag_dialogue.config import settings
from rag_dialogue.knowledge_base import list_uploaded_files
from rag_dialogue.llm import get_llm
from rag_dialogue.vector_store import retrieve


@tool
def search_knowledge_base(query: str) -> str:
    """Search the uploaded documents for information relevant to the query.

    Args:
        query: The question or search terms to look up in the knowledge base.
    """
    documents = retrieve(query, k=settings.top_k)
    if not documents:
        return "No relevant information found in the knowledge base."
    return "\n\n".join(document.page_content for document in documents)


@tool
def list_knowledge_base_files() -> str:
    """List the names of all documents currently in the knowledge base."""
    files = [path.name for path in list_uploaded_files()]
    if not files:
        return "The knowledge base is empty."
    return "\n".join(f"- {name}" for name in files)


class AgentCallLogger(BaseCallbackHandler):
    """Middleware that intercepts and records the agent's tool calls."""

    def __init__(self) -> None:
        self.steps: list[str] = []

    def on_tool_start(self, serialized, input_str, **kwargs) -> None:
        name = serialized.get("name", "tool") if isinstance(serialized, dict) else "tool"
        self.steps.append(f"🔧 呼叫工具：{name}")

    def on_tool_end(self, output, **kwargs) -> None:
        self.steps.append(f"📄 工具結果：{str(output)[:200]}")


def _build_messages(question: str, history: list[BaseMessage] | None) -> list:
    """Combine prior turns with the current question."""
    messages = list(history or [])
    messages.append(HumanMessage(content=question))
    return messages


def get_agent(language: str = "the language of the question"):
    """Build a ReAct agent with the knowledge-base tools."""
    prompt = f"You are a helpful assistant. Respond in {language}."
    return create_react_agent(
        get_llm(),
        [search_knowledge_base, list_knowledge_base_files],
        prompt=prompt,
    )


def run_agent(
    question: str,
    language: str = "the language of the question",
    history: list[BaseMessage] | None = None,
) -> str:
    """Run the agent (non-streaming) and return its final answer."""
    agent = get_agent(language)
    result = agent.invoke({"messages": _build_messages(question, history)})
    for message in reversed(result["messages"]):
        if isinstance(message, AIMessage) and message.content:
            return message.content
    return ""


def stream_agent(
    question: str,
    logger: AgentCallLogger | None = None,
    language: str = "the language of the question",
    history: list[BaseMessage] | None = None,
) -> Iterator[str]:
    """Stream the agent's final answer token by token.

    Tool calls are intercepted by the provided ``logger`` (or a fresh one).
    """
    logger = logger or AgentCallLogger()
    agent = get_agent(language)
    for chunk, _metadata in agent.stream(
        {"messages": _build_messages(question, history)},
        stream_mode="messages",
        config={"callbacks": [logger]},
    ):
        if isinstance(chunk, AIMessageChunk) and chunk.content:
            yield chunk.content
