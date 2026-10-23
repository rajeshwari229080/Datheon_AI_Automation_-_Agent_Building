# Quality Assurance & Testing Guide

This document details the test strategy, execution commands, and verified results for the Enterprise AI Automation Suite.

---

## 1. Test Suite Structure

```
tests/
├── conftest.py                       # Transactional database fixtures & test client
├── test_module1_lead_routing.py      # Lead validation, deterministic scoring, idempotency
├── test_module2_support_triage.py    # Email classification, RAG retrieval, prompt injection defense
├── test_module3_invoice_scanner.py   # PDF upload, arithmetic verification, duplicate detection, Sheets sync
├── test_module4_multi_agent.py       # Supervisor state machine, Stripe HMAC signatures, digest generation
├── test_security_and_integrity.py   # Magic bytes validation, secret masking, injection protection
└── test_performance_sla.py          # Sub-10 second SLA latency benchmarking
```

---

## 2. Test Execution Commands

### Run Full Test Suite
```bash
pytest tests/ -v
```

### Run Module-Specific Tests
```bash
# Module 1: Lead Routing
pytest tests/test_module1_lead_routing.py -v

# Module 2: Support Triage & Injection Defense
pytest tests/test_module2_support_triage.py -v

# Module 3: Invoice Scanner & Arithmetic Verification
pytest tests/test_module3_invoice_scanner.py -v

# Module 4: Multi-Agent Enterprise Operations
pytest tests/test_module4_multi_agent.py -v

# Security & SLA Performance
pytest tests/test_security_and_integrity.py tests/test_performance_sla.py -v
```

---

## 3. Verified Test Results

| Test Module | Test Case | Status | Verified Outcome |
| :--- | :--- | :--- | :--- |
| **Module 1** | `test_valid_lead_intake_and_qualification` | **PASSED** | Valid enterprise lead qualified (Score 88/100, Priority HIGH), synced to Airtable/Slack, latency < 10s |
| **Module 1** | `test_lead_idempotency_prevents_duplicate_records` | **PASSED** | Identical payload with same idempotency key returns existing lead without duplicate database rows |
| **Module 1** | `test_invalid_lead_rejected_safely` | **PASSED** | Missing consent and malformed email return 422 Unprocessable Entity |
| **Module 1** | `test_lead_listing_and_filtering` | **PASSED** | Priority filter (HIGH) and text search filter records accurately |
| **Module 2** | `test_billing_email_triage_and_grounded_draft` | **PASSED** | Billing question categorized as BILLING, draft references enterprise invoicing schedule |
| **Module 2** | `test_urgent_incident_escalation` | **PASSED** | Sev-1 production outage categorized with CRITICAL urgency and FRUSTRATED sentiment |
| **Module 2** | `test_prompt_injection_defense` | **PASSED** | Jailbreak & credential theft attempt flagged (`PROMPT_INJECTION_ATTEMPT`), hold draft generated |
| **Module 2** | `test_human_approval_gate_for_sending_email` | **PASSED** | Sending blocked until human operator authorizes; outbound email logged |
| **Module 3** | `test_valid_pdf_invoice_upload_and_extraction` | **PASSED** | In-memory generated PDF parsed into schema; subtotal + tax = total matches; status VALID |
| **Module 3** | `test_arithmetic_mismatch_flagged_for_review` | **PASSED** | Discrepancy between subtotal ($1,200) + tax ($120) and stated total ($1,800) caught; status ARITHMETIC_MISMATCH |
| **Module 3** | `test_duplicate_document_detection` | **PASSED** | Second upload of identical PDF flagged as DUPLICATE via SHA-256 fingerprint |
| **Module 3** | `test_reject_corrupt_or_unsafe_upload` | **PASSED** | Binary without valid magic bytes rejected with 400 Bad Request |
| **Module 3** | `test_google_sheets_export_and_retry` | **PASSED** | Simulated network timeout caught; retry succeeds and updates export state |
| **Module 4** | `test_multi_agent_onboarding_lifecycle` | **PASSED** | Full FSM progression: INTAKE -> QUALIFIED -> CONTRACT_DRAFTED -> PENDING_PAYMENT -> PAYMENT_VERIFIED -> COMPLETED |
| **Module 4** | `test_reject_invalid_stripe_signature` | **PASSED** | Webhook with forged HMAC signature rejected with 400 Bad Request |
| **Module 4** | `test_executive_digest_factual_reporting` | **PASSED** | Weekly digest aggregates real database payment and ticket counts |
