"""Prompt templates used by the RAG pipeline."""

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

SYSTEM_TEMPLATE = (
    "You are a helpful assistant that answers questions using ONLY the context "
    "provided below. If the answer is not in the context, say that you do not "
    "know based on the provided documents.\n\n"
    "Context:\n{context}"
)


def build_messages(
    context: str,
    question: str,
    history: list[tuple[str, str]] | None = None,
) -> list[BaseMessage]:
    """Build the ordered message list sent to the chat model.

    ``history`` is an optional list of ``(role, content)`` turns where the role
    is ``"human"`` or ``"ai"`` (``"user"``/``"assistant"`` are also accepted).
    """
    messages: list[BaseMessage] = [
        SystemMessage(content=SYSTEM_TEMPLATE.format(context=context))
    ]
    for role, content in history or []:
        if role in {"ai", "assistant"}:
            messages.append(AIMessage(content=content))
        else:
            messages.append(HumanMessage(content=content))
    messages.append(HumanMessage(content=question))
    return messages
