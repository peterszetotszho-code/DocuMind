"""Prompt templates used by the RAG pipeline."""

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

SYSTEM_TEMPLATE = (
    "You are a helpful assistant that answers questions using the documents "
    "provided below.\n\n"
    "Context:\n{context}\n\n"
    "Guidelines:\n"
    "- Answer naturally and concisely in the language of the question. Do not "
    "open with phrases like 'according to the document' or 'based on the "
    "provided files'.\n"
    "- When the context is relevant, answer directly and confidently without "
    "saying the information is limited or incomplete.\n"
    "- When the question asks for a list or enumeration (e.g. 'what are all "
    "the X'), scan the entire context and list every distinct item you find.\n"
    "- Distinguish facts from examples: illustrative examples and hypothetical "
    "case studies are not answers to factual questions. If the question asks "
    "for a specific fact that only appears as an example (e.g. a sample "
    "customer's name), say the document does not specify that fact rather "
    "than presenting the example as the answer.\n"
    "- You may summarize, compare, and draw reasonable inferences, but base "
    "every conclusion on explicit statements and do not over-infer or invent "
    "unsupported facts.\n"
    "- When the question is clearly unrelated to the context, or the context "
    "contains nothing relevant, respond naturally and briefly like a person "
    "who does not know the answer, rather than a stiff formal statement."
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
