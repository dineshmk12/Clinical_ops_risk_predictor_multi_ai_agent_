from fastapi import APIRouter

from app.agents.milestone_agent import milestone_agent

router = APIRouter(prefix="/studies/{study_id}/milestones", tags=["milestones"])


@router.get("/predict")
def predict(study_id: str, session_id: str = "api-session"):
    return milestone_agent.predict(session_id, study_id)
