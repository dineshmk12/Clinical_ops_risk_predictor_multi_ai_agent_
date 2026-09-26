from fastapi import APIRouter

from app.audit.audit_log import get_audit_trail
from app.observability.tracing import get_trace

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("")
def audit_trail(study_id: str | None = None, limit: int = 100):
    return get_audit_trail(study_id=study_id, limit=limit)


@router.get("/trace/{request_id}")
def trace(request_id: str):
    return get_trace(request_id)
