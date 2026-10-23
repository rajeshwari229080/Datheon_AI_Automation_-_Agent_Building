import hmac
import hashlib
import json
import time
from typing import Any, Dict, Tuple
from app.adapters.base import BaseAdapter
from app.config import settings, logger

class StripeAdapter(BaseAdapter):
    """Deterministic Stripe webhook signature verification and payment event processor."""

    def __init__(self):
        super().__init__("StripeAdapter")
        self.webhook_secret = settings.stripe_webhook_secret
        self.api_key = settings.stripe_api_key
        self.tolerance_seconds = 300  # 5 minutes replay attack window

    def is_configured(self) -> bool:
        return bool(self.webhook_secret and not self.is_demo_mode)

    def health_check(self) -> Dict[str, Any]:
        return {
            "status": "HEALTHY",
            "configured": bool(self.webhook_secret),
            "webhook_secret_set": bool(self.webhook_secret)
        }

    def verify_webhook_signature(self, payload_bytes: bytes, sig_header: str, secret: str = None) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Verify Stripe webhook signature according to standard HMAC-SHA256 specification.
        Returns: (is_valid: bool, error_msg: str, parsed_event: dict)
        """
        webhook_secret = secret or self.webhook_secret
        if not sig_header:
            return False, "Missing Stripe-Signature header", {}

        timestamp = None
        signatures = []

        try:
            for item in sig_header.split(","):
                item = item.strip()
                if item.startswith("t="):
                    timestamp = int(item[2:])
                elif item.startswith("v1="):
                    signatures.append(item[3:])
        except Exception as e:
            return False, f"Malformed Stripe-Signature header: {str(e)}", {}

        if timestamp is None or not signatures:
            return False, "Unable to extract timestamp or v1 signature from header", {}

        # Check timestamp replay tolerance
        now = int(time.time())
        if abs(now - timestamp) > self.tolerance_seconds:
            return False, f"Timestamp out of tolerance window ({abs(now - timestamp)}s > {self.tolerance_seconds}s)", {}

        # Compute HMAC-SHA256 of timestamp + '.' + payload
        signed_payload = f"{timestamp}.".encode("utf-8") + payload_bytes
        expected_sig = hmac.new(
            webhook_secret.encode("utf-8"),
            signed_payload,
            hashlib.sha256
        ).hexdigest()

        # Constant-time comparison against all provided v1 signatures
        is_match = False
        for sig in signatures:
            if hmac.compare_digest(expected_sig, sig):
                is_match = True
                break

        if not is_match:
            return False, "Signature verification failed: computed HMAC does not match v1 signature", {}

        # Parse event payload
        try:
            event_data = json.loads(payload_bytes.decode("utf-8"))
        except Exception as e:
            return False, f"Invalid JSON payload: {str(e)}", {}

        return True, "", event_data

    def create_mock_signed_event(self, event_type: str, data_object: Dict[str, Any], secret: str = None) -> Tuple[str, str]:
        """Helper for test suites and demo modes to generate validly signed Stripe webhook payloads."""
        webhook_secret = secret or self.webhook_secret
        timestamp = int(time.time())
        payload = {
            "id": f"evt_test_{int(time.time()*1000)}",
            "object": "event",
            "api_version": "2024-06-20",
            "created": timestamp,
            "type": event_type,
            "data": {
                "object": data_object
            }
        }
        payload_bytes = json.dumps(payload).encode("utf-8")
        signed_payload = f"{timestamp}.".encode("utf-8") + payload_bytes
        signature = hmac.new(
            webhook_secret.encode("utf-8"),
            signed_payload,
            hashlib.sha256
        ).hexdigest()
        sig_header = f"t={timestamp},v1={signature}"
        return payload_bytes.decode("utf-8"), sig_header

stripe_adapter = StripeAdapter()
