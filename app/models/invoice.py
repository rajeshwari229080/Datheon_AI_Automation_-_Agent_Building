import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, JSON, Float, Boolean, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class InvoiceRecord(Base):
    """Extracted and validated invoice record."""
    __tablename__ = "invoices"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64), index=True, nullable=False)  # SHA-256 binary hash
    upload_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    # Core extracted fields
    vendor_name = Column(String(200), nullable=True, index=True)
    invoice_number = Column(String(100), nullable=True, index=True)
    invoice_date = Column(String(50), nullable=True)
    due_date = Column(String(50), nullable=True)
    currency = Column(String(10), default="USD")

    # Financial figures
    subtotal = Column(Float, default=0.0)
    tax_rate = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    payment_status = Column(String(50), default="UNPAID")

    # Integrity & verification
    validation_status = Column(String(50), default="PENDING_REVIEW", index=True)
    # Statuses: VALID, ARITHMETIC_MISMATCH, DUPLICATE, MISSING_FIELDS, MANUAL_REVIEW, EXPORTED
    arithmetic_discrepancy = Column(Boolean, default=False)
    discrepancy_details = Column(JSON, nullable=True)
    is_duplicate = Column(Boolean, default=False)
    duplicate_of_id = Column(String(36), nullable=True)

    # Export state (Google Sheets)
    export_status = Column(String(30), default="NOT_EXPORTED")  # NOT_EXPORTED, EXPORTED, FAILED
    exported_at = Column(DateTime(timezone=True), nullable=True)
    raw_extraction = Column(JSON, nullable=True)

    line_items = relationship("InvoiceLineItem", back_populates="invoice", cascade="all, delete-orphan")
    audit_logs = relationship("InvoiceAuditLog", back_populates="invoice", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "file_hash": self.file_hash,
            "upload_date": self.upload_date.isoformat() if self.upload_date else None,
            "vendor_name": self.vendor_name,
            "invoice_number": self.invoice_number,
            "invoice_date": self.invoice_date,
            "due_date": self.due_date,
            "currency": self.currency,
            "subtotal": self.subtotal,
            "tax_rate": self.tax_rate,
            "tax_amount": self.tax_amount,
            "discount_amount": self.discount_amount,
            "total_amount": self.total_amount,
            "payment_status": self.payment_status,
            "validation_status": self.validation_status,
            "arithmetic_discrepancy": self.arithmetic_discrepancy,
            "discrepancy_details": self.discrepancy_details or {},
            "is_duplicate": self.is_duplicate,
            "duplicate_of_id": self.duplicate_of_id,
            "export_status": self.export_status,
            "exported_at": self.exported_at.isoformat() if self.exported_at else None,
            "line_items": [item.to_dict() for item in self.line_items]
        }

class InvoiceLineItem(Base):
    """Extracted line item belonging to an invoice."""
    __tablename__ = "invoice_line_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    invoice_id = Column(String(36), ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)
    description = Column(String(255), nullable=False)
    quantity = Column(Float, default=1.0)
    unit_price = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    confidence = Column(Float, default=1.0)

    invoice = relationship("InvoiceRecord", back_populates="line_items")

    def to_dict(self):
        return {
            "id": self.id,
            "description": self.description,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "total_amount": self.total_amount,
            "confidence": self.confidence
        }

class InvoiceAuditLog(Base):
    """Change history and review notes on invoices."""
    __tablename__ = "invoice_audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    invoice_id = Column(String(36), ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    action = Column(String(100), nullable=False)
    operator = Column(String(100), default="system")
    changes = Column(JSON, nullable=True)

    invoice = relationship("InvoiceRecord", back_populates="audit_logs")
