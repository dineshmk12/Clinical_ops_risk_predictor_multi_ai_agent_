"""Skill 07: recommendation_engine.

skill_name: recommendation_engine
purpose: generate prescriptive intervention recommendations
inputs: study_id, contributing_factors (from root_cause_analysis)
outputs: recommended_action, business_impact, priority_score, evidence
tools: skills.root_cause_analysis, skills.document_retrieval
evaluation_metrics: recommendation acceptance > 70% (see CLAUDE.md AI Success Metrics)

The action library below is rule-based (mapped from factor -> action), so
every recommendation traces back to a specific data-driven factor
(Development Principle 3: grounded in evidence).
"""
from app.skills import document_retrieval, root_cause_analysis

ACTION_LIBRARY = {
    "Enrollment pace below plan": {
        "action": "Activate 2-3 backup sites in high-performing countries and reallocate enrollment targets across the country mix",
        "impact": "Recovers enrollment timeline; lessons-learned data shows this approach closes gaps ~3 months faster than waiting for existing sites to ramp",
    },
    "Underperforming sites": {
        "action": "Escalate flagged sites to monthly monitoring cadence and issue CAPA plans for sites exceeding query-resolution thresholds",
        "impact": "Reduces protocol deviations and query backlog, improving site productivity score",
    },
    "Milestone slippage": {
        "action": "Convene a milestone recovery review with Study Manager to re-baseline downstream milestone dates and add resourcing to critical path",
        "impact": "Improves milestone predictability and reduces downstream CSR/closeout risk",
    },
    "Operational quality gaps": {
        "action": "Increase CRA monitoring visit frequency and expedite CAPA closure for open critical deviations",
        "impact": "Improves audit readiness and reduces inspection finding risk",
    },
    "Resource under-allocation": {
        "action": "Reallocate FTEs from lower-risk studies or request incremental headcount for under-resourced roles",
        "impact": "Reduces resource bottleneck risk and supports on-time milestone delivery",
    },
}

DEFAULT_ACTION = {
    "action": "Continue standard monitoring cadence; no intervention required at this time",
    "impact": "Maintains current study health trajectory",
}


def generate(study_id: str) -> dict:
    rca = root_cause_analysis.analyze(study_id)
    factors = rca["contributing_factors"]

    if not factors:
        top_action = DEFAULT_ACTION
        priority_score = 0.1
        risk_score = 0.1
    else:
        top_factor = factors[0]
        top_action = ACTION_LIBRARY.get(top_factor["factor"], DEFAULT_ACTION)
        priority_score = round(top_factor["magnitude"], 3)
        risk_score = priority_score

    evidence = rca["evidence"] or document_retrieval.retrieve_evidence(
        f"recommendation for {study_id}", top_k=5
    )

    explanation = (
        f"Recommendation driven by: {factors[0]['factor']} (magnitude {factors[0]['magnitude']})"
        if factors
        else "No significant risk drivers identified in current data"
    )

    return {
        "study_id": study_id,
        "risk_score": risk_score,
        "recommended_action": top_action["action"],
        "business_impact": top_action["impact"],
        "priority_score": priority_score,
        "evidence": evidence,
        "supporting_documents": [e["doc_id"] for e in evidence],
        "explanation": explanation,
        "contributing_factors": factors,
    }
