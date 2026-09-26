from fastapi import APIRouter

from app.agents.rca_agent import rca_agent

router = APIRouter(prefix="/studies/{study_id}/rca", tags=["rca"])


@router.get("")
def analyze(study_id: str, session_id: str = "api-session"):
    return rca_agent.analyze(session_id, study_id)
