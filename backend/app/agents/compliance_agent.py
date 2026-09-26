"""AGENT-05: Compliance Agent — identifies compliance risks.
KPI: False Positive Rate < 10% (see evals/agent_eval.py).
Compliance escalations require human approval (Human Approval Matrix)."""
from app.agents.base import BaseAgent
from app.bus.event_bus import publish
from app.bus.schemas import AgentEvent, EventType
from app.skills import compliance_assessment


class ComplianceAgent(BaseAgent):
    name = "ComplianceAgent"

    def assess(self, session_id: str, study_id: str) -> dict:
        assessment = compliance_assessment.assess(study_id)
        escalate = bool(assessment["escalation_actions"]) and assessment["risk_tier"] != "Healthy"
        result = self.execute(
            session_id=session_id,
            study_id=study_id,
            skill_name="compliance_assessment",
            fn=lambda: assessment,
            risk_score=assessment["risk_score"],
            approval_type="compliance_escalation" if escalate else None,
        )
        if escalate:
            publish(
                AgentEvent(
                    source_agent=self.name,
                    target_agent="Orchestrator",
                    study_id=study_id,
                    risk_score=assessment["risk_score"],
                    event_type=EventType.COMPLIANCE_ALERT,
                )
            )
        return result


compliance_agent = ComplianceAgent()
