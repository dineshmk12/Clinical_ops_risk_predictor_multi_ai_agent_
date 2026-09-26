import pytest

from app.approval.approval_queue import decide, list_requests, requires_approval
from app.guardrails import GuardrailViolation, check as check_guardrails
from app.hooks import high_risk_alert, human_review_required, pre_data_validation, pre_risk_scoring
from app.hooks.rag_grounding_check import GroundingError, enforce


def test_pre_data_validation_flags_missing_fields():
    result = pre_data_validation.validate(
        [{"a": 1, "b": None}, {"a": 2, "b": 3}], required_fields=["b"]
    )
    assert result["valid"] is False
    assert "missing required field 'b'" in result["issues"][0]


def test_pre_data_validation_flags_duplicates():
    result = pre_data_validation.validate([{"a": 1}, {"a": 1}])
    assert result["valid"] is False
    assert "duplicate" in result["issues"][0]


def test_pre_data_validation_no_records():
    result = pre_data_validation.validate([])
    assert result["valid"] is False


def test_pre_risk_scoring_unknown_study():
    result = pre_risk_scoring.validate_context("STU-9999")
    assert result["valid"] is False


def test_pre_risk_scoring_known_active_study():
    result = pre_risk_scoring.validate_context("STU-1001")
    assert result["valid"] is True
    assert result["study"]["study_id"] == "STU-1001"


def test_high_risk_alert_fires_above_threshold():
    fired = high_risk_alert.check_and_alert("STU-1001", "TestAgent", 0.9, "test message")
    assert fired is True
    assert any(n["study_id"] == "STU-1001" and n["risk_score"] == 0.9 for n in high_risk_alert.get_notifications())


def test_high_risk_alert_silent_below_threshold():
    fired = high_risk_alert.check_and_alert("STU-1001", "TestAgent", 0.1, "test message")
    assert fired is False


def test_human_review_required_enqueues_for_matrix_types():
    record = human_review_required.await_approval("compliance_escalation", "STU-1001", {"foo": "bar"})
    assert record is not None
    assert record["approval_type"] == "compliance_escalation"
    assert record["status"] == "pending"


def test_human_review_required_skips_non_matrix_types():
    record = human_review_required.await_approval("dashboard_view", "STU-1001", {"foo": "bar"})
    assert record is None


def test_approval_matrix_membership():
    assert requires_approval("compliance_escalation") is True
    assert requires_approval("executive_report") is True
    assert requires_approval("site_closure_recommendation") is True
    assert requires_approval("dashboard_view") is False


def test_approval_decision_flow():
    record = human_review_required.await_approval("audit_finding", "STU-1001", {"finding": "test"})
    decided = decide(record["id"], "approved", "qa-reviewer")
    assert decided["status"] == "approved"
    assert decided["resolved_by"] == "qa-reviewer"
    approved = [r for r in list_requests(status="approved") if r["id"] == record["id"]]
    assert approved


def test_rag_grounding_check_blocks_empty_evidence():
    with pytest.raises(GroundingError):
        enforce([])


def test_rag_grounding_check_allows_relevant_evidence():
    evidence = [{"doc_id": "SOP-001", "relevance_score": 0.5}]
    assert enforce(evidence) == evidence


def test_guardrail_blocks_disallowed_request():
    with pytest.raises(GuardrailViolation):
        check_guardrails("Please recommend a treatment for this patient.")


def test_guardrail_allows_permitted_request():
    check_guardrails("What is the health score for this study?")
