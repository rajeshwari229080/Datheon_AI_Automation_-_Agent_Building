import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, JSON, Float, Boolean, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class EnterpriseProject(Base):
    """End-to-end customer project tracking across the multi-agent operations lifecycle."""
    __tablename__ = "enterprise_projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    client_name = Column(String(150), nullable=False)
    client_email = Column(String(255), nullable=False, index=True)
    company = Column(String(150), nullable=False)
    service_type = Column(String(100), nullable=False)
    deal_value = Column(Float, default=0.0)
    currency = Column(String(10), default="USD")

    # State Machine: INTAKE_RECEIVED -> QUALIFIED -> CONTRACT_DRAFTED -> PENDING_PAYMENT -> PAYMENT_VERIFIED -> CHANNELS_PROVISIONED -> COMPLETED
    current_state = Column(String(50), default="INTAKE_RECEIVED", index=True)

    airtable_id = Column(String(100), nullable=True)
    slack_channel_id = Column(String(100), nullable=True)
    slack_channel_name = Column(String(100), nullable=True)
    stripe_customer_id = Column(String(100), nullable=True)
    stripe_invoice_id = Column(String(100), nullable=True)

    contracts = relationship("ContractDraft", back_populates="project", cascade="all, delete-orphan")
    payments = relationship("PaymentEvent", back_populates="project", cascade="all, delete-orphan")
    workflows = relationship("WorkflowExecution", back_populates="project", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "client_name": self.client_name,
            "client_email": self.client_email,
            "company": self.company,
            "service_type": self.service_type,
            "deal_value": self.deal_value,
            "currency": self.currency,
            "current_state": self.current_state,
            "airtable_id": self.airtable_id,
            "slack_channel_id": self.slack_channel_id,
            "slack_channel_name": self.slack_channel_name,
            "stripe_customer_id": self.stripe_customer_id,
            "contracts_count": len(self.contracts),
            "payments_count": len(self.payments)
        }

class ContractDraft(Base):
    """Template-based enterprise contract draft requiring explicit human authorization."""
    __tablename__ = "contract_drafts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("enterprise_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    template_name = Column(String(100), default="STANDARD_ENTERPRISE_MSA")
    clauses = Column(JSON, nullable=True)
    missing_fields = Column(JSON, nullable=True)
    draft_content = Column(Text, nullable=False)
    is_approved = Column(Boolean, default=False)
    approved_by = Column(String(100), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)

    project = relationship("EnterpriseProject", back_populates="contracts")

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "template_name": self.template_name,
            "clauses": self.clauses or [],
            "missing_fields": self.missing_fields or [],
            "draft_content": self.draft_content,
            "is_approved": self.is_approved,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None
        }

class PaymentEvent(Base):
    """Deterministically verified Stripe webhook payment events."""
    __tablename__ = "payment_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    stripe_event_id = Column(String(100), unique=True, index=True, nullable=False)
    idempotency_key = Column(String(100), unique=True, index=True, nullable=False)
    project_id = Column(String(36), ForeignKey("enterprise_projects.id", ondelete="CASCADE"), nullable=True, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="usd")
    status = Column(String(50), nullable=False)  # succeeded, failed, refunded
    verified = Column(Boolean, default=False)
    signature_valid = Column(Boolean, default=False)
    customer_email = Column(String(255), nullable=True)
    raw_event = Column(JSON, nullable=True)
    processed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    project = relationship("EnterpriseProject", back_populates="payments")

    def to_dict(self):
        return {
            "id": self.id,
            "stripe_event_id": self.stripe_event_id,
            "project_id": self.project_id,
            "amount": self.amount,
            "currency": self.currency,
            "status": self.status,
            "verified": self.verified,
            "signature_valid": self.signature_valid,
            "customer_email": self.customer_email,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None
        }

class WorkflowExecution(Base):
    """Multi-agent step-by-step state machine execution history."""
    __tablename__ = "workflow_executions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("enterprise_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True), nullable=True)
    current_agent = Column(String(100), nullable=False)
    step_name = Column(String(100), nullable=False)
    status = Column(String(30), default="IN_PROGRESS")  # IN_PROGRESS, COMPLETED, FAILED, WAITING_APPROVAL
    trace = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)

    project = relationship("EnterpriseProject", back_populates="workflows")

class ExecutiveDigestRecord(Base):
    """Weekly aggregated factual executive digest backed by true database records."""
    __tablename__ = "executive_digests"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    generated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    factual_stats = Column(JSON, nullable=False)  # Leads, revenues, tickets, invoices, project counts
    narrative_summary = Column(Text, nullable=False)
    discrepancies_flagged = Column(Integer, default=0)
    verified_revenue = Column(Float, default=0.0)

    def to_dict(self):
        stats = self.factual_stats or {}
        return {
            "id": self.id,
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
            "factual_stats": stats,
            "source_coverage": stats.get("source_coverage", ["leads", "support_tickets", "invoices", "payment_events", "enterprise_projects"]),
            "narrative_summary": self.narrative_summary,
            "discrepancies_flagged": self.discrepancies_flagged,
            "verified_revenue": self.verified_revenue
        }
