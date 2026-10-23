import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, JSON, Integer
from app.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class AuditLog(Base):
    """System-wide immutable audit trail for all critical actions and transitions."""
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    module = Column(String(50), nullable=False, index=True)  # lead_routing, support, invoices, enterprise
    action = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(String(100), nullable=True)
    actor = Column(String(100), default="system")
    status = Column(String(30), default="SUCCESS")  # SUCCESS, FAILED, WARNING, PENDING_APPROVAL
    details = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    duration_ms = Column(Integer, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "module": self.module,
            "action": self.action,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "actor": self.actor,
            "status": self.status,
            "details": self.details,
            "error_message": self.error_message,
            "duration_ms": self.duration_ms
        }
