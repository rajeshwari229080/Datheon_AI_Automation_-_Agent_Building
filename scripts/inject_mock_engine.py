"""
Inject client-side mock backend engine into app.js for seamless static hosting (GitHub Pages).
"""

mock_engine_code = r'''// =========================================================================
// Enterprise AI Automation Suite - Client-Side Mock Backend Engine
// Enables 100% interactive execution on static hosts (GitHub Pages)
// Seamlessly activates if backend /api/v1 returns 404 or fails network check
// =========================================================================

const MockBackendEngine = (() => {
  const STORAGE_KEY = 'eaas_mock_db_v1';

  const defaultDb = {
    leads: [
      {
        id: 'LD-83491',
        name: 'Sarah Johnson',
        email: 'sarah.j@apexdynamics.io',
        phone: '+1 (555) 234-5678',
        company: 'Apex Dynamics',
        company_size: '50-249',
        budget: 45000,
        business_need: 'Automate multi-channel lead qualification and CRM intake pipeline with under 10s SLA.',
        score: 88,
        priority: 'HIGH',
        qualification_status: 'QUALIFIED',
        qualification_summary: 'High-intent enterprise lead with confirmed executive budget and immediate deployment timeline.',
        talking_points: [
          'Highlight SLA latency benchmark (310ms vs 10s target).',
          'Demonstrate native Airtable and Slack real-time connectors.',
          'Discuss volume discounts for multi-seat sales team deployment.'
        ],
        airtable_status: 'SYNCED',
        slack_status: 'SENT',
        created_at: new Date(Date.now() - 3600000 * 2).toISOString(),
        execution_logs: [
          { step: 'Payload Ingestion', status: 'SUCCESS', latency_ms: 12 },
          { step: 'Deterministic Pre-scoring', status: 'SUCCESS', latency_ms: 8 },
          { step: 'AI Reasoning & Fit Analysis', status: 'SUCCESS', latency_ms: 240 },
          { step: 'Airtable & Slack Notification', status: 'SUCCESS', latency_ms: 50 }
        ]
      },
      {
        id: 'LD-83492',
        name: 'Marcus Vance',
        email: 'm.vance@globalretail.com',
        phone: '+1 (555) 876-5432',
        company: 'Global Retail Corp',
        company_size: '250-999',
        budget: 15000,
        business_need: 'Evaluating email triage and automated support ticketing for holiday sales influx.',
        score: 72,
        priority: 'MEDIUM',
        qualification_status: 'QUALIFIED',
        qualification_summary: 'Established mid-market retailer seeking support queue automation.',
        talking_points: [
          'Focus on RAG grounded knowledge base integration.',
          'Demonstrate draft-only human review queue safety.'
        ],
        airtable_status: 'SYNCED',
        slack_status: 'SENT',
        created_at: new Date(Date.now() - 3600000 * 5).toISOString(),
        execution_logs: [
          { step: 'Payload Ingestion', status: 'SUCCESS', latency_ms: 10 },
          { step: 'Deterministic Pre-scoring', status: 'SUCCESS', latency_ms: 6 },
          { step: 'AI Reasoning & Fit Analysis', status: 'SUCCESS', latency_ms: 220 },
          { step: 'Airtable & Slack Notification', status: 'SUCCESS', latency_ms: 45 }
        ]
      },
      {
        id: 'LD-83493',
        name: 'Elena Rostova',
        email: 'elena@sparklabs.dev',
        phone: '+1 (555) 111-2233',
        company: 'Spark Labs',
        company_size: '1-9',
        budget: 2500,
        business_need: 'Looking for a free or very low-cost script to parse PDF invoices.',
        score: 38,
        priority: 'LOW',
        qualification_status: 'UNQUALIFIED',
        qualification_summary: 'Sub-tier budget below enterprise minimum thresholds.',
        talking_points: ['Direct to open-source community resources or self-hosted tier.'],
        airtable_status: 'SYNCED',
        slack_status: 'SKIPPED',
        created_at: new Date(Date.now() - 3600000 * 8).toISOString(),
        execution_logs: [
          { step: 'Deterministic Pre-scoring', status: 'FAILED_CRITERIA', latency_ms: 5 }
        ]
      }
    ],
    tickets: [
      {
        id: 'TCK-45091',
        sender_name: 'Alex Thompson',
        sender_email: 'alex.t@email.com',
        subject: 'Billing Question - Invoice #45091',
        body: 'I just received invoice #45091 and noticed I was charged $120 instead of the agreed annual rate of $89.00. I also have an active discount code from last month that was not applied. Can you please check and resolve this error ASAP?',
        intent: 'billing',
        urgency: 'high',
        sentiment: 'frustrated',
        sentiment_score: 0.42,
        status: 'PENDING_APPROVAL',
        requires_approval: true,
        knowledge_citations: [
          { title: 'Pricing Tiers & Annual Billing Policy (v3)', snippet: 'Annual prepaid subscriptions are discounted to $89.00/yr. In case of billing variance, credit adjustments are generated within 24h.' },
          { title: 'Invoice Correction Policy (v1.4)', snippet: 'All billing dispute credit adjustments over $25 require operator sign-off before invoice dispatch.' }
        ],
        draft_reply: 'Dear Alex,\n\nThank you for reaching out regarding the pricing on invoice #45091. We have identified an error where your annual discount was not correctly applied.\nWe have adjusted the invoice to the agreed-upon rate of $89.00 and applied your additional discount code. Your corrected invoice #45091 is attached.\n\nWe apologize for the inconvenience.\n\nBest regards,\nSupport Team',
        created_at: new Date(Date.now() - 3600000 * 3).toISOString()
      },
      {
        id: 'TCK-45092',
        sender_name: 'DevOps Lead',
        sender_email: 'sre@mission-critical.org',
        subject: 'CRITICAL: European Webhook Gateway latency spike',
        body: 'Our primary API webhook ingestion has been failing for the past 20 minutes with 500 errors. Sev-1 outage, client data flow is blocked. Escalate immediately!',
        intent: 'urgent_incident',
        urgency: 'critical',
        sentiment: 'negative',
        sentiment_score: 0.15,
        status: 'ESCALATED',
        requires_approval: false,
        knowledge_citations: [
          { title: 'Incident Response Protocol (Sev-1)', snippet: 'Critical infrastructure disruptions must notify the secondary on-call engineer via PagerDuty immediately.' }
        ],
        draft_reply: 'Our engineering response team has acknowledged this Sev-1 incident. The primary on-call SRE has been dispatched and is currently analyzing regional network logs. Status updates will be posted to status.datheon.ai every 15 minutes.',
        created_at: new Date(Date.now() - 3600000 * 6).toISOString()
      }
    ],
    invoices: [
      {
        id: 'INV-2026-9042',
        vendor_name: 'CloudScale Infrastructure Inc.',
        invoice_number: 'INV-2026-9042',
        invoice_date: '2026-10-18',
        currency: 'USD',
        subtotal: 1800.0,
        tax_amount: 148.5,
        discount_amount: 0.0,
        total_amount: 1948.5,
        validation_status: 'VALID',
        arithmetic_discrepancy: false,
        export_status: 'EXPORTED',
        sheets_row_id: 148,
        sha256_hash: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
        line_items: [
          { description: 'Kubernetes Cluster (3 Nodes)', quantity: 1, unit_price: 1200.0, total: 1200.0 },
          { description: 'Enterprise Storage Volume 2TB', quantity: 1, unit_price: 450.0, total: 450.0 },
          { description: 'Dedicated Egress Bandwidth', quantity: 500, unit_price: 0.3, total: 150.0 }
        ],
        created_at: new Date(Date.now() - 3600000 * 12).toISOString()
      },
      {
        id: 'INV-2026-8812',
        vendor_name: 'Datacenter Logistics Ltd',
        invoice_number: 'INV-2026-8812',
        invoice_date: '2026-10-21',
        currency: 'USD',
        subtotal: 3200.0,
        tax_amount: 500.0,
        discount_amount: 0.0,
        total_amount: 4000.0,
        validation_status: 'ARITHMETIC_MISMATCH',
        arithmetic_discrepancy: true,
        export_status: 'PENDING',
        sheets_row_id: null,
        sha256_hash: '8f434346648f6b96df89dda901c5176b10a6d83961dd3c1ac88b59b2dc327aa4',
        line_items: [
          { description: 'Server Rack Space Allocation', quantity: 2, unit_price: 1600.0, total: 3200.0 }
        ],
        created_at: new Date(Date.now() - 3600000 * 24).toISOString()
      }
    ],
    projects: [
      {
        id: 'PROJ-9014',
        client_name: 'Diana Prince',
        client_email: 'diana@themyscira-holdings.com',
        company: 'Themyscira Holdings',
        service_type: 'Enterprise AI Automation Suite',
        deal_value: 50000.0,
        currency: 'USD',
        current_state: 'CONTRACT_DRAFTED',
        contract_draft: 'ENTERPRISE SERVICE AGREEMENT: Prepared for Themyscira Holdings covering 4 automation modules, 99.9% uptime SLA, and human-in-the-loop governance.',
        is_contract_approved: false,
        payment_verified: false,
        slack_channel: '#proj-themyscira-holdings',
        created_at: new Date(Date.now() - 3600000 * 18).toISOString()
      },
      {
        id: 'PROJ-8821',
        client_name: 'Bruce Wayne',
        client_email: 'bruce@wayne-enterprises.com',
        company: 'Wayne Enterprises',
        service_type: 'Multi-Agent Autonomous Operations',
        deal_value: 75000.0,
        currency: 'USD',
        current_state: 'COMPLETED',
        contract_draft: 'EXECUTED MASTER AGREEMENT: Wayne Enterprises Onboarding Complete.',
        is_contract_approved: true,
        payment_verified: true,
        slack_channel: '#proj-wayne-enterprises',
        created_at: new Date(Date.now() - 3600000 * 48).toISOString()
      }
    ],
    audit_logs: [
      { timestamp: new Date(Date.now() - 300000).toISOString(), module: 'Module 1: Leads', action: 'Lead Qualified', entity_id: 'LD-83491', actor: 'LeadIntelAgent', status: 'SUCCESS', duration_ms: 310 },
      { timestamp: new Date(Date.now() - 600000).toISOString(), module: 'Module 2: Support', action: 'Draft Created', entity_id: 'TCK-45091', actor: 'SupportTriageAgent', status: 'SUCCESS', duration_ms: 18 },
      { timestamp: new Date(Date.now() - 1200000).toISOString(), module: 'Module 3: Invoices', action: 'Arithmetic Verified', entity_id: 'INV-2026-9042', actor: 'InvoiceExtractor', status: 'SUCCESS', duration_ms: 145 },
      { timestamp: new Date(Date.now() - 1800000).toISOString(), module: 'Module 4: Enterprise', action: 'HMAC Webhook Verified', entity_id: 'evt_stripe_9014', actor: 'PaymentVerifier', status: 'SUCCESS', duration_ms: 1 }
    ]
  };

  function getDb() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) return JSON.parse(stored);
    } catch (e) {}
    localStorage.setItem(STORAGE_KEY, JSON.stringify(defaultDb));
    return JSON.parse(JSON.stringify(defaultDb));
  }

  function saveDb(db) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(db));
    } catch (e) {}
  }

  function addAudit(module, action, entityId, actor = 'system', status = 'SUCCESS', durationMs = 12) {
    const db = getDb();
    db.audit_logs.unshift({
      timestamp: new Date().toISOString(),
      module,
      action,
      entity_id: entityId,
      actor,
      status,
      duration_ms: durationMs
    });
    if (db.audit_logs.length > 100) db.audit_logs.pop();
    saveDb(db);
  }

  return {
    getDb,
    saveDb,
    addAudit,
    reset() {
      localStorage.removeItem(STORAGE_KEY);
      return getDb();
    },

    async handleRequest(url, options = {}) {
      const method = (options.method || 'GET').toUpperCase();
      const db = getDb();
      const parsedUrl = new URL(url, 'http://localhost');
      const path = parsedUrl.pathname;
      const params = parsedUrl.searchParams;

      // Small simulated latency for realistic feeling
      await new Promise(r => setTimeout(r, 60));

      // 1. Health
      if (path === '/api/v1/health') {
        return new Response(JSON.stringify({
          status: 'HEALTHY',
          demo_mode: true,
          environment: 'GitHub Pages Demo',
          adapters: {
            airtable: { status: 'DEMO_MODE', message: 'Simulated Airtable Record Sync' },
            slack: { status: 'DEMO_MODE', message: 'Simulated Slack Lead & Project Alerts' },
            email: { status: 'DEMO_MODE', message: 'Simulated Draft-Only Safety Inbox' },
            sheets: { status: 'DEMO_MODE', message: 'Simulated Google Sheets Ledger Sync' },
            stripe: { status: 'DEMO_MODE', message: 'HMAC-SHA256 Cryptographic Verifier Ready' },
            openai: { status: 'DEMO_MODE', message: 'Deterministic Structured Mock & Grounding' }
          }
        }), { status: 200, headers: { 'Content-Type': 'application/json' } });
      }

      // 2. Metrics
      if (path === '/api/v1/overview/metrics') {
        const totalLeads = db.leads.length;
        const qualifiedLeads = db.leads.filter(l => l.qualification_status === 'QUALIFIED').length;
        const totalTickets = db.tickets.length;
        const urgentTickets = db.tickets.filter(t => t.urgency === 'high' || t.urgency === 'critical').length;
        const pendingDrafts = db.tickets.filter(t => t.status === 'PENDING_APPROVAL').length;
        const totalInvoices = db.invoices.length;
        const awaitingReview = db.invoices.filter(i => i.validation_status !== 'VALID' || i.export_status !== 'EXPORTED').length;
        const discrepancies = db.invoices.filter(i => i.arithmetic_discrepancy).length;
        const exported = db.invoices.filter(i => i.export_status === 'EXPORTED').length;
        const verifiedRevenue = db.projects.filter(p => p.payment_verified).reduce((s, p) => s + p.deal_value, 0);
        const activeProjects = db.projects.filter(p => p.current_state !== 'COMPLETED').length;
        const pendingContracts = db.projects.filter(p => !p.is_contract_approved).length;

        return new Response(JSON.stringify({
          leads: { total: totalLeads, qualified: qualifiedLeads, avg_latency_ms: 310.0 },
          support: { total_tickets: totalTickets, urgent_tickets: urgentTickets, pending_drafts: pendingDrafts },
          invoices: { total_scanned: totalInvoices, awaiting_review: awaitingReview, discrepancies_caught: discrepancies, exported_to_sheets: exported },
          enterprise: { verified_revenue_usd: verifiedRevenue, active_projects: activeProjects },
          system: { total_pending_approvals: pendingDrafts + awaitingReview + pendingContracts, workflow_success: db.audit_logs.filter(a => a.status === 'SUCCESS').length, workflow_failures: 0 },
          recent_activity: db.audit_logs.slice(0, 10)
        }), { status: 200, headers: { 'Content-Type': 'application/json' } });
      }

      // 3. Leads Listing
      if (path === '/api/v1/leads' && method === 'GET') {
        let items = db.leads;
        const p = params.get('priority');
        const s = (params.get('search') || '').toLowerCase();
        if (p) items = items.filter(l => l.priority === p);
        if (s) items = items.filter(l => l.company.toLowerCase().includes(s) || l.name.toLowerCase().includes(s) || l.email.toLowerCase().includes(s));
        return new Response(JSON.stringify({ items, total: items.length }), { status: 200, headers: { 'Content-Type': 'application/json' } });
      }

      // 4. Lead Intake
      if (path === '/api/v1/leads/intake' && method === 'POST') {
        const body = JSON.parse(options.body || '{}');
        const budget = parseFloat(body.budget) || 0;
        let score = 20;
        if (budget >= 30000) score += 40;
        else if (budget >= 10000) score += 25;
        else score += 10;
        if (['50-249', '250-999', '1000+'].includes(body.company_size)) score += 30;
        else score += 10;
        score = Math.min(100, score);
        const priority = score >= 75 ? 'HIGH' : (score >= 50 ? 'MEDIUM' : 'LOW');
        const qualStatus = score >= 50 ? 'QUALIFIED' : 'UNQUALIFIED';

        const newLead = {
          id: `LD-${Math.floor(10000 + Math.random() * 90000)}`,
          name: body.name || 'Anonymous Lead',
          email: body.email,
          phone: body.phone || 'N/A',
          company: body.company || 'Enterprise Corp',
          company_size: body.company_size || '50-249',
          budget,
          business_need: body.business_need || 'Standard automation request',
          score,
          priority,
          qualification_status: qualStatus,
          qualification_summary: qualStatus === 'QUALIFIED' ? 'Enterprise lead matching core ICP criteria.' : 'Budget below enterprise SLA thresholds.',
          talking_points: ['Discuss customized SLA performance & timeline.', 'Reference case studies in similar industries.'],
          airtable_status: 'SYNCED',
          slack_status: 'SENT',
          created_at: new Date().toISOString(),
          execution_logs: [
            { step: 'Payload Intake', status: 'SUCCESS', latency_ms: 12 },
            { step: 'Deterministic Pre-scoring', status: 'SUCCESS', latency_ms: 8 },
            { step: 'AI Reasoning & Fit Analysis', status: 'SUCCESS', latency_ms: 245 },
            { step: 'Airtable & Slack Notification', status: 'SUCCESS', latency_ms: 45 }
          ]
        };

        db.leads.unshift(newLead);
        saveDb(db);
        addAudit('Module 1: Leads', 'Lead Ingested & Qualified', newLead.id, 'LeadIntelAgent', 'SUCCESS', 310);

        return new Response(JSON.stringify(newLead), { status: 200, headers: { 'Content-Type': 'application/json' } });
      }

      // 5. Single Lead
      if (path.startsWith('/api/v1/leads/') && method === 'GET') {
        const id = path.split('/')[4];
        const lead = db.leads.find(l => l.id === id) || db.leads[0];
        return new Response(JSON.stringify(lead), { status: 200, headers: { 'Content-Type': 'application/json' } });
      }

      // 6. Lead Retry
      if (path.includes('/retry') && method === 'POST') {
        return new Response(JSON.stringify({ status: 'SUCCESS', message: 'Synced to Airtable and Slack' }), { status: 200, headers: { 'Content-Type': 'application/json' } });
      }

      // 7. Support Tickets List
      if (path === '/api/v1/support/tickets' && method === 'GET') {
        let items = db.tickets;
        if (params.get('requires_approval') === 'true') {
          items = items.filter(t => t.status === 'PENDING_APPROVAL');
        }
        return new Response(JSON.stringify({ items, total: items.length }), { status: 200, headers: { 'Content-Type': 'application/json' } });
      }

      // 8. Support Ingest
      if (path === '/api/v1/support/ingest' && method === 'POST') {
        const body = JSON.parse(options.body || '{}');
        const text = (body.subject + ' ' + body.body).toLowerCase();
        let intent = 'product_inquiry';
        let urgency = 'normal';
        let sentiment = 'neutral';
        if (text.includes('bill') || text.includes('invoice') || text.includes('charge')) {
          intent = 'billing';
          urgency = 'high';
          sentiment = 'frustrated';
        } else if (text.includes('critical') || text.includes('outage') || text.includes('error')) {
          intent = 'urgent_incident';
          urgency = 'critical';
          sentiment = 'negative';
        }

        const newTicket = {
          id: `TCK-${Math.floor(10000 + Math.random() * 90000)}`,
          sender_name: body.sender_name || 'Customer',
          sender_email: body.sender_email,
          subject: body.subject,
          body: body.body,
          intent,
          urgency,
          sentiment,
          sentiment_score: 0.65,
          status: 'PENDING_APPROVAL',
          requires_approval: true,
          knowledge_citations: [
            { title: 'Standard Operating Procedures & SLA (v2.1)', snippet: 'All customer support tickets receive contextual RAG response previews.' }
          ],
          draft_reply: `Dear ${body.sender_name || 'Customer'},\n\nThank you for reaching out regarding "${body.subject}". We have classified your request under our ${intent.replace('_', ' ')} support protocol. Our team is actively reviewing your inquiry.\n\nBest regards,\nEnterprise Support Team`,
          created_at: new Date().toISOString()
        };

        db.tickets.unshift(newTicket);
        saveDb(db);
        addAudit('Module 2: Support', 'Ticket Ingested & Drafted', newTicket.id, 'SupportTriageAgent', 'SUCCESS', 18);

        return new Response(JSON.stringify(newTicket), { status: 200, headers: { 'Content-Type': 'application/json' } });
      }

      // 9. Single Support Ticket
      if (path.startsWith('/api/v1/support/tickets/') && method === 'GET') {
        const id = path.split('/')[4];
        const ticket = db.tickets.find(t => t.id === id) || db.tickets[0];
        return new Response(JSON.stringify(ticket), { status: 200, headers: { 'Content-Type': 'application/json' } });
      }

      // 10. Approve Support Ticket Draft
      if (path.includes('/approve') && path.includes('/support/')) {
        const id = path.split('/')[4];
        const ticket = db.tickets.find(t => t.id === id);
        if (ticket) ticket.status = 'APPROVED';
        saveDb(db);
        addAudit('Module 2: Support', 'Draft Approved for Dispatch', id, 'HumanSupervisor', 'SUCCESS', 25);
        return new Response(JSON.stringify({ status: 'SUCCESS', message: 'Draft approved and dispatched' }), { status: 200, headers: { 'Content-Type': 'application/json' } });
      }

      // 11. Invoices List
      if (path === '/api/v1/invoices' && method === 'GET') {
        let items = db.invoices;
        if (params.get('has_discrepancy') === 'true') {
          items = items.filter(i => i.arithmetic_discrepancy || i.validation_status !== 'VALID');
        }
        return new Response(JSON.stringify({ items, total: items.length }), { status: 200, headers: { 'Content-Type': 'application/json' } });
      }

      // 12. Upload Invoice
      if (path === '/api/v1/invoices/upload' && method === 'POST') {
        const newInv = {
          id: `INV-2026-${Math.floor(1000 + Math.random() * 9000)}`,
          vendor_name: 'Acme Cloud Hosting LLC',
          invoice_number: `INV-${Math.floor(10000 + Math.random() * 90000)}`,
          invoice_date: new Date().toISOString().split('T')[0],
          currency: 'USD',
          subtotal: 1500.0,
          tax_amount: 123.75,
          discount_amount: 0.0,
          total_amount: 1623.75,
          validation_status: 'VALID',
          arithmetic_discrepancy: false,
          export_status: 'PENDING',
          sheets_row_id: null,
          sha256_hash: 'mock_sha256_' + Date.now(),
          line_items: [
            { description: 'Cloud VPS Premium Hosting', quantity: 1, unit_price: 1500.0, total: 1500.0 }
          ],
          created_at: new Date().toISOString()
        };
        db.invoices.unshift(newInv);
        saveDb(db);
        addAudit('Module 3: Invoices', 'Invoice Uploaded & Math Verified', newInv.id, 'InvoiceExtractor', 'SUCCESS', 145);
        return new Response(JSON.stringify(newInv), { status: 200, headers: { 'Content-Type': 'application/json' } });
      }

      // 13. Single Invoice
      if (path.startsWith('/api/v1/invoices/') && method === 'GET') {
        const id = path.split('/')[4];
        const inv = db.invoices.find(i => i.id === id) || db.invoices[0];
        return new Response(JSON.stringify(inv), { status: 200, headers: { 'Content-Type': 'application/json' } });
      }

      // 14. Invoice Approve & Export
      if (path.includes('/invoices/') && (path.includes('/approve') || path.includes('/export'))) {
        const id = path.split('/')[4];
        const inv = db.invoices.find(i => i.id === id);
        if (inv) {
          inv.validation_status = 'VALID';
          inv.arithmetic_discrepancy = false;
          inv.export_status = 'EXPORTED';
          inv.sheets_row_id = 152;
        }
        saveDb(db);
        addAudit('Module 3: Invoices', 'Invoice Synchronized to Google Sheets', id, 'SheetsAdapter', 'SUCCESS', 85);
        return new Response(JSON.stringify({ status: 'SUCCESS', message: 'Invoice approved and synced to Google Sheets row #152' }), { status: 200, headers: { 'Content-Type': 'application/json' } });
      }

      // 15. Enterprise Projects List
      if (path === '/api/v1/enterprise/projects' && method === 'GET') {
        let items = db.projects;
        const st = params.get('state');
        if (st) items = items.filter(p => p.current_state === st);
        return new Response(JSON.stringify({ items, total: items.length }), { status: 200, headers: { 'Content-Type': 'application/json' } });
      }

      // 16. Enterprise Project Intake
      if (path === '/api/v1/enterprise/projects/intake' && method === 'POST') {
        const body = JSON.parse(options.body || '{}');
        const newProj = {
          id: `PROJ-${Math.floor(1000 + Math.random() * 9000)}`,
          client_name: body.client_name || 'Enterprise Customer',
          client_email: body.client_email,
          company: body.company || 'Enterprise Org',
          service_type: body.service_type || 'AI Automation Suite',
          deal_value: parseFloat(body.deal_value) || 25000.0,
          currency: 'USD',
          current_state: 'INTAKE_RECEIVED',
          contract_draft: `SERVICE PROPOSAL: Customer ${body.company} intake registered.`,
          is_contract_approved: false,
          payment_verified: false,
          slack_channel: `#proj-${(body.company || 'client').toLowerCase().replace(/\s+/g, '-')}`,
          created_at: new Date().toISOString()
        };
        db.projects.unshift(newProj);
        saveDb(db);
        addAudit('Module 4: Enterprise', 'Enterprise Project Intake Received', newProj.id, 'IntakeAgent', 'SUCCESS', 45);
        return new Response(JSON.stringify(newProj), { status: 200, headers: { 'Content-Type': 'application/json' } });
      }

      // 17. Single Project
      if (path.startsWith('/api/v1/enterprise/projects/') && method === 'GET') {
        const id = path.split('/')[4];
        const proj = db.projects.find(p => p.id === id) || db.projects[0];
        return new Response(JSON.stringify(proj), { status: 200, headers: { 'Content-Type': 'application/json' } });
      }

      // 18. Draft / Approve Contract
      if (path.includes('/contracts/draft')) {
        const id = path.split('/')[4];
        const proj = db.projects.find(p => p.id === id);
        if (proj) {
          proj.current_state = 'CONTRACT_DRAFTED';
          proj.contract_draft = `MASTER AUTOMATION AGREEMENT: Generated for ${proj.company}. Approved clauses: 99.9% uptime, human authorization gates, sub-second SLAs.`;
        }
        saveDb(db);
        addAudit('Module 4: Enterprise', 'Contract Drafted via Template', id, 'ContractAgent', 'SUCCESS', 120);
        return new Response(JSON.stringify(proj), { status: 200, headers: { 'Content-Type': 'application/json' } });
      }

      if (path.includes('/contracts/approve')) {
        const id = path.split('/')[4];
        const proj = db.projects.find(p => p.id === id);
        if (proj) {
          proj.is_contract_approved = true;
          proj.current_state = 'CONTRACT_APPROVED';
        }
        saveDb(db);
        addAudit('Module 4: Enterprise', 'Contract Approved by Legal Officer', id, 'LegalOfficer', 'SUCCESS', 30);
        return new Response(JSON.stringify(proj), { status: 200, headers: { 'Content-Type': 'application/json' } });
      }

      // 19. Collaborate / Slack Channel
      if (path.includes('/collaborate')) {
        const id = path.split('/')[4];
        const proj = db.projects.find(p => p.id === id);
        if (proj) {
          proj.slack_channel = `#proj-${proj.company.toLowerCase().replace(/\s+/g, '-')}`;
        }
        saveDb(db);
        addAudit('Module 4: Enterprise', 'Slack Project Channel Provisioned', id, 'CollaborationAgent', 'SUCCESS', 55);
        return new Response(JSON.stringify({ status: 'SUCCESS', channel: proj ? proj.slack_channel : '#general' }), { status: 200, headers: { 'Content-Type': 'application/json' } });
      }

      // 20. Executive Digest
      if (path.includes('/executive-digest')) {
        return new Response(JSON.stringify({
          period_start: new Date(Date.now() - 3600000 * 24 * 7).toISOString(),
          period_end: new Date().toISOString(),
          source_coverage: '100% Verified SQLite / Mock Ledger',
          summary_text: `Executive Operations Digest: During this period, ${db.leads.length} leads were ingested with a 310ms average SLA latency. ${db.tickets.length} support requests were categorized with zero unreviewed outgoing messages. ${db.invoices.length} invoices were parsed with arithmetic balance verified. Total verified platform revenue stands at $${db.projects.filter(p => p.payment_verified).reduce((s, p) => s + p.deal_value, 0).toLocaleString()}.`,
          factual_stats: {
            leads_qualified: db.leads.filter(l => l.qualification_status === 'QUALIFIED').length,
            leads_unqualified: db.leads.filter(l => l.qualification_status === 'UNQUALIFIED').length,
            support_tickets_handled: db.tickets.length,
            invoices_processed: db.invoices.length,
            verified_revenue: db.projects.filter(p => p.payment_verified).reduce((s, p) => s + p.deal_value, 0),
            active_projects: db.projects.filter(p => p.current_state !== 'COMPLETED').length
          }
        }), { status: 200, headers: { 'Content-Type': 'application/json' } });
      }

      // 21. Audit Logs
      if (path === '/api/v1/system/audit-logs' && method === 'GET') {
        let items = db.audit_logs;
        const m = params.get('module');
        if (m) items = items.filter(a => a.module === m);
        return new Response(JSON.stringify({ items, total: items.length }), { status: 200, headers: { 'Content-Type': 'application/json' } });
      }

      // 22. Toggle Demo Mode
      if (path === '/api/v1/system/demo-mode/toggle') {
        return new Response(JSON.stringify({ status: 'SUCCESS', message: 'Demo mode active (Mock Adapters engaged)' }), { status: 200, headers: { 'Content-Type': 'application/json' } });
      }

      // Fallback 404
      return new Response(JSON.stringify({ detail: 'Mock route not mapped' }), { status: 404, headers: { 'Content-Type': 'application/json' } });
    }
  };
})();

// Intercept window.fetch to provide transparent mock fallback on static hosts
const originalFetch = window.fetch;
window.fetch = async function(url, options = {}) {
  const urlStr = typeof url === 'string' ? url : (url.url || '');
  
  // If running directly on GitHub Pages or file: protocol, use MockBackendEngine immediately
  const isStaticHost = window.location.protocol === 'file:' || 
                       window.location.hostname.includes('github.io') ||
                       (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1' && window.location.port === '');

  if (isStaticHost && urlStr.startsWith('/api/v1/')) {
    return MockBackendEngine.handleRequest(urlStr, options);
  }

  try {
    const res = await originalFetch(url, options);
    if (res.status === 404 && urlStr.startsWith('/api/v1/')) {
      return MockBackendEngine.handleRequest(urlStr, options);
    }
    return res;
  } catch (err) {
    if (urlStr.startsWith('/api/v1/')) {
      return MockBackendEngine.handleRequest(urlStr, options);
    }
    throw err;
  }
};

'''

with open('app/dashboard/static/js/app.js', 'r', encoding='utf-8') as f:
    existing_content = f.read()

# Only prepend if not already present
if 'MockBackendEngine' not in existing_content:
    new_content = mock_engine_code + existing_content
    with open('app/dashboard/static/js/app.js', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Successfully injected MockBackendEngine into app/dashboard/static/js/app.js!")
else:
    print("MockBackendEngine already present in app.js.")
