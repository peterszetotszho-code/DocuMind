"""Factory for the DeepSeek chat model used to generate answers."""

from langchain_openai import ChatOpenAI

from rag_dialogue.config import settings


def get_llm(temperature: float = 0.0) -> ChatOpenAI:
    """Build a DeepSeek-backed chat model through the OpenAI-compatible API."""
    if not settings.deepseek_api_key:
        raise ValueError(
            "DEEPSEEK_API_KEY is not set. Add it to your .env file first."
        )
    return ChatOpenAI(
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
        model=settings.deepseek_model,
        temperature=temperature,
    )
