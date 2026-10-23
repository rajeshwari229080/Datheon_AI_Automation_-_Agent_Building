# Client Onboarding, Training & Handover Plan

This document outlines the handover process, prerequisites, operational roles, and training syllabus for enterprise clients deploying the AI Automation Suite.

---

## 1. Client Prerequisites & Access Checklist

Before transitioning from local testing to enterprise production deployment, ensure the following credentials and accounts are provisioned:

| Integration | Minimum Required Role / Scope | Key / Identifier Name |
| :--- | :--- | :--- |
| **OpenAI** | Organization Admin | `OPENAI_API_KEY` |
| **Airtable** | Base Creator / Editor | `AIRTABLE_API_KEY`, `AIRTABLE_BASE_ID` |
| **Slack** | Workspace Admin / Bot User | `SLACK_BOT_TOKEN`, `SLACK_DEFAULT_CHANNEL` |
| **Email Provider** | Service Account (Gmail API or SMTP) | `EMAIL_USER`, `EMAIL_PASSWORD` |
| **Google Cloud** | Service Account with Google Sheets API | `GOOGLE_SERVICE_ACCOUNT_JSON`, `GOOGLE_SHEET_ID` |
| **Stripe** | Developer / Webhook Read-Write | `STRIPE_API_KEY`, `STRIPE_WEBHOOK_SECRET` |

---

## 2. Operational Roles & Responsibilities

1. **Sales & Growth Operations**:
   - Monitors the **Lead Intelligence** pipeline.
   - Reviews AI qualification scores, priority assignments, and personalized sales talking points.
   - Re-triggers Airtable/Slack synchronization if external network issues occur.

2. **Customer Support Operations**:
   - Manages the **Support Triage** inbox.
   - Reviews grounded response drafts before approval.
   - Authorizes escalation for Sev-1 incidents, customer complaints, or sensitive requests.

3. **Finance & Accounting Operations**:
   - Oversees the **Invoice Scanner** queue.
   - Audits invoices flagged with `ARITHMETIC_MISMATCH` or `DUPLICATE`.
   - Uses the interactive Line-Item Editor to correct vendor OCR misreadings.
   - Authorizes and exports approved invoices to the central Google Sheets journal.

4. **Legal & Executive Operations**:
   - Reviews template-based contract drafts in the **Enterprise Operations** workspace.
   - Countersigns contracts and authorizes state progression to `PENDING_PAYMENT`.
   - Inspects weekly evidence-grounded **Executive Digests** delivered to Slack.

---

## 3. Handover Training Syllabus

- **Session 1: Platform Overview & Navigation (30 mins)**: Dashboard navigation, health checks, demo mode vs live mode toggling.
- **Session 2: Sales & Support Automation (45 mins)**: Webhook endpoints, lead scoring rules, prompt injection defenses, grounded draft approvals.
- **Session 3: Accounting Sync & Financial Integrity (45 mins)**: PDF scanning, arithmetic verification formulas, resolving line-item discrepancies.
- **Session 4: Multi-Agent Enterprise Orchestration (45 mins)**: State machine lifecycle, Stripe webhook signature configuration, Slack channel auto-provisioning.
