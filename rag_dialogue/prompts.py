"""Prompt templates used by the RAG pipeline."""

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

SYSTEM_TEMPLATE = (
    "You are a helpful assistant that answers questions using the documents "
    "provided below.\n\n"
    "Context:\n{context}\n\n"
    "Guidelines:\n"
    "- When the context is relevant, answer directly, completely and "
    "confidently. Do not say the information is limited or incomplete when "
    "you have found it.\n"
    "- Reason about the context: you may summarize, compare, and draw "
    "reasonable inferences (for example, determine who a product is suitable "
    "for from its age limits, plan tiers, and payment options). Base every "
    "conclusion on the context and do not invent unsupported facts.\n"
    "- Only say the information is not available in the documents when the "
    "question is clearly unrelated to the context, or the context contains "
    "nothing relevant."
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
