"""Short-term memory — stand-in for Redis, 24h retention as specified in
CLAUDE.md. In-process TTL cache; swap for a real Redis client later without
changing the get/set interface."""
import threading
import time

from app.config import settings

_store: dict[str, tuple[float, object]] = {}
_lock = threading.Lock()


def set(key: str, value: object, ttl_hours: float | None = None) -> None:
    ttl = (ttl_hours if ttl_hours is not None else settings.short_term_memory_ttl_hours) * 3600
    with _lock:
        _store[key] = (time.time() + ttl, value)


def get(key: str) -> object | None:
    with _lock:
        entry = _store.get(key)
        if entry is None:
            return None
        expires_at, value = entry
        if time.time() > expires_at:
            del _store[key]
            return None
        return value


def clear_expired() -> int:
    now = time.time()
    with _lock:
        expired = [k for k, (exp, _) in _store.items() if now > exp]
        for k in expired:
            del _store[k]
        return len(expired)
