"""AGENT-07: Recommendation Agent — generates intervention recommendations.
Outputs: recommended action, business impact, priority score. Every
recommendation is grounded in evidence (Grounding Requirement, CLAUDE.md)."""
import logging

from app.agents.base import BaseAgent
from app.llm import generate
from app.skills import recommendation_engine

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are the Recommendation Agent for a clinical trial operations platform. "
    "Given a rule-based recommended action, business impact, and evidence excerpts, "
    "write a 2-4 sentence executive-ready explanation of WHY this action is "
    "recommended, citing document IDs in parentheses. You MAY NOT recommend "
    "treatments, diagnoses, protocol amendments, regulatory filings, or changes to "
    "clinical/enrollment data — operational/administrative actions only."
)


class RecommendationAgent(BaseAgent):
    name = "RecommendationAgent"
    model_version = "claude-sonnet-5"

    def recommend(self, session_id: str, study_id: str) -> dict:
        rec = recommendation_engine.generate(study_id)

        evidence_text = "\n".join(f"- ({e['doc_id']}) {e['title']}: {e['excerpt'][:200]}" for e in rec["evidence"])
        user_prompt = (
            f"Study: {study_id}\nRecommended action: {rec['recommended_action']}\n"
            f"Business impact: {rec['business_impact']}\nPriority score: {rec['priority_score']}\n\n"
            f"Evidence:\n{evidence_text or 'None retrieved'}\n\nWrite the explanation."
        )
        try:
            explanation = generate(SYSTEM_PROMPT, user_prompt)
        except Exception:
            logger.error("LLM generate() failed in RecommendationAgent.recommend", exc_info=True)
            raise

        # Per the Human Approval Matrix, only closure recommendations require
        # sign-off — general recommendations are drafts (no approval needed).
        is_closure = "closure" in rec["recommended_action"].lower()

        return self.execute(
            session_id=session_id,
            study_id=study_id,
            skill_name="recommendation_engine",
            fn=lambda: {
                "risk_score": rec["risk_score"],
                "recommended_action": rec["recommended_action"],
                "business_impact": rec["business_impact"],
                "priority_score": rec["priority_score"],
                "supporting_documents": rec["supporting_documents"],
                "explanation": explanation,
            },
            risk_score=rec["risk_score"],
            evidence=rec["evidence"],
            approval_type="site_closure_recommendation" if is_closure else None,
        )


recommendation_agent = RecommendationAgent()
