from fastapi import APIRouter

from app.agents.recommendation_agent import recommendation_agent

router = APIRouter(prefix="/studies/{study_id}/recommendations", tags=["recommendations"])


@router.get("")
def recommend(study_id: str, session_id: str = "api-session"):
    return recommendation_agent.recommend(session_id, study_id)
