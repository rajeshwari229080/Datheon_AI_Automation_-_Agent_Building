# Enterprise Suite — 16 Demonstration Scenarios Walkthrough

This guide provides repeatable, step-by-step instructions for demonstrating all 16 acceptance scenarios required for enterprise evaluation and client handover.

---

## Scenario 1: Qualified Lead Stored & Routed to Sales
- **Action**: Navigate to **Lead Intelligence** tab. Submit:
  - Name: `Bruce Wayne`, Email: `bruce@wayneenterprises.com`
  - Company: `Wayne Enterprises` (Size: `1000+`)
  - Budget: `$95,000`
  - Need: `Automating enterprise workflow operations and accounting sync across our subsidiaries.`
- **Expected Outcome**: Lead score >= 85, Priority `HIGH`, Status `QUALIFIED`. Airtable record generated, Slack alert dispatched with personalized talking points.

## Scenario 2: Incomplete Lead Flagged for Review
- **Action**: Submit lead with brief need (`< 15` characters, e.g. `Need software`) and no phone.
- **Expected Outcome**: Status set to `INCOMPLETE` or `MANUAL_REVIEW`. Missing fields explicitly flagged in lead detail drawer.

## Scenario 3: Duplicate Lead Handled Idempotently
- **Action**: Submit the exact same lead from Scenario 1 a second time.
- **Expected Outcome**: Instant response with `is_duplicate: true`. Lead count does not increase; no duplicate Airtable records or Slack alerts created.

## Scenario 4: Urgent Support Message Escalated
- **Action**: In **Support Triage**, click **Load Sev-1 Outage** button and submit.
- **Expected Outcome**: Intent classified as `URGENT_INCIDENT`, Urgency set to `CRITICAL`, Sentiment `FRUSTRATED`. Ticket routed to human review with immediate Slack escalation alert.

## Scenario 5: Billing Email Receives Knowledge-Grounded Draft
- **Action**: Click **Load Billing Sample** button in Support Triage and submit.
- **Expected Outcome**: Intent classified as `BILLING`. Draft generated referencing enterprise invoicing cycles (1st of month) without hallucinating unverified policies. Saved to provider as draft.

## Scenario 6: Ambiguous Email Routed to Human
- **Action**: Ingest support email with vague text: `Something happened yesterday, please assist.`
- **Expected Outcome**: Intent categorized as `UNKNOWN`. Flagged for human review; draft requests polite clarification.

## Scenario 7: Valid Invoice Extracted & Reviewed
- **Action**: In **Invoice Scanner**, upload a clean balanced PDF (e.g. Subtotal $1,200 + Tax $120 = Total $1,320).
- **Expected Outcome**: Status displays `VALID` (green badge). Line items, tax, and total extracted accurately. Arithmetic verification passes.

## Scenario 8: Invoice with Incorrect Total Flagged
- **Action**: Upload an invoice where line items or subtotal + tax do not equal the grand total (e.g. Subtotal $1,200 + Tax $120, stated Total $1,800).
- **Expected Outcome**: Flagged with `ARITHMETIC_MISMATCH` (red badge). Discrepancy details show the exact $480.00 delta. Export button blocked until human review.

## Scenario 9: Duplicate Invoice Detected
- **Action**: Upload the same PDF file a second time.
- **Expected Outcome**: SHA-256 fingerprint matches existing record. Flagged as `DUPLICATE` with link to original invoice.

## Scenario 10: Failed Spreadsheet Export Can Be Retried
- **Action**: Click **Export** on an approved invoice.
- **Expected Outcome**: In case of transient network failure (simulated via adapter), status shows `FAILED` with retry button. Retrying successfully exports to Google Sheets.

## Scenario 11: Contract Prepared but Not Sent Automatically
- **Action**: In **Enterprise Operations**, initialize project for `Stark Industries` ($75,000). Click **Draft Enterprise MSA**.
- **Expected Outcome**: State advances to `CONTRACT_DRAFTED`. Contract contains standard legal clauses with explicit notice that it is an unreviewed draft. Never sent or countersigned automatically.

## Scenario 12: Valid Stripe Event Verified & Recorded
- **Action**: Authorize contract (advances to `PENDING_PAYMENT`). Click **Simulate Verified Stripe Webhook**.
- **Expected Outcome**: Cryptographic HMAC-SHA256 signature verified. State transitions to `PAYMENT_VERIFIED`. Airtable updated with payment status.

## Scenario 13: Invalid Stripe Signature Rejected
- **Action**: Post to `/api/v1/enterprise/stripe/webhook` with an altered payload or invalid signature header.
- **Expected Outcome**: Endpoint rejects request with `400 Bad Request` ("Signature verification failed"). Project state remains unchanged.

## Scenario 14: Duplicate Payment Event Idempotency
- **Action**: Re-deliver the same Stripe webhook event ID.
- **Expected Outcome**: Response indicates `ALREADY_PROCESSED`. No duplicate revenue or state transitions recorded.

## Scenario 15: Slack Notification Failure Visible & Recoverable
- **Action**: If Slack network is unreachable, lead record marks `slack_status: FAILED`.
- **Expected Outcome**: Failure is visible in dashboard. Clicking **Retry Airtable/Slack Sync** recovers the notification.

## Scenario 16: Executive Digest Summarizes Actual Stored Data
- **Action**: Click **Generate Fresh Digest** in Enterprise Operations.
- **Expected Outcome**: Digest summarizes real counts: actual leads received, qualified count, support tickets, discrepancies caught, and verified payment revenue.
