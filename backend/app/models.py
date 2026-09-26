from datetime import datetime

from sqlalchemy import Column, String, Float, Integer, Date, DateTime, JSON, Text

from app.db import Base


class Study(Base):
    __tablename__ = "studies"

    study_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    phase = Column(String)
    therapeutic_area = Column(String)
    status = Column(String, default="Active")
    country = Column(String)
    target_enrollment = Column(Integer)
    start_date = Column(Date)


class Site(Base):
    __tablename__ = "sites"

    site_id = Column(String, primary_key=True)
    study_id = Column(String, index=True)
    country = Column(String)
    pi_name = Column(String)
    status = Column(String, default="Active")
    planned_activation_date = Column(Date)
    actual_activation_date = Column(Date)


class EnrollmentRecord(Base):
    __tablename__ = "enrollment_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    study_id = Column(String, index=True)
    site_id = Column(String, index=True)
    date = Column(Date)
    subjects_screened = Column(Integer, default=0)
    subjects_enrolled = Column(Integer, default=0)


class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    study_id = Column(String, index=True)
    milestone_type = Column(String)  # Study Startup, FPI, LPI, DB Lock, CSR, Closeout
    planned_date = Column(Date)
    actual_date = Column(Date, nullable=True)
    status = Column(String, default="Planned")


class Deviation(Base):
    __tablename__ = "deviations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    study_id = Column(String, index=True)
    site_id = Column(String, index=True)
    date = Column(Date)
    severity = Column(String)  # Minor, Major, Critical
    description = Column(Text)


class Query(Base):
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    study_id = Column(String, index=True)
    site_id = Column(String, index=True)
    opened_date = Column(Date)
    closed_date = Column(Date, nullable=True)
    status = Column(String, default="Open")


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    study_id = Column(String, index=True)
    role = Column(String)
    allocated_fte = Column(Float)
    required_fte = Column(Float)


class Document(Base):
    __tablename__ = "documents"

    doc_id = Column(String, primary_key=True)
    study_id = Column(String, index=True, nullable=True)
    doc_type = Column(String)  # SOP, Protocol, CAPA, Lessons Learned, Monitoring Report, Audit Report
    title = Column(String)
    content_path = Column(String)
    version = Column(String, default="1.0")
    owner = Column(String)
    effective_date = Column(Date)
    country = Column(String, nullable=True)
    site = Column(String, nullable=True)
    protocol = Column(String, nullable=True)


class TrainingCompliance(Base):
    __tablename__ = "training_compliance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    study_id = Column(String, index=True)
    site_id = Column(String, index=True)
    role = Column(String)
    training_complete_pct = Column(Float)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(String, index=True)
    session_id = Column(String, index=True)
    study_id = Column(String, index=True, nullable=True)
    agent = Column(String)
    skill = Column(String)
    documents_used = Column(JSON, default=list)
    model_version = Column(String)
    prediction = Column(JSON)
    confidence = Column(Float, nullable=True)
    approved_by = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    retain_until = Column(DateTime, nullable=True)


class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    approval_type = Column(String)  # compliance_escalation, audit_finding, executive_report, site_closure, study_closure
    study_id = Column(String, nullable=True)
    payload = Column(JSON)
    status = Column(String, default="pending")  # pending, approved, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_by = Column(String, nullable=True)
    resolved_at = Column(DateTime, nullable=True)


class RiskEvent(Base):
    __tablename__ = "risk_events"

    event_id = Column(String, primary_key=True)
    event_type = Column(String)
    source_agent = Column(String)
    target_agent = Column(String, nullable=True)
    study_id = Column(String, index=True)
    risk_score = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
