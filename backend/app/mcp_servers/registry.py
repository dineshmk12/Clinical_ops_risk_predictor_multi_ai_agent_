"""Mock MCP tool registry — a simple name-based dispatcher standing in for
real MCP tool registration/transport. Swap for real MCP client wiring later
without changing any skill or agent code (they only call `call_tool`).
"""
from app.mcp_servers import ctms_mcp, camp_mcp, cord_mcp, etmf_mcp, sharepoint_mcp
from app.observability.metrics import Timer, record_mcp_call

TOOLS = {
    "ctms.get_studies": ctms_mcp.get_studies,
    "ctms.get_sites": ctms_mcp.get_sites,
    "ctms.get_enrollment": ctms_mcp.get_enrollment,
    "ctms.get_milestones": ctms_mcp.get_milestones,
    "ctms.get_resources": ctms_mcp.get_resources,
    "camp.startup_status": camp_mcp.startup_status,
    "camp.activation_status": camp_mcp.activation_status,
    "camp.approval_status": camp_mcp.approval_status,
    "cord.operational_metrics": cord_mcp.operational_metrics,
    "cord.site_operational_metrics": cord_mcp.site_operational_metrics,
    "cord.resource_metrics": cord_mcp.resource_metrics,
    "cord.study_metrics": cord_mcp.study_metrics,
    "etmf.retrieve_documents": etmf_mcp.retrieve_documents,
    "etmf.audit_status": etmf_mcp.audit_status,
    "etmf.site_training_compliance": etmf_mcp.site_training_compliance,
    "etmf.inspection_documents": etmf_mcp.inspection_documents,
    "sharepoint.search_documents": sharepoint_mcp.search_documents,
    "sharepoint.retrieve_sops": sharepoint_mcp.retrieve_sops,
    "sharepoint.retrieve_lessons_learned": sharepoint_mcp.retrieve_lessons_learned,
}


def call_tool(name: str, **kwargs):
    if name not in TOOLS:
        raise ValueError(f"Unknown MCP tool: {name}")
    timer = Timer()
    try:
        result = TOOLS[name](**kwargs)
        record_mcp_call(name, timer.elapsed_ms(), error=False)
        return result
    except Exception:
        record_mcp_call(name, timer.elapsed_ms(), error=True)
        raise
