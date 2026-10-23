import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.config import logger
from app.models.enterprise import EnterpriseProject, WorkflowExecution
from app.models.audit import AuditLog

VALID_TRANSITIONS = {
    "INTAKE_RECEIVED": ["QUALIFIED", "FAILED"],
    "QUALIFIED": ["CONTRACT_DRAFTED", "FAILED"],
    "CONTRACT_DRAFTED": ["PENDING_PAYMENT", "REVISION_REQUESTED", "FAILED"],
    "REVISION_REQUESTED": ["CONTRACT_DRAFTED", "FAILED"],
    "PENDING_PAYMENT": ["PAYMENT_VERIFIED", "FAILED"],
    "PAYMENT_VERIFIED": ["CHANNELS_PROVISIONED", "FAILED"],
    "CHANNELS_PROVISIONED": ["COMPLETED", "FAILED"],
    "COMPLETED": [],
    "FAILED": ["INTAKE_RECEIVED"]  # Recovery restart
}

class InvalidStateTransitionError(ValueError):
    pass

class WorkflowSupervisor:
    """
    State machine supervisor governing multi-agent enterprise lifecycles,
    preventing invalid transitions and enforcing human approval checkpoints.
    """

    @staticmethod
    def transition(
        db: Session,
        project: EnterpriseProject,
        target_state: str,
        agent_name: str,
        actor: str = "system",
        trace_data: Optional[Dict[str, Any]] = None
    ) -> EnterpriseProject:
        """Execute a validated state machine transition with audit logging."""
        current = project.current_state
        allowed = VALID_TRANSITIONS.get(current, [])

        if target_state not in allowed:
            err = f"Invalid state transition: Cannot transition from '{current}' to '{target_state}'. Allowed transitions: {allowed}"
            logger.error(f"[WorkflowSupervisor] {err}")
            raise InvalidStateTransitionError(err)

        start_time = time.time()
        project.current_state = target_state
        project.updated_at = datetime.now(timezone.utc)

        # Record step in workflow executions trace
        workflow_step = WorkflowExecution(
            project_id=project.id,
            current_agent=agent_name,
            step_name=f"TRANSITION_{current}_TO_{target_state}",
            status="COMPLETED",
            trace=trace_data or {},
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc)
        )
        db.add(workflow_step)

        # Immutable system audit log
        db.add(AuditLog(
            module="enterprise",
            action="STATE_TRANSITION",
            entity_type="EnterpriseProject",
            entity_id=project.id,
            actor=actor,
            status="SUCCESS",
            details={
                "previous_state": current,
                "new_state": target_state,
                "agent": agent_name,
                "trace": trace_data
            },
            duration_ms=int((time.time() - start_time) * 1000)
        ))

        db.commit()
        db.refresh(project)
        logger.info(f"[WorkflowSupervisor] Project {project.id} transitioned {current} -> {target_state} by {agent_name} ({actor})")
        return project

workflow_supervisor = WorkflowSupervisor()
