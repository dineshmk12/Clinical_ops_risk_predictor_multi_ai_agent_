from fastapi import APIRouter

from app.agents.site_intelligence_agent import site_intelligence_agent
from app.mcp_servers.registry import call_tool
from app.schemas import DEFAULT_SESSION_ID

router = APIRouter(prefix="/studies/{study_id}/sites", tags=["sites"])


@router.get("")
def list_sites(study_id: str):
    return call_tool("ctms.get_sites", study_id=study_id)


@router.get("/risk")
def site_risk(study_id: str, session_id: str = DEFAULT_SESSION_ID):
    return site_intelligence_agent.assess(session_id, study_id)
