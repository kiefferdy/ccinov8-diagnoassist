"""
Workflow Service for DiagnoAssist Backend

This service provides high-level workflow management and orchestration capabilities.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.core.workflow_engine import workflow_engine, WorkflowPriority, WorkflowStatus
from app.models.patient import PatientModel
from app.models.encounter import EncounterModel
from app.models.auth import UserModel
from app.core.exceptions import ValidationException, NotFoundError

logger = logging.getLogger(__name__)


class WorkflowService:
    """High-level workflow management service"""
    
    def __init__(self):
        self.engine = workflow_engine
    
    async def start_patient_registration(
        self, 
        patient: PatientModel,
        user: Optional[UserModel] = None,
        merge_policy: str = "fail"
    ) -> str:
        """
        Start patient registration workflow
        
        Args:
            patient: Patient data to register
            user: User performing the registration
            merge_policy: How to handle duplicates ("fail", "merge", "create_anyway")
        
        Returns:
            Workflow instance ID
        """
        try:
            context_data = {
                "patient": patient.model_dump(),
                "merge_policy": merge_policy
            }
            
            instance_id = await self.engine.start_workflow(
                workflow_id="patient.registration",
                context_data=context_data,
                user=user,
                priority=WorkflowPriority.NORMAL
            )
            
            logger.info(f"Started patient registration workflow {instance_id} for {patient.demographics.name}")
            
            return instance_id
            
        except Exception as e:
            logger.error(f"Error starting patient registration workflow: {e}")
            raise
    
    async def start_encounter_documentation(
        self,
        encounter: EncounterModel,
        user: Optional[UserModel] = None,
        auto_sign: bool = False
    ) -> str:
        """
        Start encounter documentation workflow
        
        Args:
            encounter: Encounter data to create
            user: User creating the encounter
            auto_sign: Whether to automatically sign after validation
        
        Returns:
            Workflow instance ID
        """
        try:
            context_data = {
                "encounter": encounter.model_dump(),
                "auto_sign": auto_sign
            }
            
            instance_id = await self.engine.start_workflow(
                workflow_id="encounter.documentation",
                context_data=context_data,
                user=user,
                priority=WorkflowPriority.HIGH
            )
            
            logger.info(f"Started encounter documentation workflow {instance_id} for patient {encounter.patient_id}")
            
            return instance_id
            
        except Exception as e:
            logger.error(f"Error starting encounter documentation workflow: {e}")
            raise
    
    async def start_encounter_signing(
        self,
        encounter_id: str,
        user: Optional[UserModel] = None,
        signing_notes: Optional[str] = None
    ) -> str:
        """
        Start encounter signing workflow for existing encounter
        
        Args:
            encounter_id: ID of encounter to sign
            user: User signing the encounter
            signing_notes: Optional notes to add during signing
        
        Returns:
            Workflow instance ID
        """
        try:
            context_data = {
                "encounter_id": encounter_id,
                "signing_notes": signing_notes
            }
            
            instance_id = await self.engine.start_workflow(
                workflow_id="encounter.signing",
                context_data=context_data,
                user=user,
                priority=WorkflowPriority.HIGH
            )
            
            logger.info(f"Started encounter signing workflow {instance_id} for encounter {encounter_id}")
            
            return instance_id
            
        except Exception as e:
            logger.error(f"Error starting encounter signing workflow: {e}")
            raise
    
    async def get_workflow_status(self, instance_id: str) -> Dict[str, Any]:
        """
        Get comprehensive workflow status
        
        Args:
            instance_id: Workflow instance ID
        
        Returns:
            Workflow status information
        """
        try:
            instance = await self.engine.get_instance(instance_id)
            if not instance:
                raise NotFoundError("Workflow instance", instance_id)
            
            # Calculate execution time
            execution_time = None
            if instance.started_at:
                end_time = instance.completed_at or datetime.utcnow()
                execution_time = (end_time - instance.started_at).total_seconds()
            
            # Get step details
            steps = []
            for step_result in instance.context.execution_history:
                steps.append({
                    "step_id": step_result.step_id,
                    "status": step_result.status.value,
                    "execution_time_ms": step_result.execution_time_ms,
                    "retry_count": step_result.retry_count,
                    "error": step_result.error,
                    "data": step_result.data
                })
            
            status_info = {
                "instance_id": instance_id,
                "workflow_id": instance.workflow_id,
                "status": instance.status.value,
                "current_step": instance.current_step,
                "started_at": instance.started_at.isoformat() if instance.started_at else None,
                "completed_at": instance.completed_at.isoformat() if instance.completed_at else None,
                "execution_time_seconds": execution_time,
                "error": instance.error,
                "priority": instance.priority.value,
                "retry_count": instance.retry_count,
                "steps": steps,
                "context_data": instance.context.data,
                "context_variables": instance.context.variables
            }
            
            return status_info
            
        except Exception as e:
            logger.error(f"Error getting workflow status {instance_id}: {e}")
            raise
    
    async def cancel_workflow(self, instance_id: str) -> bool:
        """
        Cancel a running workflow
        
        Args:
            instance_id: Workflow instance ID
        
        Returns:
            True if cancelled successfully
        """
        try:
            success = await self.engine.cancel_workflow(instance_id)
            
            if success:
                logger.info(f"Cancelled workflow {instance_id}")
            else:
                logger.warning(f"Failed to cancel workflow {instance_id} (may not be running)")
            
            return success
            
        except Exception as e:
            logger.error(f"Error cancelling workflow {instance_id}: {e}")
            raise
    
    async def get_workflow_history(
        self,
        workflow_id: Optional[str] = None,
        user_id: Optional[str] = None,
        status: Optional[WorkflowStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get workflow execution history with filters
        
        Args:
            workflow_id: Filter by workflow type
            user_id: Filter by user who started workflow
            status: Filter by workflow status
            limit: Maximum number of results
            offset: Offset for pagination
        
        Returns:
            List of workflow instances
        """
        try:
            # Get all instances (in a real implementation, this would be paginated from database)
            all_instances = []
            
            for instance in self.engine._instances.values():
                # Apply filters
                if workflow_id and instance.workflow_id != workflow_id:
                    continue
                
                if user_id and (not instance.context.user or instance.context.user.id != user_id):
                    continue
                
                if status and instance.status != status:
                    continue
                
                # Calculate execution time
                execution_time = None
                if instance.started_at:
                    end_time = instance.completed_at or datetime.utcnow()
                    execution_time = (end_time - instance.started_at).total_seconds()
                
                instance_info = {
                    "instance_id": instance.instance_id,
                    "workflow_id": instance.workflow_id,
                    "status": instance.status.value,
                    "started_at": instance.started_at.isoformat() if instance.started_at else None,
                    "completed_at": instance.completed_at.isoformat() if instance.completed_at else None,
                    "execution_time_seconds": execution_time,
                    "error": instance.error,
                    "priority": instance.priority.value,
                    "user_id": instance.context.user.id if instance.context.user else None,
                    "steps_completed": len([s for s in instance.context.execution_history if s.status.value == "completed"]),
                    "total_steps": len(instance.context.execution_history)
                }
                
                all_instances.append(instance_info)
            
            # Sort by start time (newest first)
            all_instances.sort(key=lambda x: x["started_at"] or "", reverse=True)
            
            # Apply pagination
            paginated_instances = all_instances[offset:offset + limit]
            
            return paginated_instances
            
        except Exception as e:
            logger.error(f"Error getting workflow history: {e}")
            return []
    
    async def get_workflow_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive workflow statistics
        
        Returns:
            Workflow execution statistics
        """
        try:
            # Get basic statistics from engine
            basic_stats = await self.engine.get_workflow_statistics()
            
            # Add additional medical workflow specific statistics
            medical_stats = {
                "patient_registrations": {
                    "total": 0,
                    "successful": 0,
                    "failed": 0,
                    "with_duplicates": 0
                },
                "encounter_workflows": {
                    "total": 0,
                    "signed": 0,
                    "failed_validation": 0,
                    "fhir_sync_failures": 0
                },
                "average_completion_times": {},
                "common_failure_reasons": {},
                "user_activity": {}
            }
            
            # Analyze instances for medical-specific metrics
            for instance in self.engine._instances.values():
                if instance.workflow_id == "patient.registration":
                    medical_stats["patient_registrations"]["total"] += 1
                    if instance.status == WorkflowStatus.COMPLETED:
                        medical_stats["patient_registrations"]["successful"] += 1
                    elif instance.status == WorkflowStatus.FAILED:
                        medical_stats["patient_registrations"]["failed"] += 1
                    
                    # Check for duplicate handling
                    if instance.context.data.get("duplicate_found"):
                        medical_stats["patient_registrations"]["with_duplicates"] += 1
                
                elif instance.workflow_id in ["encounter.documentation", "encounter.signing"]:
                    medical_stats["encounter_workflows"]["total"] += 1
                    
                    # Check if encounter was signed
                    signed_steps = [s for s in instance.context.execution_history if s.step_id == "encounter.sign" and s.status.value == "completed"]
                    if signed_steps:
                        medical_stats["encounter_workflows"]["signed"] += 1
                    
                    # Check for validation failures
                    validation_failures = [s for s in instance.context.execution_history if s.step_id == "encounter.validate" and s.status.value == "failed"]
                    if validation_failures:
                        medical_stats["encounter_workflows"]["failed_validation"] += 1
                    
                    # Check for FHIR sync failures
                    fhir_failures = [s for s in instance.context.execution_history if s.step_id == "encounter.fhir_sync" and s.status.value == "failed"]
                    if fhir_failures:
                        medical_stats["encounter_workflows"]["fhir_sync_failures"] += 1
                
                # Track user activity
                if instance.context.user:
                    user_id = instance.context.user.id
                    if user_id not in medical_stats["user_activity"]:
                        medical_stats["user_activity"][user_id] = {"workflows_started": 0, "workflows_completed": 0}
                    
                    medical_stats["user_activity"][user_id]["workflows_started"] += 1
                    if instance.status == WorkflowStatus.COMPLETED:
                        medical_stats["user_activity"][user_id]["workflows_completed"] += 1
                
                # Calculate completion times
                if instance.started_at and instance.completed_at:
                    execution_time = (instance.completed_at - instance.started_at).total_seconds()
                    workflow_id = instance.workflow_id
                    
                    if workflow_id not in medical_stats["average_completion_times"]:
                        medical_stats["average_completion_times"][workflow_id] = {"total_time": 0, "count": 0}
                    
                    medical_stats["average_completion_times"][workflow_id]["total_time"] += execution_time
                    medical_stats["average_completion_times"][workflow_id]["count"] += 1
                
                # Track failure reasons
                if instance.status == WorkflowStatus.FAILED and instance.error:
                    error_key = instance.error[:50]  # First 50 chars of error
                    medical_stats["common_failure_reasons"][error_key] = medical_stats["common_failure_reasons"].get(error_key, 0) + 1
            
            # Calculate averages
            for workflow_id, timing_data in medical_stats["average_completion_times"].items():
                if timing_data["count"] > 0:
                    timing_data["average_seconds"] = timing_data["total_time"] / timing_data["count"]
            
            # Combine statistics
            combined_stats = {
                **basic_stats,
                "medical_workflows": medical_stats
            }
            
            return combined_stats
            
        except Exception as e:
            logger.error(f"Error getting workflow statistics: {e}")
            return {"error": str(e)}
    
    async def retry_failed_workflow(self, instance_id: str) -> str:
        """
        Retry a failed workflow by creating a new instance with same data
        
        Args:
            instance_id: ID of failed workflow instance
        
        Returns:
            New workflow instance ID
        """
        try:
            # Get original instance
            original_instance = await self.engine.get_instance(instance_id)
            if not original_instance:
                raise NotFoundError("Workflow instance", instance_id)
            
            if original_instance.status != WorkflowStatus.FAILED:
                raise ValidationException(f"Workflow {instance_id} is not in failed state")
            
            # Start new workflow with same data
            new_instance_id = await self.engine.start_workflow(
                workflow_id=original_instance.workflow_id,
                context_data=original_instance.context.data,
                user=original_instance.context.user,
                priority=original_instance.priority
            )
            
            logger.info(f"Retried failed workflow {instance_id} as new instance {new_instance_id}")
            
            return new_instance_id
            
        except Exception as e:
            logger.error(f"Error retrying workflow {instance_id}: {e}")
            raise


# Create service instance
workflow_service = WorkflowService()