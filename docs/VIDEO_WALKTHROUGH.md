# Video Walkthrough & Demonstration Checkpoints

This recording script provides a structured timeline for recording an executive product demonstration or portfolio video of the Enterprise AI Automation Suite.

---

## Recording Plan & Scene Breakdown

### Scene 1: Executive Overview & Dashboard (0:00 - 1:15)
- **Visual**: Unified Operations Dashboard (`http://127.0.0.1:8000/`)
- **Talking Points**:
  - Introduce the suite: four isolated automation engines united in a single executive operations portal.
  - Highlight the live metrics bar: Qualified leads, support inbox, invoice scanner, verified revenue ($), and pending approvals queue.
  - Point out the Demo/Live mode toggle in the sidebar.

### Scene 2: Module 1 — Lead Intelligence (1:15 - 2:45)
- **Visual**: **Lead Intelligence** Tab
- **Actions**:
  - Fill in the lead intake form with enterprise parameters (e.g. Wayne Enterprises, $95,000 budget).
  - Submit and observe immediate scoring (Score: 88/100, Priority: HIGH).
  - Open the lead detail drawer: explain the AI qualification summary, tailored sales talking points, and sub-10 second execution latency.
  - Demonstrate deduplication by submitting the same lead again to show instant idempotent recovery.

### Scene 3: Module 2 — Support Triage & Injection Defense (2:45 - 4:15)
- **Visual**: **Support Triage** Tab
- **Actions**:
  - Click **Load Billing Sample**: demonstrate RAG grounding referencing approved invoicing policies. Show that response is saved as a provider draft (default draft-only safety).
  - Click **Test Prompt Injection**: submit a simulated attack attempting to steal API keys and demand refunds. Show how the engine neutralizes the attack, flags `PROMPT_INJECTION_ATTEMPT`, and locks the draft into human review.
  - In the Human Approvals Queue, demonstrate operator authorization.

### Scene 4: Module 3 — AI Vision Invoice Scanner (4:15 - 5:45)
- **Visual**: **Invoice Scanner** Tab
- **Actions**:
  - Upload a valid PDF invoice: observe instant schema extraction and green `VALID` badge.
  - Upload an invoice with intentional math errors: show red `ARITHMETIC_MISMATCH` badge highlighting the exact discrepancy delta.
  - Open the interactive **Line-Item Editor**: correct the misread values, save to re-verify arithmetic, and export to Google Sheets.

### Scene 5: Module 4 — Multi-Agent Enterprise Operations (5:45 - 7:15)
- **Visual**: **Enterprise Operations** Tab
- **Actions**:
  - Onboard a new customer project ($75,000 deal value).
  - Step 1 to 2: Show state transition to `QUALIFIED`.
  - Step 2 to 3: Generate template-based MSA contract draft. Review legal disclaimer and authorize.
  - Step 3 to 4: Simulate a verified Stripe signed webhook. Show cryptographic signature verification advancing project to `PAYMENT_VERIFIED`.
  - Step 4 to 5: Auto-provision dedicated Slack workspace `#proj-company` and mark `COMPLETED`.
  - Review the evidence-grounded **Weekly Executive Digest** summarizing actual database metrics.

### Scene 6: Architectural Summary & Wrap-up (7:15 - 8:00)
- **Visual**: Terminal showing passing pytest suite (`pytest tests/ -v`).
- **Talking Points**:
  - Review clean test coverage across all 4 modules.
  - Highlight Make.com and n8n blueprint configurations.
  - Reiterate enterprise readiness, security boundaries, and production maintainability.
