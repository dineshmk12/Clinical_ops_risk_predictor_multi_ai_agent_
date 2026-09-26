"""Skill 06: root_cause_analysis.

skill_name: root_cause_analysis
purpose: identify and rank the drivers behind a study's risk profile
inputs: study_id
outputs: ranked contributing_factors, confidence_level, grounding evidence
tools: cord.operational_metrics, cord.resource_metrics, camp.activation_status,
       skills.enrollment_forecasting, skills.site_performance, skills.milestone_prediction,
       skills.document_retrieval
evaluation_metrics: n/a (explainability agent; see AGENT-06 in CLAUDE.md)

Produces the structured factor list the RCA agent turns into a business
narrative via the Claude API — the causal ranking itself is rule-based so
every factor is traceable to an underlying metric (Development Principle 1).
"""
from app.mcp_servers.registry import call_tool
from app.skills import document_retrieval, enrollment_forecasting, milestone_prediction, site_performance


def analyze(study_id: str) -> dict:
    factors = []

    forecast = enrollment_forecasting.forecast(study_id)
    if forecast["delay_probability"] > 0.3:
        factors.append(
            {
                "factor": "Enrollment pace below plan",
                "magnitude": forecast["delay_probability"],
                "detail": f"Weekly enrollment rate {forecast['weekly_rate']} vs planned {forecast.get('planned_weekly_rate')}",
            }
        )

    sites = site_performance.score_sites(study_id)
    high_risk_sites = [s for s in sites if s["risk_score"] > 0.4]
    if high_risk_sites:
        factors.append(
            {
                "factor": "Underperforming sites",
                "magnitude": round(sum(s["risk_score"] for s in high_risk_sites) / len(high_risk_sites), 3),
                "detail": f"{len(high_risk_sites)} of {len(sites)} sites flagged At Risk or Critical: "
                + ", ".join(s["site_id"] for s in high_risk_sites[:5]),
            }
        )

    milestones = milestone_prediction.predict(study_id)
    at_risk_milestones = [m for m in milestones if m["risk_category"] in ("At Risk", "Critical")]
    if at_risk_milestones:
        factors.append(
            {
                "factor": "Milestone slippage",
                "magnitude": round(
                    sum(m["delay_probability"] for m in at_risk_milestones) / len(at_risk_milestones), 3
                ),
                "detail": ", ".join(m["milestone_type"] for m in at_risk_milestones),
            }
        )

    ops = call_tool("cord.operational_metrics", study_id=study_id)
    if ops.get("critical_deviations", 0) > 0 or (ops.get("avg_query_resolution_days") or 0) > 30:
        factors.append(
            {
                "factor": "Operational quality gaps",
                "magnitude": min(1.0, ops.get("critical_deviations", 0) * 0.2 + (ops.get("avg_query_resolution_days") or 0) / 60),
                "detail": f"{ops.get('critical_deviations', 0)} critical deviations, "
                f"avg query resolution {ops.get('avg_query_resolution_days')} days",
            }
        )

    resources = call_tool("cord.resource_metrics", study_id=study_id)
    if resources.get("overall_utilization_pct") is not None and resources["overall_utilization_pct"] < 80:
        factors.append(
            {
                "factor": "Resource under-allocation",
                "magnitude": round((100 - resources["overall_utilization_pct"]) / 100, 3),
                "detail": f"Overall FTE utilization at {resources['overall_utilization_pct']}% of required",
            }
        )

    factors.sort(key=lambda f: f["magnitude"], reverse=True)

    query = " ".join(f["factor"] for f in factors) or f"study {study_id} risk drivers"
    evidence = document_retrieval.retrieve_evidence(query, top_k=5)

    confidence_level = "High" if len(factors) >= 3 else ("Medium" if factors else "Low")

    return {
        "study_id": study_id,
        "contributing_factors": factors,
        "confidence_level": confidence_level,
        "evidence": evidence,
    }
