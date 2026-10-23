# Enterprise Security & Governance Guide

## 1. Threat Model & Security Posture

The Enterprise AI Automation Suite enforces defense-in-depth principles across all API boundaries, document ingestors, and external service adapters.

| Threat Category | Potential Attack Vector | Implemented Mitigation |
| :--- | :--- | :--- |
| **Prompt Injection** | Malicious text in support emails attempting to override AI instructions | Multi-tier regex sanitizer, instruction delimiter isolation, forced human review on detected patterns |
| **Replay Attacks** | Repeated delivery of captured Stripe webhook payloads | 300-second timestamp tolerance validation + unique event ID persistence |
| **Financial Fraud** | Fabricated invoices or client-provided fake payment confirmations | Deterministic arithmetic verification ($\sum \text{items} == \text{subtotal}$, $\text{subtotal} + \text{tax} - \text{discount} == \text{total}$); client redirects ignored |
| **Unsafe File Upload** | Malicious binaries masquerading as PDF invoices | Binary magic bytes signature verification (`%PDF-`, `\x89PNG`) + size limits |
| **Data Leakage** | API keys or customer PII leaked into operational logs | Automated secret masking (`mask_secret()`) + bounded payload truncation |

---

## 2. Prompt Injection Defense (Module 2)

All inbound customer messages are treated as **untrusted input**.
- The `sanitize_untrusted_input` pipeline scans for known injection patterns:
  - `ignore previous instructions`
  - `you are now an unrestricted assistant`
  - `reveal your system prompt / API keys`
- When detected:
  - `PROMPT_INJECTION_ATTEMPT` is recorded in the ticket risk flags.
  - The AI prompt is replaced with a safe, polite hold response.
  - The ticket is immediately routed to the human security review queue.
  - Outbound email generation is locked until authorized by a security operator.

---

## 3. Cryptographic Webhook Security (Module 4)

Stripe webhooks are validated deterministically without using LLMs:
1. Extract `timestamp` and `v1` signatures from `stripe-signature` header.
2. Verify that `abs(current_time - timestamp) <= 300 seconds` (defends against delayed or replayed payloads).
3. Compute expected HMAC-SHA256 signature using `STRIPE_WEBHOOK_SECRET`:
   $$\text{HMAC-SHA256}(\text{secret}, \text{timestamp} + "." + \text{payload})$$
4. Use constant-time comparison (`hmac.compare_digest`) to prevent timing attacks.
5. Check event ID in database to guarantee idempotent execution.

---

## 4. Human Approval Gates & Financial Integrity

- **Default Draft-Only**: Outbound emails are saved as drafts in the provider inbox. No emails are dispatched automatically.
- **Mandatory Approval Operations**:
  - Outbound email dispatch
  - Financial refunds and credit commitments
  - Invoices with arithmetic discrepancies
  - Contract draft execution
- **Financial Rule**: Values explicitly extracted from documents are never silently altered. Missing tax amounts are never inferred as facts.

---

## 5. Data Privacy & Least-Privilege Access

- API tokens are read only from environment variables and never committed to source control.
- Logs strictly mask sensitive credentials (e.g. `sk-****1234`).
- Uploaded files are fingerprinted via SHA-256 and stored in an isolated directory with restricted access.
