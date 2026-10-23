from datetime import datetime, timezone, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.lead import LeadRecord
from app.models.email_support import SupportTicket
from app.models.invoice import InvoiceRecord
from app.models.enterprise import EnterpriseProject, PaymentEvent, ExecutiveDigestRecord
from app.adapters.slack_adapter import slack_adapter
from app.config import logger

class ReportingAgent:
    """Agent 8: Prepares factual, evidence-grounded executive digests strictly aggregated from database records."""

    @staticmethod
    def generate_weekly_digest(db: Session, days: int = 7) -> ExecutiveDigestRecord:
        now = datetime.now(timezone.utc)
        start_date = now - timedelta(days=days)

        # 1. True Database Metric Aggregations
        total_leads = db.query(LeadRecord).filter(LeadRecord.created_at >= start_date).count()
        qualified_leads = db.query(LeadRecord).filter(
            LeadRecord.created_at >= start_date,
            LeadRecord.qualification_status == "QUALIFIED"
        ).count()

        total_tickets = db.query(SupportTicket).filter(SupportTicket.created_at >= start_date).count()
        urgent_tickets = db.query(SupportTicket).filter(
            SupportTicket.created_at >= start_date,
            SupportTicket.urgency.in_(["HIGH", "CRITICAL"])
        ).count()

        total_invoices = db.query(InvoiceRecord).filter(InvoiceRecord.upload_date >= start_date).count()
        discrepant_invoices = db.query(InvoiceRecord).filter(
            InvoiceRecord.upload_date >= start_date,
            InvoiceRecord.arithmetic_discrepancy == True
        ).count()
        exported_invoices = db.query(InvoiceRecord).filter(
            InvoiceRecord.upload_date >= start_date,
            InvoiceRecord.export_status == "EXPORTED"
        ).count()

        verified_revenue = db.query(func.sum(PaymentEvent.amount)).filter(
            PaymentEvent.processed_at >= start_date,
            PaymentEvent.verified == True
        ).scalar() or 0.0

        active_projects = db.query(EnterpriseProject).filter(
            EnterpriseProject.current_state != "COMPLETED"
        ).count()

        factual_stats = {
            "period_days": days,
            "leads_received": total_leads,
            "leads_qualified": qualified_leads,
            "support_tickets_triaged": total_tickets,
            "urgent_incidents_flagged": urgent_tickets,
            "invoices_scanned": total_invoices,
            "arithmetic_discrepancies_caught": discrepant_invoices,
            "invoices_exported_to_accounting": exported_invoices,
            "verified_revenue_usd": round(float(verified_revenue), 2),
            "active_client_projects": active_projects,
            "source_coverage": ["leads", "support_tickets", "invoices", "payment_events", "enterprise_projects"],
            "last_refresh_utc": now.isoformat()
        }

        # 2. Evidence-grounded narrative
        narrative = (
            f"During the {days}-day reporting window, the Enterprise Automation Suite processed "
            f"{total_leads} incoming leads ({qualified_leads} qualified for sales follow-up). "
            f"The support engine triaged {total_tickets} inquiries, immediately escalating {urgent_tickets} urgent issues. "
            f"Accounting operations scanned {total_invoices} vendor documents, deterministically catching {discrepant_invoices} "
            f"arithmetic discrepancies before spreadsheet sync. Cryptographically verified payments totaled ${verified_revenue:,.2f} USD "
            f"across {active_projects} active onboarding projects."
        )

        record = ExecutiveDigestRecord(
            period_start=start_date,
            period_end=now,
            factual_stats=factual_stats,
            narrative_summary=narrative,
            discrepancies_flagged=discrepant_invoices,
            verified_revenue=round(float(verified_revenue), 2)
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        # Notify Slack with summary preview
        slack_adapter.send_approval_notification(
            title="Weekly Executive Digest Generated",
            details={
                "Reporting Window": f"{days} Days",
                "Verified Revenue": f"${verified_revenue:,.2f}",
                "Qualified Leads": f"{qualified_leads}/{total_leads}",
                "Discrepancies Caught": discrepant_invoices,
                "Digest ID": record.id
            }
        )

        logger.info(f"[ReportingAgent] Generated Executive Digest {record.id}")
        return record

reporting_agent = ReportingAgent()
