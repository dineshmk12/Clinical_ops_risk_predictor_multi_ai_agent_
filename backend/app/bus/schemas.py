"""Agent communication protocol — JSON message schema exactly as declared in
CLAUDE.md. Transport is normally Azure Service Bus; here it is the in-process
pub/sub in app.bus.event_bus."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid


class EventType(str, Enum):
    STUDY_RISK_DETECTED = "study_risk_detected"
    ENROLLMENT_RISK_DETECTED = "enrollment_risk_detected"
    SITE_RISK_DETECTED = "site_risk_detected"
    COMPLIANCE_ALERT = "compliance_alert"
    MILESTONE_ALERT = "milestone_alert"
    REPORT_GENERATED = "report_generated"


@dataclass
class AgentEvent:
    source_agent: str
    target_agent: str
    study_id: str
    risk_score: float
    event_type: EventType
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "source_agent": self.source_agent,
            "target_agent": self.target_agent,
            "study_id": self.study_id,
            "risk_score": self.risk_score,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
        }
