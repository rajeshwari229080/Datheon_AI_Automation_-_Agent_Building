import time
from sqlalchemy.orm import Session
from app.models.enterprise import EnterpriseProject
from app.adapters.airtable_adapter import airtable_adapter
from app.modules.multi_agent_ops.schemas import ProjectIntakeRequest
from app.modules.multi_agent_ops.supervisor import workflow_supervisor
from app.config import logger

class IntakeAgent:
    """Agent 1: Validates customer onboarding requests and creates central tracked projects."""

    @staticmethod
    def execute(db: Session, request: ProjectIntakeRequest) -> EnterpriseProject:
        # Check duplicate by client email & company
        existing = db.query(EnterpriseProject).filter(
            EnterpriseProject.client_email == str(request.client_email).lower(),
            EnterpriseProject.company == request.company.strip()
        ).first()

        if existing:
            logger.info(f"[IntakeAgent] Project already exists for {request.client_email} ({existing.id})")
            return existing

        project_id = f"PROJ-{int(time.time()*100)%1000000:06d}"
        project = EnterpriseProject(
            id=project_id,
            client_name=request.client_name.strip(),
            client_email=str(request.client_email).lower(),
            company=request.company.strip(),
            service_type=request.service_type,
            deal_value=request.deal_value,
            currency=request.currency.upper(),
            current_state="INTAKE_RECEIVED"
        )
        db.add(project)
        db.flush()

        # Sync to central Airtable
        airtable_res = airtable_adapter.sync_lead({
            "Project ID": project.id,
            "Client Name": project.client_name,
            "Company": project.company,
            "Email": project.client_email,
            "Deal Value": project.deal_value,
            "Status": "INTAKE_RECEIVED"
        })
        if airtable_res.get("success"):
            project.airtable_id = airtable_res.get("record_id")

        # Automatically transition to QUALIFIED
        workflow_supervisor.transition(
            db=db,
            project=project,
            target_state="QUALIFIED",
            agent_name="IntakeAgent",
            actor="system",
            trace_data={"deal_value": project.deal_value, "service": project.service_type}
        )

        db.commit()
        db.refresh(project)
        return project

intake_agent = IntakeAgent()
