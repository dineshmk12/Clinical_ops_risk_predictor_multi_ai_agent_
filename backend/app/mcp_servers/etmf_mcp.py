"""eTMF MCP (mock) — electronic Trial Master File stand-in."""
from app.db import SessionLocal
from app.models import Document, TrainingCompliance


def retrieve_documents(study_id: str | None = None, doc_type: str | None = None) -> list[dict]:
    db = SessionLocal()
    try:
        q = db.query(Document)
        if study_id:
            q = q.filter((Document.study_id == study_id) | (Document.study_id.is_(None)))
        if doc_type:
            q = q.filter(Document.doc_type == doc_type)
        return [
            {
                "doc_id": d.doc_id,
                "title": d.title,
                "doc_type": d.doc_type,
                "version": d.version,
                "owner": d.owner,
                "effective_date": d.effective_date.isoformat() if d.effective_date else None,
                "content_path": d.content_path,
            }
            for d in q.all()
        ]
    finally:
        db.close()


def site_training_compliance(study_id: str, site_id: str) -> float | None:
    db = SessionLocal()
    try:
        training = (
            db.query(TrainingCompliance)
            .filter(TrainingCompliance.study_id == study_id, TrainingCompliance.site_id == site_id)
            .all()
        )
        return round(sum(t.training_complete_pct for t in training) / len(training), 1) if training else None
    finally:
        db.close()


def audit_status(study_id: str) -> dict:
    db = SessionLocal()
    try:
        training = db.query(TrainingCompliance).filter(TrainingCompliance.study_id == study_id).all()
        avg_training = (
            round(sum(t.training_complete_pct for t in training) / len(training), 1) if training else None
        )
        required_doc_types = {"SOP", "Protocol"}
        present_types = {
            d.doc_type
            for d in db.query(Document).filter((Document.study_id == study_id) | (Document.study_id.is_(None))).all()
        }
        missing = list(required_doc_types - present_types)
        audit_readiness_pct = round(
            (0.5 * (avg_training or 0)) + (0.5 * (100 if not missing else 100 - 25 * len(missing))), 1
        )
        return {
            "study_id": study_id,
            "avg_training_compliance_pct": avg_training,
            "missing_document_types": missing,
            "audit_readiness_pct": max(0.0, min(100.0, audit_readiness_pct)),
        }
    finally:
        db.close()


def inspection_documents(study_id: str) -> list[dict]:
    return retrieve_documents(study_id=study_id, doc_type="Audit Report") + retrieve_documents(
        study_id=study_id, doc_type="CAPA"
    )
