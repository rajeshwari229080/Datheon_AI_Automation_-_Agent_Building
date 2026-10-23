from sqlalchemy.orm import Session
from app.models.enterprise import EnterpriseProject
from app.adapters.slack_adapter import slack_adapter
from app.modules.multi_agent_ops.supervisor import workflow_supervisor
from app.config import logger

class CollaborationAgent:
    """Agent 7: Coordinates Slack project channels, alerts, and team onboarding."""

    @staticmethod
    def provision_project_space(db: Session, project: EnterpriseProject) -> dict:
        if project.current_state not in ("PAYMENT_VERIFIED", "CHANNELS_PROVISIONED"):
            raise ValueError(f"Cannot provision collaboration channels in state '{project.current_state}'. Payment must be verified.")

        # Avoid duplicate channel creation
        if project.slack_channel_id:
            logger.info(f"[CollaborationAgent] Channel already exists: {project.slack_channel_name}")
            return {
                "success": True,
                "channel_id": project.slack_channel_id,
                "channel_name": project.slack_channel_name,
                "note": "Existing channel preserved"
            }

        ch_res = slack_adapter.provision_project_channel(
            project_name=project.company,
            client_name=project.client_name
        )

        project.slack_channel_id = ch_res.get("channel_id")
        project.slack_channel_name = ch_res.get("channel_name")

        # Send project kickoff message
        kickoff_msg = (
            f"🚀 *Welcome {project.company} to Enterprise Operations*\n"
            f"• Project ID: `{project.id}`\n"
            f"• Client Lead: {project.client_name} <{project.client_email}>\n"
            f"• Contract Tier: {project.service_type}\n"
            f"• Status: *Active & Onboarded*"
        )
        slack_adapter.send_approval_notification(
            title="Project Workspace Active",
            details={"Channel": f"#{project.slack_channel_name}", "Client": project.client_name, "Deal Value": f"${project.deal_value:,.2f}"}
        )

        # Transition to CHANNELS_PROVISIONED then COMPLETED
        workflow_supervisor.transition(
            db=db,
            project=project,
            target_state="CHANNELS_PROVISIONED",
            agent_name="CollaborationAgent",
            actor="system",
            trace_data={"channel_id": project.slack_channel_id, "channel_name": project.slack_channel_name}
        )

        workflow_supervisor.transition(
            db=db,
            project=project,
            target_state="COMPLETED",
            agent_name="WorkflowSupervisor",
            actor="system",
            trace_data={"lifecycle": "SUCCESSFULLY_COMPLETED"}
        )

        db.commit()
        db.refresh(project)
        return ch_res

collaboration_agent = CollaborationAgent()
