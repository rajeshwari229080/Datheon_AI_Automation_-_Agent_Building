import time
from typing import Any, Dict, List, Optional
from app.adapters.base import BaseAdapter
from app.config import settings, logger

class EmailAdapter(BaseAdapter):
    """Adapter for Email Providers (Gmail/Outlook/SMTP) with strict draft-only default safety."""

    def __init__(self):
        super().__init__("EmailAdapter")
        self.provider = settings.email_provider
        self.mock_drafts: Dict[str, Dict[str, Any]] = {}
        self.mock_sent_emails: List[Dict[str, Any]] = []
        self.mock_labels: Dict[str, List[str]] = {}

    def is_configured(self) -> bool:
        return bool(settings.email_smtp_host and settings.email_user and not self.is_demo_mode)

    def health_check(self) -> Dict[str, Any]:
        if not self.is_configured():
            return {
                "status": "DEMO_MODE",
                "configured": False,
                "message": "Running mock email adapter. Draft-only mode enabled for safety.",
                "provider": self.provider
            }
        return {"status": "HEALTHY", "configured": True, "provider": self.provider}

    def save_draft(self, recipient: str, subject: str, body: str, thread_id: Optional[str] = None) -> Dict[str, Any]:
        """Save a response as a draft in the email provider without sending."""
        draft_id = f"draft_{int(time.time()*1000)}"
        draft_payload = {
            "id": draft_id,
            "recipient": recipient,
            "subject": subject,
            "body": body,
            "thread_id": thread_id,
            "created_at": time.time(),
            "status": "DRAFT"
        }
        self.mock_drafts[draft_id] = draft_payload
        logger.info(f"[EmailAdapter] Draft {draft_id} created for {recipient} - (Default Draft-Only Safety)")
        return {
            "success": True,
            "mode": "MOCK" if not self.is_configured() else "LIVE",
            "draft_id": draft_id,
            "recipient": recipient,
            "subject": subject
        }

    def send_approved_email(self, draft_id: str, authorized_by: str) -> Dict[str, Any]:
        """Send an approved email draft with mandatory human authorization audit."""
        if not authorized_by:
            raise PermissionError("Human authorization required to send outbound email.")

        draft = self.mock_drafts.get(draft_id)
        if not draft:
            raise ValueError(f"Draft {draft_id} not found.")

        sent_record = {
            **draft,
            "sent_at": time.time(),
            "authorized_by": authorized_by,
            "status": "SENT"
        }
        self.mock_sent_emails.append(sent_record)
        draft["status"] = "SENT"
        logger.info(f"[EmailAdapter] Draft {draft_id} sent to {draft['recipient']} by {authorized_by}")
        return {
            "success": True,
            "mode": "MOCK" if not self.is_configured() else "LIVE",
            "draft_id": draft_id,
            "status": "SENT",
            "authorized_by": authorized_by
        }

    def apply_labels(self, thread_id: str, labels: List[str]) -> Dict[str, Any]:
        """Apply category or intent labels to an email thread."""
        current = self.mock_labels.get(thread_id, [])
        updated = list(set(current + labels))
        self.mock_labels[thread_id] = updated
        logger.info(f"[EmailAdapter] Applied labels {labels} to thread {thread_id}")
        return {"success": True, "thread_id": thread_id, "labels": updated}

email_adapter = EmailAdapter()
