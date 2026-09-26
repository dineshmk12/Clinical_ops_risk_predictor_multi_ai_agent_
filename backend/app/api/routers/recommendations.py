from fastapi import APIRouter

from app.agents.recommendation_agent import recommendation_agent
from app.schemas import DEFAULT_SESSION_ID

router = APIRouter(prefix="/studies/{study_id}/recommendations", tags=["recommendations"])


@router.get("")
def recommend(study_id: str, session_id: str = DEFAULT_SESSION_ID):
    return recommendation_agent.recommend(session_id, study_id)
