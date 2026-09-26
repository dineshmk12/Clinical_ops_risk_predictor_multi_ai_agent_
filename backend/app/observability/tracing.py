"""Trace-chain recorder for the CLAUDE.md traceability requirement:
User Request -> Agent -> Skill -> MCP Tool -> Retrieved Documents ->
Model Version -> Prediction -> Recommendation -> Approval -> Audit Record."""
import threading
from collections import defaultdict
from datetime import datetime

_lock = threading.Lock()
_traces: dict[str, list[dict]] = defaultdict(list)


def add_step(request_id: str, step: str, detail: str = "") -> None:
    with _lock:
        _traces[request_id].append({"step": step, "detail": detail, "timestamp": datetime.utcnow().isoformat()})


def get_trace(request_id: str) -> list[dict]:
    with _lock:
        return list(_traces.get(request_id, []))
