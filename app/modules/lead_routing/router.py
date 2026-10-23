from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, func
from app.database import get_db
from app.models.lead import LeadRecord, LeadExecutionLog
from app.modules.lead_routing.schemas import LeadIntakeRequest, LeadResponse
from app.modules.lead_routing.service import lead_routing_service
from app.adapters.airtable_adapter import airtable_adapter
from app.adapters.slack_adapter import slack_adapter

router = APIRouter(prefix="/leads", tags=["Module 1 - Lead Routing"])

@router.post("/intake", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def intake_lead(payload: LeadIntakeRequest, db: Session = Depends(get_db)):
    """Intake, validate, qualify, and route an incoming lead from web forms, webhooks, or CRM integrations."""
    try:
        return lead_routing_service.process_lead(db=db, payload=payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Lead processing error: {str(e)}")

@router.get("", response_model=dict)
def list_leads(
    priority: Optional[str] = Query(None, description="Filter by priority: HIGH, MEDIUM, LOW"),
    status: Optional[str] = Query(None, description="Filter by status: QUALIFIED, UNQUALIFIED, INCOMPLETE, MANUAL_REVIEW"),
    search: Optional[str] = Query(None, description="Search by name, company, or email"),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Retrieve filtered, searchable list of ingested leads."""
    query = db.query(LeadRecord)

    if priority:
        query = query.filter(LeadRecord.priority == priority.upper())
    if status:
        query = query.filter(LeadRecord.qualification_status == status.upper())
    if search:
        search_filter = f"%{search.strip()}%"
        query = query.filter(
            or_(
                LeadRecord.name.ilike(search_filter),
                LeadRecord.company.ilike(search_filter),
                LeadRecord.email.ilike(search_filter)
            )
        )

    total = query.count()
    leads = query.order_by(desc(LeadRecord.created_at)).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [lead.to_dict() for lead in leads]
    }

@router.get("/stats/summary", response_model=dict)
def get_leads_summary(db: Session = Depends(get_db)):
    """Aggregate statistics for the lead intelligence pipeline."""
    total = db.query(LeadRecord).count()
    qualified = db.query(LeadRecord).filter(LeadRecord.qualification_status == "QUALIFIED").count()
    high_priority = db.query(LeadRecord).filter(LeadRecord.priority == "HIGH").count()
    avg_score = db.query(func.avg(LeadRecord.score)).scalar() or 0.0

    # Calculate average execution latency from logs
    avg_latency = db.query(func.avg(LeadExecutionLog.latency_ms)).scalar() or 0.0

    return {
        "total_leads": total,
        "qualified_leads": qualified,
        "high_priority_leads": high_priority,
        "average_score": round(float(avg_score), 1),
        "average_latency_ms": round(float(avg_latency), 1)
    }

@router.get("/{lead_id}", response_model=dict)
def get_lead_detail(lead_id: str, db: Session = Depends(get_db)):
    """Get full lead detail with qualification explanation and step execution logs."""
    lead = db.query(LeadRecord).filter(LeadRecord.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

    logs = db.query(LeadExecutionLog).filter(LeadExecutionLog.lead_id == lead_id).order_by(LeadExecutionLog.timestamp).all()

    data = lead.to_dict()
    data["execution_logs"] = [
        {
            "step": log.step_name,
            "status": log.status,
            "latency_ms": log.latency_ms,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None
        }
        for log in logs
    ]
    return data

@router.post("/{lead_id}/retry", response_model=dict)
def retry_lead_sync(lead_id: str, target: str = Query("all", description="Target: airtable, slack, or all"), db: Session = Depends(get_db)):
    """Manually retry failed Airtable or Slack synchronization for a lead."""
    lead = db.query(LeadRecord).filter(LeadRecord.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

    results = {}
    if target in ("airtable", "all"):
        airtable_data = {
            "Lead ID": lead.id,
            "Name": lead.name,
            "Email": lead.email,
            "Company": lead.company,
            "Score": lead.score,
            "Priority": lead.priority,
            "Status": lead.qualification_status
        }
        res = airtable_adapter.sync_lead(airtable_data)
        lead.airtable_status = "SYNCED" if res.get("success") else "FAILED"
        if res.get("record_id"):
            lead.airtable_record_id = res.get("record_id")
        results["airtable"] = res

    if target in ("slack", "all"):
        slack_summary = {
            "name": lead.name,
            "email": lead.email,
            "phone": lead.phone,
            "company": lead.company,
            "budget": lead.budget,
            "score": lead.score,
            "priority": lead.priority,
            "qualification_status": lead.qualification_status,
            "qualification_summary": lead.qualification_summary,
            "talking_points": lead.talking_points
        }
        res = slack_adapter.send_lead_alert(slack_summary)
        lead.slack_status = "SENT" if res.get("success") else "FAILED"
        results["slack"] = res

    db.commit()
    db.refresh(lead)

    return {
        "success": True,
        "lead_id": lead.id,
        "airtable_status": lead.airtable_status,
        "slack_status": lead.slack_status,
        "results": results
    }
