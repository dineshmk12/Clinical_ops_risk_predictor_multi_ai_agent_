"""Skill 01: risk_scoring — shared weighted risk aggregator used by every
specialist agent to combine domain sub-scores into a single 0-1 risk score.

skill_name: risk_scoring
purpose: combine weighted risk components into a single normalized score
inputs: components (dict[str, float] each 0-1), weights (dict[str, float])
outputs: risk_score (float 0-1), risk_tier (str)
tools: none (pure function)
evaluation_metrics: n/a (deterministic aggregation used by scored agents)
"""
from app.config import settings


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def compute_risk_score(components: dict[str, float], weights: dict[str, float] | None = None) -> float:
    if not components:
        return 0.0
    weights = weights or {k: 1.0 for k in components}
    total_weight = sum(weights.get(k, 1.0) for k in components) or 1.0
    score = sum(components[k] * weights.get(k, 1.0) for k in components) / total_weight
    return round(clamp(score), 3)


def risk_tier(risk_score: float) -> str:
    if risk_score >= settings.risk_tier_critical_threshold:
        return "Critical"
    if risk_score >= settings.risk_tier_at_risk_threshold:
        return "At Risk"
    return "Healthy"
