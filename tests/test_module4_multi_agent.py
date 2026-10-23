import json
import pytest
from app.models.enterprise import EnterpriseProject, PaymentEvent, ContractDraft, ExecutiveDigestRecord
from app.adapters.stripe_adapter import stripe_adapter

def test_multi_agent_onboarding_lifecycle(client, db_session):
    """Test end-to-end multi-agent customer lifecycle from intake through contract draft and approval."""
    # 1. Intake Agent
    intake_payload = {
        "client_name": "Tony Stark",
        "client_email": "tony@starkindustries.com",
        "company": "Stark Industries",
        "service_type": "Enterprise Multi-Agent Automation Suite",
        "deal_value": 75000.0,
        "currency": "USD"
    }
    res = client.post("/api/v1/enterprise/projects/intake", json=intake_payload)
    assert res.status_code == 201
    proj_data = res.json()["project"]
    project_id = proj_data["id"]
    assert proj_data["current_state"] == "QUALIFIED"

    # 2. Contract Preparation Agent
    contract_res = client.post(f"/api/v1/enterprise/projects/{project_id}/contracts/draft")
    assert contract_res.status_code == 200
    draft_data = contract_res.json()["draft"]
    assert draft_data["is_approved"] is False
    assert "MASTER SERVICES AGREEMENT" in draft_data["draft_content"]
    assert "Stark Industries" in draft_data["draft_content"]

    # Verify project state is CONTRACT_DRAFTED
    p_check = db_session.query(EnterpriseProject).filter(EnterpriseProject.id == project_id).first()
    assert p_check.current_state == "CONTRACT_DRAFTED"

    # 3. Human Approval Gate
    approve_res = client.post(f"/api/v1/enterprise/projects/{project_id}/contracts/approve?reviewer=GeneralCounsel")
    assert approve_res.status_code == 200
    assert approve_res.json()["state"] == "PENDING_PAYMENT"

    # 4. Deterministic Stripe Webhook Payment Verification
    mock_charge = {
        "id": "ch_test_stark_9901",
        "amount": 7500000,  # $75,000.00 in cents
        "currency": "usd",
        "status": "succeeded",
        "receipt_email": "tony@starkindustries.com",
        "metadata": {"project_id": project_id}
    }
    raw_payload, sig_header = stripe_adapter.create_mock_signed_event("charge.succeeded", mock_charge)

    webhook_res = client.post(
        "/api/v1/enterprise/stripe/webhook",
        content=raw_payload,
        headers={"stripe-signature": sig_header, "Content-Type": "application/json"}
    )
    assert webhook_res.status_code == 200
    w_data = webhook_res.json()
    assert w_data["verified"] is True
    assert w_data["signature_valid"] is True
    assert w_data["amount"] == 75000.0

    # Project should now be PAYMENT_VERIFIED
    db_session.refresh(p_check)
    assert p_check.current_state == "PAYMENT_VERIFIED"

    # 5. Replay Attack Defense (Same webhook delivered again)
    replay_res = client.post(
        "/api/v1/enterprise/stripe/webhook",
        content=raw_payload,
        headers={"stripe-signature": sig_header, "Content-Type": "application/json"}
    )
    assert replay_res.status_code == 200
    assert replay_res.json()["status"] == "ALREADY_PROCESSED"

    # 6. Collaboration Agent (Provision Slack workspace)
    collab_res = client.post(f"/api/v1/enterprise/projects/{project_id}/collaborate")
    assert collab_res.status_code == 200
    db_session.refresh(p_check)
    assert p_check.current_state == "COMPLETED"
    assert p_check.slack_channel_name is not None

def test_reject_invalid_stripe_signature(client):
    """Test that unauthorized, forged, or altered Stripe webhook signatures are strictly rejected."""
    fake_payload = json.dumps({"type": "charge.succeeded", "data": {"object": {"amount": 100000}}})
    fake_sig = "t=1700000000,v1=bad_forged_signature_hex_value"

    res = client.post(
        "/api/v1/enterprise/stripe/webhook",
        content=fake_payload,
        headers={"stripe-signature": fake_sig, "Content-Type": "application/json"}
    )
    assert res.status_code == 400
    assert "Signature verification failed" in res.json()["detail"]

def test_executive_digest_factual_reporting(client, db_session):
    """Test that the Reporting Agent generates an evidence-grounded digest from real database records."""
    # Seed a verified payment event
    p_event = PaymentEvent(
        stripe_event_id="evt_test_digest_101",
        idempotency_key="idemp_digest_101",
        amount=12500.0,
        currency="usd",
        status="succeeded",
        verified=True,
        signature_valid=True
    )
    db_session.add(p_event)
    db_session.commit()

    res = client.post("/api/v1/enterprise/reports/executive-digest/generate?days=7")
    assert res.status_code == 200
    data = res.json()["digest"]

    assert data["verified_revenue"] >= 12500.0
    assert "factual_stats" in data
    assert "narrative_summary" in data
    assert len(data["source_coverage"]) >= 4
