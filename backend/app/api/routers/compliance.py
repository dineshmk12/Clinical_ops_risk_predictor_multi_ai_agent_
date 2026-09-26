from fastapi import APIRouter

from app.agents.compliance_agent import compliance_agent
from app.schemas import DEFAULT_SESSION_ID

router = APIRouter(prefix="/studies/{study_id}/compliance", tags=["compliance"])


@router.get("")
def assess(study_id: str, session_id: str = DEFAULT_SESSION_ID):
    return compliance_agent.assess(session_id, study_id)
