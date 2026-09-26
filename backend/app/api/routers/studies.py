from fastapi import APIRouter

from app.mcp_servers.registry import call_tool
from app.agents.study_health_agent import study_health_agent

router = APIRouter(prefix="/studies", tags=["studies"])


@router.get("")
def list_studies():
    return call_tool("ctms.get_studies")


@router.get("/{study_id}")
def get_study(study_id: str):
    studies = call_tool("ctms.get_studies", study_id=study_id)
    if not studies:
        return {"error": f"study '{study_id}' not found"}
    return studies[0]


@router.get("/{study_id}/health")
def get_study_health(study_id: str, session_id: str = "api-session"):
    return study_health_agent.assess(session_id, study_id)
