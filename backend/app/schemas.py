from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel

# Default session identifier for API calls made without an explicit session
# (e.g. curl/docs exploration) — used as the default across api/routers/*.py.
DEFAULT_SESSION_ID = "api-session"


class StudyOut(BaseModel):
    study_id: str
    name: str
    phase: Optional[str] = None
    therapeutic_area: Optional[str] = None
    status: Optional[str] = None
    country: Optional[str] = None
    target_enrollment: Optional[int] = None
    start_date: Optional[date] = None

    class Config:
        from_attributes = True


class StudyHealthOut(BaseModel):
    study_id: str
    health_score: float
    health_trend: str
    health_summary: str
    contributing_factors: dict[str, Any]
    confidence: float
    request_id: str


class EnrollmentForecastOut(BaseModel):
    study_id: str
    forecasted_enrollment: float
    delay_probability: float
    confidence: float
    risk_score: float
    request_id: str


class SiteRiskOut(BaseModel):
    site_id: str
    study_id: str
    risk_score: float
    risk_tier: str
    improvement_actions: list[str]
    request_id: str


class MilestonePredictionOut(BaseModel):
    study_id: str
    milestone_type: str
    predicted_date: Optional[date]
    delay_probability: float
    risk_category: str
    request_id: str


class ComplianceOut(BaseModel):
    study_id: str
    compliance_score: float
    findings: list[str]
    escalation_actions: list[str]
    false_positive_estimate: float
    request_id: str
    requires_approval: bool


class RCAOut(BaseModel):
    study_id: str
    contributing_factors: list[str]
    confidence_level: str
    business_narrative: str
    evidence: list[dict[str, Any]]
    request_id: str


class RecommendationOut(BaseModel):
    study_id: str
    risk_score: float
    recommended_action: str
    business_impact: str
    priority_score: float
    evidence: list[dict[str, Any]]
    supporting_documents: list[str]
    explanation: str
    request_id: str
    requires_approval: bool


class CopilotAskIn(BaseModel):
    session_id: str
    study_id: Optional[str] = None
    question: str


class CopilotAskOut(BaseModel):
    answer: str
    grounded: bool
    evidence: list[dict[str, Any]]
    request_id: str
    trace: list[str]


class ApprovalOut(BaseModel):
    id: int
    approval_type: str
    study_id: Optional[str]
    payload: dict[str, Any]
    status: str
    created_at: datetime
    resolved_by: Optional[str]

    class Config:
        from_attributes = True


class ApprovalDecisionIn(BaseModel):
    decision: str  # approved | rejected
    resolved_by: str


class AuditLogOut(BaseModel):
    id: int
    request_id: str
    session_id: Optional[str]
    study_id: Optional[str]
    agent: str
    skill: str
    documents_used: list[Any]
    model_version: str
    prediction: dict[str, Any]
    confidence: Optional[float]
    approved_by: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True
