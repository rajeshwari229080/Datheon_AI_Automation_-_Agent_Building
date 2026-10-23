import time
import httpx
from typing import Any, Dict, Optional
from app.adapters.base import BaseAdapter
from app.config import settings, logger, mask_secret

class AirtableAdapter(BaseAdapter):
    """Adapter for Airtable API with deterministic mock fallback."""

    def __init__(self):
        super().__init__("AirtableAdapter")
        self.api_key = settings.airtable_api_key
        self.base_id = settings.airtable_base_id
        self.table_name = settings.airtable_table_name
        self._mock_records: Dict[str, Dict[str, Any]] = {}

    def is_configured(self) -> bool:
        return bool(self.api_key and self.base_id and not self.is_demo_mode)

    def health_check(self) -> Dict[str, Any]:
        if not self.is_configured():
            return {
                "status": "DEMO_MODE",
                "configured": False,
                "message": "Running mock Airtable adapter. Set AIRTABLE_API_KEY and AIRTABLE_BASE_ID for live mode.",
                "table_name": self.table_name
            }
        try:
            url = f"https://api.airtable.com/v0/{self.base_id}/{self.table_name}?maxRecords=1"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            with httpx.Client(timeout=5.0) as client:
                res = client.get(url, headers=headers)
                if res.status_code == 200:
                    return {"status": "HEALTHY", "configured": True, "message": "Successfully connected to Airtable"}
                return {"status": "ERROR", "configured": True, "error": f"Airtable returned {res.status_code}: {res.text}"}
        except Exception as e:
            return {"status": "ERROR", "configured": True, "error": str(e)}

    def sync_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update a lead in Airtable."""
        if not self.is_configured():
            # Deterministic mock record creation
            record_id = f"rec_mock_{int(time.time()*1000)}"
            self._mock_records[record_id] = lead_data
            logger.info(f"[AirtableAdapter-MOCK] Stored lead {lead_data.get('email')} as {record_id}")
            return {
                "success": True,
                "mode": "MOCK",
                "record_id": record_id,
                "table": self.table_name,
                "fields": lead_data
            }

        # Live Airtable API call
        url = f"https://api.airtable.com/v0/{self.base_id}/{self.table_name}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {"fields": lead_data}
        with httpx.Client(timeout=10.0) as client:
            res = client.post(url, headers=headers, json=payload)
            if res.status_code in (200, 201):
                data = res.json()
                return {
                    "success": True,
                    "mode": "LIVE",
                    "record_id": data.get("id"),
                    "table": self.table_name,
                    "fields": data.get("fields")
                }
            raise RuntimeError(f"Airtable API error ({res.status_code}): {res.text}")

airtable_adapter = AirtableAdapter()
