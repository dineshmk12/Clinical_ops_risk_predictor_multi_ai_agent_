"""Hook 05: human_review_required — enqueues await_approval() for
compliance risk, audit findings, and executive reports (Human Approval
Matrix, per CLAUDE.md)."""
from app.approval.approval_queue import requires_approval, enqueue


def await_approval(approval_type: str, study_id: str | None, payload: dict) -> dict | None:
    if not requires_approval(approval_type):
        return None
    return enqueue(approval_type, study_id, payload)
