"""Authentication and role-based access control for the demo app."""

import hashlib
import hmac

_SALT = "rag-dialogue-demo-salt"


def _hash(password: str) -> str:
    """Return a salted SHA-256 hex digest of the password."""
    return hashlib.sha256((_SALT + password).encode("utf-8")).hexdigest()


# Demo accounts. Passwords are stored as salted hashes, not plaintext.
_USERS: dict[str, dict[str, str]] = {
    "admin": {"password_hash": _hash("123456"), "role": "admin"},
    "user": {"password_hash": _hash("666666"), "role": "user"},
}


def authenticate(username: str, password: str) -> dict[str, str] | None:
    """Return ``{"username": ..., "role": ...}`` on success, else ``None``."""
    user = _USERS.get(username)
    if user is None:
        return None
    if not hmac.compare_digest(_hash(password), user["password_hash"]):
        return None
    return {"username": username, "role": user["role"]}
