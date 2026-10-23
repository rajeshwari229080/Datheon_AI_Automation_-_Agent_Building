import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, JSON, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class SupportTicket(Base):
    """Customer support thread record with intent, urgency, and approval requirements."""
    __tablename__ = "support_tickets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    thread_id = Column(String(100), index=True, nullable=True)
    customer_email = Column(String(255), nullable=False, index=True)
    customer_name = Column(String(150), nullable=True)
    subject = Column(String(255), nullable=False)

    # Classification attributes
    intent = Column(String(50), nullable=False, default="UNKNOWN", index=True)
    # Intents: BILLING, TECHNICAL, ACCOUNT_ACCESS, PRODUCT_ORDER, COMPLAINT, URGENT_INCIDENT, SPAM, UNKNOWN
    urgency = Column(String(20), nullable=False, default="NORMAL", index=True)  # LOW, NORMAL, HIGH, CRITICAL
    sentiment = Column(String(20), nullable=False, default="NEUTRAL")  # POSITIVE, NEUTRAL, NEGATIVE, FRUSTRATED
    confidence = Column(Float, default=1.0)

    # Safety & Approval Gate
    requires_human_approval = Column(Boolean, default=True, nullable=False)
    risk_flags = Column(JSON, nullable=True)  # e.g., ["PAYMENT_COMMITMENT", "PROMPT_INJECTION_SUSPECTED"]
    status = Column(String(30), default="TRIAGED", index=True)  # TRIAGED, DRAFTED, ESCALATED, APPROVED, RESOLVED
    assigned_agent = Column(String(100), nullable=True)

    messages = relationship("SupportMessage", back_populates="ticket", cascade="all, delete-orphan")
    drafts = relationship("EmailDraft", back_populates="ticket", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "thread_id": self.thread_id,
            "customer_email": self.customer_email,
            "customer_name": self.customer_name,
            "subject": self.subject,
            "intent": self.intent,
            "urgency": self.urgency,
            "sentiment": self.sentiment,
            "confidence": self.confidence,
            "requires_human_approval": self.requires_human_approval,
            "risk_flags": self.risk_flags or [],
            "status": self.status,
            "assigned_agent": self.assigned_agent
        }

class SupportMessage(Base):
    """Raw and processed messages within a support thread."""
    __tablename__ = "support_messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    ticket_id = Column(String(36), ForeignKey("support_tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    direction = Column(String(20), default="INBOUND")  # INBOUND, OUTBOUND
    body = Column(Text, nullable=False)
    received_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    raw_headers = Column(JSON, nullable=True)

    ticket = relationship("SupportTicket", back_populates="messages")

class EmailDraft(Base):
    """Context-aware, RAG-grounded email draft awaiting review or provider sync."""
    __tablename__ = "email_drafts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    ticket_id = Column(String(36), ForeignKey("support_tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    grounded_sources = Column(JSON, nullable=True)  # References to approved KB documents
    status = Column(String(30), default="PENDING_APPROVAL", index=True)  # PENDING_APPROVAL, APPROVED, REJECTED, SENT
    approved_by = Column(String(100), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)

    ticket = relationship("SupportTicket", back_populates="drafts")

    def to_dict(self):
        return {
            "id": self.id,
            "ticket_id": self.ticket_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "subject": self.subject,
            "body": self.body,
            "grounded_sources": self.grounded_sources or [],
            "status": self.status,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None
        }

class KnowledgeArticle(Base):
    """Approved enterprise knowledge-base articles used for RAG grounding."""
    __tablename__ = "knowledge_articles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    category = Column(String(50), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(JSON, nullable=True)
    approved = Column(Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "slug": self.slug,
            "category": self.category,
            "title": self.title,
            "content": self.content,
            "tags": self.tags or [],
            "approved": self.approved
        }
