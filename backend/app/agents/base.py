"""Shared BaseAgent — implements the governance pipeline every specialist
agent runs through (hooks + audit + observability), so each agent only
needs to implement its own domain logic and call `self.execute(...)`.

Trace chain (per CLAUDE.md Traceability section):
User Request -> Agent -> Skill -> MCP Tool -> Retrieved Documents ->
Model Version -> Prediction -> Recommendation -> Approval -> Audit Record
"""
import uuid

from app.bus.event_bus import publish
from app.bus.schemas import AgentEvent, EventType
from app.hooks import high_risk_alert, human_review_required, post_risk_scoring, pre_risk_scoring
from app.hooks.rag_grounding_check import enforce as enforce_grounding
from app.observability import metrics, tracing


class BaseAgent:
    name: str = "BaseAgent"
    model_version: str = "rule-based-v1"

    def publish_event(self, event_type: EventType, study_id: str, risk_score: float) -> None:
        """Publish an AgentEvent to the Orchestrator — shared by the specialist
        agents that raise risk-detected events (see AGENT COMMUNICATION
        PROTOCOL in CLAUDE.md)."""
        publish(
            AgentEvent(
                source_agent=self.name,
                target_agent="Orchestrator",
                study_id=study_id,
                risk_score=risk_score,
                event_type=event_type,
            )
        )

    def execute(
        self,
        *,
        session_id: str,
        study_id: str | None,
        skill_name: str,
        fn,
        risk_score: float | None = None,
        confidence: float | None = None,
        documents_used: list | None = None,
        evidence: list[dict] | None = None,
        approval_type: str | None = None,
        approval_payload: dict | None = None,
    ) -> dict:
        request_id = str(uuid.uuid4())
        timer = metrics.Timer()
        tracing.add_step(request_id, "user_request", f"agent={self.name} skill={skill_name}")

        if study_id:
            context = pre_risk_scoring.validate_context(study_id)
            if not context["valid"]:
                raise ValueError(context["reason"])
            tracing.add_step(request_id, "pre_risk_scoring", "context validated")

        tracing.add_step(request_id, f"agent:{self.name}")
        result = fn()
        tracing.add_step(request_id, f"skill:{skill_name}")

        if evidence is not None:
            enforce_grounding(evidence)
            metrics.record_rag_retrieval(grounded=True, num_results=len(evidence))
            tracing.add_step(request_id, "retrieved_documents", f"{len(evidence)} document(s)")

        effective_risk_score = risk_score if risk_score is not None else result.get("risk_score")
        effective_confidence = confidence if confidence is not None else result.get("confidence")

        tracing.add_step(request_id, "model_version", self.model_version)
        tracing.add_step(request_id, "prediction", "computed")

        approval_record = None
        if approval_type:
            approval_record = human_review_required.await_approval(
                approval_type, study_id, approval_payload or result
            )
            if approval_record:
                tracing.add_step(request_id, "approval", f"queued id={approval_record['id']}")

        post_risk_scoring.create_audit_trail(
            request_id=request_id,
            session_id=session_id,
            study_id=study_id,
            agent=self.name,
            skill=skill_name,
            documents_used=documents_used or [e.get("doc_id") for e in (evidence or [])],
            model_version=self.model_version,
            prediction=result,
            confidence=effective_confidence,
        )
        tracing.add_step(request_id, "audit_record", "written")

        if effective_risk_score is not None and study_id:
            high_risk_alert.check_and_alert(
                study_id, self.name, effective_risk_score, f"{skill_name} risk_score={effective_risk_score}"
            )

        metrics.record_agent_execution(self.name, timer.elapsed_ms(), success=True)
        if effective_confidence is not None:
            metrics.record_prediction(self.name, effective_confidence)

        return {
            **result,
            "request_id": request_id,
            "requires_approval": bool(approval_type),
            "approval": approval_record,
        }
