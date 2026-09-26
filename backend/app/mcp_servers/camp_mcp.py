"""CAMP MCP (mock) — Clinical Activation & Milestone Platform stand-in.
Derives startup/activation/approval status from the CTMS-seeded milestone and
site data (no separate CAMP dataset exists in this prototype).
"""
from datetime import date

from app.db import session_scope
from app.models import Site, Milestone


def startup_status(study_id: str) -> dict:
    with session_scope() as db:
        startup = (
            db.query(Milestone)
            .filter(Milestone.study_id == study_id, Milestone.milestone_type == "Study Startup")
            .first()
        )
        if not startup:
            return {"study_id": study_id, "status": "unknown"}
        delay_days = (
            (startup.actual_date - startup.planned_date).days
            if startup.actual_date and startup.planned_date
            else 0
        )
        return {
            "study_id": study_id,
            "status": startup.status,
            "planned_date": startup.planned_date.isoformat() if startup.planned_date else None,
            "actual_date": startup.actual_date.isoformat() if startup.actual_date else None,
            "delay_days": delay_days,
        }


def activation_status(study_id: str) -> dict:
    with session_scope() as db:
        sites = db.query(Site).filter(Site.study_id == study_id).all()
        total = len(sites)
        activated = [s for s in sites if s.actual_activation_date]
        delayed = [
            s
            for s in activated
            if s.planned_activation_date and (s.actual_activation_date - s.planned_activation_date).days > 30
        ]
        return {
            "study_id": study_id,
            "total_sites": total,
            "activated_sites": len(activated),
            "pending_sites": total - len(activated),
            "delayed_sites": len(delayed),
            "delayed_site_ids": [s.site_id for s in delayed],
        }


def approval_status(study_id: str) -> dict:
    with session_scope() as db:
        milestones = db.query(Milestone).filter(Milestone.study_id == study_id).all()
        due = [m for m in milestones if m.planned_date and m.planned_date <= date.today()]
        completed = [m for m in due if m.status == "Completed"]
        pending_approval = [m.milestone_type for m in due if m.status != "Completed"]
        approval_rate = round(len(completed) / len(due), 2) if due else 1.0
        return {
            "study_id": study_id,
            "milestones_due": len(due),
            "milestones_approved": len(completed),
            "approval_rate": approval_rate,
            "pending_approval_milestones": pending_approval,
        }
