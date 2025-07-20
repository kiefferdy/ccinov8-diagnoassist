"""
Workflow Orchestration Engine for DiagnoAssist Backend

This module provides a comprehensive workflow management system for orchestrating
complex medical processes and business operations.
"""
import asyncio
import uuid
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Union, Type
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import logging

from app.models.auth import UserModel, UserRoleEnum
from app.models.patient import PatientModel
from app.models.encounter import EncounterModel, EncounterStatusEnum
from app.models.episode import EpisodeModel
from app.core.exceptions import ValidationException, BusinessRuleException

logger = logging.getLogger(__name__)


class WorkflowStatus(str, Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class StepStatus(str, Enum):
    """Individual step status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRY = "retry"


class WorkflowPriority(str, Enum):
    """Workflow execution priority"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class StepResult(BaseModel):
    """Result of a workflow step execution"""
    step_id: str
    status: StepStatus
    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    execution_time_ms: float
    retry_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowContext(BaseModel):
    """Context data passed through workflow execution"""
    workflow_id: str
    instance_id: str
    user: Optional[UserModel] = None
    data: Dict[str, Any] = Field(default_factory=dict)
    variables: Dict[str, Any] = Field(default_factory=dict)
    execution_history: List[StepResult] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class WorkflowInstance(BaseModel):
    """Runtime instance of a workflow"""
    instance_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_step: Optional[str] = None
    context: WorkflowContext
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    priority: WorkflowPriority = WorkflowPriority.NORMAL
    timeout_seconds: Optional[int] = None
    retry_count: int = 0
    max_retries: int = 3


class WorkflowStep(ABC):
    """Abstract base class for workflow steps"""
    
    def __init__(
        self, 
        step_id: str, 
        name: str, 
        description: str = "",
        timeout_seconds: Optional[int] = None,
        retryable: bool = True,
        max_retries: int = 3
    ):
        self.step_id = step_id
        self.name = name
        self.description = description
        self.timeout_seconds = timeout_seconds
        self.retryable = retryable
        self.max_retries = max_retries
    
    @abstractmethod
    async def execute(self, context: WorkflowContext) -> StepResult:
        """Execute the workflow step"""
        pass
    
    async def can_execute(self, context: WorkflowContext) -> bool:
        """Check if step can be executed (conditional logic)"""
        return True
    
    async def on_failure(self, context: WorkflowContext, error: Exception) -> bool:
        """Handle step failure, return True to retry"""
        return self.retryable
    
    async def on_success(self, context: WorkflowContext, result: StepResult) -> None:
        """Handle successful step completion"""
        pass


class WorkflowDefinition(BaseModel):
    """Definition of a workflow"""
    workflow_id: str
    name: str
    description: str
    version: str = "1.0"
    steps: List[str] = Field(default_factory=list)
    dependencies: Dict[str, List[str]] = Field(default_factory=dict)
    parallel_groups: List[List[str]] = Field(default_factory=list)
    timeout_seconds: Optional[int] = None
    default_priority: WorkflowPriority = WorkflowPriority.NORMAL
    auto_cleanup: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowEngine:
    """Core workflow orchestration engine"""
    
    def __init__(self):
        self._workflows: Dict[str, WorkflowDefinition] = {}
        self._steps: Dict[str, WorkflowStep] = {}
        self._instances: Dict[str, WorkflowInstance] = {}
        self._running_instances: Dict[str, asyncio.Task] = {}
        
    def register_workflow(self, definition: WorkflowDefinition):
        """Register a workflow definition"""
        self._workflows[definition.workflow_id] = definition
        logger.info(f"Registered workflow: {definition.workflow_id}")
    
    def register_step(self, step: WorkflowStep):
        """Register a workflow step"""
        self._steps[step.step_id] = step
        logger.info(f"Registered workflow step: {step.step_id}")
    
    async def start_workflow(
        self, 
        workflow_id: str, 
        context_data: Optional[Dict[str, Any]] = None,
        user: Optional[UserModel] = None,
        priority: WorkflowPriority = WorkflowPriority.NORMAL
    ) -> str:
        """Start a new workflow instance"""
        
        if workflow_id not in self._workflows:
            raise ValidationException(f"Unknown workflow: {workflow_id}")
        
        workflow_def = self._workflows[workflow_id]
        instance_id = str(uuid.uuid4())
        
        # Create workflow context
        context = WorkflowContext(
            workflow_id=workflow_id,
            instance_id=instance_id,
            user=user,
            data=context_data or {},
            variables={}
        )
        
        # Create workflow instance
        instance = WorkflowInstance(
            instance_id=instance_id,
            workflow_id=workflow_id,
            context=context,
            priority=priority,
            timeout_seconds=workflow_def.timeout_seconds
        )
        
        self._instances[instance_id] = instance
        
        # Start execution
        task = asyncio.create_task(self._execute_workflow(instance))
        self._running_instances[instance_id] = task
        
        logger.info(f"Started workflow {workflow_id} with instance {instance_id}")
        
        return instance_id
    
    async def _execute_workflow(self, instance: WorkflowInstance) -> None:
        """Execute a workflow instance"""
        try:
            instance.status = WorkflowStatus.RUNNING
            instance.started_at = datetime.utcnow()
            
            workflow_def = self._workflows[instance.workflow_id]
            
            # Execute steps according to dependencies and parallel groups
            await self._execute_steps(instance, workflow_def)
            
            instance.status = WorkflowStatus.COMPLETED
            instance.completed_at = datetime.utcnow()
            
            logger.info(f"Completed workflow instance {instance.instance_id}")
            
        except Exception as e:
            instance.status = WorkflowStatus.FAILED
            instance.error = str(e)
            instance.completed_at = datetime.utcnow()
            
            logger.error(f"Failed workflow instance {instance.instance_id}: {e}")
        
        finally:
            # Cleanup running instance reference
            if instance.instance_id in self._running_instances:
                del self._running_instances[instance.instance_id]
    
    async def _execute_steps(self, instance: WorkflowInstance, workflow_def: WorkflowDefinition):
        """Execute workflow steps with dependency resolution"""
        completed_steps = set()
        failed_steps = set()
        
        # Create dependency graph
        remaining_steps = set(workflow_def.steps)
        
        while remaining_steps:
            # Find steps that can be executed (dependencies satisfied)
            ready_steps = []
            parallel_groups_ready = []
            
            for step_id in remaining_steps:
                dependencies = workflow_def.dependencies.get(step_id, [])
                if all(dep in completed_steps for dep in dependencies):
                    ready_steps.append(step_id)
            
            # Check for parallel groups
            for group in workflow_def.parallel_groups:
                if all(step in ready_steps for step in group):
                    parallel_groups_ready.append(group)
                    # Remove from individual ready steps
                    for step in group:
                        if step in ready_steps:
                            ready_steps.remove(step)
            
            if not ready_steps and not parallel_groups_ready:
                if remaining_steps:
                    raise ValidationException(f"Workflow deadlock detected. Remaining steps: {remaining_steps}")
                break
            
            # Execute parallel groups
            for group in parallel_groups_ready:
                await self._execute_parallel_steps(instance, group)
                for step_id in group:
                    completed_steps.add(step_id)
                    remaining_steps.discard(step_id)
            
            # Execute individual ready steps
            for step_id in ready_steps:
                result = await self._execute_single_step(instance, step_id)
                
                if result.status == StepStatus.COMPLETED:
                    completed_steps.add(step_id)
                else:
                    failed_steps.add(step_id)
                    # Fail workflow if critical step fails
                    raise ValidationException(f"Critical step {step_id} failed: {result.error}")
                
                remaining_steps.discard(step_id)
    
    async def _execute_parallel_steps(self, instance: WorkflowInstance, step_ids: List[str]):
        """Execute multiple steps in parallel"""
        tasks = [self._execute_single_step(instance, step_id) for step_id in step_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                step_id = step_ids[i]
                logger.error(f"Parallel step {step_id} failed: {result}")
                raise result
    
    async def _execute_single_step(self, instance: WorkflowInstance, step_id: str) -> StepResult:
        """Execute a single workflow step"""
        if step_id not in self._steps:
            raise ValidationException(f"Unknown step: {step_id}")
        
        step = self._steps[step_id]
        instance.current_step = step_id
        instance.context.updated_at = datetime.utcnow()
        
        # Check if step can be executed
        if not await step.can_execute(instance.context):
            result = StepResult(
                step_id=step_id,
                status=StepStatus.SKIPPED,
                execution_time_ms=0
            )
            instance.context.execution_history.append(result)
            return result
        
        start_time = datetime.utcnow()
        retry_count = 0
        
        while retry_count <= step.max_retries:
            try:
                # Execute step with timeout if specified
                if step.timeout_seconds:
                    result = await asyncio.wait_for(
                        step.execute(instance.context),
                        timeout=step.timeout_seconds
                    )
                else:
                    result = await step.execute(instance.context)
                
                result.execution_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                result.retry_count = retry_count
                
                # Call success handler
                await step.on_success(instance.context, result)
                
                instance.context.execution_history.append(result)
                return result
                
            except Exception as e:
                retry_count += 1
                logger.warning(f"Step {step_id} failed (attempt {retry_count}): {e}")
                
                # Check if should retry
                should_retry = await step.on_failure(instance.context, e)
                
                if not should_retry or retry_count > step.max_retries:
                    result = StepResult(
                        step_id=step_id,
                        status=StepStatus.FAILED,
                        error=str(e),
                        execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                        retry_count=retry_count
                    )
                    instance.context.execution_history.append(result)
                    raise e
                
                # Wait before retry (exponential backoff)
                await asyncio.sleep(min(2 ** retry_count, 30))
    
    async def get_instance(self, instance_id: str) -> Optional[WorkflowInstance]:
        """Get workflow instance by ID"""
        return self._instances.get(instance_id)
    
    async def cancel_workflow(self, instance_id: str) -> bool:
        """Cancel a running workflow"""
        if instance_id in self._running_instances:
            task = self._running_instances[instance_id]
            task.cancel()
            
            if instance_id in self._instances:
                self._instances[instance_id].status = WorkflowStatus.CANCELLED
                self._instances[instance_id].completed_at = datetime.utcnow()
            
            logger.info(f"Cancelled workflow instance {instance_id}")
            return True
        
        return False
    
    async def get_workflow_statistics(self) -> Dict[str, Any]:
        """Get workflow execution statistics"""
        stats = {
            "total_instances": len(self._instances),
            "running_instances": len(self._running_instances),
            "by_status": {},
            "by_workflow": {},
            "average_duration": {},
            "success_rate": {}
        }
        
        # Analyze instances
        for instance in self._instances.values():
            # Status statistics
            status = instance.status.value
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            
            # Workflow type statistics
            workflow_id = instance.workflow_id
            if workflow_id not in stats["by_workflow"]:
                stats["by_workflow"][workflow_id] = {"total": 0, "completed": 0, "failed": 0}
            
            stats["by_workflow"][workflow_id]["total"] += 1
            
            if instance.status == WorkflowStatus.COMPLETED:
                stats["by_workflow"][workflow_id]["completed"] += 1
            elif instance.status == WorkflowStatus.FAILED:
                stats["by_workflow"][workflow_id]["failed"] += 1
        
        # Calculate success rates
        for workflow_id, data in stats["by_workflow"].items():
            if data["total"] > 0:
                stats["success_rate"][workflow_id] = data["completed"] / data["total"]
        
        return stats


# Pre-defined workflow steps for common operations
class ValidationStep(WorkflowStep):
    """Generic validation step"""
    
    def __init__(self, step_id: str, validator: Callable[[WorkflowContext], bool], error_message: str):
        super().__init__(step_id, "Validation", "Validate workflow context")
        self.validator = validator
        self.error_message = error_message
    
    async def execute(self, context: WorkflowContext) -> StepResult:
        start_time = datetime.utcnow()
        
        try:
            is_valid = await self.validator(context) if asyncio.iscoroutinefunction(self.validator) else self.validator(context)
            
            if not is_valid:
                raise ValidationException(self.error_message)
            
            return StepResult(
                step_id=self.step_id,
                status=StepStatus.COMPLETED,
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )
            
        except Exception as e:
            return StepResult(
                step_id=self.step_id,
                status=StepStatus.FAILED,
                error=str(e),
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )


class DataTransformStep(WorkflowStep):
    """Generic data transformation step"""
    
    def __init__(self, step_id: str, transformer: Callable[[WorkflowContext], Dict[str, Any]]):
        super().__init__(step_id, "Data Transform", "Transform workflow data")
        self.transformer = transformer
    
    async def execute(self, context: WorkflowContext) -> StepResult:
        start_time = datetime.utcnow()
        
        try:
            result_data = await self.transformer(context) if asyncio.iscoroutinefunction(self.transformer) else self.transformer(context)
            
            # Update context with transformed data
            context.data.update(result_data)
            
            return StepResult(
                step_id=self.step_id,
                status=StepStatus.COMPLETED,
                data=result_data,
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )
            
        except Exception as e:
            return StepResult(
                step_id=self.step_id,
                status=StepStatus.FAILED,
                error=str(e),
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )


class NotificationStep(WorkflowStep):
    """Generic notification step"""
    
    def __init__(self, step_id: str, message_template: str, recipients: List[str]):
        super().__init__(step_id, "Notification", "Send notification")
        self.message_template = message_template
        self.recipients = recipients
    
    async def execute(self, context: WorkflowContext) -> StepResult:
        start_time = datetime.utcnow()
        
        try:
            # Format message with context data
            message = self.message_template.format(**context.data, **context.variables)
            
            # TODO: Implement actual notification sending (email, SMS, etc.)
            logger.info(f"Notification sent to {self.recipients}: {message}")
            
            return StepResult(
                step_id=self.step_id,
                status=StepStatus.COMPLETED,
                data={"message": message, "recipients": self.recipients},
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )
            
        except Exception as e:
            return StepResult(
                step_id=self.step_id,
                status=StepStatus.FAILED,
                error=str(e),
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )


# Global workflow engine instance
workflow_engine = WorkflowEngine()