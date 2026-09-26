"""Per-agent evaluation harness for all 8 platform agents (CLAUDE.md Agent
Definitions / Evaluation Framework). Run: `python evals/agent_eval.py` from
the repo root (after `python -m app.seed_data` from `backend/`).

Study-level ground truth: evals/golden_dataset.csv (5 studies).
Site-level ground truth: evals/golden_dataset_sites.csv (28 sites).

Site-level labels are derived independently of site_performance.py's own
weighted risk formula, so Site Intelligence precision is a genuine test
against an external rule rather than a comparison against the model's own
score. A site is labeled expected_at_risk=true if ANY of the following raw
thresholds — each already used elsewhere in this codebase — is exceeded:
  - activation_delay_days > 30      (site activation delay / SOP-001 language)
  - critical_deviations >= 1        (compliance_assessment.py already flags
                                      any critical deviation as a finding)
  - avg_query_resolution_days > 30  (the literal "30-day SOP threshold" in
                                      site_performance.py's _improvement_actions)
  - training_complete_pct < 80      (the literal "80% audit-readiness
                                      benchmark" in compliance_assessment.py)

RCA (AGENT-06) and Recommendation (AGENT-07) have no numeric KPI in CLAUDE.md
(only qualitative outputs are specified), so they are reported as labeled
proxy checks rather than PASS/FAIL against a compliance threshold.

These are illustrative accuracy numbers for a synthetic dataset — see
CLAUDE.md's evaluation framework targets for the production targets this
prototype's rule-based/statistical models are a stand-in for.
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.skills import (
    compliance_assessment,
    enrollment_forecasting,
    milestone_prediction,
    recommendation_engine,
    root_cause_analysis,
    site_performance,
    study_health_scoring,
)


def health_tier(score: float) -> str:
    if score >= 75:
        return "Healthy"
    if score >= 50:
        return "At Risk"
    return "Critical"


def load_csv(path: Path) -> list[dict]:
    with open(path) as f:
        return list(csv.DictReader(f))


def report(label: str, value_pct: float, target_pct: float, comparator: str) -> str:
    passed = value_pct > target_pct if comparator == ">" else value_pct < target_pct
    status = "PASS" if passed else "FAIL"
    return f"{label}: {value_pct:.0f}% ({status}, target {comparator}{target_pct}%)"


def run():
    rows = load_csv(Path(__file__).parent / "golden_dataset.csv")
    site_rows = load_csv(Path(__file__).parent / "golden_dataset_sites.csv")
    site_expected = {(r["study_id"], r["site_id"]): r["expected_at_risk"] == "true" for r in site_rows}

    health_correct = enrollment_correct = milestone_correct = 0
    compliance_fp = compliance_neg_total = 0
    rca_match = rec_match = 0
    site_tp = site_fp = site_fn = 0

    for row in rows:
        study_id = row["study_id"]
        expected_overall_at_risk = row["expected_health_tier"] != "Healthy"

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
        if row["expected_compliance_at_risk"] == "false":
            compliance_neg_total += 1
            compliance_fp += predicted_compliance_at_risk

        sites = site_performance.score_sites(study_id)
        for s in sites:
            expected = site_expected[(study_id, s["site_id"])]
            predicted = s["risk_tier"] != "Healthy"
            if predicted and expected:
                site_tp += 1
            elif predicted and not expected:
                site_fp += 1
            elif not predicted and expected:
                site_fn += 1

        rca = root_cause_analysis.analyze(study_id)
        rca_fires = bool(rca["contributing_factors"])
        rca_match += rca_fires == expected_overall_at_risk

        rec = recommendation_engine.generate(study_id)
        rec_intervenes = rec["recommended_action"] != recommendation_engine.DEFAULT_ACTION["action"]
        rec_match += rec_intervenes == expected_overall_at_risk

        print(
            f"{study_id}: health={predicted_tier} (expected {row['expected_health_tier']}), "
            f"enrollment_at_risk={predicted_enrollment_at_risk}, "
            f"milestone_at_risk={predicted_milestone_at_risk}, "
            f"compliance_at_risk={predicted_compliance_at_risk}, "
            f"rca_fires={rca_fires}, rec_intervenes={rec_intervenes}"
        )

    n = len(rows)
    compliance_fpr = 100 * compliance_fp / compliance_neg_total if compliance_neg_total else 0.0
    site_precision = 100 * site_tp / (site_tp + site_fp) if (site_tp + site_fp) else 0.0
    site_recall = 100 * site_tp / (site_tp + site_fn) if (site_tp + site_fn) else 0.0

    print("\n--- Agent Eval Summary (per CLAUDE.md Agent Definitions) ---")

    print("\nAGENT-01 Study Health Agent")
    print(" ", report("Health Accuracy", 100 * health_correct / n, 85, ">"))

    print("\nAGENT-02 Enrollment Prediction Agent")
    print(" ", report("Forecast Accuracy", 100 * enrollment_correct / n, 85, ">"))

    print("\nAGENT-03 Site Intelligence Agent")
    print(" ", report("Precision", site_precision, 80, ">"))
    print(f"   Recall: {site_recall:.0f}% ({site_tp}/{site_tp + site_fn}, no CLAUDE.md target — reported for context)")

    print("\nAGENT-04 Milestone Prediction Agent")
    print(" ", report("Prediction Accuracy", 100 * milestone_correct / n, 85, ">"))

    print("\nAGENT-05 Compliance Agent")
    print(" ", report("False Positive Rate", compliance_fpr, 10, "<"))

    print("\nAGENT-06 Root Cause Analysis Agent (proxy, no CLAUDE.md KPI)")
    print(f"   Risk-driver detection rate: {100 * rca_match / n:.0f}% ({rca_match}/{n}) — "
          f"fires a contributing factor iff the study is expected at-risk overall")

    print("\nAGENT-07 Recommendation Agent (proxy, no CLAUDE.md KPI)")
    print(f"   Intervention-trigger rate: {100 * rec_match / n:.0f}% ({rec_match}/{n}) — "
          f"recommends a non-default action iff the study is expected at-risk overall")

    print("\nAGENT-08 Clinical Operations Copilot")
    print("   See evals/llm_eval.py — Groundedness/Correctness/Helpfulness >90% targets, guardrail rejection.")


if __name__ == "__main__":
    run()
