from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models.email_support import SupportTicket, SupportMessage, EmailDraft, KnowledgeArticle
from app.models.audit import AuditLog
from app.adapters.email_adapter import email_adapter
from app.modules.customer_support.schemas import (
    EmailIngestRequest,
    EmailApprovalRequest,
    SupportTicketResponse
)
from app.modules.customer_support.service import customer_support_service

router = APIRouter(prefix="/support", tags=["Module 2 - Customer Support"])

@router.post("/ingest", response_model=SupportTicketResponse, status_code=status.HTTP_201_CREATED)
def ingest_support_email(payload: EmailIngestRequest, db: Session = Depends(get_db)):
    """Ingest, sanitize, classify, and draft grounded responses for incoming support emails."""
    try:
        return customer_support_service.triage_email(db=db, payload=payload)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Support triage error: {str(e)}")

@router.get("/tickets", response_model=dict)
def list_support_tickets(
    intent: Optional[str] = Query(None, description="Filter by intent"),
    urgency: Optional[str] = Query(None, description="Filter by urgency: LOW, NORMAL, HIGH, CRITICAL"),
    status: Optional[str] = Query(None, description="Filter by status: TRIAGED, DRAFTED, APPROVED, ESCALATED, RESOLVED"),
    requires_approval: Optional[bool] = Query(None, description="Filter by human approval queue"),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List and filter customer support tickets."""
    query = db.query(SupportTicket)

    if intent:
        query = query.filter(SupportTicket.intent == intent.upper())
    if urgency:
        query = query.filter(SupportTicket.urgency == urgency.upper())
    if status:
        query = query.filter(SupportTicket.status == status.upper())
    if requires_approval is not None:
        query = query.filter(SupportTicket.requires_human_approval == requires_approval)

    total = query.count()
    tickets = query.order_by(desc(SupportTicket.created_at)).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [t.to_dict() for t in tickets]
    }

@router.get("/tickets/{ticket_id}", response_model=dict)
def get_ticket_detail(ticket_id: str, db: Session = Depends(get_db)):
    """Retrieve full details of a support ticket including messages and drafts."""
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Support ticket not found")

    messages = db.query(SupportMessage).filter(SupportMessage.ticket_id == ticket_id).order_by(SupportMessage.received_at).all()
    drafts = db.query(EmailDraft).filter(EmailDraft.ticket_id == ticket_id).order_by(desc(EmailDraft.created_at)).all()

    data = ticket.to_dict()
    data["messages"] = [
        {"id": m.id, "direction": m.direction, "body": m.body, "received_at": m.received_at.isoformat() if m.received_at else None}
        for m in messages
    ]
    data["drafts"] = [d.to_dict() for d in drafts]
    return data

@router.post("/tickets/{ticket_id}/approve", response_model=dict)
def approve_ticket_action(ticket_id: str, payload: EmailApprovalRequest, db: Session = Depends(get_db)):
    """
    Human approval gate for sensitive actions (sending email, issuing approvals, or escalating).
    Ensures no email is silently sent without authorization.
    """
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Support ticket not found")

    draft = db.query(EmailDraft).filter(EmailDraft.ticket_id == ticket_id).order_by(desc(EmailDraft.created_at)).first()

    action = payload.action.upper()
    now = datetime.now(timezone.utc)

    if action == "APPROVE_DRAFT":
        if draft:
            draft.status = "APPROVED"
            draft.approved_by = payload.approved_by
            draft.approved_at = now
        ticket.status = "APPROVED"
        ticket.requires_human_approval = False

    elif action == "SEND_EMAIL":
        if not draft:
            raise HTTPException(status_code=400, detail="No draft exists to send.")
        email_adapter.send_approved_email(draft_id=draft.id, authorized_by=payload.approved_by)
        draft.status = "SENT"
        draft.approved_by = payload.approved_by
        draft.approved_at = now
        ticket.status = "RESOLVED"
        ticket.requires_human_approval = False

    elif action == "ESCALATE":
        ticket.status = "ESCALATED"
        ticket.assigned_agent = payload.approved_by

    elif action == "REJECT":
        if draft:
            draft.status = "REJECTED"
        ticket.status = "TRIAGED"

    else:
        raise HTTPException(status_code=400, detail=f"Unsupported approval action: {payload.action}")

    # Audit Log
    db.add(AuditLog(
        module="support",
        action=f"SUPPORT_TICKET_{action}",
        entity_type="SupportTicket",
        entity_id=ticket.id,
        actor=payload.approved_by,
        status="SUCCESS",
        details={"notes": payload.custom_notes, "action": action}
    ))

    db.commit()
    db.refresh(ticket)

    return {
        "success": True,
        "ticket_id": ticket.id,
        "action": action,
        "status": ticket.status,
        "authorized_by": payload.approved_by,
        "requires_human_approval": ticket.requires_human_approval
    }

@router.get("/knowledge-base", response_model=List[dict])
def list_knowledge_articles(db: Session = Depends(get_db)):
    """Retrieve all approved knowledge base articles for inspection and grounding reference."""
    articles = db.query(KnowledgeArticle).filter(KnowledgeArticle.approved == True).all()
    return [a.to_dict() for a in articles]
