"""Persist per-user chat conversations to a JSON file."""

import json
from datetime import datetime
from pathlib import Path

from rag_dialogue.config import settings


def conversations_path() -> Path:
    """Return the path of the conversations JSON file."""
    return settings.kb_index_path.parent / "conversations.json"


def _load_all() -> dict:
    """Load the whole ``{username: [conversation, ...]}`` mapping."""
    path = conversations_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _save_all(data: dict) -> None:
    """Persist the whole username-to-conversations mapping to disk."""
    path = conversations_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_conversations(username: str) -> list[dict]:
    """Return the conversations belonging to a user (empty when none)."""
    return _load_all().get(username, [])


def save_conversations(username: str, conversations: list[dict]) -> None:
    """Persist a user's conversations, leaving other users untouched."""
    data = _load_all()
    data[username] = conversations
    _save_all(data)


def new_conversation() -> dict:
    """Create a fresh conversation with a unique id and no messages."""
    return {
        "id": datetime.now().strftime("%Y%m%d_%H%M%S_%f"),
        "title": "新對話",
        "messages": [],
    }
