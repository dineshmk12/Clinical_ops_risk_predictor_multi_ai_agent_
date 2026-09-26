"""Human Approval Matrix, per CLAUDE.md.

Requires approval: compliance escalations, audit findings, executive
reports, site closure recommendations, study closure recommendations.
No approval required: dashboards, risk visualization, forecasts, reporting
drafts. Backs the human_review_required hook's await_approval() action.
"""
from datetime import datetime

from app.db import SessionLocal
from app.models import ApprovalRequest

REQUIRES_APPROVAL = {
    "compliance_escalation",
    "audit_finding",
    "executive_report",
    "site_closure_recommendation",
    "study_closure_recommendation",
}


def requires_approval(approval_type: str) -> bool:
    return approval_type in REQUIRES_APPROVAL


def enqueue(approval_type: str, study_id: str | None, payload: dict) -> dict:
    db = SessionLocal()
    try:
        req = ApprovalRequest(
            approval_type=approval_type,
            study_id=study_id,
            payload=payload,
            status="pending",
            created_at=datetime.utcnow(),
        )
        db.add(req)
        db.commit()
        db.refresh(req)
        return {"id": req.id, "approval_type": req.approval_type, "status": req.status}
    finally:
        db.close()


def list_requests(status: str | None = None) -> list[dict]:
    db = SessionLocal()
    try:
        q = db.query(ApprovalRequest).order_by(ApprovalRequest.created_at.desc())
        if status:
            q = q.filter(ApprovalRequest.status == status)
        return [
            {
                "id": r.id,
                "approval_type": r.approval_type,
                "study_id": r.study_id,
                "payload": r.payload,
                "status": r.status,
                "created_at": r.created_at.isoformat(),
                "resolved_by": r.resolved_by,
            }
            for r in q.all()
        ]
    finally:
        db.close()


def decide(request_id: int, decision: str, resolved_by: str) -> dict:
    if decision not in ("approved", "rejected"):
        raise ValueError("decision must be 'approved' or 'rejected'")
    db = SessionLocal()
    try:
        req = db.query(ApprovalRequest).filter(ApprovalRequest.id == request_id).first()
        if not req:
            raise ValueError(f"approval request {request_id} not found")
        req.status = decision
        req.resolved_by = resolved_by
        req.resolved_at = datetime.utcnow()
        db.commit()
        return {"id": req.id, "status": req.status, "resolved_by": req.resolved_by}
    finally:
        db.close()
