"""In-process pub/sub — stand-in for Azure Service Bus. Same JSON message
schema and event types as the spec, so a real Service Bus client can replace
this module later without touching agent/hook code."""
import logging
import threading
from collections import defaultdict
from typing import Callable

from app.bus.schemas import AgentEvent

logger = logging.getLogger(__name__)

_subscribers: dict[str, list[Callable[[dict], None]]] = defaultdict(list)
_history: list[dict] = []
_lock = threading.Lock()


def subscribe(event_type: str, handler: Callable[[dict], None]) -> None:
    _subscribers[event_type].append(handler)


def publish(event: AgentEvent) -> dict:
    payload = event.to_dict()
    with _lock:
        _history.append(payload)
    for handler in _subscribers.get(event.event_type.value, []):
        try:
            handler(payload)
        except Exception:
            logger.error("event handler failed for event_type=%s event_id=%s", event.event_type.value, event.event_id, exc_info=True)
    return payload


def get_history(study_id: str | None = None, limit: int = 100) -> list[dict]:
    with _lock:
        events = list(_history)
    if study_id:
        events = [e for e in events if e["study_id"] == study_id]
    return events[-limit:]
