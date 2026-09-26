"""Lightweight in-process observability — stand-in for Langfuse/OpenTelemetry/
Azure Monitor/Grafana. Tracks the metric categories named in CLAUDE.md
(LLM, agent, RAG, MCP, prediction) and exposes them via GET /metrics."""
import threading
import time
from collections import defaultdict

_lock = threading.Lock()
_counters = defaultdict(int)
_timers = defaultdict(list)


def record_llm_usage(prompt_tokens: int, completion_tokens: int, latency_ms: float) -> None:
    with _lock:
        _counters["llm.prompt_tokens"] += prompt_tokens
        _counters["llm.completion_tokens"] += completion_tokens
        _counters["llm.calls"] += 1
        _timers["llm.latency_ms"].append(latency_ms)


def record_agent_execution(agent: str, duration_ms: float, success: bool) -> None:
    with _lock:
        _counters[f"agent.{agent}.executions"] += 1
        _counters[f"agent.{agent}.{'success' if success else 'failure'}"] += 1
        _timers[f"agent.{agent}.duration_ms"].append(duration_ms)


def record_rag_retrieval(grounded: bool, num_results: int) -> None:
    with _lock:
        _counters["rag.retrievals"] += 1
        _counters["rag.grounded" if grounded else "rag.ungrounded"] += 1
        _timers["rag.num_results"].append(num_results)


def record_mcp_call(tool: str, latency_ms: float, error: bool = False) -> None:
    with _lock:
        _counters[f"mcp.{tool}.calls"] += 1
        if error:
            _counters[f"mcp.{tool}.errors"] += 1
        _timers[f"mcp.{tool}.latency_ms"].append(latency_ms)


def record_prediction(agent: str, confidence: float) -> None:
    with _lock:
        _counters[f"prediction.{agent}.count"] += 1
        _timers[f"prediction.{agent}.confidence"].append(confidence)


def snapshot() -> dict:
    with _lock:
        avg_timers = {k: round(sum(v) / len(v), 3) for k, v in _timers.items() if v}
        return {"counters": dict(_counters), "averages": avg_timers}


class Timer:
    def __init__(self):
        self.start = time.perf_counter()

    def elapsed_ms(self) -> float:
        return (time.perf_counter() - self.start) * 1000
