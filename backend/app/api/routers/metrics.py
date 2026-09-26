from fastapi import APIRouter

from app.hooks.high_risk_alert import get_notifications
from app.observability.metrics import snapshot

router = APIRouter(tags=["observability"])


@router.get("/metrics")
def metrics():
    return snapshot()


@router.get("/notifications")
def notifications():
    return get_notifications()
