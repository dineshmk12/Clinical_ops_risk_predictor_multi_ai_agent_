"""Skill 04: milestone_prediction.

skill_name: milestone_prediction
purpose: predict delay risk and expected date for upcoming study milestones
inputs: study_id
outputs: predicted_date, delay_probability, risk_category per milestone
tools: ctms.get_milestones, camp.activation_status
evaluation_metrics: prediction accuracy > 85% (see evals/agent_eval.py)

Uses historical delay-chain propagation (delay observed on completed
milestones + site activation delay ratio) as a lightweight stand-in for the
XGBoost/Prophet/LSTM models named in CLAUDE.md.
"""
from datetime import date, timedelta

from app.mcp_servers.registry import call_tool
from app.skills.risk_scoring import compute_risk_score, risk_tier


def predict(study_id: str) -> list[dict]:
    milestones = call_tool("ctms.get_milestones", study_id=study_id)
    activation = call_tool("camp.activation_status", study_id=study_id)

    completed = [m for m in milestones if m["actual_date"]]
    observed_delays = [m["delay_days"] for m in completed if m["delay_days"] is not None]
    avg_delay = sum(observed_delays) / len(observed_delays) if observed_delays else 0
    delayed_ratio = (
        activation["delayed_sites"] / activation["total_sites"] if activation.get("total_sites") else 0.0
    )

    results = []
    for m in milestones:
        if m["actual_date"]:
            delay_days = m["delay_days"] or 0
            delay_probability = 1.0 if delay_days > 0 else 0.0
            results.append(
                {
                    "study_id": study_id,
                    "milestone_type": m["milestone_type"],
                    "predicted_date": m["actual_date"],
                    "delay_probability": delay_probability,
                    "risk_category": risk_tier(delay_probability) if delay_days else "Healthy",
                    "status": "Completed",
                }
            )
            continue

        historical_component = max(0.0, min(1.0, avg_delay / 60))
        delay_probability = compute_risk_score(
            {"historical_delay": historical_component, "site_activation_delay": delayed_ratio},
            weights={"historical_delay": 1.0, "site_activation_delay": 1.0},
        )
        planned = m["planned_date"]
        predicted_date = None
        if planned:
            planned_date = date.fromisoformat(planned) if isinstance(planned, str) else planned
            predicted_date = (planned_date + timedelta(days=round(avg_delay))).isoformat()

        results.append(
            {
                "study_id": study_id,
                "milestone_type": m["milestone_type"],
                "predicted_date": predicted_date,
                "delay_probability": delay_probability,
                "risk_category": risk_tier(delay_probability),
                "status": m["status"],
            }
        )
    return results
