import hashlib
import time
import os
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.config import settings, logger
from app.models.invoice import InvoiceRecord, InvoiceLineItem, InvoiceAuditLog
from app.models.audit import AuditLog
from app.adapters.sheets_adapter import sheets_adapter
from app.modules.invoice_scanner.extractor import invoice_extractor
from app.modules.invoice_scanner.schemas import (
    InvoiceExtractionSchema,
    InvoiceValidationResult,
    InvoiceResponse,
    LineItemSchema,
    LineItemUpdateRequest
)

class InvoiceScannerService:
    """Enterprise service orchestrating document ingestion, arithmetic audit, deduplication, and accounting sync."""

    @staticmethod
    def compute_file_hash(content: bytes) -> str:
        """Compute SHA-256 hexadecimal hash of binary document."""
        return hashlib.sha256(content).hexdigest()

    @staticmethod
    def verify_financial_arithmetic(extraction: InvoiceExtractionSchema) -> InvoiceValidationResult:
        """
        Deterministic arithmetic verification:
        1. sum(line_item.qty * unit_price) == subtotal
        2. subtotal + tax_amount - discount_amount == total_amount
        """
        line_items_sum = sum(round(item.quantity * item.unit_price, 2) for item in extraction.line_items)
        subtotal = round(extraction.subtotal, 2)
        tax = round(extraction.tax_amount, 2)
        discount = round(extraction.discount_amount, 2)
        total = round(extraction.total_amount, 2)

        expected_total = round(subtotal + tax - discount, 2)

        # Allow minor 5-cent rounding threshold for currency conversions
        delta_subtotal = round(abs(line_items_sum - subtotal), 2)
        delta_total = round(abs(expected_total - total), 2)

        has_math_discrepancy = (delta_subtotal > 0.05 and len(extraction.line_items) > 1) or (delta_total > 0.05)

        discrepancy_details = {}
        if has_math_discrepancy:
            discrepancy_details = {
                "line_items_sum": line_items_sum,
                "stated_subtotal": subtotal,
                "delta_subtotal": delta_subtotal,
                "calculated_expected_total": expected_total,
                "stated_grand_total": total,
                "delta_total": delta_total,
                "error_reason": f"Grand total mismatch: stated ${total:,.2f} vs calculated ${expected_total:,.2f} (diff ${delta_total:,.2f})"
            }

        status = "ARITHMETIC_MISMATCH" if has_math_discrepancy else "VALID"
        if not extraction.vendor_name or total <= 0:
            status = "MISSING_FIELDS"

        return InvoiceValidationResult(
            is_valid=(not has_math_discrepancy and status == "VALID"),
            status=status,
            arithmetic_discrepancy=has_math_discrepancy,
            discrepancy_details=discrepancy_details,
            is_duplicate=False,
            calculated_subtotal=line_items_sum,
            calculated_total=expected_total,
            delta_subtotal=delta_subtotal,
            delta_total=delta_total
        )

    def process_invoice_upload(self, db: Session, filename: str, content: bytes) -> InvoiceResponse:
        start_time = time.time()

        # 1. Binary Magic Bytes Verification
        is_valid_type, mime_type = invoice_extractor.verify_file_signature(content)
        if not is_valid_type:
            raise ValueError(f"Unsafe or corrupted file: {mime_type}")

        # 2. Document Fingerprinting & Binary Deduplication
        file_hash = self.compute_file_hash(content)
        existing_by_hash = db.query(InvoiceRecord).filter(InvoiceRecord.file_hash == file_hash).first()

        # Save file to uploads directory securely
        os.makedirs(settings.upload_dir, exist_ok=True)
        file_path = os.path.join(settings.upload_dir, f"{file_hash[:16]}_{filename}")
        with open(file_path, "wb") as f:
            f.write(content)

        # 3. Text/Vision Extraction Pipeline
        extraction = invoice_extractor.parse_document(content, filename)

        # 4. Arithmetic & Financial Integrity Verification
        validation = self.verify_financial_arithmetic(extraction)

        # 5. Business Duplicate Detection (Vendor + Invoice# + Date + Total)
        is_duplicate = False
        duplicate_of_id = None

        if existing_by_hash:
            is_duplicate = True
            duplicate_of_id = existing_by_hash.id
        elif extraction.vendor_name and extraction.invoice_number:
            existing_by_business = db.query(InvoiceRecord).filter(
                and_(
                    InvoiceRecord.vendor_name.ilike(extraction.vendor_name.strip()),
                    InvoiceRecord.invoice_number.ilike(extraction.invoice_number.strip())
                )
            ).first()
            if existing_by_business:
                is_duplicate = True
                duplicate_of_id = existing_by_business.id

        if is_duplicate:
            validation.status = "DUPLICATE"
            validation.is_duplicate = True
            validation.duplicate_of_id = duplicate_of_id

        # 6. Database Persistence
        invoice_record = InvoiceRecord(
            filename=filename,
            file_path=file_path,
            file_hash=file_hash,
            vendor_name=extraction.vendor_name,
            invoice_number=extraction.invoice_number,
            invoice_date=extraction.invoice_date,
            due_date=extraction.due_date,
            currency=extraction.currency,
            subtotal=extraction.subtotal,
            tax_rate=extraction.tax_rate,
            tax_amount=extraction.tax_amount,
            discount_amount=extraction.discount_amount,
            total_amount=extraction.total_amount,
            payment_status=extraction.payment_status or "UNPAID",
            validation_status=validation.status,
            arithmetic_discrepancy=validation.arithmetic_discrepancy,
            discrepancy_details=validation.discrepancy_details,
            is_duplicate=is_duplicate,
            duplicate_of_id=duplicate_of_id,
            export_status="NOT_EXPORTED",
            raw_extraction=extraction.model_dump()
        )
        db.add(invoice_record)
        db.flush()

        # Add line items
        for item in extraction.line_items:
            db.add(InvoiceLineItem(
                invoice_id=invoice_record.id,
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_amount=item.total_amount,
                confidence=item.confidence
            ))

        # Change audit log
        db.add(InvoiceAuditLog(
            invoice_id=invoice_record.id,
            action="INVOICE_INGESTED",
            operator="system",
            changes={"validation_status": validation.status, "total": extraction.total_amount}
        ))

        # System Audit Log
        db.add(AuditLog(
            module="invoices",
            action="INVOICE_PROCESSED",
            entity_type="InvoiceRecord",
            entity_id=invoice_record.id,
            status="SUCCESS" if validation.status == "VALID" else "WARNING",
            details={"vendor": extraction.vendor_name, "total": extraction.total_amount, "status": validation.status},
            duration_ms=int((time.time() - start_time) * 1000)
        ))

        db.commit()
        db.refresh(invoice_record)

        return InvoiceResponse(
            success=True,
            invoice_id=invoice_record.id,
            filename=invoice_record.filename,
            file_hash=invoice_record.file_hash,
            vendor_name=invoice_record.vendor_name,
            invoice_number=invoice_record.invoice_number,
            invoice_date=invoice_record.invoice_date,
            currency=invoice_record.currency,
            subtotal=invoice_record.subtotal,
            tax_amount=invoice_record.tax_amount,
            discount_amount=invoice_record.discount_amount,
            total_amount=invoice_record.total_amount,
            validation_status=invoice_record.validation_status,
            arithmetic_discrepancy=invoice_record.arithmetic_discrepancy,
            is_duplicate=invoice_record.is_duplicate,
            export_status=invoice_record.export_status,
            line_items=[LineItemSchema(**item.to_dict()) for item in invoice_record.line_items],
            discrepancy_details=invoice_record.discrepancy_details or {}
        )

    def export_to_google_sheets(self, db: Session, invoice_id: str, operator: str = "accountant") -> Dict[str, Any]:
        """Export an approved and reviewed invoice to Google Sheets."""
        invoice = db.query(InvoiceRecord).filter(InvoiceRecord.id == invoice_id).first()
        if not invoice:
            raise ValueError(f"Invoice {invoice_id} not found.")

        # Require human review if arithmetic discrepancy or duplicate
        if invoice.arithmetic_discrepancy and invoice.validation_status != "APPROVED_BY_HUMAN":
            raise PermissionError("Cannot export invoice with unresolved arithmetic discrepancy without human approval.")

        export_res = sheets_adapter.append_invoice_row(invoice.to_dict())

        invoice.export_status = "EXPORTED"
        invoice.exported_at = datetime.now(timezone.utc)
        invoice.validation_status = "EXPORTED"

        db.add(InvoiceAuditLog(
            invoice_id=invoice.id,
            action="EXPORTED_TO_GOOGLE_SHEETS",
            operator=operator,
            changes={"export_res": export_res}
        ))
        db.commit()
        db.refresh(invoice)

        return {
            "success": True,
            "invoice_id": invoice.id,
            "export_status": invoice.export_status,
            "exported_at": invoice.exported_at.isoformat(),
            "export_details": export_res
        }

invoice_scanner_service = InvoiceScannerService()
