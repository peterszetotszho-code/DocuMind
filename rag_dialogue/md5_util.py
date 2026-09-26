"""Helpers for computing MD5 digests used to deduplicate uploads."""

import hashlib
from pathlib import Path

_CHUNK_SIZE = 8192


def get_file_md5(path: str | Path) -> str:
    """Return the MD5 hex digest of a file's contents.

    Used to detect whether an uploaded file has already been indexed so that
    unchanged files can be skipped during knowledge-base updates.
    """
    digest = hashlib.md5()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(_CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()
