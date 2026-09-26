"""Claude API client wrapper used by the narrative-generating agents (RCA,
Recommendation, Copilot). Falls back to a deterministic templated narrative
if no ANTHROPIC_API_KEY is configured, so the platform still runs end-to-end
without live API calls."""
from anthropic import Anthropic

from app.config import settings
from app.observability.metrics import Timer, record_llm_usage

_client: Anthropic | None = None


def _get_client() -> Anthropic | None:
    global _client
    if not settings.anthropic_api_key:
        return None
    if _client is None:
        _client = Anthropic(api_key=settings.anthropic_api_key)
    return _client


def generate(system_prompt: str, user_prompt: str, max_tokens: int = 600) -> str:
    client = _get_client()
    if client is None:
        return (
            "[LLM disabled — set ANTHROPIC_API_KEY to enable narrative generation]\n"
            + user_prompt[:500]
        )

    timer = Timer()
    response = client.messages.create(
        model=settings.claude_model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    record_llm_usage(
        prompt_tokens=response.usage.input_tokens,
        completion_tokens=response.usage.output_tokens,
        latency_ms=timer.elapsed_ms(),
    )
    return "".join(block.text for block in response.content if block.type == "text")
