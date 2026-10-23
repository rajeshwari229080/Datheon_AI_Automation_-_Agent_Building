import time
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.config import logger
from app.models.email_support import SupportTicket, SupportMessage, EmailDraft
from app.models.audit import AuditLog
from app.adapters.email_adapter import email_adapter
from app.adapters.openai_adapter import openai_adapter
from app.adapters.slack_adapter import slack_adapter
from app.modules.customer_support.schemas import (
    EmailIngestRequest,
    TriageClassificationResult,
    SupportTicketResponse,
    sanitize_untrusted_input
)
from app.modules.customer_support.knowledge_base import kb_retriever

class CustomerSupportService:
    """Enterprise service for intelligent email triage, sentiment analysis, RAG grounding, and draft safety."""

    @staticmethod
    def classify_deterministic_rules(subject: str, body: str) -> Tuple[str, str, str, bool, List[str]]:
        """
        Evaluate deterministic business rules and safety triggers.
        Returns: (intent, urgency, sentiment, requires_human_approval, risk_flags)
        """
        cleaned_text, detected_risks = sanitize_untrusted_input(f"{subject}\n{body}")
        text_lower = cleaned_text.lower()

        intent = "UNKNOWN"
        urgency = "NORMAL"
        sentiment = "NEUTRAL"
        requires_approval = True  # Enterprise default is draft-only with human review

        # Check for urgent incidents
        if "CRITICAL_INCIDENT" in detected_risks or any(w in text_lower for w in ["outage", "production down", "sev-1", "crash"]):
            intent = "URGENT_INCIDENT"
            urgency = "CRITICAL"
            sentiment = "FRUSTRATED"
            requires_approval = True
        elif "REFUND_REQUEST" in detected_risks or any(w in text_lower for w in ["refund", "billing", "chargeback", "invoice"]):
            intent = "BILLING"
            urgency = "HIGH" if "refund" in text_lower else "NORMAL"
            sentiment = "NEGATIVE" if "refund" in text_lower else "NEUTRAL"
            requires_approval = True  # Financial integrity rule
        elif "ACCOUNT_DELETION" in detected_risks or any(w in text_lower for w in ["delete my account", "password reset", "locked out"]):
            intent = "ACCOUNT_ACCESS"
            urgency = "HIGH"
            requires_approval = True
        elif any(w in text_lower for w in ["api", "error", "500", "timeout", "bug", "rate limit"]):
            intent = "TECHNICAL"
            urgency = "NORMAL"
        elif any(w in text_lower for w in ["unacceptable", "furious", "terrible", "complaint", "worst"]):
            intent = "COMPLAINT"
            sentiment = "FRUSTRATED"
            urgency = "HIGH"
            requires_approval = True
        elif any(w in text_lower for w in ["buy", "order", "pricing", "feature", "enterprise plan"]):
            intent = "PRODUCT_ORDER"
            sentiment = "POSITIVE"

        if "PROMPT_INJECTION_ATTEMPT" in detected_risks:
            requires_approval = True
            urgency = "HIGH"

        return intent, urgency, sentiment, requires_approval, detected_risks

    def triage_email(self, db: Session, payload: EmailIngestRequest) -> SupportTicketResponse:
        start_time = time.time()
        kb_retriever.seed_articles(db)

        # 1. Deterministic rules & sanitization
        det_intent, det_urgency, det_sentiment, requires_approval, detected_risks = self.classify_deterministic_rules(
            payload.subject, payload.body
        )

        # 2. RAG Knowledge Base Retrieval
        relevant_articles = kb_retriever.retrieve_relevant_passages(db, f"{payload.subject} {payload.body}")
        grounded_sources = [a["title"] for a in relevant_articles]

        # 3. Handle Prompt Injection Attempts with extreme safety
        if "PROMPT_INJECTION_ATTEMPT" in detected_risks:
            logger.warning(f"[SupportTriage-SECURITY] Neutralized prompt injection from {payload.sender_email}")
            draft_subject = f"Re: {payload.subject} - Security Review Required"
            draft_body = (
                f"Hello {payload.sender_name or 'there'},\n\n"
                f"Thank you for contacting Enterprise Support. Your message contained commands or formatting "
                f"that require manual review by our security and compliance team. A customer representative "
                f"will follow up with you directly.\n\n"
                f"Reference Ticket: [Pending Human Review]\n\n"
                f"Best regards,\nEnterprise Support Operations"
            )
            intent = "UNKNOWN"
            urgency = "HIGH"
            sentiment = "NEUTRAL"
            requires_approval = True
        else:
            # 4. AI-Assisted Grounded Draft Generation
            kb_context = "\n\n".join([f"Source: {a['title']}\nContent: {a['content']}" for a in relevant_articles])
            ai_prompt = (
                f"Customer Subject: {payload.subject}\n"
                f"Customer Message: {payload.body}\n"
                f"Deterministic Intent: {det_intent}, Urgency: {det_urgency}\n\n"
                f"Approved Enterprise Knowledge Base Content:\n{kb_context if kb_context else 'No matching articles found.'}\n\n"
                f"INSTRUCTIONS:\n"
                f"- Ground your response ONLY in the approved KB content.\n"
                f"- If KB does not answer the question, state politely that a specialist will review and request clarification.\n"
                f"- NEVER promise refunds, credit card chargebacks, or unauthorized system changes.\n"
                f"- Keep tone polite, professional, and concise."
            )
            ai_res = openai_adapter.generate_chat_json(
                system_prompt="You are an enterprise customer support triage agent. Produce polite, grounded response drafts.",
                user_prompt=ai_prompt,
                expected_schema=TriageClassificationResult.model_json_schema()
            )

            intent = det_intent if det_intent != "UNKNOWN" else ai_res.get("intent", "TECHNICAL")
            urgency = det_urgency if det_urgency != "NORMAL" else ai_res.get("urgency", "NORMAL")
            sentiment = det_sentiment if det_sentiment != "NEUTRAL" else ai_res.get("sentiment", "NEUTRAL")
            draft_subject = f"Re: {payload.subject}"
            draft_body = ai_res.get("draft_body", (
                f"Hello,\n\nThank you for reaching out to Enterprise Support. We have received your inquiry regarding "
                f"'{payload.subject}'. Our engineering and operations team is reviewing your request and will follow up shortly.\n\n"
                f"Best regards,\nEnterprise Support Team"
            ))

        # 5. Persist Ticket in Database
        ticket = SupportTicket(
            thread_id=payload.thread_id or f"th_{int(time.time()*1000)}",
            customer_email=str(payload.sender_email).lower(),
            customer_name=payload.sender_name,
            subject=payload.subject,
            intent=intent,
            urgency=urgency,
            sentiment=sentiment,
            requires_human_approval=requires_approval,
            risk_flags=detected_risks,
            status="TRIAGED"
        )
        db.add(ticket)
        db.flush()

        # Add inbound message
        db.add(SupportMessage(
            ticket_id=ticket.id,
            direction="INBOUND",
            body=payload.body
        ))

        # 6. Save Draft locally and to Email Provider (Draft-Only Safety)
        email_draft = EmailDraft(
            ticket_id=ticket.id,
            subject=draft_subject,
            body=draft_body,
            grounded_sources=grounded_sources,
            status="PENDING_APPROVAL"
        )
        db.add(email_draft)
        db.flush()

        # Save to email adapter (Gmail/Outlook draft)
        provider_draft = email_adapter.save_draft(
            recipient=ticket.customer_email,
            subject=draft_subject,
            body=draft_body,
            thread_id=ticket.thread_id,
            draft_id=email_draft.id
        )

        # Apply thread labels
        email_adapter.apply_labels(
            thread_id=ticket.thread_id,
            labels=[f"intent:{intent.lower()}", f"urgency:{urgency.lower()}"]
        )

        # 7. Escalation Alert if Urgent or High Risk
        if urgency in ("HIGH", "CRITICAL") or requires_approval:
            slack_adapter.send_approval_notification(
                title=f"Support Escalation [{intent}] - Urgency: {urgency}",
                details={
                    "Customer": f"{ticket.customer_name or 'N/A'} <{ticket.customer_email}>",
                    "Subject": ticket.subject,
                    "Urgency": urgency,
                    "Sentiment": sentiment,
                    "Risk Flags": ", ".join(detected_risks) if detected_risks else "None",
                    "Ticket ID": ticket.id
                }
            )

        # Audit Log
        db.add(AuditLog(
            module="support",
            action="SUPPORT_EMAIL_TRIAGED",
            entity_type="SupportTicket",
            entity_id=ticket.id,
            status="SUCCESS",
            details={"intent": intent, "urgency": urgency, "requires_approval": requires_approval, "risks": detected_risks},
            duration_ms=int((time.time() - start_time) * 1000)
        ))

        db.commit()
        db.refresh(ticket)

        return SupportTicketResponse(
            success=True,
            ticket_id=ticket.id,
            thread_id=ticket.thread_id,
            intent=ticket.intent,
            urgency=ticket.urgency,
            sentiment=ticket.sentiment,
            status=ticket.status,
            requires_human_approval=ticket.requires_human_approval,
            risk_flags=ticket.risk_flags or [],
            draft_id=email_draft.id,
            draft_subject=email_draft.subject,
            draft_body=email_draft.body,
            grounded_sources=grounded_sources,
            provider_draft_status=provider_draft.get("status", "DRAFT")
        )

customer_support_service = CustomerSupportService()
