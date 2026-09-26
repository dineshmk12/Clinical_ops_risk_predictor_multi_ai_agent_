"""Agent-level evaluation against evals/golden_dataset.csv.

Checks Study Health tier, Enrollment/Milestone/Compliance at-risk flags
produced by the specialist agents' underlying skills against the golden
labels. Run: `python evals/agent_eval.py` from the repo root (after
`python backend/app/seed_data.py`).

These are illustrative accuracy numbers for a synthetic dataset — see
CLAUDE.md's evaluation framework targets (Enrollment 85%, Site 80% precision,
Milestone 85%, Compliance <10% false positive) for the production targets
this prototype's rule-based/statistical models are a stand-in for.
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.skills import compliance_assessment, enrollment_forecasting, milestone_prediction, study_health_scoring


def health_tier(score: float) -> str:
    if score >= 75:
        return "Healthy"
    if score >= 50:
        return "At Risk"
    return "Critical"


def run():
    dataset_path = Path(__file__).parent / "golden_dataset.csv"
    with open(dataset_path) as f:
        rows = list(csv.DictReader(f))

    health_correct = enrollment_correct = milestone_correct = compliance_correct = 0

    for row in rows:
        study_id = row["study_id"]

        health = study_health_scoring.compute(study_id)
        predicted_tier = health_tier(health["health_score"])
        health_correct += predicted_tier == row["expected_health_tier"]

        forecast = enrollment_forecasting.forecast(study_id)
        predicted_enrollment_at_risk = forecast["delay_probability"] > 0.3
        enrollment_correct += str(predicted_enrollment_at_risk).lower() == row["expected_enrollment_at_risk"]

        milestones = milestone_prediction.predict(study_id)
        predicted_milestone_at_risk = any(m["risk_category"] != "Healthy" for m in milestones)
        milestone_correct += str(predicted_milestone_at_risk).lower() == row["expected_milestone_at_risk"]

        compliance = compliance_assessment.assess(study_id)
        predicted_compliance_at_risk = compliance["risk_tier"] != "Healthy"
        compliance_correct += str(predicted_compliance_at_risk).lower() == row["expected_compliance_at_risk"]

        print(
            f"{study_id}: health={predicted_tier} (expected {row['expected_health_tier']}), "
            f"enrollment_at_risk={predicted_enrollment_at_risk}, "
            f"milestone_at_risk={predicted_milestone_at_risk}, "
            f"compliance_at_risk={predicted_compliance_at_risk}"
        )

    n = len(rows)
    print("\n--- Agent Eval Summary ---")
    print(f"Study Health tier accuracy:     {health_correct}/{n} ({100 * health_correct / n:.0f}%)")
    print(f"Enrollment at-risk accuracy:     {enrollment_correct}/{n} ({100 * enrollment_correct / n:.0f}%)")
    print(f"Milestone at-risk accuracy:      {milestone_correct}/{n} ({100 * milestone_correct / n:.0f}%)")
    print(f"Compliance at-risk accuracy:     {compliance_correct}/{n} ({100 * compliance_correct / n:.0f}%)")


if __name__ == "__main__":
    run()
