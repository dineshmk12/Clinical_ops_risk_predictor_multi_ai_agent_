"""Hook 03: post_risk_scoring — creates the audit trail entry for a
completed risk-scoring (or other agent) action."""
from app.audit.audit_log import write_audit_log


def create_audit_trail(**kwargs) -> dict:
    return write_audit_log(**kwargs)
