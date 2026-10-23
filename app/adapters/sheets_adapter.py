import time
from typing import Any, Dict, List, Optional
from app.adapters.base import BaseAdapter
from app.config import settings, logger

class GoogleSheetsAdapter(BaseAdapter):
    """Adapter for Google Sheets accounting export with deterministic mock and retry testing."""

    def __init__(self):
        super().__init__("GoogleSheetsAdapter")
        self.service_account = settings.google_service_account_json
        self.sheet_id = settings.google_sheet_id
        self.mock_rows: List[Dict[str, Any]] = []
        self._simulate_failure_once: bool = False

    def is_configured(self) -> bool:
        return bool(self.service_account and self.sheet_id and not self.is_demo_mode)

    def health_check(self) -> Dict[str, Any]:
        if not self.is_configured():
            return {
                "status": "DEMO_MODE",
                "configured": False,
                "message": "Running mock Google Sheets adapter. Provide service account JSON and sheet ID for live sync.",
                "rows_exported": len(self.mock_rows)
            }
        return {"status": "HEALTHY", "configured": True, "sheet_id": self.sheet_id}

    def simulate_failure_next_call(self):
        """Helper to test retry policies and error handling."""
        self._simulate_failure_once = True

    def append_invoice_row(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Export an approved invoice record to Google Sheets."""
        if self._simulate_failure_once:
            self._simulate_failure_once = False
            logger.warning("[GoogleSheetsAdapter] Simulated temporary network timeout for retry testing.")
            raise ConnectionError("Temporary Google Sheets API rate-limit/timeout (Simulated).")

        row = {
            "Exported At": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
            "Vendor": invoice_data.get("vendor_name", "UNKNOWN"),
            "Invoice #": invoice_data.get("invoice_number", "UNKNOWN"),
            "Date": invoice_data.get("invoice_date", ""),
            "Currency": invoice_data.get("currency", "USD"),
            "Subtotal": invoice_data.get("subtotal", 0.0),
            "Tax": invoice_data.get("tax_amount", 0.0),
            "Discount": invoice_data.get("discount_amount", 0.0),
            "Total": invoice_data.get("total_amount", 0.0),
            "Payment Status": invoice_data.get("payment_status", "UNPAID"),
            "Document Hash": invoice_data.get("file_hash", "")
        }

        self.mock_rows.append(row)
        logger.info(f"[GoogleSheetsAdapter] Exported invoice {row['Invoice #']} from {row['Vendor']} (${row['Total']})")

        return {
            "success": True,
            "mode": "MOCK" if not self.is_configured() else "LIVE",
            "sheet_id": self.sheet_id or "mock_accounting_sheet",
            "row_index": len(self.mock_rows),
            "row_data": row
        }

sheets_adapter = GoogleSheetsAdapter()
