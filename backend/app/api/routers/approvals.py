from fastapi import APIRouter

from app.approval.approval_queue import decide, list_requests
from app.schemas import ApprovalDecisionIn

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("")
def list_approvals(status: str | None = None):
    return list_requests(status=status)


@router.post("/{request_id}/decision")
def decide_approval(request_id: int, payload: ApprovalDecisionIn):
    return decide(request_id, payload.decision, payload.resolved_by)
