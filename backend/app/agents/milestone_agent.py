"""AGENT-04: Milestone Prediction Agent — predicts milestone delays.
KPI: Prediction Accuracy > 85% (see evals/agent_eval.py)."""
from app.agents.base import BaseAgent
from app.bus.schemas import EventType
from app.skills import milestone_prediction


class MilestoneAgent(BaseAgent):
    name = "MilestoneAgent"

    def predict(self, session_id: str, study_id: str) -> dict:
        milestones = milestone_prediction.predict(study_id)
        max_risk = max((m["delay_probability"] for m in milestones), default=0.0)
        result = self.execute(
            session_id=session_id,
            study_id=study_id,
            skill_name="milestone_prediction",
            fn=lambda: {"milestones": milestones, "risk_score": max_risk},
            risk_score=max_risk,
        )
        for m in milestones:
            if m["risk_category"] == "Critical":
                self.publish_event(EventType.MILESTONE_ALERT, study_id, m["delay_probability"])
        return result


milestone_agent = MilestoneAgent()
