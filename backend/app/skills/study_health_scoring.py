"""Skill 10: study_health_scoring.

skill_name: study_health_scoring
purpose: assess overall study health across enrollment, sites, milestones,
         compliance, and resources
inputs: study_id
outputs: health_score, health_trend, health_summary, contributing_factors
tools: cord.study_metrics, cord.resource_metrics, ctms.get_enrollment,
       skills.site_performance, skills.milestone_prediction, skills.compliance_assessment
evaluation_metrics: health accuracy > 85% (see evals/agent_eval.py)
"""
from collections import defaultdict

from app.mcp_servers.registry import call_tool
from app.skills import compliance_assessment, milestone_prediction, site_performance
from app.skills.risk_scoring import compute_risk_score


def _trend(study_id: str) -> str:
    records = call_tool("ctms.get_enrollment", study_id=study_id, weeks=12)
    weekly = defaultdict(int)
    for r in records:
        weekly[r["date"]] += r["subjects_enrolled"]
    dates = sorted(weekly.keys())
    if len(dates) < 6:
        return "Stable"
    midpoint = len(dates) // 2
    earlier_avg = sum(weekly[d] for d in dates[:midpoint]) / midpoint
    recent_avg = sum(weekly[d] for d in dates[midpoint:]) / (len(dates) - midpoint)
    if recent_avg > earlier_avg * 1.1:
        return "Improving"
    if recent_avg < earlier_avg * 0.9:
        return "Declining"
    return "Stable"


def compute(study_id: str) -> dict:
    study_metrics = call_tool("cord.study_metrics", study_id=study_id)
    resource_metrics = call_tool("cord.resource_metrics", study_id=study_id)
    sites = site_performance.score_sites(study_id)
    milestones = milestone_prediction.predict(study_id)
    compliance = compliance_assessment.assess(study_id)

    achievement = study_metrics.get("enrollment_achievement_pct") or 0
    enrollment_component = max(0.0, min(1.0, (100 - achievement) / 100))
    site_component = (sum(s["risk_score"] for s in sites) / len(sites)) if sites else 0.0
    at_risk_milestones = [m for m in milestones if m["risk_category"] in ("At Risk", "Critical")]
    milestone_component = len(at_risk_milestones) / len(milestones) if milestones else 0.0
    compliance_component = compliance["risk_score"]
    utilization = resource_metrics.get("overall_utilization_pct")
    resource_component = max(0.0, min(1.0, (100 - utilization) / 100)) if utilization is not None else 0.3

    components = {
        "enrollment": enrollment_component,
        "sites": site_component,
        "milestones": milestone_component,
        "compliance": compliance_component,
        "resources": resource_component,
    }
    weights = {"enrollment": 1.2, "sites": 1.0, "milestones": 1.0, "compliance": 1.0, "resources": 0.8}
    risk_score = compute_risk_score(components, weights)
    health_score = round((1 - risk_score) * 100, 1)

    trend = _trend(study_id)

    ranked_factors = sorted(components.items(), key=lambda kv: kv[1], reverse=True)
    top_driver = ranked_factors[0][0] if ranked_factors[0][1] > 0.3 else None
    if health_score >= 75:
        summary = f"Study is healthy (score {health_score}/100), trend {trend.lower()}."
    elif top_driver:
        summary = (
            f"Study health score {health_score}/100 ({trend.lower()} trend); "
            f"primary driver is {top_driver} (component score {round(components[top_driver], 2)})."
        )
    else:
        summary = f"Study health score {health_score}/100 ({trend.lower()} trend); no single dominant risk driver."

    confidence = round(0.6 + 0.3 * min(1.0, len(sites) / 5), 3)

    return {
        "study_id": study_id,
        "health_score": health_score,
        "health_trend": trend,
        "health_summary": summary,
        "contributing_factors": components,
        "confidence": confidence,
    }
