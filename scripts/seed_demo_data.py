#!/usr/bin/env python3
"""
Enterprise Demo Data Seeder.
Populates realistic synthetic operational fixtures across all four modules for demonstration.
Conforms to workflow-automation-scripting standards with --dry-run and idempotent checks.
"""

import argparse
import sys
import os
import time

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal, init_db
from app.modules.lead_routing.schemas import LeadIntakeRequest
from app.modules.lead_routing.service import lead_routing_service
from app.modules.customer_support.schemas import EmailIngestRequest
from app.modules.customer_support.service import customer_support_service
from app.modules.multi_agent_ops.schemas import ProjectIntakeRequest
from app.modules.multi_agent_ops.agents.intake_agent import intake_agent

SAMPLE_LEADS = [
    {
        "name": "Sarah Connor",
        "email": "sarah.connor@cyberdyne-defense.com",
        "phone": "+1-555-839-2001",
        "company": "Cyberdyne Systems",
        "company_size": "201-1000",
        "budget": 85000.0,
        "business_need": "We need an enterprise-grade multi-agent operations platform to automate our supplier intake, email triage, and accounting exports.",
        "product_interest": "Enterprise Operations Suite",
        "consent": True
    },
    {
        "name": "Bruce Wayne",
        "email": "bruce.wayne@wayneenterprises.com",
        "phone": "+1-555-888-9999",
        "company": "Wayne Enterprises",
        "company_size": "1000+",
        "budget": 120000.0,
        "business_need": "Automating logistics pipelines, financial invoice audits, and dedicated secure communications.",
        "product_interest": "Enterprise AI Automation Suite",
        "consent": True
    },
    {
        "name": "Peter Parker",
        "email": "peter@dailybugle.net",
        "phone": "+1-555-012-3456",
        "company": "Daily Bugle Media",
        "company_size": "11-50",
        "budget": 3500.0,
        "business_need": "Basic content filtering tools.",
        "product_interest": "Lead Intelligence Starter",
        "consent": True
    }
]

SAMPLE_SUPPORT = [
    {
        "sender_email": "finance@acme-global.com",
        "sender_name": "Finance Director",
        "subject": "Invoicing schedule and VAT receipt retrieval",
        "body": "Hello, could you please confirm when our monthly invoices are generated each month and where we can access verified VAT receipts?"
    },
    {
        "sender_email": "devops@mission-critical.org",
        "sender_name": "SRE Lead",
        "subject": "CRITICAL: Production API 500 errors across Europe",
        "body": "Sev-1 incident: Our production ingestion pipelines are failing with 500 internal server errors. Needs immediate engineering escalation!"
    }
]

SAMPLE_PROJECTS = [
    {
        "client_name": "Diana Prince",
        "client_email": "diana@themyscira-holdings.com",
        "company": "Themyscira Holdings",
        "service_type": "Enterprise AI Automation Suite",
        "deal_value": 65000.0,
        "currency": "USD"
    }
]

def seed_data(dry_run: bool = False, verbose: bool = False):
    init_db()
    db = SessionLocal()

    print(f"[*] Starting Demo Data Seeding (Dry-run: {dry_run})...")

    # 1. Seed Leads
    for idx, lead_dict in enumerate(SAMPLE_LEADS, 1):
        if verbose:
            print(f"  -> Processing Lead #{idx}: {lead_dict['company']} ({lead_dict['email']})")
        if not dry_run:
            payload = LeadIntakeRequest(**lead_dict)
            res = lead_routing_service.process_lead(db, payload)
            if verbose:
                print(f"     Status: {res.qualification_status} | Score: {res.score}/100 | Priority: {res.priority}")

    # 2. Seed Support Emails
    for idx, sup_dict in enumerate(SAMPLE_SUPPORT, 1):
        if verbose:
            print(f"  -> Triaging Support Message #{idx}: {sup_dict['subject']}")
        if not dry_run:
            payload = EmailIngestRequest(**sup_dict)
            res = customer_support_service.triage_email(db, payload)
            if verbose:
                print(f"     Intent: {res.intent} | Urgency: {res.urgency} | Approval Needed: {res.requires_human_approval}")

    # 3. Seed Enterprise Projects
    for idx, proj_dict in enumerate(SAMPLE_PROJECTS, 1):
        if verbose:
            print(f"  -> Onboarding Enterprise Project #{idx}: {proj_dict['company']}")
        if not dry_run:
            payload = ProjectIntakeRequest(**proj_dict)
            proj = intake_agent.execute(db, payload)
            if verbose:
                print(f"     Project ID: {proj.id} | State: {proj.current_state}")

    db.close()
    print("[+] Seeding complete! All demonstration fixtures ready.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enterprise AI Automation Suite Demo Seeder")
    parser.add_argument("--dry-run", action="store_true", help="Simulate seeding without database changes")
    parser.add_argument("--verbose", action="store_true", help="Print detailed progress logs")
    args = parser.parse_args()

    seed_data(dry_run=args.dry_run, verbose=args.verbose)
