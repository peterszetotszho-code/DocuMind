"""ReAct agent that answers questions using a knowledge-base search tool."""

from langchain_core.messages import AIMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

from rag_dialogue.config import settings
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


def get_agent():
    """Build a ReAct agent equipped with the knowledge-base search tool."""
    return create_react_agent(get_llm(), [search_knowledge_base])


def run_agent(question: str) -> str:
    """Run the agent and return the final answer it produces."""
    agent = get_agent()
    result = agent.invoke({"messages": [("user", question)]})
    for message in reversed(result["messages"]):
        if isinstance(message, AIMessage) and message.content:
            return message.content
    return ""
