"""Hook 02: pre_risk_scoring — validates study context before any risk
scoring skill runs."""
from app.mcp_servers.ctms_mcp import get_studies


def validate_context(study_id: str) -> dict:
    studies = get_studies(study_id=study_id)
    if not studies:
        return {"valid": False, "reason": f"unknown study_id '{study_id}'"}
    study = studies[0]
    if study.get("status") not in ("Active",):
        return {"valid": False, "reason": f"study '{study_id}' is not active (status={study.get('status')})"}
    return {"valid": True, "study": study}
