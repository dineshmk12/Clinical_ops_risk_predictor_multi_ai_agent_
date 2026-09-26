"""Long-term memory — stand-in for PostgreSQL, 7-year audit retention as
specified in CLAUDE.md. Delegates storage to the same SQLite audit_log table
used by app.audit.audit_log; this module is the read-side used for historical
context (e.g. RCA agent pulling prior risk events for a study)."""
from app.audit.audit_log import get_audit_trail
from app.bus.event_bus import get_history


def get_historical_context(study_id: str, limit: int = 20) -> dict:
    return {
        "study_id": study_id,
        "audit_trail": get_audit_trail(study_id=study_id, limit=limit),
        "risk_events": get_history(study_id=study_id, limit=limit),
    }
