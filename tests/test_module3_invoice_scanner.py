import io
import pytest
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from app.models.invoice import InvoiceRecord
from app.adapters.sheets_adapter import sheets_adapter

def create_sample_pdf(invoice_num="INV-2026-001", vendor="Acme Enterprise Cloud", subtotal=1200.0, tax=120.0, total=1320.0) -> bytes:
    """Generate a clean synthetic PDF invoice in-memory using reportlab."""
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, f"INVOICE: {invoice_num}")
    p.setFont("Helvetica", 12)
    p.drawString(100, 730, f"Vendor: {vendor}")
    p.drawString(100, 710, "Date: 2026-10-18")
    p.drawString(100, 680, "Line Item 1: Cloud Platform Hosting (Qty: 2, Unit: $500.00, Total: $1,000.00)")
    p.drawString(100, 660, "Line Item 2: Technical Support Plan (Qty: 1, Unit: $200.00, Total: $200.00)")
    p.drawString(100, 620, f"Subtotal: ${subtotal:,.2f}")
    p.drawString(100, 600, f"Tax: ${tax:,.2f}")
    p.drawString(100, 580, f"Total Amount: ${total:,.2f}")
    p.save()
    buffer.seek(0)
    return buffer.getvalue()

def test_valid_pdf_invoice_upload_and_extraction(client, db_session):
    """Test valid PDF upload produces schema-valid extraction with no arithmetic discrepancy."""
    pdf_bytes = create_sample_pdf(invoice_num="INV-99001", subtotal=1200.0, tax=120.0, total=1320.0)

    files = {"file": ("test_invoice.pdf", pdf_bytes, "application/pdf")}
    res = client.post("/api/v1/invoices/upload", files=files)
    assert res.status_code == 201
    data = res.json()

    assert data["success"] is True
    assert data["invoice_number"] == "INV-99001"
    assert data["total_amount"] == 1320.0
    assert data["subtotal"] == 1200.0
    assert data["tax_amount"] == 120.0
    assert data["arithmetic_discrepancy"] is False
    assert data["validation_status"] == "VALID"
    assert data["is_duplicate"] is False

def test_arithmetic_mismatch_flagged_for_review(client, db_session):
    """Test that arithmetic calculation errors on an invoice are caught deterministically."""
    # Deliberate mismatch: Subtotal $1200 + Tax $120 != Total $1800 (error by vendor)
    bad_pdf_bytes = create_sample_pdf(invoice_num="INV-BAD-MATH", subtotal=1200.0, tax=120.0, total=1800.0)

    files = {"file": ("bad_math_invoice.pdf", bad_pdf_bytes, "application/pdf")}
    res = client.post("/api/v1/invoices/upload", files=files)
    assert res.status_code == 201
    data = res.json()

    assert data["arithmetic_discrepancy"] is True
    assert data["validation_status"] == "ARITHMETIC_MISMATCH"
    assert "delta_total" in data["discrepancy_details"]
    assert data["discrepancy_details"]["delta_total"] == 480.0

def test_duplicate_document_detection(client, db_session):
    """Test that uploading the exact same document twice is flagged as DUPLICATE."""
    pdf_bytes = create_sample_pdf(invoice_num="INV-DUP-TEST", subtotal=500.0, tax=50.0, total=550.0)

    files1 = {"file": ("dup_test.pdf", pdf_bytes, "application/pdf")}
    res1 = client.post("/api/v1/invoices/upload", files=files1)
    assert res1.status_code == 201
    data1 = res1.json()
    assert data1["is_duplicate"] is False

    # Second upload of same file bytes
    files2 = {"file": ("dup_test.pdf", pdf_bytes, "application/pdf")}
    res2 = client.post("/api/v1/invoices/upload", files=files2)
    assert res2.status_code == 201
    data2 = res2.json()
    assert data2["is_duplicate"] is True
    assert data2["validation_status"] == "DUPLICATE"

def test_reject_corrupt_or_unsafe_upload(client):
    """Test that binary files without valid signatures are rejected safely."""
    fake_exe_bytes = b"MZ\x90\x00\x03\x00\x00\x00malicious executable pretending to be a pdf"
    files = {"file": ("malicious.pdf", fake_exe_bytes, "application/pdf")}
    res = client.post("/api/v1/invoices/upload", files=files)
    assert res.status_code == 400
    assert "Unsafe or corrupted file" in res.json()["detail"]

def test_google_sheets_export_and_retry(client, db_session):
    """Test export of approved invoice to Google Sheets and recovery from temporary failures."""
    pdf_bytes = create_sample_pdf(invoice_num="INV-EXPORT-001", subtotal=800.0, tax=80.0, total=880.0)
    files = {"file": ("export_invoice.pdf", pdf_bytes, "application/pdf")}
    res = client.post("/api/v1/invoices/upload", files=files)
    invoice_id = res.json()["invoice_id"]

    # Test simulated transient failure
    sheets_adapter.simulate_failure_next_call()
    failed_res = client.post(f"/api/v1/invoices/{invoice_id}/export")
    assert failed_res.status_code == 502

    # Retry export (succeeds)
    success_res = client.post(f"/api/v1/invoices/{invoice_id}/export")
    assert success_res.status_code == 200
    assert success_res.json()["export_status"] == "EXPORTED"

    # Verify invoice record updated
    inv = db_session.query(InvoiceRecord).filter(InvoiceRecord.id == invoice_id).first()
    assert inv.export_status == "EXPORTED"
    assert inv.exported_at is not None
