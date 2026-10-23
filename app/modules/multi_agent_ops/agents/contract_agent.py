import time
from sqlalchemy.orm import Session
from app.models.enterprise import EnterpriseProject, ContractDraft
from app.modules.multi_agent_ops.supervisor import workflow_supervisor
from app.config import logger

STANDARD_MSA_TEMPLATE = """
MASTER SERVICES AGREEMENT (ENTERPRISE SCHEDULE)
================================================
Reference Contract: {contract_ref}
Date: {issue_date}

PARTIES:
1. Datheon AI Automation Suite ("Service Provider")
2. {company_name}, Attention: {client_name} <{client_email}> ("Client")

1. SCOPE OF SERVICES:
   The Service Provider shall deploy and maintain the {service_type} for Client operations.

2. COMMERCIAL TERMS:
   Agreed Contract Value: ${deal_value:,.2f} {currency}
   Payment Milestones: Initial payment due upon agreement execution via verified Stripe webhook.

3. DATA PROTECTION & CONFIDENTIALITY:
   Both parties agree to uphold strict data minimization, encryption in transit and at rest,
   and least-privilege access controls.

4. DRAFT STATUS NOTICE:
   [NOTICE] THIS DOCUMENT IS AN AI-PREPARED DRAFT REQUIRING AUTHORIZED EXECUTIVE HUMAN SIGNATURE.
   THIS DRAFT DOES NOT CONSTITUTE A BINDING LEGAL OBLIGATION UNTIL EXPLICITLY COUNTERSIGNED.
"""

class ContractPreparationAgent:
    """Agent 5: Prepares authorized template-based contract drafts without hallucinating terms."""

    @staticmethod
    def generate_draft(db: Session, project: EnterpriseProject) -> ContractDraft:
        # Check if project is in QUALIFIED or REVISION_REQUESTED state
        if project.current_state not in ("QUALIFIED", "REVISION_REQUESTED", "CONTRACT_DRAFTED"):
            raise ValueError(f"Cannot generate contract draft in state '{project.current_state}'. Project must be QUALIFIED.")

        contract_ref = f"CNT-{project.id}"
        issue_date = time.strftime("%Y-%m-%d", time.gmtime())

        draft_content = STANDARD_MSA_TEMPLATE.format(
            contract_ref=contract_ref,
            issue_date=issue_date,
            company_name=project.company,
            client_name=project.client_name,
            client_email=project.client_email,
            service_type=project.service_type,
            deal_value=project.deal_value,
            currency=project.currency
        )

        clauses = [
            "Standard Enterprise Master Services Agreement v2.4",
            "SLA Schedule A: 99.9% Operational Uptime",
            "Confidentiality and Data Processing Agreement (DPA)",
            "Verified Payment Trigger via Official Stripe Processing"
        ]

        missing_fields = []
        if project.deal_value <= 0:
            missing_fields.append("Verified commercial deal value")

        draft = ContractDraft(
            project_id=project.id,
            template_name="STANDARD_ENTERPRISE_MSA",
            clauses=clauses,
            missing_fields=missing_fields,
            draft_content=draft_content,
            is_approved=False
        )
        db.add(draft)

        if project.current_state != "CONTRACT_DRAFTED":
            workflow_supervisor.transition(
                db=db,
                project=project,
                target_state="CONTRACT_DRAFTED",
                agent_name="ContractPreparationAgent",
                actor="system",
                trace_data={"contract_ref": contract_ref, "template": "STANDARD_ENTERPRISE_MSA"}
            )

        db.commit()
        db.refresh(draft)
        logger.info(f"[ContractAgent] Draft {draft.id} generated for project {project.id} (Draft-only status)")
        return draft

contract_agent = ContractPreparationAgent()
