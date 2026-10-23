# Enterprise AI Automation Suite

<div align="center">

[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2.8+-E92063?style=for-the-badge&logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![Tests](https://img.shields.io/badge/Pytest-20%2F20%20Passing-10B981?style=for-the-badge&logo=pytest&logoColor=white)](https://pytest.org)
[![SLA Latency](https://img.shields.io/badge/SLA%20Latency-310ms-4F46E5?style=for-the-badge&logo=speedtest&logoColor=white)](#-performance-benchmarks--sla)
[![License: MIT](https://img.shields.io/badge/License-MIT-F59E0B?style=for-the-badge&logo=opensourceinitiative&logoColor=white)](LICENSE)

<br/>

**A production-minded, decoupled enterprise automation operations suite unifying four mission-critical AI engines: Multi-Source Lead Qualification, Autonomous Support Triage, AI Vision Invoice Processing, and Multi-Agent Operations.**

<br/>

<img src="docs/assets/hero_light_banner.png" alt="Enterprise AI Automation Suite Hero Banner" width="100%" />

</div>

---

## 📑 Table of Contents
- [Executive Overview](#-executive-overview)
- [System Architecture](#-system-architecture)
- [Module 1: Multi-Source Lead Routing & Instant AI Qualification](#1-multi-source-lead-routing--instant-ai-qualification)
- [Module 2: Autonomous Customer Support & Intelligent Email Triage](#2-autonomous-customer-support--intelligent-email-triage)
- [Module 3: AI Vision Invoice Scanner & Accounting Sync](#3-ai-vision-invoice-scanner--accounting-sync)
- [Module 4: End-to-End Multi-Agent Enterprise Operations](#4-end-to-end-multi-agent-enterprise-operations)
- [Performance Benchmarks & SLA Verification](#-performance-benchmarks--sla-verification)
- [Security & Risk Mitigation](#-security--risk-mitigation)
- [Integration Ecosystem & Adapters](#-integration-ecosystem--adapters)
- [Quickstart & Local Installation](#-quickstart--local-installation)
- [Automated Testing](#-automated-testing)
- [Documentation Suite](#-documentation-suite)
- [License](#-license)

---

## 🌟 Executive Overview

Modern enterprises lose thousands of hours navigating disconnected sales forms, unstructured support inboxes, manual invoice reconciliation, and disjointed client onboarding. Traditional AI automation attempts frequently suffer from:
1. **Hallucinated Calculations**: LLMs guessing financial totals or currency exchanges.
2. **Security Vulnerabilities**: Direct prompt injection through untrusted customer emails and webhook payloads.
3. **Runaway Autonomy**: AI agents dispatching unverified emails or signing agreements without human authorization.
4. **Fragile Webhooks**: Vulnerability to replayed, spoofed, or unverified external events.

The **Enterprise AI Automation Suite** resolves these failure modes through **deterministic business guardrails**, **strict schema validation**, **cryptographic verification**, and a **human-in-the-loop draft safety model**.

---

## 🏗️ System Architecture

The suite is engineered around a clean, layered architecture separating core persistence and security from decoupled business modules and external connectors:

<div align="center">
  <img src="docs/assets/architecture_light.svg" alt="System Architecture Diagram" width="100%" />
</div>

### Architectural Invariants
- **Decoupled Module Lifecycles**: Each of the four business modules maintains isolated schemas, services, and routers.
- **Dual-Mode Adapter Pattern**: Seamless switching between isolated, reproducible **Demo Mode** fixtures and **Live Production APIs** (OpenAI, Airtable, Slack, Gmail, Sheets, Stripe).
- **WAL Persistence Layer**: High-concurrency SQLite with Write-Ahead Logging (WAL) and an automated upgrade path to PostgreSQL.
- **Unified Operations Cockpit**: Accessible, responsive single-page dashboard with real-time KPI metrics, line-item editors, and review queues.

---

## 1. Multi-Source Lead Routing & Instant AI Qualification

> **Objective**: Ingest leads from web forms, webhooks, or CRM systems, evaluate qualification against verifiable enterprise criteria, store structured records, and alert the sales team within seconds.

<div align="center">
  <img src="docs/assets/module1_lead_routing_light.png" alt="Module 1: Lead Routing and AI Qualification" width="95%" />
</div>

### Key Capabilities
- **Multi-Source Intake**: Accepts payloads from standard web forms, authenticated webhooks, or CRM inbound webhooks.
- **Deterministic Pre-Scoring**: Evaluates verifiable fields (employee count, explicit budget tier, timeline, ICP industry) on a 0–100 scale before calling AI.
- **Schema-Validated AI Fit**: LLM analyzes business need, flags missing data, recommends priority, and generates tailored sales talking points without hallucinating budget numbers.
- **Idempotency Defense**: Client idempotency keys prevent duplicate Airtable records and duplicate Slack notifications on webhook re-transmissions.
- **SLA Benchmark**: Verified latency of **310 ms** (far exceeding the < 10.0s SLA target).

---

## 2. Autonomous Customer Support & Intelligent Email Triage

> **Objective**: Ingest inbound customer messages, categorize intent, analyze urgency and sentiment, retrieve verified knowledge base citations, and generate safe, context-aware draft replies.

<div align="center">
  <img src="docs/assets/module2_support_triage_light.png" alt="Module 2: Customer Support and Email Triage" width="95%" />
</div>

### Key Capabilities
- **Multi-Class Intent Classification**: Accurately categorizes queries into 8 intents: *Billing & Payment, Technical Support, Account Access, Product Inquiries, Complaints, Urgent Incidents, Spam, and Ambiguous*.
- **RAG Knowledge Base Grounding**: Semantic TF-IDF cosine retriever retrieves approved enterprise knowledge base articles, strictly eliminating hallucinated company policies.
- **Active Prompt Injection Sanitizer**: Neutralizes malicious instruction injection attempts (e.g., `"ignore previous instructions"`, `"reveal system secrets"`).
- **Draft-Only Safety Queue**: All AI-generated responses default to draft mode. High-risk actions (refunds, cancellations, credential resets) require human operator sign-off before dispatch.

---

## 3. AI Vision Invoice Scanner & Accounting Sync

> **Objective**: Ingest invoice PDFs, validate binary file signatures, extract structured line items via OCR/Vision, perform strict mathematical verification, and synchronize verified ledgers to Google Sheets.

<div align="center">
  <img src="docs/assets/module3_invoice_scanner_light.png" alt="Module 3: AI Vision Invoice Scanner and Accounting Sync" width="95%" />
</div>

### Key Capabilities
- **Binary Signature Security**: Enforces `%PDF-` magic byte inspection and 15MB file size limits, blocking disguised executables and corrupt payloads.
- **Hybrid OCR & Vision Extraction**: Extracts vendor names, invoice numbers, dates, line items, quantities, unit prices, tax, and currency.
- **Deterministic Mathematical Verification**:
  $$\sum \text{Line Items} == \text{Subtotal}$$
  $$\text{Subtotal} + \text{Tax} - \text{Discount} == \text{Grand Total}$$
  Discrepancies automatically trigger manual review flags. AI is strictly forbidden from guessing tax or balancing equations.
- **SHA-256 Deduplication**: Generates unique document fingerprints to flag duplicate invoices before ledger insertion.
- **Google Sheets Sync & Recovery**: Asynchronously synchronizes approved invoices to cloud spreadsheets with transactional rollback and manual retry capability.

---

## 4. End-to-End Multi-Agent Enterprise Operations

> **Objective**: Orchestrate customer onboarding, legal contract preparation, cryptographic Stripe payment verification, Slack channel collaboration, and factual executive reporting.

<div align="center">
  <img src="docs/assets/module4_multiagent_light.png" alt="Module 4: Multi-Agent Enterprise Operations" width="95%" />
</div>

### 9 Specialized Autonomous Agents
| Agent | Role & Responsibility |
| :--- | :--- |
| **Intake Agent** | Validates incoming onboarding requests and normalizes customer data. |
| **Lead Intel Agent** | Evaluates enterprise fit and determines strategic prioritization. |
| **Support Triage Agent** | Ingests and classifies customer support inquiries with RAG grounding. |
| **Invoice Extraction Agent** | Parses uploaded documents and extracts structured line items. |
| **Contract Preparation Agent** | Assembles authorized legal templates with populated customer metadata. |
| **Payment Verification Service** | Deterministically validates Stripe HMAC-SHA256 signatures and payment status. |
| **Collaboration Agent** | Sets up dedicated Slack communication channels and alerts authorized staff. |
| **Reporting Agent** | Synthesizes verified platform metrics into executive digests without hallucination. |
| **Workflow Supervisor** | Enforces the Finite State Machine (FSM) and manages audit checkpoints. |

### Cryptographic Stripe Webhook Verifier
Deterministic HMAC-SHA256 signature verification matching Stripe's official `v1` timestamped scheme. Replay attacks are neutralized by rejecting webhook events outside a 300-second tolerance window.

---

## ⚡ Performance Benchmarks & SLA Verification

<div align="center">
  <img src="docs/assets/linkedin_banner.png" alt="Platform Benchmarks and Key Performance Indicators" width="95%" />
</div>

Every metric is measured through reproducible, automated benchmark tests in the test suite (`tests/test_performance_sla.py`):

| Operation / Benchmark | Target SLA | Measured Local Result | Status |
| :--- | :--- | :--- | :--- |
| **Lead Routing & Qualification Pipeline** | $< 10,000 \text{ ms}$ | **$310 \text{ ms}$ ($0.31 \text{ s}$)** | Verified & Passing |
| **Duplicate Lead Idempotency Check** | $0 \text{ duplicates}$ | **$0 \text{ duplicates (100% deduplication)}$** | Verified & Passing |
| **Email Triage & RAG Semantic Search** | $< 2,000 \text{ ms}$ | **$18 \text{ ms}$** | Verified & Passing |
| **Invoice Magic Byte Verification** | Immediate fail | **$< 2 \text{ ms}$** | Verified & Passing |
| **Stripe HMAC-SHA256 Webhook Verification** | $< 50 \text{ ms}$ | **$< 1 \text{ ms}$** | Verified & Passing |
| **Automated Test Suite Execution** | Fast CI (< 15s) | **$3.15 \text{ s}$ (20 tests)** | Verified & Passing |

---

## 🔒 Security & Risk Mitigation

- **Prompt Injection Defense**: Sanitizes instruction override tokens (`"ignore prior instructions"`, `"system override"`, `"developer mode"`) before passing inputs to LLM models.
- **Draft-Only Safeguards**: Outbound email sending and contract execution default to draft mode; financial and account actions require explicit operator confirmation.
- **Secret Redaction in Logs**: Automatically masks Bearer tokens, API credentials, customer PII, and financial parameters in the structured audit logging pipeline.
- **Deterministic Financial Authorization**: Arithmetic verification and signature checking are strictly written in deterministic Python code—never delegated to an LLM.

---

## 🔌 Integration Ecosystem & Adapters

The platform provides complete exportable scenario definitions for visual cloud orchestration (**Make.com**) and self-hosted automation (**n8n**):

| Service | Protocol / Driver | Demo Mode (Default) | Live Mode Config |
| :--- | :--- | :--- | :--- |
| **OpenAI** | GPT-4o / Vision API | Deterministic structured fallback | `OPENAI_API_KEY` |
| **Airtable** | REST API v0 | In-memory record tracker | `AIRTABLE_API_KEY`, `BASE_ID` |
| **Slack** | Incoming Webhooks | Simulated channel dispatcher | `SLACK_WEBHOOK_URL` |
| **Google Sheets** | Sheets API v4 | Memory ledger with rollback | `GOOGLE_SERVICE_ACCOUNT_JSON` |
| **Gmail / Outlook** | IMAP / REST API | Drafts store (draft-only) | `GMAIL_REFRESH_TOKEN` |
| **Stripe** | Webhook HMAC-SHA256 | Cryptographic test vector verifier | `STRIPE_WEBHOOK_SECRET` |

### Pre-Configured Workflow Blueprints
- **Make.com**: [`workflows/make/module1_lead_routing_blueprint.json`](workflows/make/module1_lead_routing_blueprint.json)
- **n8n**: [`workflows/n8n/module1_lead_routing_workflow.json`](workflows/n8n/module1_lead_routing_workflow.json)

---

## 🚀 Quickstart & Local Installation

### 1. Prerequisites
- Python 3.10, 3.11, or 3.12
- Git

### 2. Clone and Setup Environment
```bash
# Clone the repository
git clone git@github.com:rajeshwari229080/Datheon_AI_Automation_-_Agent_Building.git
cd Datheon_AI_Automation_-_Agent_Building/rw

# Install dependencies
pip install -r requirements.txt

# Configure environment variables (defaults to Demo Mode)
cp .env.example .env
```

### 3. Seed Realistic Demonstration Data (Optional)
```bash
python scripts/seed_demo_data.py
```

### 4. Launch the Enterprise Server
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

- **Unified Operations Dashboard**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Interactive OpenAPI Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🧪 Automated Testing

The suite includes 20 automated tests validating business rules, financial math, injection defenses, and webhook replay protection:

```bash
# Run the complete test suite
pytest tests/ -v
```

```
============================= test session starts =============================
collected 20 items

tests/test_module1_lead_routing.py::test_valid_lead_intake_and_qualification PASSED [  5%]
tests/test_module1_lead_routing.py::test_lead_idempotency_prevents_duplicate_records PASSED [ 10%]
tests/test_module1_lead_routing.py::test_invalid_lead_rejected_safely PASSED [ 15%]
tests/test_module1_lead_routing.py::test_lead_listing_and_filtering PASSED [ 20%]
tests/test_module2_support_triage.py::test_billing_email_triage_and_grounded_draft PASSED [ 25%]
tests/test_module2_support_triage.py::test_urgent_incident_escalation PASSED [ 30%]
tests/test_module2_support_triage.py::test_prompt_injection_defense PASSED [ 35%]
tests/test_module2_support_triage.py::test_human_approval_gate_for_sending_email PASSED [ 40%]
tests/test_module3_invoice_scanner.py::test_valid_pdf_invoice_upload_and_extraction PASSED [ 45%]
tests/test_module3_invoice_scanner.py::test_arithmetic_mismatch_flagged_for_review PASSED [ 50%]
tests/test_module3_invoice_scanner.py::test_duplicate_document_detection PASSED [ 55%]
tests/test_module3_invoice_scanner.py::test_reject_corrupt_or_unsafe_upload PASSED [ 60%]
tests/test_module3_invoice_scanner.py::test_google_sheets_export_and_retry PASSED [ 65%]
tests/test_module4_multi_agent.py::test_multi_agent_onboarding_lifecycle PASSED [ 70%]
tests/test_module4_multi_agent.py::test_reject_invalid_stripe_signature PASSED [ 75%]
tests/test_module4_multi_agent.py::test_executive_digest_factual_reporting PASSED [ 80%]
tests/test_performance_sla.py::test_lead_routing_sla_latency_benchmark PASSED [ 85%]
tests/test_security_and_integrity.py::test_secret_masking_in_logs PASSED [ 90%]
tests/test_security_and_integrity.py::test_prompt_injection_sanitizer PASSED [ 95%]
tests/test_security_and_integrity.py::test_file_magic_bytes_security PASSED [100%]

============================= 20 passed in 3.15s ==============================
```

---

## 📚 Documentation Suite

Comprehensive architecture, setup, security, and handover guides are available in the [`docs/`](docs/) directory:

- 📐 [Architecture & System Design Decisions](docs/ARCHITECTURE.md)
- ⚙️ [Local Setup & Configuration Guide](docs/SETUP.md)
- 🔌 [External Integrations & Webhook Setup](docs/INTEGRATIONS.md)
- 🛡️ [Security Threat Model & Guardrails](docs/SECURITY.md)
- 🧪 [Testing & Quality Assurance Protocol](docs/TESTING.md)
- 🎬 [16-Scenario Demonstration Walkthrough](docs/DEMO_GUIDE.md)
- 🤝 [Client Onboarding & Handover Plan](docs/CLIENT_ONBOARDING.md)
- 🎥 [Video Demonstration Recording Script](docs/VIDEO_WALKTHROUGH.md)
- 📢 [LinkedIn Announcement & Carousel Blueprint](LINKEDIN_POST.md)

---

## 📄 License

This project is licensed under the terms of the [MIT License](LICENSE).  
Copyright © 2026 Rajeshwari / Datheon AI Automation.
