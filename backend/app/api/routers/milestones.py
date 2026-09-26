from fastapi import APIRouter

from app.agents.milestone_agent import milestone_agent
from app.schemas import DEFAULT_SESSION_ID

router = APIRouter(prefix="/studies/{study_id}/milestones", tags=["milestones"])


@router.get("/predict")
def predict(study_id: str, session_id: str = DEFAULT_SESSION_ID):
    return milestone_agent.predict(session_id, study_id)
