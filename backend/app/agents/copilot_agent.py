"""AGENT-08: Clinical Operations Copilot — natural language interface for
all platform intelligence (ask questions, summarize risks, retrieve
evidence, explain recommendations)."""
import json

from app.agents import orchestrator
from app.agents.base import BaseAgent
from app.guardrails import check as check_guardrails
from app.llm import generate
from app.memory import short_term
from app.observability.tracing import get_trace
from app.skills import executive_reporting

SYSTEM_PROMPT = (
    "You are the Clinical Operations Copilot for a clinical trial risk platform. "
    "Answer the user's question using ONLY the structured agent data provided below. "
    "Always state the relevant risk score(s) and cite supporting document IDs in "
    "parentheses when evidence is present. If data is insufficient, say so plainly. "
    "You MAY NOT recommend treatments, diagnoses, protocol amendments, regulatory "
    "filings, or changes to clinical/enrollment data — you may only predict risks, "
    "explain risks, recommend operational actions, and summarize evidence."
)


class CopilotAgent(BaseAgent):
    name = "CopilotAgent"
    model_version = "claude-sonnet-5"

    def ask(self, session_id: str, study_id: str | None, question: str) -> dict:
        check_guardrails(question)

        if not study_id:
            raise ValueError("study_id is required for this prototype's Copilot (no portfolio-wide routing yet)")

        agent_results = orchestrator.dispatch(session_id, study_id, question)
        short_term.set(f"copilot:{session_id}", {"question": question, "results": agent_results})

        evidence: list[dict] = []
        for intent_result in agent_results.values():
            if isinstance(intent_result, dict):
                evidence.extend(intent_result.get("evidence", []) or [])

        risk_scores = [
            r.get("risk_score") for r in agent_results.values() if isinstance(r, dict) and r.get("risk_score") is not None
        ]
        max_risk = max(risk_scores) if risk_scores else None

        user_prompt = f"Question: {question}\n\nAgent data:\n{json.dumps(agent_results, indent=2, default=str)}"
        answer = generate(SYSTEM_PROMPT, user_prompt)

        result = self.execute(
            session_id=session_id,
            study_id=study_id,
            skill_name="copilot",
            fn=lambda: {
                "answer": answer,
                "grounded": bool(evidence),
                "evidence": evidence,
                "intents": list(agent_results.keys()),
            },
            risk_score=max_risk,
        )
        result["trace"] = [f"{s['step']}: {s['detail']}" for s in get_trace(result["request_id"])]
        return result

    def generate_report(self, session_id: str, study_id: str) -> dict:
        """Executive Reporting (Skill 09) — always requires human approval
        before release, per the Human Approval Matrix in CLAUDE.md."""
        report = executive_reporting.build_report(study_id)
        return self.execute(
            session_id=session_id,
            study_id=study_id,
            skill_name="executive_reporting",
            fn=lambda: report,
            risk_score=1 - report["health_score"] / 100,
            approval_type="executive_report",
        )


copilot_agent = CopilotAgent()
