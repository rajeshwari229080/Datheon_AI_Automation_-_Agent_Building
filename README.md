# Enterprise AI Automation Suite

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2.8+-e92063.svg)](https://docs.pydantic.dev/)
[![Tests Passing](https://img.shields.io/badge/tests-passing-brightgreen)](https://pytest.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-grade, four-module enterprise operations platform integrating **Lead Intelligence**, **Autonomous Support Triage**, **AI Vision Invoice Scanning**, and **Multi-Agent Enterprise Orchestration** into a unified executive dashboard.

---

## 🌟 Executive Overview & Key Capabilities

The Enterprise AI Automation Suite addresses core operational bottlenecks across sales intake, customer support, accounts payable, and client onboarding:

1. **Module 1 — Multi-Source Lead Routing & Instant AI Qualification**
   - Ingests leads from web forms, webhooks, or external CRM triggers.
   - Deterministic enterprise criteria scoring combined with schema-validated LLM qualification.
   - Live & mock adapters for **Airtable** and **Slack** lead notifications.
   - Idempotency key tracking to safely ignore duplicate webhook re-deliveries.
   - Guaranteed SLA target: sub-10 second end-to-end processing.

2. **Module 2 — Autonomous Customer Support & Intelligent Email Triage**
   - 8 distinct intent categories, independent urgency, and sentiment analysis.
   - Grounded RAG retrieval referencing an approved enterprise knowledge base.
   - Multi-tier prompt injection defense preventing unauthorized command execution.
   - Strict draft-only operation with human approval queues for refunds, cancellations, and escalations.

3. **Module 3 — AI Vision Invoice Scanner & Accounting Sync**
   - Secure PDF and receipt uploads with magic byte binary signature validation.
   - Hybrid regex and vision parsing extracting vendors, line items, taxes, and totals.
   - Deterministic mathematical verification checking that subtotal, tax, and discount equal the stated total.
   - SHA-256 fingerprint deduplication, interactive line-item editor, and **Google Sheets** accounting sync with retry recovery.

4. **Module 4 — End-to-End Multi-Agent Enterprise Operations System**
   - 9 specialized agents (*Intake, Lead Intelligence, Support Triage, Invoice Extraction, Contract Preparation, Payment Verification, Collaboration, Reporting, Workflow Supervisor*).
   - Strict Finite State Machine (FSM) enforcing valid business progression.
   - Deterministic HMAC-SHA256 signature verification for **Stripe Webhooks** with replay window protection.
   - Evidence-grounded weekly executive operations digest strictly derived from true database records.

5. **Unified Enterprise Operations Dashboard**
   - Modern, high-contrast, WCAG AA compliant single-page application.
   - Live metrics, interactive forms, review queues, audit logs, and integration diagnostics.
   - Instant Demo Mode toggle simulating external dependencies with realistic test fixtures.

---

## 🚀 Quickstart & Local Setup

### Prerequisites
- Python 3.10+ (tested on Python 3.12)
- Git

### Installation
```bash
# Clone the repository
git clone git@github.com:rajeshwari229080/Datheon_AI_Automation_-_Agent_Building.git
cd Datheon_AI_Automation_-_Agent_Building/rw

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
```

### Running the Application
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser to:
- **Unified Operations Dashboard**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Interactive OpenAPI Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🧪 Testing & Verification

The suite includes an automated test suite verifying business logic, financial math, injection defenses, and webhook replay protection:

```bash
# Run all automated tests
pytest tests/ -v
```

---

## 📁 Repository Structure

```
├── app/
│   ├── main.py                     # FastAPI application factory & API gateway
│   ├── config.py                   # Pydantic Settings & environment variables
│   ├── database.py                 # SQLite WAL engine & session manager
│   ├── models/                     # SQLAlchemy persistence domain models
│   ├── adapters/                   # Integration adapters (Live + Mock)
│   ├── modules/
│   │   ├── lead_routing/           # Module 1
│   │   ├── customer_support/       # Module 2
│   │   ├── invoice_scanner/        # Module 3
│   │   └── multi_agent_ops/        # Module 4
│   └── dashboard/                  # Unified web dashboard templates & static assets
├── workflows/
│   ├── make/                       # Make.com scenario blueprint JSONs
│   └── n8n/                        # n8n workflow definitions
├── tests/                          # Pytest unit and integration test suites
└── docs/                           # Enterprise documentation suite
```

---

## 📚 Documentation Suite
- [Architecture & Design Decisions](docs/ARCHITECTURE.md)
- [Local Installation & Setup](docs/SETUP.md)
- [External Integrations & Blueprints](docs/INTEGRATIONS.md)
- [Security Threat Model & Guardrails](docs/SECURITY.md)
- [Testing & Quality Assurance](docs/TESTING.md)
- [16-Scenario Demonstration Walkthrough](docs/DEMO_GUIDE.md)
- [Client Onboarding & Training Plan](docs/CLIENT_ONBOARDING.md)
- [Video Demonstration Script](docs/VIDEO_WALKTHROUGH.md)
