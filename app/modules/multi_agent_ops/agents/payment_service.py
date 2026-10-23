import time
from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.config import logger
from app.models.enterprise import EnterpriseProject, PaymentEvent
from app.adapters.stripe_adapter import stripe_adapter
from app.adapters.airtable_adapter import airtable_adapter
from app.modules.multi_agent_ops.supervisor import workflow_supervisor
from app.modules.multi_agent_ops.schemas import StripeWebhookResponse

class PaymentVerificationService:
    """Agent 6: Deterministic Stripe webhook signature verification and financial reconciliation."""

    @staticmethod
    def process_webhook(db: Session, raw_payload: bytes, sig_header: str) -> StripeWebhookResponse:
        # 1. Deterministic Signature Verification
        is_valid_sig, sig_err, event_data = stripe_adapter.verify_webhook_signature(
            payload_bytes=raw_payload,
            sig_header=sig_header
        )

        if not is_valid_sig:
            logger.warning(f"[PaymentService-SECURITY] Rejected invalid Stripe webhook signature: {sig_err}")
            return StripeWebhookResponse(
                success=False,
                event_id="unknown",
                event_type="unknown",
                verified=False,
                signature_valid=False,
                project_id=None,
                amount=0.0,
                currency="usd",
                status="REJECTED_INVALID_SIGNATURE",
                message=f"Signature verification failed: {sig_err}"
            )

        event_id = event_data.get("id", f"evt_{int(time.time()*1000)}")
        event_type = event_data.get("type", "unknown")
        data_obj = event_data.get("data", {}).get("object", {})

        # 2. Idempotency & Replay Attack Defense
        existing_event = db.query(PaymentEvent).filter(PaymentEvent.stripe_event_id == event_id).first()
        if existing_event:
            logger.info(f"[PaymentService] Duplicate event replayed ({event_id}). Idempotently ignoring.")
            return StripeWebhookResponse(
                success=True,
                event_id=event_id,
                event_type=event_type,
                verified=True,
                signature_valid=True,
                project_id=existing_event.project_id,
                amount=existing_event.amount,
                currency=existing_event.currency,
                status="ALREADY_PROCESSED",
                message="Event was already processed previously (Idempotent response)."
            )

        # 3. Extract Verified Payment Details
        # Amount in Stripe is in cents
        raw_amount = data_obj.get("amount", 0)
        amount = round(raw_amount / 100.0, 2) if raw_amount > 0 else 0.0
        currency = data_obj.get("currency", "usd").lower()
        payment_status = data_obj.get("status", "unknown")
        customer_email = data_obj.get("receipt_email") or data_obj.get("customer_email") or data_obj.get("billing_details", {}).get("email")

        # Project resolution (from metadata or customer email)
        project_id = data_obj.get("metadata", {}).get("project_id")
        project = None
        if project_id:
            project = db.query(EnterpriseProject).filter(EnterpriseProject.id == project_id).first()
        if not project and customer_email:
            project = db.query(EnterpriseProject).filter(EnterpriseProject.client_email == customer_email.lower()).first()

        # 4. Record Verified Payment Event
        payment_record = PaymentEvent(
            stripe_event_id=event_id,
            idempotency_key=f"idemp_{event_id}",
            project_id=project.id if project else None,
            amount=amount,
            currency=currency,
            status=payment_status,
            verified=True,
            signature_valid=True,
            customer_email=customer_email,
            raw_event=event_data
        )
        db.add(payment_record)
        db.flush()

        # 5. Transition Project State if Payment Succeeded
        if project and payment_status in ("succeeded", "paid"):
            logger.info(f"[PaymentService] Verified payment of ${amount:,.2f} for project {project.id}")
            if project.current_state == "PENDING_PAYMENT":
                workflow_supervisor.transition(
                    db=db,
                    project=project,
                    target_state="PAYMENT_VERIFIED",
                    agent_name="PaymentVerificationService",
                    actor="stripe_webhook",
                    trace_data={"stripe_event_id": event_id, "amount": amount, "currency": currency}
                )

                # Sync verified payment to Airtable
                airtable_adapter.sync_lead({
                    "Project ID": project.id,
                    "Payment Status": "VERIFIED",
                    "Amount Paid": amount,
                    "Stripe Event ID": event_id
                })

        db.commit()
        db.refresh(payment_record)

        return StripeWebhookResponse(
            success=True,
            event_id=event_id,
            event_type=event_type,
            verified=True,
            signature_valid=True,
            project_id=project.id if project else None,
            amount=amount,
            currency=currency,
            status=payment_status,
            message="Payment successfully verified against cryptographic signature."
        )

payment_service = PaymentVerificationService()
