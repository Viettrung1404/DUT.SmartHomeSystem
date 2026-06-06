from dataclasses import dataclass, asdict
from threading import RLock
from typing import Any


@dataclass
class MemoryContext:
    session_id: str
    user_id: str
    home_id: str | None = None
    last_intent: str | None = None
    last_device_slug: str | None = None
    last_device_name: str | None = None
    last_time_range: str | None = None
    conversation_summary: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class InMemoryStore:
    def __init__(self) -> None:
        self._data: dict[str, MemoryContext] = {}
        self._lock = RLock()

    def _key(self, session_id: str, user_id: str) -> str:
        return f"{user_id}:{session_id}"

    def get(self, session_id: str, user_id: str) -> MemoryContext | None:
        with self._lock:
            return self._data.get(self._key(session_id, user_id))

    def upsert(self, context: MemoryContext) -> None:
        with self._lock:
            self._data[self._key(context.session_id, context.user_id)] = context

    def reset(self, session_id: str, user_id: str) -> None:
        with self._lock:
            self._data.pop(self._key(session_id, user_id), None)


memory_store = InMemoryStore()

