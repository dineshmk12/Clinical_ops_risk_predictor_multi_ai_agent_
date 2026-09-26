"""AGENT-02: Enrollment Prediction Agent — predicts future recruitment
performance. KPI: Forecast Accuracy > 85% (see evals/agent_eval.py)."""
from app.agents.base import BaseAgent
from app.bus.event_bus import publish
from app.bus.schemas import AgentEvent, EventType
from app.skills import enrollment_forecasting


class EnrollmentAgent(BaseAgent):
    name = "EnrollmentAgent"

    def predict(self, session_id: str, study_id: str) -> dict:
        forecast = enrollment_forecasting.forecast(study_id)
        risk_score = forecast["delay_probability"]
        result = self.execute(
            session_id=session_id,
            study_id=study_id,
            skill_name="enrollment_forecasting",
            fn=lambda: {**forecast, "risk_score": risk_score},
            risk_score=risk_score,
            confidence=forecast["confidence"],
        )
        if risk_score > 0.5:
            publish(
                AgentEvent(
                    source_agent=self.name,
                    target_agent="Orchestrator",
                    study_id=study_id,
                    risk_score=risk_score,
                    event_type=EventType.ENROLLMENT_RISK_DETECTED,
                )
            )
        return {**result, "risk_score": risk_score}


enrollment_agent = EnrollmentAgent()
