"""In-memory conversation history used for multi-turn context."""

from collections.abc import Iterator


class ChatHistory:
    """Store a bounded list of ``(role, content)`` turns."""

    def __init__(self, max_turns: int = 10) -> None:
        self.max_turns = max_turns
        self._turns: list[tuple[str, str]] = []

    def add(self, role: str, content: str) -> None:
        """Append a turn and trim to the configured maximum."""
        self._turns.append((role, content))
        if len(self._turns) > self.max_turns:
            self._turns = self._turns[-self.max_turns :]

    def add_user(self, content: str) -> None:
        self.add("human", content)

    def add_assistant(self, content: str) -> None:
        self.add("ai", content)

    @property
    def turns(self) -> list[tuple[str, str]]:
        return list(self._turns)

    def __iter__(self) -> Iterator[tuple[str, str]]:
        return iter(self._turns)

    def __len__(self) -> int:
        return len(self._turns)
