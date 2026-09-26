"""Audit trail — implements the CLAUDE.md Audit Record Schema. Backs the
post_risk_scoring hook's write_audit_log() action and the long-term memory
(PostgreSQL in the spec; SQLite here) 7-year retention policy."""
from datetime import datetime, timedelta

from app.config import settings
from app.db import SessionLocal
from app.models import AuditLog


def write_audit_log(
    request_id: str,
    session_id: str,
    study_id: str | None,
    agent: str,
    skill: str,
    documents_used: list,
    model_version: str,
    prediction: dict,
    confidence: float | None = None,
    approved_by: str | None = None,
) -> dict:
    db = SessionLocal()
    try:
        record = AuditLog(
            request_id=request_id,
            session_id=session_id,
            study_id=study_id,
            agent=agent,
            skill=skill,
            documents_used=documents_used,
            model_version=model_version,
            prediction=prediction,
            confidence=confidence,
            approved_by=approved_by,
            timestamp=datetime.utcnow(),
            retain_until=datetime.utcnow() + timedelta(days=365 * settings.long_term_memory_retention_years),
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return {
            "id": record.id,
            "request_id": record.request_id,
            "agent": record.agent,
            "skill": record.skill,
            "timestamp": record.timestamp.isoformat(),
        }
    finally:
        db.close()


def get_audit_trail(study_id: str | None = None, limit: int = 100) -> list[dict]:
    db = SessionLocal()
    try:
        q = db.query(AuditLog).order_by(AuditLog.timestamp.desc())
        if study_id:
            q = q.filter(AuditLog.study_id == study_id)
        rows = q.limit(limit).all()
        return [
            {
                "id": r.id,
                "request_id": r.request_id,
                "session_id": r.session_id,
                "study_id": r.study_id,
                "agent": r.agent,
                "skill": r.skill,
                "documents_used": r.documents_used,
                "model_version": r.model_version,
                "prediction": r.prediction,
                "confidence": r.confidence,
                "approved_by": r.approved_by,
                "timestamp": r.timestamp.isoformat(),
            }
            for r in rows
        ]
    finally:
        db.close()
