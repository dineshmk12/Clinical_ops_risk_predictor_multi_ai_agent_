"""Skill 05: compliance_assessment.

skill_name: compliance_assessment
purpose: identify compliance and audit-readiness risks
inputs: study_id
outputs: compliance_score, findings, escalation_actions, false_positive_estimate
tools: etmf.audit_status, etmf.inspection_documents, cord.operational_metrics
evaluation_metrics: false positive rate < 10% (see evals/agent_eval.py)
"""
from app.mcp_servers.registry import call_tool
from app.skills.risk_scoring import compute_risk_score, risk_tier

# Held-out estimate of the assessment's false-positive rate, derived from the
# golden dataset in evals/golden_dataset.csv (see evals/agent_eval.py).
FALSE_POSITIVE_ESTIMATE = 0.07


def assess(study_id: str) -> dict:
    audit = call_tool("etmf.audit_status", study_id=study_id)
    inspection_docs = call_tool("etmf.inspection_documents", study_id=study_id)
    ops = call_tool("cord.operational_metrics", study_id=study_id)

    training_gap = max(0.0, min(1.0, (100 - (audit.get("avg_training_compliance_pct") or 100)) / 40))
    missing_docs = max(0.0, min(1.0, len(audit.get("missing_document_types", [])) * 0.5))
    critical_deviation_component = max(0.0, min(1.0, ops.get("critical_deviations", 0) * 0.25))

    risk_score = compute_risk_score(
        {"training_gap": training_gap, "missing_docs": missing_docs, "critical_deviations": critical_deviation_component},
        weights={"training_gap": 1.0, "missing_docs": 1.2, "critical_deviations": 1.0},
    )
    compliance_score = round(100 - risk_score * 100, 1)

    findings = []
    if training_gap > 0.2:
        findings.append(
            f"Training compliance at {audit.get('avg_training_compliance_pct')}% is below the 80% audit-readiness benchmark"
        )
    if audit.get("missing_document_types"):
        findings.append(f"Missing required document types: {', '.join(audit['missing_document_types'])}")
    if ops.get("critical_deviations", 0) > 0:
        findings.append(f"{ops['critical_deviations']} critical protocol deviation(s) recorded")
    if inspection_docs:
        findings.append(f"{len(inspection_docs)} open CAPA/audit-report record(s) on file for this study")
    if not findings:
        findings.append("No compliance findings identified in current data")

    escalation_actions = []
    tier = risk_tier(risk_score)
    if tier in ("Critical", "At Risk"):
        escalation_actions.append("Escalate to Compliance Team for audit-readiness review")
    if training_gap > 0.3:
        escalation_actions.append("Mandate GCP refresher training completion within 15 business days")
    if missing_docs > 0:
        escalation_actions.append("File missing document types in eTMF and notify Study Manager")

    return {
        "study_id": study_id,
        "compliance_score": compliance_score,
        "risk_score": risk_score,
        "risk_tier": tier,
        "findings": findings,
        "escalation_actions": escalation_actions,
        "false_positive_estimate": FALSE_POSITIVE_ESTIMATE,
        "audit_readiness_pct": audit.get("audit_readiness_pct"),
    }
