from fastapi import APIRouter

from app.agents.enrollment_agent import enrollment_agent
from app.mcp_servers.registry import call_tool

router = APIRouter(prefix="/studies/{study_id}/enrollment", tags=["enrollment"])


@router.get("/forecast")
def forecast(study_id: str, session_id: str = "api-session"):
    return enrollment_agent.predict(session_id, study_id)


@router.get("/history")
def history(study_id: str, weeks: int = 26):
    return call_tool("ctms.get_enrollment", study_id=study_id, weeks=weeks)
