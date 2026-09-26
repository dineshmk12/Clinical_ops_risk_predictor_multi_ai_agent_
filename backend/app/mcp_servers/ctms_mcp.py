"""CTMS MCP (mock) — stands in for the real Clinical Trial Management System
MCP server. Exposes the exact function names declared in CLAUDE.md, backed by
the local SQLite database seeded by app.seed_data.
"""
from datetime import date, timedelta

from app.db import SessionLocal
from app.models import Study, Site, EnrollmentRecord, Milestone, Resource


def get_studies(study_id: str | None = None) -> list[dict]:
    db = SessionLocal()
    try:
        q = db.query(Study)
        if study_id:
            q = q.filter(Study.study_id == study_id)
        return [
            {
                "study_id": s.study_id,
                "name": s.name,
                "phase": s.phase,
                "therapeutic_area": s.therapeutic_area,
                "status": s.status,
                "country": s.country,
                "target_enrollment": s.target_enrollment,
                "start_date": s.start_date.isoformat() if s.start_date else None,
            }
            for s in q.all()
        ]
    finally:
        db.close()


def get_sites(study_id: str) -> list[dict]:
    db = SessionLocal()
    try:
        sites = db.query(Site).filter(Site.study_id == study_id).all()
        return [
            {
                "site_id": s.site_id,
                "study_id": s.study_id,
                "country": s.country,
                "pi_name": s.pi_name,
                "status": s.status,
                "planned_activation_date": s.planned_activation_date.isoformat() if s.planned_activation_date else None,
                "actual_activation_date": s.actual_activation_date.isoformat() if s.actual_activation_date else None,
                "activation_delay_days": (
                    (s.actual_activation_date - s.planned_activation_date).days
                    if s.actual_activation_date and s.planned_activation_date
                    else None
                ),
            }
            for s in sites
        ]
    finally:
        db.close()


def get_enrollment(study_id: str, weeks: int = 26) -> list[dict]:
    db = SessionLocal()
    try:
        cutoff = date.today() - timedelta(weeks=weeks)
        records = (
            db.query(EnrollmentRecord)
            .filter(EnrollmentRecord.study_id == study_id, EnrollmentRecord.date >= cutoff)
            .order_by(EnrollmentRecord.date)
            .all()
        )
        return [
            {
                "study_id": r.study_id,
                "site_id": r.site_id,
                "date": r.date.isoformat(),
                "subjects_screened": r.subjects_screened,
                "subjects_enrolled": r.subjects_enrolled,
            }
            for r in records
        ]
    finally:
        db.close()


def get_milestones(study_id: str) -> list[dict]:
    db = SessionLocal()
    try:
        milestones = db.query(Milestone).filter(Milestone.study_id == study_id).all()
        return [
            {
                "study_id": m.study_id,
                "milestone_type": m.milestone_type,
                "planned_date": m.planned_date.isoformat() if m.planned_date else None,
                "actual_date": m.actual_date.isoformat() if m.actual_date else None,
                "status": m.status,
                "delay_days": (
                    (m.actual_date - m.planned_date).days if m.actual_date and m.planned_date else None
                ),
            }
            for m in milestones
        ]
    finally:
        db.close()


def get_resources(study_id: str) -> list[dict]:
    db = SessionLocal()
    try:
        resources = db.query(Resource).filter(Resource.study_id == study_id).all()
        return [
            {
                "study_id": r.study_id,
                "role": r.role,
                "allocated_fte": r.allocated_fte,
                "required_fte": r.required_fte,
                "utilization_pct": round((r.allocated_fte / r.required_fte) * 100, 1) if r.required_fte else None,
            }
            for r in resources
        ]
    finally:
        db.close()
