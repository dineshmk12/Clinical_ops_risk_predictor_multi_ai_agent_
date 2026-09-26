from app.agents import orchestrator
from app.agents.compliance_agent import compliance_agent
from app.agents.copilot_agent import copilot_agent
from app.agents.enrollment_agent import enrollment_agent
from app.agents.milestone_agent import milestone_agent
from app.agents.site_intelligence_agent import site_intelligence_agent
from app.agents.study_health_agent import study_health_agent
from app.approval.approval_queue import list_requests
from app.guardrails import GuardrailViolation
from app.observability.tracing import get_trace

STUDY_ID = "STU-1003"  # seeded "critical" health profile — exercises escalation paths


def test_study_health_agent_produces_traceable_result():
    result = study_health_agent.assess("test-session", STUDY_ID)
    assert "health_score" in result
    assert result["request_id"]
    trace = get_trace(result["request_id"])
    steps = [s["step"] for s in trace]
    assert "user_request" in steps
    assert "audit_record" in steps


def test_enrollment_agent_returns_risk_score():
    result = enrollment_agent.predict("test-session", STUDY_ID)
    assert 0 <= result["risk_score"] <= 1


def test_site_intelligence_agent_returns_sites():
    result = site_intelligence_agent.assess("test-session", STUDY_ID)
    assert "sites" in result
    assert isinstance(result["sites"], list)


def test_milestone_agent_returns_milestones():
    result = milestone_agent.predict("test-session", STUDY_ID)
    assert "milestones" in result


def test_compliance_agent_escalates_and_requires_approval():
    result = compliance_agent.assess("test-session", STUDY_ID)
    if result["requires_approval"]:
        assert result["approval"] is not None
        pending = list_requests(status="pending")
        assert any(r["id"] == result["approval"]["id"] for r in pending)


def test_orchestrator_classifies_intents():
    assert orchestrator.classify_intents("How is this study doing overall?") == ["health"]
    assert "enrollment" in orchestrator.classify_intents("Why is enrollment behind?")
    assert "compliance" in orchestrator.classify_intents("Are there any audit findings?")


def test_orchestrator_defaults_to_health_when_unmatched():
    assert orchestrator.classify_intents("blah blah blah") == ["health"]


def test_orchestrator_dispatch_aggregates_results():
    results = orchestrator.dispatch("test-session", STUDY_ID, "What is the overall health of this study?")
    assert "health" in results
    assert "health_score" in results["health"]


def test_copilot_ask_rejects_guardrail_violations():
    try:
        copilot_agent.ask("test-session", STUDY_ID, "Please approve the CAPA plan for this site.")
        assert False, "expected GuardrailViolation"
    except GuardrailViolation:
        pass


def test_copilot_ask_requires_study_id():
    try:
        copilot_agent.ask("test-session", None, "What is the overall health?")
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_copilot_ask_returns_grounded_answer_and_trace():
    result = copilot_agent.ask("test-session", STUDY_ID, "What is the overall health of this study?")
    assert result["answer"]
    assert result["intents"] == ["health"]
    assert result["trace"]


def test_copilot_generate_report_requires_approval():
    result = copilot_agent.generate_report("test-session", STUDY_ID)
    assert result["requires_approval"] is True
    assert result["approval"] is not None
