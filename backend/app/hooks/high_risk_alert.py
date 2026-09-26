"""Hook 04: high_risk_alert — fires send_notification() when
risk_score > HIGH_RISK_THRESHOLD (default 0.85, per CLAUDE.md)."""
import logging

from app.config import settings

logger = logging.getLogger("high_risk_alert")
_notifications: list[dict] = []


def send_notification(study_id: str, agent: str, risk_score: float, message: str) -> dict:
    notification = {"study_id": study_id, "agent": agent, "risk_score": risk_score, "message": message}
    _notifications.append(notification)
    logger.warning("HIGH RISK ALERT [%s] study=%s risk_score=%.2f: %s", agent, study_id, risk_score, message)
    return notification


def check_and_alert(study_id: str, agent: str, risk_score: float, message: str) -> bool:
    if risk_score > settings.high_risk_threshold:
        send_notification(study_id, agent, risk_score, message)
        return True
    return False


def get_notifications() -> list[dict]:
    return list(_notifications)
