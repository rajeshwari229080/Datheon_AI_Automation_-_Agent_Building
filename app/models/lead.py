import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, JSON, Integer, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class LeadRecord(Base):
    """Database entity representing an ingested and qualified sales lead."""
    __tablename__ = "leads"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Core contact details
    name = Column(String(150), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(50), nullable=True)
    company = Column(String(150), nullable=False, index=True)
    company_size = Column(String(50), nullable=False)
    budget = Column(Float, nullable=False, default=0.0)
    budget_range = Column(String(50), nullable=True)
    business_need = Column(Text, nullable=False)
    product_interest = Column(String(100), nullable=True)
    consent = Column(Boolean, default=True, nullable=False)

    # Qualification & Routing
    qualification_status = Column(String(30), default="PENDING", index=True)  # QUALIFIED, UNQUALIFIED, INCOMPLETE, MANUAL_REVIEW
    score = Column(Integer, default=0, index=True)  # 0 to 100
    priority = Column(String(20), default="LOW", index=True)  # HIGH, MEDIUM, LOW
    qualification_summary = Column(Text, nullable=True)
    talking_points = Column(JSON, nullable=True)  # List of personalized sales talking points
    missing_info = Column(JSON, nullable=True)  # List of identified missing data points
    confidence = Column(Float, default=1.0)  # 0.0 to 1.0

    # Synchronization state
    airtable_record_id = Column(String(100), nullable=True)
    airtable_status = Column(String(30), default="PENDING")  # PENDING, SYNCED, FAILED
    slack_status = Column(String(30), default="PENDING")  # PENDING, SENT, FAILED
    idempotency_key = Column(String(64), unique=True, index=True, nullable=False)
    raw_payload = Column(JSON, nullable=True)

    execution_logs = relationship("LeadExecutionLog", back_populates="lead", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "company": self.company,
            "company_size": self.company_size,
            "budget": self.budget,
            "budget_range": self.budget_range,
            "business_need": self.business_need,
            "product_interest": self.product_interest,
            "consent": self.consent,
            "qualification_status": self.qualification_status,
            "score": self.score,
            "priority": self.priority,
            "qualification_summary": self.qualification_summary,
            "talking_points": self.talking_points or [],
            "missing_info": self.missing_info or [],
            "confidence": self.confidence,
            "airtable_record_id": self.airtable_record_id,
            "airtable_status": self.airtable_status,
            "slack_status": self.slack_status,
            "idempotency_key": self.idempotency_key
        }

class LeadExecutionLog(Base):
    """Step-level latency and audit log for lead routing workflows."""
    __tablename__ = "lead_execution_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    lead_id = Column(String(36), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    step_name = Column(String(100), nullable=False)
    status = Column(String(30), default="SUCCESS")
    latency_ms = Column(Integer, nullable=False)
    details = Column(JSON, nullable=True)

    lead = relationship("LeadRecord", back_populates="execution_logs")
