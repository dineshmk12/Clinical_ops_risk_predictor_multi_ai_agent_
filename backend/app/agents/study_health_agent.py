"""AGENT-01: Study Health Agent — assesses overall study health.
KPI: Health Accuracy > 85% (see evals/agent_eval.py)."""
from app.agents.base import BaseAgent
from app.skills import study_health_scoring


class StudyHealthAgent(BaseAgent):
    name = "StudyHealthAgent"

    def assess(self, session_id: str, study_id: str) -> dict:
        return self.execute(
            session_id=session_id,
            study_id=study_id,
            skill_name="study_health_scoring",
            fn=lambda: study_health_scoring.compute(study_id),
        )


study_health_agent = StudyHealthAgent()
