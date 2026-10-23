# Enterprise Architecture & System Design

## 1. Architectural Strategy
The Datheon Enterprise AI Automation Suite is engineered around modular domain boundaries, decoupling business logic from external cloud APIs through an abstract adapter architecture.

```mermaid
graph TD
    Client[Web Dashboard / Webhooks / API Clients] --> Gateway[FastAPI API Gateway]
    
    subgraph Gateway Layer
        Gateway --> Auth[CORS & Input Validation]
        Gateway --> Audit[Audit Trail Interceptor]
    end

    subgraph Service Modules
        Auth --> M1[Module 1: Lead Routing Engine]
        Auth --> M2[Module 2: Customer Support Triage]
        Auth --> M3[Module 3: Invoice Vision Scanner]
        Auth --> M4[Module 4: Multi-Agent Enterprise Ops]
    end

    subgraph State Machine Supervisor
        M4 --> FSM[Finite State Machine Supervisor]
        FSM --> A1[1. Intake Agent]
        FSM --> A2[2. Lead Agent]
        FSM --> A3[3. Support Agent]
        FSM --> A4[4. Invoice Agent]
        FSM --> A5[5. Contract Agent]
        FSM --> A6[6. Payment Service]
        FSM --> A7[7. Collaboration Agent]
        FSM --> A8[8. Reporting Agent]
    end

    subgraph Data & Adapter Layer
        M1 & M2 & M3 & M4 --> Adapters[Adapter Abstraction Registry]
        Adapters --> Airtable[Airtable Adapter]
        Adapters --> Slack[Slack Adapter]
        Adapters --> Email[Gmail/Outlook Adapter]
        Adapters --> Sheets[Google Sheets Adapter]
        Adapters --> Stripe[Stripe Adapter]
        Adapters --> OpenAI[OpenAI Adapter]
        M1 & M2 & M3 & M4 --> DB[(SQLite Database WAL Mode)]
    end
```

## 2. Core Modules Architecture

### Module 1: Lead Routing & Instant AI Qualification
- **Intake Pipeline**: Ingests JSON from web forms, webhooks, or CRM systems.
- **Deterministic Scorer**: Evaluates budget tiers (40 pts), company size (30 pts), business need clarity (20 pts), and contact completeness (10 pts).
- **AI Qualification**: Enriches with semantic objection handling, suggested talking points, and confidence estimation.
- **Idempotency Engine**: Hashes `email + company` to guarantee identical requests yield identical results without duplicate syncs.

### Module 2: Autonomous Support & Intelligent Email Triage
- **Sanitizer & Anti-Injection Guardrail**: Neutralizes prompt injection strings and flags sensitive requests (refunds, cancellations, Sev-1 outages).
- **RAG Knowledge Base**: Retrieves approved enterprise policies and SLAs using keyword/token overlap scoring.
- **Grounded Draft Engine**: Produces polite responses strictly adhering to retrieved evidence.
- **Safety Gate**: Default draft-only mode; human approval mandatory to send emails.

### Module 3: AI Vision Invoice Scanner & Accounting Sync
- **File Signature Guard**: Verifies binary magic bytes (`%PDF-`, `\x89PNG`) to prevent executable file uploads.
- **Text & Vision Extraction**: Uses `pypdf` with fallback to OpenAI vision/text parser.
- **Arithmetic Verification**:
  $$\sum (\text{item\_qty} \times \text{unit\_price}) \approx \text{subtotal}$$
  $$\text{subtotal} + \text{tax} - \text{discount} \approx \text{total}$$
  Flags mismatches > $0.05 for human review.
- **Deduplication**: SHA-256 binary hash + composite vendor/invoice number index.

### Module 4: Multi-Agent Enterprise Operations
- **9 Narrow Agents**:
  1. Intake Agent
  2. Lead Intelligence Agent
  3. Support Triage Agent
  4. Invoice Extraction Agent
  5. Contract Preparation Agent
  6. Payment Verification Service
  7. Collaboration Agent
  8. Reporting Agent
  9. Workflow Supervisor
- **Deterministic Stripe Webhook Verification**: Cryptographically validates HMAC-SHA256 signatures with a 300-second replay tolerance window.
- **Reporting Agent**: Aggregates factual metrics directly from SQLite.

## 3. Storage & Persistence
- Local development utilizes SQLite in WAL (Write-Ahead Logging) mode with foreign key enforcement.
- Schema is designed to migrate to PostgreSQL with zero model changes.
