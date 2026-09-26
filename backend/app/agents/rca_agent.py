"""AGENT-06: Root Cause Analysis Agent — explains WHY a risk exists.
Outputs: contributing factors, confidence level, business narrative
(Development Principle 1: every recommendation must be explainable)."""
from app.agents.base import BaseAgent
from app.llm import generate
from app.skills import root_cause_analysis

SYSTEM_PROMPT = (
    "You are the Root Cause Analysis Agent for a clinical trial operations platform. "
    "Explain, in 3-5 sentences, why a clinical study is at risk, using ONLY the "
    "structured factors and evidence excerpts provided. Cite document IDs in "
    "parentheses when referencing evidence. Do not recommend treatments, diagnoses, "
    "or any change to clinical/enrollment data — explain operational risk drivers only."
)


class RCAAgent(BaseAgent):
    name = "RCAAgent"
    model_version = "claude-sonnet-5"

    def analyze(self, session_id: str, study_id: str) -> dict:
        rca = root_cause_analysis.analyze(study_id)

        factors_text = "\n".join(f"- {f['factor']} (magnitude {f['magnitude']}): {f['detail']}" for f in rca["contributing_factors"])
        evidence_text = "\n".join(f"- ({e['doc_id']}) {e['title']}: {e['excerpt'][:200]}" for e in rca["evidence"])
        user_prompt = (
            f"Study: {study_id}\n\nContributing factors:\n{factors_text or 'None identified'}\n\n"
            f"Evidence:\n{evidence_text or 'None retrieved'}\n\nWrite the business narrative."
        )
        narrative = generate(SYSTEM_PROMPT, user_prompt)

        return self.execute(
            session_id=session_id,
            study_id=study_id,
            skill_name="root_cause_analysis",
            fn=lambda: {
                "contributing_factors": [f["factor"] for f in rca["contributing_factors"]],
                "confidence_level": rca["confidence_level"],
                "business_narrative": narrative,
            },
            evidence=rca["evidence"],
        )


rca_agent = RCAAgent()
