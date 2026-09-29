"""Persist chat conversations to a JSON file."""

import json
from datetime import datetime
from pathlib import Path

from rag_dialogue.config import settings


def conversations_path() -> Path:
    """Return the path of the conversations JSON file."""
    return settings.kb_index_path.parent / "conversations.json"


def load_conversations() -> list[dict]:
    """Load all saved conversations (an empty list when none exist)."""
    path = conversations_path()
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def save_conversations(conversations: list[dict]) -> None:
    """Persist the conversations to disk as JSON."""
    path = conversations_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(conversations, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def new_conversation() -> dict:
    """Create a fresh conversation with a unique id and no messages."""
    return {
        "id": datetime.now().strftime("%Y%m%d_%H%M%S_%f"),
        "title": "新對話",
        "messages": [],
    }
