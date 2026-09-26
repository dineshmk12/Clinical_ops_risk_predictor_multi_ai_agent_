"""AGENT-03: Site Intelligence Agent — detects underperforming sites.
KPI: Precision > 80% (see evals/agent_eval.py)."""
from app.agents.base import BaseAgent
from app.bus.schemas import EventType
from app.config import settings
from app.skills import site_performance


class SiteIntelligenceAgent(BaseAgent):
    name = "SiteIntelligenceAgent"

    def assess(self, session_id: str, study_id: str) -> dict:
        sites = site_performance.score_sites(study_id)
        max_risk = max((s["risk_score"] for s in sites), default=0.0)
        result = self.execute(
            session_id=session_id,
            study_id=study_id,
            skill_name="site_performance",
            fn=lambda: {"sites": sites, "risk_score": max_risk},
            risk_score=max_risk,
        )
        for site in sites:
            if site["risk_score"] > settings.site_risk_publish_threshold:
                self.publish_event(EventType.SITE_RISK_DETECTED, study_id, site["risk_score"])
        return result


site_intelligence_agent = SiteIntelligenceAgent()
