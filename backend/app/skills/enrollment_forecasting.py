"""Skill 02: enrollment_forecasting.

skill_name: enrollment_forecasting
purpose: forecast future enrollment and estimate delay probability
inputs: study_id
outputs: forecasted_enrollment, delay_probability, confidence_score, weekly_rate
tools: ctms.get_enrollment, ctms.get_studies
evaluation_metrics: forecast accuracy > 85% (see evals/agent_eval.py)

Uses a linear-trend regression as a lightweight, dependency-light stand-in
for the XGBoost/Prophet/LSTM models named in CLAUDE.md.
"""
from collections import defaultdict

import numpy as np

from app.mcp_servers.registry import call_tool

PLANNED_ENROLLMENT_WINDOW_WEEKS = 26  # per SOP-002 baseline enrollment curve
FORECAST_HORIZON_WEEKS = 12


def forecast(study_id: str) -> dict:
    enrollment = call_tool("ctms.get_enrollment", study_id=study_id, weeks=26)
    studies = call_tool("ctms.get_studies", study_id=study_id)
    target_enrollment = studies[0]["target_enrollment"] if studies else None

    weekly_totals: dict[str, int] = defaultdict(int)
    for r in enrollment:
        weekly_totals[r["date"]] += r["subjects_enrolled"]

    dates_sorted = sorted(weekly_totals.keys())
    cumulative = np.cumsum([weekly_totals[d] for d in dates_sorted]) if dates_sorted else np.array([0])
    n = len(cumulative)

    if n < 2:
        return {
            "study_id": study_id,
            "forecasted_enrollment": float(cumulative[-1]) if n else 0.0,
            "delay_probability": 0.5,
            "confidence": 0.2,
            "weekly_rate": 0.0,
        }

    x = np.arange(n)
    slope, intercept = np.polyfit(x, cumulative, 1)
    predicted = slope * x + intercept
    residuals = cumulative - predicted
    ss_res = float(np.sum(residuals**2))
    ss_tot = float(np.sum((cumulative - np.mean(cumulative)) ** 2)) or 1.0
    r_squared = max(0.0, 1 - ss_res / ss_tot)

    forecasted_enrollment = float(cumulative[-1] + slope * FORECAST_HORIZON_WEEKS)

    planned_weekly_rate = (target_enrollment / PLANNED_ENROLLMENT_WINDOW_WEEKS) if target_enrollment else slope
    pace_ratio = (slope / planned_weekly_rate) if planned_weekly_rate else 1.0
    delay_probability = round(max(0.0, min(1.0, 1 - pace_ratio)), 3)

    confidence = round(max(0.2, min(0.95, 0.4 + 0.5 * r_squared)), 3)

    return {
        "study_id": study_id,
        "forecasted_enrollment": round(forecasted_enrollment, 1),
        "target_enrollment": target_enrollment,
        "delay_probability": delay_probability,
        "confidence": confidence,
        "weekly_rate": round(float(slope), 2),
        "planned_weekly_rate": round(planned_weekly_rate, 2) if planned_weekly_rate else None,
    }
