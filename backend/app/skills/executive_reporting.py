"""Skill 09: executive_reporting.

skill_name: executive_reporting
purpose: aggregate portfolio/study-level data into an executive summary
inputs: study_id
outputs: structured executive report (requires human approval before release)
tools: skills.study_health_scoring, skills.enrollment_forecasting,
       skills.site_performance, skills.milestone_prediction, skills.compliance_assessment
evaluation_metrics: manual reporting reduction > 50% (see CLAUDE.md AI Success Metrics)
"""
from app.skills import compliance_assessment, enrollment_forecasting, milestone_prediction, site_performance, study_health_scoring


def build_report(study_id: str) -> dict:
    health = study_health_scoring.compute(study_id)
    forecast = enrollment_forecasting.forecast(study_id)
    sites = site_performance.score_sites(study_id)
    milestones = milestone_prediction.predict(study_id)
    compliance = compliance_assessment.assess(study_id)

    high_risk_sites = [s for s in sites if s["risk_tier"] != "Healthy"]
    at_risk_milestones = [m for m in milestones if m["risk_category"] != "Healthy"]

    return {
        "study_id": study_id,
        "health_score": health["health_score"],
        "health_trend": health["health_trend"],
        "health_summary": health["health_summary"],
        "enrollment_forecast": forecast,
        "site_summary": {
            "total_sites": len(sites),
            "high_risk_sites": len(high_risk_sites),
            "site_details": sites,
        },
        "milestone_summary": {
            "at_risk_count": len(at_risk_milestones),
            "milestones": milestones,
        },
        "compliance_summary": compliance,
        "generated_for": "Executive Leadership / Clinical Operations Managers",
    }
