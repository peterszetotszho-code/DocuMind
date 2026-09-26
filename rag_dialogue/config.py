"""Application configuration loaded from environment variables."""

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
CHROMA_DIR = DATA_DIR / "chroma"

# Load a .env file from the project root when one exists.
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the RAG application.

    Every field can be overridden through an environment variable; sensible
    defaults are provided so the project runs out of the box.
    """

    # DeepSeek chat model (OpenAI-compatible API).
    deepseek_api_key: str = field(
        default_factory=lambda: os.getenv("DEEPSEEK_API_KEY", "")
    )
    deepseek_base_url: str = field(
        default_factory=lambda: os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    )
    deepseek_model: str = field(
        default_factory=lambda: os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    )

    # Local Ollama embedding model.
    ollama_base_url: str = field(
        default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    )
    embedding_model: str = field(
        default_factory=lambda: os.getenv("EMBEDDING_MODEL", "bge-m3")
    )

    # Filesystem locations.
    upload_dir: Path = field(
        default_factory=lambda: Path(os.getenv("UPLOAD_DIR", str(UPLOAD_DIR)))
    )
    chroma_dir: Path = field(
        default_factory=lambda: Path(os.getenv("CHROMA_DIR", str(CHROMA_DIR)))
    )
    kb_index_path: Path = field(
        default_factory=lambda: Path(
            os.getenv("KB_INDEX_PATH", str(DATA_DIR / "kb_index.json"))
        )
    )

    # RAG pipeline parameters.
    chunk_size: int = field(
        default_factory=lambda: int(os.getenv("CHUNK_SIZE", "500"))
    )
    chunk_overlap: int = field(
        default_factory=lambda: int(os.getenv("CHUNK_OVERLAP", "50"))
    )
    top_k: int = field(default_factory=lambda: int(os.getenv("TOP_K", "6")))


settings = Settings()
