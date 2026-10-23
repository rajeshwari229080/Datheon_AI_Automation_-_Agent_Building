import os
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Query, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.config import settings, logger
from app.database import init_db, get_db
from app.models.audit import AuditLog
from app.models.lead import LeadRecord, LeadExecutionLog
from app.models.email_support import SupportTicket, EmailDraft
from app.models.invoice import InvoiceRecord
from app.models.enterprise import EnterpriseProject, PaymentEvent, ContractDraft
from app.modules.lead_routing.router import router as leads_router
from app.modules.customer_support.router import router as support_router
from app.modules.invoice_scanner.router import router as invoices_router
from app.modules.multi_agent_ops.router import router as enterprise_router
from app.adapters.airtable_adapter import airtable_adapter
from app.adapters.slack_adapter import slack_adapter
from app.adapters.email_adapter import email_adapter
from app.adapters.sheets_adapter import sheets_adapter
from app.adapters.stripe_adapter import stripe_adapter
from app.adapters.openai_adapter import openai_adapter

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist and seed default knowledge base
    init_db()
    logger.info("Application startup: database ready, adapters initialized.")
    yield
    logger.info("Application shutdown.")

app = FastAPI(
    title=settings.app_name,
    description="Enterprise AI Automation Suite with Lead Intelligence, Support Triage, Invoice Scanner, and Multi-Agent Ops.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(leads_router, prefix="/api/v1")
app.include_router(support_router, prefix="/api/v1")
app.include_router(invoices_router, prefix="/api/v1")
app.include_router(enterprise_router, prefix="/api/v1")

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "dashboard", "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse, tags=["Dashboard"])
def get_dashboard_index():
    """Serve unified enterprise operations dashboard HTML entry point."""
    template_path = os.path.join(os.path.dirname(__file__), "dashboard", "templates", "index.html")
    if os.path.exists(template_path):
        return FileResponse(template_path)
    return HTMLResponse("<h1>Enterprise AI Automation Suite</h1><p>Dashboard UI loading...</p>")

@app.get("/api/v1/health", tags=["System"])
def health_check():
    """System health check and adapter connectivity status."""
    return {
        "status": "HEALTHY",
        "demo_mode": settings.demo_mode,
        "environment": settings.app_env,
        "adapters": {
            "airtable": airtable_adapter.health_check(),
            "slack": slack_adapter.health_check(),
            "email": email_adapter.health_check(),
            "sheets": sheets_adapter.health_check(),
            "stripe": stripe_adapter.health_check(),
            "openai": openai_adapter.health_check()
        }
    }

@app.get("/api/v1/overview/metrics", tags=["System"])
def get_overview_metrics(db: Session = Depends(get_db)):
    """Unified operational metrics derived strictly from active database entities."""
    # Lead Intelligence Metrics
    total_leads = db.query(LeadRecord).count()
    qualified_leads = db.query(LeadRecord).filter(LeadRecord.qualification_status == "QUALIFIED").count()
    avg_latency = db.query(func.avg(LeadExecutionLog.latency_ms)).scalar() or 0.0

    # Support Triage Metrics
    total_tickets = db.query(SupportTicket).count()
    urgent_tickets = db.query(SupportTicket).filter(SupportTicket.urgency.in_(["HIGH", "CRITICAL"])).count()
    pending_drafts = db.query(EmailDraft).filter(EmailDraft.status == "PENDING_APPROVAL").count()

    # Invoice Intelligence Metrics
    total_invoices = db.query(InvoiceRecord).count()
    awaiting_review_invoices = db.query(InvoiceRecord).filter(InvoiceRecord.validation_status.in_(["ARITHMETIC_MISMATCH", "PENDING_REVIEW"])).count()
    discrepant_invoices = db.query(InvoiceRecord).filter(InvoiceRecord.arithmetic_discrepancy == True).count()
    exported_invoices = db.query(InvoiceRecord).filter(InvoiceRecord.export_status == "EXPORTED").count()

    # Enterprise Multi-Agent Ops Metrics
    verified_revenue = db.query(func.sum(PaymentEvent.amount)).filter(PaymentEvent.verified == True).scalar() or 0.0
    active_projects = db.query(EnterpriseProject).filter(EnterpriseProject.current_state != "COMPLETED").count()
    pending_contracts = db.query(ContractDraft).filter(ContractDraft.is_approved == False).count()

    # Workflow System Success/Failure
    workflow_success = db.query(AuditLog).filter(AuditLog.status == "SUCCESS").count()
    workflow_failures = db.query(AuditLog).filter(AuditLog.status.in_(["FAILED", "ERROR"])).count()

    # Recent activity stream
    recent_logs = db.query(AuditLog).order_by(desc(AuditLog.timestamp)).limit(10).all()

    total_pending_approvals = pending_drafts + awaiting_review_invoices + pending_contracts

    return {
        "leads": {
            "total": total_leads,
            "qualified": qualified_leads,
            "avg_latency_ms": round(float(avg_latency), 1)
        },
        "support": {
            "total_tickets": total_tickets,
            "urgent_tickets": urgent_tickets,
            "pending_drafts": pending_drafts
        },
        "invoices": {
            "total_scanned": total_invoices,
            "awaiting_review": awaiting_review_invoices,
            "discrepancies_caught": discrepant_invoices,
            "exported_to_sheets": exported_invoices
        },
        "enterprise": {
            "verified_revenue_usd": round(float(verified_revenue), 2),
            "active_projects": active_projects,
            "pending_contracts": pending_contracts
        },
        "system": {
            "demo_mode": settings.demo_mode,
            "workflow_success_count": workflow_success,
            "workflow_failure_count": workflow_failures,
            "total_pending_approvals": total_pending_approvals
        },
        "recent_activity": [log.to_dict() for log in recent_logs]
    }

@app.get("/api/v1/system/audit-logs", tags=["System"])
def list_system_audit_logs(
    module: Optional[str] = Query(None, description="Filter: lead_routing, support, invoices, enterprise"),
    status: Optional[str] = Query(None, description="Filter: SUCCESS, FAILED, WARNING"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Retrieve immutable audit logs across the enterprise suite."""
    query = db.query(AuditLog)
    if module:
        query = query.filter(AuditLog.module == module.lower())
    if status:
        query = query.filter(AuditLog.status == status.upper())

    total = query.count()
    logs = query.order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit).all()
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [log.to_dict() for log in logs]
    }

@app.post("/api/v1/system/demo-mode/toggle", tags=["System"])
def toggle_demo_mode():
    """Toggle between Demo Mode (deterministic mocks) and Live Mode (external API calls)."""
    settings.demo_mode = not settings.demo_mode
    logger.info(f"[System] DEMO_MODE toggled to: {settings.demo_mode}")
    return {"demo_mode": settings.demo_mode, "message": f"Demo mode is now {'ENABLED' if settings.demo_mode else 'DISABLED'}."}
