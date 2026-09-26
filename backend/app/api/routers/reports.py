from fastapi import APIRouter

from app.agents.copilot_agent import copilot_agent
from app.schemas import DEFAULT_SESSION_ID

router = APIRouter(prefix="/studies/{study_id}/report", tags=["reports"])


@router.get("")
def generate_report(study_id: str, session_id: str = DEFAULT_SESSION_ID):
    """Executive report draft — requires human approval before release
    (Human Approval Matrix, per CLAUDE.md)."""
    return copilot_agent.generate_report(session_id, study_id)
