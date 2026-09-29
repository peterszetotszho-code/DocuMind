"""Knowledge-base update service: incremental indexing of uploaded files."""

import json
from pathlib import Path

from rag_dialogue.config import settings
from rag_dialogue.document_loaders import SUPPORTED_SUFFIXES, load_document
from rag_dialogue.md5_util import get_file_md5
from rag_dialogue.text_splitter import split_documents
from rag_dialogue.vector_store import add_documents, delete_by_source


def load_index() -> dict[str, str]:
    """Return the ``{filename: md5}`` mapping of already-indexed files."""
    if not settings.kb_index_path.exists():
        return {}
    return json.loads(settings.kb_index_path.read_text(encoding="utf-8"))


def save_index(index: dict[str, str]) -> None:
    """Persist the ``{filename: md5}`` index to disk."""
    settings.kb_index_path.parent.mkdir(parents=True, exist_ok=True)
    settings.kb_index_path.write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def list_uploaded_files() -> list[Path]:
    """List supported files present in the upload directory."""
    if not settings.upload_dir.exists():
        return []
    return [
        path
        for path in settings.upload_dir.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
    ]


def update_knowledge_base() -> list[str]:
    """Index new or changed files and return the names of files processed.

    Files whose MD5 digest already exists in the index are skipped, so only
    new or modified uploads are embedded and stored.
    """
    index = load_index()
    processed: list[str] = []
    for path in list_uploaded_files():
        digest = get_file_md5(path)
        if index.get(path.name) == digest:
            continue
        chunks = split_documents(load_document(path))
        add_documents(chunks)
        index[path.name] = digest
        processed.append(path.name)
    save_index(index)
    return processed


def delete_document(filename: str) -> None:
    """Remove a file from the knowledge base, the vector store, and disk."""
    index = load_index()
    index.pop(filename, None)
    save_index(index)

    delete_by_source(str(settings.upload_dir / filename))

    file_path = settings.upload_dir / filename
    if file_path.exists():
        file_path.unlink()
