from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, Header, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models.enterprise import EnterpriseProject, ContractDraft, PaymentEvent, WorkflowExecution, ExecutiveDigestRecord
from app.modules.multi_agent_ops.schemas import (
    ProjectIntakeRequest,
    ContractDraftResponse,
    StripeWebhookResponse,
    ExecutiveDigestResponse,
    ProjectStateTransitionRequest
)
from app.modules.multi_agent_ops.supervisor import workflow_supervisor
from app.modules.multi_agent_ops.agents.intake_agent import intake_agent
from app.modules.multi_agent_ops.agents.contract_agent import contract_agent
from app.modules.multi_agent_ops.agents.payment_service import payment_service
from app.modules.multi_agent_ops.agents.collaboration_agent import collaboration_agent
from app.modules.multi_agent_ops.agents.reporting_agent import reporting_agent

router = APIRouter(prefix="/enterprise", tags=["Module 4 - Multi-Agent Enterprise Operations"])

@router.post("/projects/intake", response_model=dict, status_code=status.HTTP_201_CREATED)
def intake_enterprise_customer(payload: ProjectIntakeRequest, db: Session = Depends(get_db)):
    """Customer intake: creates central tracked project and initializes multi-agent workflow."""
    try:
        project = intake_agent.execute(db=db, request=payload)
        return {"success": True, "project": project.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Customer intake failed: {str(e)}")

@router.get("/projects", response_model=dict)
def list_projects(
    state: Optional[str] = Query(None, description="Filter by state"),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List and filter enterprise projects across state machine lifecycle."""
    query = db.query(EnterpriseProject)
    if state:
        query = query.filter(EnterpriseProject.current_state == state.upper())

    total = query.count()
    projects = query.order_by(desc(EnterpriseProject.created_at)).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [p.to_dict() for p in projects]
    }

@router.get("/projects/{project_id}", response_model=dict)
def get_project_workspace(project_id: str, db: Session = Depends(get_db)):
    """Retrieve full project workspace details, contracts, verified payments, and step trace."""
    project = db.query(EnterpriseProject).filter(EnterpriseProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    contracts = db.query(ContractDraft).filter(ContractDraft.project_id == project_id).all()
    payments = db.query(PaymentEvent).filter(PaymentEvent.project_id == project_id).all()
    workflows = db.query(WorkflowExecution).filter(WorkflowExecution.project_id == project_id).order_by(WorkflowExecution.started_at).all()

    data = project.to_dict()
    data["contracts"] = [c.to_dict() for c in contracts]
    data["payments"] = [p.to_dict() for p in payments]
    data["workflow_executions"] = [
        {
            "step": w.step_name,
            "agent": w.current_agent,
            "status": w.status,
            "trace": w.trace,
            "timestamp": w.started_at.isoformat() if w.started_at else None
        }
        for w in workflows
    ]
    return data

@router.post("/projects/{project_id}/contracts/draft", response_model=dict)
def generate_contract_draft(project_id: str, db: Session = Depends(get_db)):
    """AI-assisted Contract Agent: generate authorized template draft for human review."""
    project = db.query(EnterpriseProject).filter(EnterpriseProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        draft = contract_agent.generate_draft(db=db, project=project)
        return {"success": True, "draft": draft.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Contract preparation error: {str(e)}")

@router.post("/projects/{project_id}/contracts/approve", response_model=dict)
def approve_contract(project_id: str, reviewer: str = Query("legal_counsel"), db: Session = Depends(get_db)):
    """Human review authorization: approves contract draft and advances state to PENDING_PAYMENT."""
    project = db.query(EnterpriseProject).filter(EnterpriseProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    draft = db.query(ContractDraft).filter(ContractDraft.project_id == project_id).order_by(desc(ContractDraft.created_at)).first()
    if not draft:
        raise HTTPException(status_code=400, detail="No contract draft exists to approve.")

    draft.is_approved = True
    draft.approved_by = reviewer
    draft.approved_at = datetime.now(timezone.utc)

    # Transition to PENDING_PAYMENT
    workflow_supervisor.transition(
        db=db,
        project=project,
        target_state="PENDING_PAYMENT",
        agent_name="ContractPreparationAgent",
        actor=reviewer,
        trace_data={"approved_contract_id": draft.id, "approved_by": reviewer}
    )

    db.commit()
    db.refresh(project)
    return {"success": True, "project_id": project.id, "state": project.current_state, "approved_by": reviewer}

@router.post("/stripe/webhook", response_model=StripeWebhookResponse)
async def stripe_webhook_endpoint(
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="stripe-signature"),
    db: Session = Depends(get_db)
):
    """
    Deterministic Stripe Webhook Handler:
    Cryptographically verifies HMAC signature, defends against replay attacks,
    and advances project to PAYMENT_VERIFIED upon valid confirmation.
    """
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")

    body_bytes = await request.body()
    res = payment_service.process_webhook(db=db, raw_payload=body_bytes, sig_header=stripe_signature)

    if not res.signature_valid:
        raise HTTPException(status_code=400, detail=res.message)

    return res

@router.post("/projects/{project_id}/collaborate", response_model=dict)
def provision_collaboration_space(project_id: str, db: Session = Depends(get_db)):
    """Collaboration Agent: provisions Slack channel and completes onboarding."""
    project = db.query(EnterpriseProject).filter(EnterpriseProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        res = collaboration_agent.provision_project_space(db=db, project=project)
        return {"success": True, "project_id": project.id, "channel": res}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Collaboration provisioning error: {str(e)}")

@router.get("/reports/executive-digest", response_model=dict)
def get_latest_executive_digest(db: Session = Depends(get_db)):
    """Retrieve the most recent evidence-grounded executive digest."""
    digest = db.query(ExecutiveDigestRecord).order_by(desc(ExecutiveDigestRecord.generated_at)).first()
    if not digest:
        # Generate one automatically if none exists
        digest = reporting_agent.generate_weekly_digest(db=db)
    return {"success": True, "digest": digest.to_dict()}

@router.post("/reports/executive-digest/generate", response_model=dict)
def trigger_executive_digest_generation(days: int = Query(7, ge=1, le=90), db: Session = Depends(get_db)):
    """Reporting Agent: trigger fresh weekly digest generation from stored database facts."""
    digest = reporting_agent.generate_weekly_digest(db=db, days=days)
    return {"success": True, "digest": digest.to_dict()}
