# External Integrations & Automation Blueprints

This guide provides configuration, authentication requirements, and import instructions for external integrations and visual automation workflows.

---

## 1. Visual Automation Platforms

### Make.com Scenarios
Pre-configured importable scenario blueprints are located in `workflows/make/`:
- `workflows/make/module1_lead_routing_blueprint.json`
- `workflows/make/module2_email_triage_blueprint.json`
- `workflows/make/module3_invoice_scanner_blueprint.json`
- `workflows/make/module4_enterprise_ops_blueprint.json`

**How to Import into Make.com**:
1. Log in to [Make.com](https://www.make.com/).
2. Create a new scenario.
3. Click the three dots menu (**More**) at the bottom and select **Import Blueprint**.
4. Select the desired blueprint JSON file.
5. Re-link your account connections for OpenAI, Airtable, Slack, Gmail, Google Sheets, or Stripe.
6. Click **Save** and activate the scenario.

### n8n Workflows
Self-hostable workflow JSON definitions are located in `workflows/n8n/`:
- `workflows/n8n/module1_lead_routing_n8n.json`
- `workflows/n8n/module2_email_triage_n8n.json`
- `workflows/n8n/module3_invoice_scanner_n8n.json`
- `workflows/n8n/module4_enterprise_ops_n8n.json`

**How to Import into n8n**:
1. Open your n8n workspace.
2. Click **Add Workflow** -> **Import from File**.
3. Select the target n8n JSON file.
4. Set credentials for the imported nodes.
5. Activate the workflow.

---

## 2. Service-Specific Configuration

### OpenAI (LLM & Vision)
- **Required Secret**: `OPENAI_API_KEY`
- **Models Used**:
  - `OPENAI_MODEL`: `gpt-4o-mini` (fast, cost-effective qualification and triage)
  - `OPENAI_VISION_MODEL`: `gpt-4o` (invoice visual and OCR extraction)
- **Offline Fallback**: When `OPENAI_API_KEY` is omitted, the built-in deterministic engine generates structured, schema-valid qualification outputs without throwing errors.

### Airtable (Module 1 & 4)
- **Required Secrets**:
  - `AIRTABLE_API_KEY` (Personal Access Token with `data.records:read`, `data.records:write`, `schema.bases:read`)
  - `AIRTABLE_BASE_ID` (e.g. `appXXXXXXXXXXXXXX`)
  - `AIRTABLE_TABLE_NAME`: Default `Leads`
- **Schema Fields**:
  - `Lead ID` (Single line text)
  - `Name` (Single line text)
  - `Email` (Email)
  - `Company` (Single line text)
  - `Budget` (Currency)
  - `Score` (Number)
  - `Priority` (Single select: HIGH, MEDIUM, LOW)
  - `Status` (Single select: QUALIFIED, UNQUALIFIED, INCOMPLETE, MANUAL_REVIEW)

### Slack (Module 1 & 4)
- **Required Secrets**:
  - `SLACK_WEBHOOK_URL` (Incoming Webhook URL) OR
  - `SLACK_BOT_TOKEN` (Bot User OAuth Token with `chat:write`, `channels:manage`)
  - `SLACK_DEFAULT_CHANNEL`: `#enterprise-alerts`

### Gmail / Microsoft Outlook (Module 2)
- **Draft-Only Safety**: The email adapter saves generated replies as drafts in the provider inbox. Emails are never dispatched automatically without explicit human sign-off.
- **Environment**:
  - `EMAIL_PROVIDER`: `mock`, `gmail`, or `smtp`
  - `EMAIL_SMTP_HOST`, `EMAIL_SMTP_PORT`, `EMAIL_USER`, `EMAIL_PASSWORD`

### Google Sheets (Module 3)
- **Required Secrets**:
  - `GOOGLE_SERVICE_ACCOUNT_JSON`: Path to service account key file
  - `GOOGLE_SHEET_ID`: Target Google Spreadsheet ID
- **Target Columns**: `Exported At`, `Vendor`, `Invoice #`, `Date`, `Currency`, `Subtotal`, `Tax`, `Discount`, `Total`, `Payment Status`, `Document Hash`.

### Stripe (Module 4)
- **Webhook Endpoint**: `POST /api/v1/enterprise/stripe/webhook`
- **Required Secret**: `STRIPE_WEBHOOK_SECRET` (e.g. `whsec_...`)
- **Required Header**: `stripe-signature` containing timestamp `t=` and HMAC signature `v1=`
- **Security Check**: Events older than 300 seconds are rejected as replay attacks.
