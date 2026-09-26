"""Agent Orchestrator — supervisor that routes a natural-language request to
one or more specialist agents and aggregates their outputs, per the
Supervisor + Specialist Agents pattern in CLAUDE.md."""
from app.agents.compliance_agent import compliance_agent
from app.agents.enrollment_agent import enrollment_agent
from app.agents.milestone_agent import milestone_agent
from app.agents.rca_agent import rca_agent
from app.agents.recommendation_agent import recommendation_agent
from app.agents.site_intelligence_agent import site_intelligence_agent
from app.agents.study_health_agent import study_health_agent

INTENT_ROUTES = {
    "health": lambda session_id, study_id: study_health_agent.assess(session_id, study_id),
    "enrollment": lambda session_id, study_id: enrollment_agent.predict(session_id, study_id),
    "site": lambda session_id, study_id: site_intelligence_agent.assess(session_id, study_id),
    "milestone": lambda session_id, study_id: milestone_agent.predict(session_id, study_id),
    "compliance": lambda session_id, study_id: compliance_agent.assess(session_id, study_id),
    "root_cause": lambda session_id, study_id: rca_agent.analyze(session_id, study_id),
    "recommendation": lambda session_id, study_id: recommendation_agent.recommend(session_id, study_id),
}

KEYWORD_MAP = {
    "health": ["health", "overall", "status", "how is"],
    "enrollment": ["enroll", "recruit", "screen"],
    "site": ["site", "underperform", "activation"],
    "milestone": ["milestone", "fpi", "lpi", "db lock", "csr", "closeout", "startup"],
    "compliance": ["compliance", "audit", "training", "capa", "inspection"],
    "root_cause": ["why", "root cause", "cause", "driver", "reason"],
    "recommendation": ["recommend", "should we", "what action", "what can we do", "fix"],
}


def classify_intents(question: str) -> list[str]:
    q = question.lower()
    matched = [intent for intent, keywords in KEYWORD_MAP.items() if any(kw in q for kw in keywords)]
    return matched or ["health"]


def dispatch(session_id: str, study_id: str, question: str) -> dict:
    intents = classify_intents(question)
    results = {}
    for intent in intents:
        try:
            results[intent] = INTENT_ROUTES[intent](session_id, study_id)
        except Exception as exc:  # noqa: BLE001 — surfaced to caller per-intent
            results[intent] = {"error": str(exc)}
    return results
