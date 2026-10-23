from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.config import settings
from app.models.invoice import InvoiceRecord, InvoiceLineItem, InvoiceAuditLog
from app.modules.invoice_scanner.schemas import (
    InvoiceResponse,
    LineItemUpdateRequest,
    InvoiceExtractionSchema,
    LineItemSchema
)
from app.modules.invoice_scanner.service import invoice_scanner_service

router = APIRouter(prefix="/invoices", tags=["Module 3 - Invoice Scanner"])

@router.post("/upload", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def upload_invoice(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload and process an invoice document (PDF or Image) with arithmetic validation and duplicate detection."""
    content = await file.read()
    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(status_code=413, detail=f"File exceeds maximum allowed size of {settings.max_upload_size_bytes // (1024*1024)}MB")

    try:
        return invoice_scanner_service.process_invoice_upload(db=db, filename=file.filename or "invoice.pdf", content=content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

@router.get("", response_model=dict)
def list_invoices(
    status: Optional[str] = Query(None, description="Filter: VALID, ARITHMETIC_MISMATCH, DUPLICATE, MISSING_FIELDS, EXPORTED"),
    has_discrepancy: Optional[bool] = Query(None, description="Filter invoices with arithmetic errors"),
    is_duplicate: Optional[bool] = Query(None, description="Filter duplicate invoices"),
    export_status: Optional[str] = Query(None, description="Filter: NOT_EXPORTED, EXPORTED, FAILED"),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List and filter invoices with discrepancy flags and export statuses."""
    query = db.query(InvoiceRecord)

    if status:
        query = query.filter(InvoiceRecord.validation_status == status.upper())
    if has_discrepancy is not None:
        query = query.filter(InvoiceRecord.arithmetic_discrepancy == has_discrepancy)
    if is_duplicate is not None:
        query = query.filter(InvoiceRecord.is_duplicate == is_duplicate)
    if export_status:
        query = query.filter(InvoiceRecord.export_status == export_status.upper())

    total = query.count()
    invoices = query.order_by(desc(InvoiceRecord.upload_date)).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [inv.to_dict() for inv in invoices]
    }

@router.get("/{invoice_id}", response_model=dict)
def get_invoice_detail(invoice_id: str, db: Session = Depends(get_db)):
    """Retrieve full extracted invoice, line items, discrepancy details, and change audit history."""
    invoice = db.query(InvoiceRecord).filter(InvoiceRecord.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    audit_logs = db.query(InvoiceAuditLog).filter(InvoiceAuditLog.invoice_id == invoice_id).order_by(InvoiceAuditLog.timestamp).all()
    data = invoice.to_dict()
    data["audit_history"] = [
        {"action": log.action, "operator": log.operator, "timestamp": log.timestamp.isoformat(), "changes": log.changes}
        for log in audit_logs
    ]
    return data

@router.put("/{invoice_id}/line-items", response_model=dict)
def update_invoice_line_items(invoice_id: str, payload: LineItemUpdateRequest, db: Session = Depends(get_db)):
    """
    Line-item editor screen endpoint: manually correct OCR extraction errors,
    re-runs deterministic arithmetic verification, and updates audit history.
    """
    invoice = db.query(InvoiceRecord).filter(InvoiceRecord.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    old_total = invoice.total_amount

    # Update metadata fields if provided
    if payload.vendor_name:
        invoice.vendor_name = payload.vendor_name
    if payload.invoice_number:
        invoice.invoice_number = payload.invoice_number
    if payload.currency:
        invoice.currency = payload.currency
    if payload.subtotal is not None:
        invoice.subtotal = payload.subtotal
    if payload.tax_amount is not None:
        invoice.tax_amount = payload.tax_amount
    if payload.discount_amount is not None:
        invoice.discount_amount = payload.discount_amount
    if payload.total_amount is not None:
        invoice.total_amount = payload.total_amount

    # Replace line items if provided
    if payload.line_items:
        db.query(InvoiceLineItem).filter(InvoiceLineItem.invoice_id == invoice_id).delete()
        for item in payload.line_items:
            db.add(InvoiceLineItem(
                invoice_id=invoice.id,
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_amount=item.total_amount,
                confidence=1.0
            ))

    # Re-verify arithmetic
    extraction = InvoiceExtractionSchema(
        vendor_name=invoice.vendor_name,
        invoice_number=invoice.invoice_number,
        invoice_date=invoice.invoice_date,
        currency=invoice.currency,
        subtotal=invoice.subtotal,
        tax_amount=invoice.tax_amount,
        discount_amount=invoice.discount_amount,
        total_amount=invoice.total_amount,
        line_items=payload.line_items or [LineItemSchema(**it.to_dict()) for it in invoice.line_items]
    )
    val = invoice_scanner_service.verify_financial_arithmetic(extraction)
    invoice.arithmetic_discrepancy = val.arithmetic_discrepancy
    invoice.discrepancy_details = val.discrepancy_details
    invoice.validation_status = val.status

    db.add(InvoiceAuditLog(
        invoice_id=invoice.id,
        action="LINE_ITEMS_CORRECTED",
        operator="human_reviewer",
        changes={"old_total": old_total, "new_total": invoice.total_amount, "new_status": invoice.validation_status}
    ))

    db.commit()
    db.refresh(invoice)

    return {
        "success": True,
        "invoice_id": invoice.id,
        "validation_status": invoice.validation_status,
        "arithmetic_discrepancy": invoice.arithmetic_discrepancy,
        "total_amount": invoice.total_amount,
        "discrepancy_details": invoice.discrepancy_details
    }

@router.post("/{invoice_id}/approve", response_model=dict)
def approve_invoice_for_export(invoice_id: str, reviewer: str = Query("finance_manager"), db: Session = Depends(get_db)):
    """Human approval action authorizing an invoice with flagged discrepancies for accounting sync."""
    invoice = db.query(InvoiceRecord).filter(InvoiceRecord.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    invoice.validation_status = "APPROVED_BY_HUMAN"
    db.add(InvoiceAuditLog(
        invoice_id=invoice.id,
        action="HUMAN_OVERRIDE_APPROVAL",
        operator=reviewer,
        changes={"approved_status": "APPROVED_BY_HUMAN"}
    ))
    db.commit()
    db.refresh(invoice)
    return {"success": True, "invoice_id": invoice.id, "status": invoice.validation_status, "approved_by": reviewer}

@router.post("/{invoice_id}/export", response_model=dict)
def export_invoice(invoice_id: str, operator: str = Query("accountant"), db: Session = Depends(get_db)):
    """Export an approved invoice to Google Sheets."""
    try:
        return invoice_scanner_service.export_to_google_sheets(db=db, invoice_id=invoice_id, operator=operator)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Google Sheets sync failed: {str(e)}")
