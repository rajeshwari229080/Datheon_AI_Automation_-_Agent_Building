import hashlib
import time
from typing import Any, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from app.config import logger
from app.models.lead import LeadRecord, LeadExecutionLog
from app.models.audit import AuditLog
from app.adapters.airtable_adapter import airtable_adapter
from app.adapters.slack_adapter import slack_adapter
from app.adapters.openai_adapter import openai_adapter
from app.modules.lead_routing.schemas import LeadIntakeRequest, LeadQualificationResult, LeadResponse

class LeadRoutingService:
    """Enterprise service orchestrating lead intake, deterministic scoring, AI qualification, and sync."""

    @staticmethod
    def generate_idempotency_key(payload: LeadIntakeRequest) -> str:
        if payload.idempotency_key:
            return payload.idempotency_key
        raw = f"{payload.email.strip().lower()}:{payload.company.strip().lower()}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def calculate_deterministic_score(payload: LeadIntakeRequest) -> Tuple[int, str, str]:
        """
        Deterministic scoring based on strict enterprise criteria.
        Returns: (score: int 0-100, priority: HIGH/MEDIUM/LOW, status: QUALIFIED/UNQUALIFIED/INCOMPLETE/MANUAL_REVIEW)
        """
        score = 0

        # 1. Budget points (max 40)
        budget = payload.budget or 0.0
        if budget >= 50000:
            score += 40
        elif budget >= 20000:
            score += 30
        elif budget >= 5000:
            score += 20
        elif budget >= 1000:
            score += 10
        else:
            score += 5

        # 2. Company size points (max 30)
        size = payload.company_size.strip().lower()
        if "1000+" in size or "enterprise" in size:
            score += 30
        elif "201-1000" in size or "500" in size:
            score += 25
        elif "51-200" in size:
            score += 20
        elif "11-50" in size:
            score += 15
        else:
            score += 10

        # 3. Business Need depth & clarity (max 20)
        need_len = len(payload.business_need.strip())
        if need_len >= 120:
            score += 20
        elif need_len >= 50:
            score += 15
        elif need_len >= 20:
            score += 10
        else:
            score += 5

        # 4. Contact completeness (max 10)
        if payload.phone:
            score += 10
        else:
            score += 5

        score = min(max(score, 0), 100)

        # Priority determination
        if score >= 75:
            priority = "HIGH"
        elif score >= 45:
            priority = "MEDIUM"
        else:
            priority = "LOW"

        # Qualification status
        if need_len < 15:
            status = "INCOMPLETE"
        elif score >= 55 and budget >= 5000:
            status = "QUALIFIED"
        elif budget < 1000 and score < 40:
            status = "UNQUALIFIED"
        else:
            status = "MANUAL_REVIEW"

        return score, priority, status

    def process_lead(self, db: Session, payload: LeadIntakeRequest) -> LeadResponse:
        start_time = time.time()
        idempotency_key = self.generate_idempotency_key(payload)

        # 1. Idempotency Check
        existing_lead = db.query(LeadRecord).filter(LeadRecord.idempotency_key == idempotency_key).first()
        if existing_lead:
            total_duration_ms = int((time.time() - start_time) * 1000)
            logger.info(f"[LeadRouting] Duplicate lead detected: {payload.email} ({idempotency_key})")
            return LeadResponse(
                success=True,
                lead_id=existing_lead.id,
                qualification_status=existing_lead.qualification_status,
                score=existing_lead.score,
                priority=existing_lead.priority,
                latency_ms=total_duration_ms,
                airtable_status=existing_lead.airtable_status,
                slack_status=existing_lead.slack_status,
                summary=existing_lead.qualification_summary or "Existing qualified lead",
                talking_points=existing_lead.talking_points or [],
                is_duplicate=True,
                message="Lead was already processed (Idempotent response)."
            )

        # 2. Deterministic Scoring
        step_start = time.time()
        score, priority, status = self.calculate_deterministic_score(payload)
        scoring_latency_ms = int((time.time() - step_start) * 1000)

        # 3. AI Qualification & Talking Points Enrichment
        step_start = time.time()
        ai_prompt = (
            f"Analyze this sales lead:\n"
            f"Prospect Name: {payload.name}\n"
            f"Company: {payload.company} (Size: {payload.company_size})\n"
            f"Budget: ${payload.budget:,.2f}\n"
            f"Product Interest: {payload.product_interest}\n"
            f"Business Need: {payload.business_need}\n"
            f"Deterministic Score: {score}/100, Priority: {priority}"
        )
        ai_res = openai_adapter.generate_chat_json(
            system_prompt="You are an enterprise AI lead qualification engine. Generate structured summary and sales talking points.",
            user_prompt=ai_prompt,
            expected_schema=LeadQualificationResult.model_json_schema()
        )
        ai_latency_ms = int((time.time() - step_start) * 1000)

        summary = ai_res.get("lead_summary", f"{payload.company} evaluating {payload.product_interest}")
        talking_points = ai_res.get("talking_points", [
            f"Inquire about specific scaling targets for {payload.company}.",
            f"Confirm current workflow automation bottlenecks.",
            f"Present tailored enterprise demo for {payload.product_interest}."
        ])
        missing_info = ai_res.get("missing_info", [])
        confidence = float(ai_res.get("confidence", 0.95))

        # Check if incomplete
        if missing_info and status == "QUALIFIED" and not payload.phone:
            missing_info.append("Direct phone number")

        # 4. Save to Database
        lead_record = LeadRecord(
            name=payload.name.strip(),
            email=str(payload.email).strip().lower(),
            phone=payload.phone,
            company=payload.company.strip(),
            company_size=payload.company_size,
            budget=payload.budget or 0.0,
            budget_range=payload.budget_range,
            business_need=payload.business_need.strip(),
            product_interest=payload.product_interest,
            consent=payload.consent,
            qualification_status=status,
            score=score,
            priority=priority,
            qualification_summary=summary,
            talking_points=talking_points,
            missing_info=missing_info,
            confidence=confidence,
            idempotency_key=idempotency_key,
            raw_payload=payload.model_dump()
        )
        db.add(lead_record)
        db.flush()

        # 5. Airtable Synchronization
        step_start = time.time()
        airtable_data = {
            "Lead ID": lead_record.id,
            "Name": lead_record.name,
            "Email": lead_record.email,
            "Company": lead_record.company,
            "Company Size": lead_record.company_size,
            "Budget": lead_record.budget,
            "Score": lead_record.score,
            "Priority": lead_record.priority,
            "Status": lead_record.qualification_status,
            "Summary": lead_record.qualification_summary
        }
        airtable_res = airtable_adapter.sync_lead(airtable_data)
        airtable_latency_ms = int((time.time() - step_start) * 1000)

        if airtable_res.get("success"):
            lead_record.airtable_status = "SYNCED"
            lead_record.airtable_record_id = airtable_res.get("record_id")
        else:
            lead_record.airtable_status = "FAILED"

        # 6. Slack Alert Notification
        step_start = time.time()
        slack_summary = {
            "name": lead_record.name,
            "email": lead_record.email,
            "phone": lead_record.phone,
            "company": lead_record.company,
            "budget": lead_record.budget,
            "score": lead_record.score,
            "priority": lead_record.priority,
            "qualification_status": lead_record.qualification_status,
            "qualification_summary": lead_record.qualification_summary,
            "talking_points": lead_record.talking_points
        }
        slack_res = slack_adapter.send_lead_alert(slack_summary)
        slack_latency_ms = int((time.time() - step_start) * 1000)

        lead_record.slack_status = "SENT" if slack_res.get("success") else "FAILED"

        # 7. Record Execution Step Logs
        db.add(LeadExecutionLog(lead_id=lead_record.id, step_name="DETERMINISTIC_SCORING", status="SUCCESS", latency_ms=scoring_latency_ms))
        db.add(LeadExecutionLog(lead_id=lead_record.id, step_name="AI_QUALIFICATION", status="SUCCESS", latency_ms=ai_latency_ms))
        db.add(LeadExecutionLog(lead_id=lead_record.id, step_name="AIRTABLE_SYNC", status=lead_record.airtable_status, latency_ms=airtable_latency_ms))
        db.add(LeadExecutionLog(lead_id=lead_record.id, step_name="SLACK_ALERT", status=lead_record.slack_status, latency_ms=slack_latency_ms))

        # System Audit Log
        db.add(AuditLog(
            module="lead_routing",
            action="LEAD_INTAKE_QUALIFIED",
            entity_type="Lead",
            entity_id=lead_record.id,
            status="SUCCESS",
            details={"score": score, "priority": priority, "status": status, "email": lead_record.email},
            duration_ms=int((time.time() - start_time) * 1000)
        ))

        db.commit()
        db.refresh(lead_record)

        total_latency_ms = int((time.time() - start_time) * 1000)
        logger.info(f"[LeadRouting] Successfully qualified lead {lead_record.id} in {total_latency_ms}ms (SLA target < 10,000ms)")

        return LeadResponse(
            success=True,
            lead_id=lead_record.id,
            qualification_status=lead_record.qualification_status,
            score=lead_record.score,
            priority=lead_record.priority,
            latency_ms=total_latency_ms,
            airtable_status=lead_record.airtable_status,
            slack_status=lead_record.slack_status,
            summary=lead_record.qualification_summary,
            talking_points=lead_record.talking_points,
            is_duplicate=False
        )

lead_routing_service = LeadRoutingService()
