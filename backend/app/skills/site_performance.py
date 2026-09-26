"""Skill 03: site_performance.

skill_name: site_performance
purpose: score and rank sites within a study to detect underperformance
inputs: study_id
outputs: per-site risk_score, risk_tier, improvement_actions
tools: ctms.get_sites, cord.site_operational_metrics, etmf.site_training_compliance
evaluation_metrics: precision > 80% (see evals/agent_eval.py)
"""
from app.mcp_servers.registry import call_tool
from app.skills.risk_scoring import clamp, compute_risk_score, risk_tier


def _activation_component(site: dict) -> float:
    delay = site.get("activation_delay_days")
    if delay is None:
        return 0.3
    return clamp(delay / 90)


def _deviation_component(ops: dict) -> float:
    score = ops.get("critical_deviations", 0) * 0.3 + ops.get("major_deviations", 0) * 0.15
    return clamp(score)


def _query_component(ops: dict) -> float:
    avg_resolution = ops.get("avg_query_resolution_days")
    if avg_resolution is None:
        return 0.2
    return clamp(avg_resolution / 45)


def _training_component(training_pct: float | None) -> float:
    if training_pct is None:
        return 0.3
    return clamp((100 - training_pct) / 40)


def _improvement_actions(components: dict[str, float]) -> list[str]:
    actions = []
    if components["activation"] > 0.4:
        actions.append("Escalate site activation delay per SOP-001; request documented recovery plan")
    if components["deviations"] > 0.3:
        actions.append("Increase monitoring visit cadence to monthly per SOP-001 deviation threshold")
    if components["queries"] > 0.4:
        actions.append("Initiate CAPA for query resolution time exceeding 30-day SOP threshold")
    if components["training"] > 0.4:
        actions.append("Schedule GCP refresher training to close compliance gap")
    if not actions:
        actions.append("No corrective action required — continue standard monitoring cadence")
    return actions


def score_sites(study_id: str) -> list[dict]:
    sites = call_tool("ctms.get_sites", study_id=study_id)
    results = []
    for site in sites:
        ops = call_tool("cord.site_operational_metrics", study_id=study_id, site_id=site["site_id"])
        training_pct = call_tool("etmf.site_training_compliance", study_id=study_id, site_id=site["site_id"])

        components = {
            "activation": _activation_component(site),
            "deviations": _deviation_component(ops),
            "queries": _query_component(ops),
            "training": _training_component(training_pct),
        }
        score = compute_risk_score(
            components, weights={"activation": 1.0, "deviations": 1.2, "queries": 1.0, "training": 0.8}
        )
        results.append(
            {
                "site_id": site["site_id"],
                "study_id": study_id,
                "risk_score": score,
                "risk_tier": risk_tier(score),
                "components": components,
                "improvement_actions": _improvement_actions(components),
            }
        )
    return sorted(results, key=lambda r: r["risk_score"], reverse=True)
