import pytest
from app.models.lead import LeadRecord, LeadExecutionLog
from app.modules.lead_routing.schemas import LeadIntakeRequest
from app.modules.lead_routing.service import lead_routing_service

def test_valid_lead_intake_and_qualification(client, db_session):
    """Test valid lead intake: deterministic scoring, AI qualification, and sync."""
    payload = {
        "name": "Sarah Connor",
        "email": "sarah.connor@cyberdyne-defense.com",
        "phone": "+1-555-839-2001",
        "company": "Cyberdyne Systems",
        "company_size": "201-1000",
        "budget": 35000.0,
        "business_need": "We need an enterprise-grade multi-agent operations platform to automate our supplier intake, email classification, and accounting exports.",
        "product_interest": "Enterprise Operations Suite",
        "consent": True
    }

    response = client.post("/api/v1/leads/intake", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["success"] is True
    assert data["qualification_status"] == "QUALIFIED"
    assert data["priority"] == "HIGH"
    assert data["score"] >= 75
    assert data["is_duplicate"] is False
    assert len(data["talking_points"]) > 0
    assert data["airtable_status"] == "SYNCED"
    assert data["slack_status"] == "SENT"
    assert data["latency_ms"] < 10000  # SLA requirement: < 10 seconds

    # Check persistence
    stored = db_session.query(LeadRecord).filter(LeadRecord.email == payload["email"]).first()
    assert stored is not None
    assert stored.company == "Cyberdyne Systems"
    assert stored.score == data["score"]

def test_lead_idempotency_prevents_duplicate_records(client, db_session):
    """Test that repeated lead submissions with identical idempotency key return existing record."""
    payload = {
        "name": "Alex Murphy",
        "email": "alex.murphy@omnicorp.org",
        "phone": "555-019-2831",
        "company": "Omni Consumer Products",
        "company_size": "1000+",
        "budget": 60000.0,
        "business_need": "Automating enterprise incident response and financial approval workflows across our global subsidiaries.",
        "consent": True,
        "idempotency_key": "idemp_test_omni_unique_001"
    }

    # First submission
    res1 = client.post("/api/v1/leads/intake", json=payload)
    assert res1.status_code == 201
    data1 = res1.json()
    assert data1["is_duplicate"] is False

    # Second submission with same idempotency key
    res2 = client.post("/api/v1/leads/intake", json=payload)
    assert res2.status_code == 201
    data2 = res2.json()
    assert data2["is_duplicate"] is True
    assert data2["lead_id"] == data1["lead_id"]

    # Verify database only contains exactly 1 record
    count = db_session.query(LeadRecord).filter(LeadRecord.idempotency_key == "idemp_test_omni_unique_001").count()
    assert count == 1

def test_invalid_lead_rejected_safely(client):
    """Test that invalid payload missing consent or with invalid email is safely rejected."""
    # Missing consent
    bad_payload = {
        "name": "Anonymous User",
        "email": "valid.email@example.com",
        "company": "No Consent LLC",
        "company_size": "1-10",
        "business_need": "Looking for tools.",
        "consent": False
    }
    res = client.post("/api/v1/leads/intake", json=bad_payload)
    assert res.status_code == 422

    # Malformed email
    bad_payload2 = {
        "name": "Jane Doe",
        "email": "not-an-email-address",
        "company": "Bad Email Corp",
        "company_size": "11-50",
        "business_need": "We need email automation.",
        "consent": True
    }
    res2 = client.post("/api/v1/leads/intake", json=bad_payload2)
    assert res2.status_code == 422

def test_lead_listing_and_filtering(client, db_session):
    """Test searching and filtering leads by priority and status."""
    # Seed 2 leads
    lead1 = LeadIntakeRequest(
        name="Leader One",
        email="lead1@enterprise.com",
        company="Alpha Corp",
        company_size="1000+",
        budget=80000.0,
        business_need="High priority enterprise automation needs across all departments.",
        consent=True
    )
    lead2 = LeadIntakeRequest(
        name="Leader Two",
        email="lead2@smallbiz.com",
        company="Beta Studio",
        company_size="1-10",
        budget=500.0,
        business_need="Basic tools.",
        consent=True
    )
    lead_routing_service.process_lead(db_session, lead1)
    lead_routing_service.process_lead(db_session, lead2)

    # Filter by HIGH priority
    res = client.get("/api/v1/leads?priority=HIGH")
    assert res.status_code == 200
    items = res.json()["items"]
    assert any(l["email"] == "lead1@enterprise.com" for l in items)
    assert not any(l["email"] == "lead2@smallbiz.com" for l in items)

    # Search by company name
    res_search = client.get("/api/v1/leads?search=Beta")
    assert res_search.status_code == 200
    items_search = res_search.json()["items"]
    assert len(items_search) == 1
    assert items_search[0]["company"] == "Beta Studio"
