from fastapi import APIRouter

from app.agents.rca_agent import rca_agent
from app.schemas import DEFAULT_SESSION_ID

router = APIRouter(prefix="/studies/{study_id}/rca", tags=["rca"])


@router.get("")
def analyze(study_id: str, session_id: str = DEFAULT_SESSION_ID):
    return rca_agent.analyze(session_id, study_id)
