"""CORD MCP (mock) — Clinical Operations Reporting & Data platform stand-in.
Aggregates operational/resource/study-level metrics from the CTMS-seeded data.
"""
from app.db import session_scope
from app.models import Deviation, Query, Resource, EnrollmentRecord, Study, Site


def operational_metrics(study_id: str, site_id: str | None = None) -> dict:
    with session_scope() as db:
        deviation_q = db.query(Deviation).filter(Deviation.study_id == study_id)
        query_q = db.query(Query).filter(Query.study_id == study_id)
        if site_id:
            deviation_q = deviation_q.filter(Deviation.site_id == site_id)
            query_q = query_q.filter(Query.site_id == site_id)

        deviations = deviation_q.all()
        queries = query_q.all()
        closed = [q for q in queries if q.status == "Closed" and q.closed_date]
        resolution_days = [(q.closed_date - q.opened_date).days for q in closed if q.opened_date]
        avg_resolution = round(sum(resolution_days) / len(resolution_days), 1) if resolution_days else None

        result = {
            "study_id": study_id,
            "total_deviations": len(deviations),
            "critical_deviations": len([d for d in deviations if d.severity == "Critical"]),
            "major_deviations": len([d for d in deviations if d.severity == "Major"]),
            "open_queries": len([q for q in queries if q.status == "Open"]),
            "avg_query_resolution_days": avg_resolution,
        }
        if site_id:
            result["site_id"] = site_id
        return result


def site_operational_metrics(study_id: str, site_id: str) -> dict:
    """Site-level drill-down of operational_metrics, used by the Site
    Intelligence skill."""
    return operational_metrics(study_id, site_id=site_id)


def resource_metrics(study_id: str) -> dict:
    with session_scope() as db:
        resources = db.query(Resource).filter(Resource.study_id == study_id).all()
        if not resources:
            return {"study_id": study_id, "roles": [], "overall_utilization_pct": None}
        roles = [
            {
                "role": r.role,
                "allocated_fte": r.allocated_fte,
                "required_fte": r.required_fte,
                "utilization_pct": round((r.allocated_fte / r.required_fte) * 100, 1) if r.required_fte else None,
            }
            for r in resources
        ]
        overall = round(sum(r["utilization_pct"] for r in roles if r["utilization_pct"] is not None) / len(roles), 1)
        return {"study_id": study_id, "roles": roles, "overall_utilization_pct": overall}


def study_metrics(study_id: str) -> dict:
    with session_scope() as db:
        study = db.query(Study).filter(Study.study_id == study_id).first()
        if not study:
            return {"study_id": study_id, "error": "not found"}
        total_enrolled = (
            db.query(EnrollmentRecord).filter(EnrollmentRecord.study_id == study_id).all()
        )
        enrolled_sum = sum(r.subjects_enrolled for r in total_enrolled)
        site_count = db.query(Site).filter(Site.study_id == study_id).count()
        achievement_pct = (
            round((enrolled_sum / study.target_enrollment) * 100, 1) if study.target_enrollment else None
        )
        return {
            "study_id": study_id,
            "target_enrollment": study.target_enrollment,
            "actual_enrollment": enrolled_sum,
            "enrollment_achievement_pct": achievement_pct,
            "site_count": site_count,
        }
