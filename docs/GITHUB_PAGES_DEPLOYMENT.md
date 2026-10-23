# 🌐 GitHub Pages Deployment & Hosting Guide

This repository is engineered to deploy seamlessly to **GitHub Pages**, providing a public, interactive web showcase of the **Enterprise AI Automation Suite**.

---

## 🎯 Live Deployment URL

Once enabled, your site will be live at:
👉 **`https://rajeshwari229080.github.io/Datheon_AI_Automation_-_Agent_Building/`**

---

## 🚀 How to Enable GitHub Pages (3 Options Supported)

In your GitHub repository, navigate to:
**Settings** ➔ **Pages** (under the "Code and automation" section on the left sidebar).

Under **Build and deployment**, GitHub provides two source options:

---

### Option 1: GitHub Actions (Recommended) ⭐️
1. Under **Source**, select **`GitHub Actions`** from the dropdown.
2. That's it! The pre-configured [`.github/workflows/deploy-pages.yml`](../.github/workflows/deploy-pages.yml) workflow will automatically run, execute the test suite, package the assets, and publish your site.
3. You can monitor the deployment under the **Actions** tab.

---

### Option 2: Deploy from a branch (Direct Root or /docs)
If you prefer branch-based publishing without waiting for GitHub Actions:
1. Under **Source**, select **`Deploy from a branch`**.
2. Under **Branch**:
   - Choose **`main`**.
   - For folder, choose either:
     - **`/ (root)`** (pre-synchronized with `index.html`, `static/`, and `.nojekyll`), OR
     - **`/docs`** (pre-synchronized with `docs/index.html`, `docs/static/`, and `docs/.nojekyll`).
3. Click **Save**.
4. GitHub Pages will build and deploy the site within 60–90 seconds.

---

### Option 3: Deploy from the `gh-pages` branch
1. Under **Source**, select **`Deploy from a branch`**.
2. Under **Branch**, select **`gh-pages`** and folder **`/ (root)`**.
3. Click **Save**.

---

## 💡 How the Dashboard Works on GitHub Pages

Because GitHub Pages is a static CDN host (it does not execute Python/FastAPI/SQLite servers on its edges), the dashboard features an intelligent **Client-Side Mock Backend Engine** (`MockBackendEngine`):

- **Automatic Detection**: When hosted on `*.github.io`, the dashboard detects the static host and activates the interactive in-browser engine.
- **Full Interactive Capability**:
  - **Module 1**: Submit the lead intake form $\to$ deterministic score (e.g. 88/100) and SLA latency (~310ms) are calculated in real time, updating the searchable table.
  - **Module 2**: Ingest customer support emails $\to$ categorizes intent, computes sentiment gauge, displays RAG knowledge base citations, and drafts responses for the Human Approval Queue.
  - **Module 3**: Upload sample invoice $\to$ extracts line items, validates financial arithmetic ($\sum \text{items} == \text{subtotal}$), and simulates Google Sheets export.
  - **Module 4**: Progress through the 9 multi-agents, simulate Stripe HMAC-SHA256 signature events, and review the live executive digest.
  - **Approvals & Audit Trail**: Approve pending contracts/drafts and inspect real-time audit logs.
- **Local Persistence**: State changes are saved into `localStorage`, so your demo actions persist across page refreshes!
- **Zero Console Errors**: 100% of API endpoints gracefully respond with realistic HTTP 200 JSON payloads.

---

## ☁️ Full-Stack Backend Hosting (Optional)

If you also wish to host the live Python FastAPI backend with active webhook receivers on the public internet:

| Platform | Setup Steps | Free / Low-Cost Tier |
| :--- | :--- | :--- |
| **Render** | Connect GitHub repo $\to$ New Web Service $\to$ Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT` | Free Web Service Tier |
| **Railway** | Connect GitHub repo $\to$ Auto-detects Python $\to$ Generates public URL | $5 Starter Credit |
| **Fly.io** | Run `fly launch` in project root $\to$ Deploys Dockerfile | Free Allowance |
