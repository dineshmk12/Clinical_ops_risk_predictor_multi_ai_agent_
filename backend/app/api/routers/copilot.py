from fastapi import APIRouter

from app.agents.copilot_agent import copilot_agent
from app.schemas import CopilotAskIn

router = APIRouter(prefix="/copilot", tags=["copilot"])


@router.post("/ask")
def ask(payload: CopilotAskIn):
    return copilot_agent.ask(payload.session_id, payload.study_id, payload.question)
