"""
Predefined Medical Workflows for DiagnoAssist Backend

This module contains specific workflow implementations for common medical processes.
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from app.core.workflow_engine import (
    WorkflowStep, WorkflowDefinition, WorkflowContext, StepResult, StepStatus,
    workflow_engine, WorkflowPriority
)
from app.models.patient import PatientModel
from app.models.encounter import EncounterModel, EncounterStatusEnum
from app.models.episode import EpisodeModel
from app.models.auth import UserModel
from app.repositories.patient_repository import patient_repository
from app.repositories.encounter_repository import encounter_repository
from app.repositories.episode_repository import episode_repository
from app.services.fhir_sync_service import fhir_sync_service
from app.core.business_rules import business_rules_engine, RuleContext
from app.core.exceptions import ValidationException, NotFoundError
import logging

logger = logging.getLogger(__name__)


# Patient Registration Workflow Steps
class PatientValidationStep(WorkflowStep):
    """Validate patient data before registration"""
    
    def __init__(self):
        super().__init__(
            step_id="patient.validate",
            name="Patient Data Validation",
            description="Validate patient demographic and medical information"
        )
    
    async def execute(self, context: WorkflowContext) -> StepResult:
        start_time = datetime.utcnow()
        
        try:
            patient_data = context.data.get("patient")
            if not patient_data:
                raise ValidationException("Patient data is required")
            
            # Convert dict to PatientModel if needed
            if isinstance(patient_data, dict):
                patient = PatientModel(**patient_data)
            else:
                patient = patient_data
            
            # Use business rules for validation
            violations = await business_rules_engine.validate(
                patient,
                RuleContext.PATIENT_REGISTRATION,
                user=context.user,
                additional_data={"action": "register_patient"}
            )
            
            # Check for blocking violations
            blocking_violations = [
                v for v in violations 
                if v.severity.value in ["error", "critical"]
            ]
            
            if blocking_violations:
                raise ValidationException(f"Patient validation failed: {[v.message for v in blocking_violations]}")
            
            # Store validated patient in context
            context.data["validated_patient"] = patient
            context.variables["validation_warnings"] = [v.message for v in violations if v.severity.value == "warning"]
            
            return StepResult(
                step_id=self.step_id,
                status=StepStatus.COMPLETED,
                data={"violations": len(violations), "warnings": len(context.variables["validation_warnings"])},
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )
            
        except Exception as e:
            return StepResult(
                step_id=self.step_id,
                status=StepStatus.FAILED,
                error=str(e),
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )


class PatientDuplicateCheckStep(WorkflowStep):
    """Check for duplicate patients"""
    
    def __init__(self):
        super().__init__(
            step_id="patient.duplicate_check",
            name="Duplicate Patient Check",
            description="Check for existing patients with same demographics"
        )
    
    async def execute(self, context: WorkflowContext) -> StepResult:
        start_time = datetime.utcnow()
        
        try:
            patient = context.data.get("validated_patient")
            if not patient:
                raise ValidationException("Validated patient data is required")
            
            # Check for duplicate by email
            existing_patient = None
            if patient.demographics.email:
                existing_patient = await patient_repository.get_by_email(patient.demographics.email)
            
            if existing_patient:
                # Store duplicate information
                context.data["duplicate_found"] = True
                context.data["existing_patient_id"] = existing_patient.id
                context.variables["duplicate_message"] = f"Patient with email {patient.demographics.email} already exists"
                
                # Decide whether to proceed or merge
                merge_policy = context.data.get("merge_policy", "fail")
                if merge_policy == "fail":
                    raise ValidationException(f"Duplicate patient found: {existing_patient.id}")
                elif merge_policy == "merge":
                    context.variables["action"] = "merge"
                elif merge_policy == "create_anyway":
                    context.variables["action"] = "create"
            else:
                context.data["duplicate_found"] = False
                context.variables["action"] = "create"
            
            return StepResult(
                step_id=self.step_id,
                status=StepStatus.COMPLETED,
                data={"duplicate_found": context.data["duplicate_found"], "action": context.variables["action"]},
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )
            
        except Exception as e:
            return StepResult(
                step_id=self.step_id,
                status=StepStatus.FAILED,
                error=str(e),
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )


class PatientCreationStep(WorkflowStep):
    """Create patient in database"""
    
    def __init__(self):
        super().__init__(
            step_id="patient.create",
            name="Patient Creation",
            description="Create patient record in database"
        )
    
    async def can_execute(self, context: WorkflowContext) -> bool:
        """Only execute if action is to create patient"""
        return context.variables.get("action") in ["create", "create_anyway"]
    
    async def execute(self, context: WorkflowContext) -> StepResult:
        start_time = datetime.utcnow()
        
        try:
            patient = context.data.get("validated_patient")
            if not patient:
                raise ValidationException("Validated patient data is required")
            
            # Create patient in database
            created_patient = await patient_repository.create(patient)
            
            # Store created patient
            context.data["created_patient"] = created_patient
            context.data["patient_id"] = created_patient.id
            
            logger.info(f"Created patient {created_patient.id}: {patient.demographics.name}")
            
            return StepResult(
                step_id=self.step_id,
                status=StepStatus.COMPLETED,
                data={"patient_id": created_patient.id, "patient_name": patient.demographics.name},
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )
            
        except Exception as e:
            return StepResult(
                step_id=self.step_id,
                status=StepStatus.FAILED,
                error=str(e),
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )


class PatientFHIRSyncStep(WorkflowStep):
    """Sync patient to FHIR server"""
    
    def __init__(self):
        super().__init__(
            step_id="patient.fhir_sync",
            name="FHIR Synchronization",
            description="Synchronize patient data with FHIR server",
            retryable=True,
            max_retries=3
        )
    
    async def execute(self, context: WorkflowContext) -> StepResult:
        start_time = datetime.utcnow()
        
        try:
            patient = context.data.get("created_patient")
            if not patient:
                # Try to get from validated patient if creation was skipped
                patient = context.data.get("validated_patient")
            
            if not patient:
                raise ValidationException("Patient data is required for FHIR sync")
            
            # Sync with FHIR server
            sync_response = await fhir_sync_service.sync_patient(patient)
            
            if sync_response.success:
                context.data["fhir_id"] = sync_response.fhir_id
                context.variables["fhir_sync_success"] = True
                
                return StepResult(
                    step_id=self.step_id,
                    status=StepStatus.COMPLETED,
                    data={"fhir_id": sync_response.fhir_id},
                    execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
                )
            else:
                raise ValidationException(f"FHIR sync failed: {sync_response.errors}")
            
        except Exception as e:
            return StepResult(
                step_id=self.step_id,
                status=StepStatus.FAILED,
                error=str(e),
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )
    
    async def on_failure(self, context: WorkflowContext, error: Exception) -> bool:
        """Allow workflow to continue even if FHIR sync fails"""
        logger.warning(f"FHIR sync failed, continuing workflow: {error}")
        context.variables["fhir_sync_success"] = False
        context.variables["fhir_sync_error"] = str(error)
        return False  # Don't retry, continue workflow


# Encounter Documentation Workflow Steps
class EncounterCreationStep(WorkflowStep):
    """Create encounter record"""
    
    def __init__(self):
        super().__init__(
            step_id="encounter.create",
            name="Encounter Creation",
            description="Create encounter record in database"
        )
    
    async def execute(self, context: WorkflowContext) -> StepResult:
        start_time = datetime.utcnow()
        
        try:
            encounter_data = context.data.get("encounter")
            if not encounter_data:
                raise ValidationException("Encounter data is required")
            
            # Convert dict to EncounterModel if needed
            if isinstance(encounter_data, dict):
                encounter = EncounterModel(**encounter_data)
            else:
                encounter = encounter_data
            
            # Validate encounter using business rules
            await business_rules_engine.validate_and_raise(
                encounter,
                RuleContext.ENCOUNTER_CREATION,
                user=context.user,
                additional_data={"action": "create_encounter"}
            )
            
            # Create encounter
            created_encounter = await encounter_repository.create(encounter)
            
            # Store in context
            context.data["created_encounter"] = created_encounter
            context.data["encounter_id"] = created_encounter.id
            
            logger.info(f"Created encounter {created_encounter.id} for patient {encounter.patient_id}")
            
            return StepResult(
                step_id=self.step_id,
                status=StepStatus.COMPLETED,
                data={"encounter_id": created_encounter.id},
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )
            
        except Exception as e:
            return StepResult(
                step_id=self.step_id,
                status=StepStatus.FAILED,
                error=str(e),
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )


class EncounterValidationStep(WorkflowStep):
    """Validate encounter completeness before signing"""
    
    def __init__(self):
        super().__init__(
            step_id="encounter.validate",
            name="Encounter Validation",
            description="Validate encounter documentation completeness"
        )
    
    async def execute(self, context: WorkflowContext) -> StepResult:
        start_time = datetime.utcnow()
        
        try:
            encounter = context.data.get("encounter")
            if not encounter:
                raise ValidationException("Encounter data is required")
            
            # Use business rules for validation
            violations = await business_rules_engine.validate(
                encounter,
                RuleContext.ENCOUNTER_SIGNING,
                user=context.user,
                additional_data={"action": "validate_completeness"}
            )
            
            # Check for blocking violations
            blocking_violations = [
                v for v in violations 
                if v.severity.value in ["error", "critical"]
            ]
            
            if blocking_violations:
                context.variables["can_sign"] = False
                context.variables["validation_errors"] = [v.message for v in blocking_violations]
                
                return StepResult(
                    step_id=self.step_id,
                    status=StepStatus.COMPLETED,
                    data={"can_sign": False, "errors": len(blocking_violations)},
                    execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
                )
            else:
                context.variables["can_sign"] = True
                context.variables["validation_warnings"] = [v.message for v in violations if v.severity.value == "warning"]
                
                return StepResult(
                    step_id=self.step_id,
                    status=StepStatus.COMPLETED,
                    data={"can_sign": True, "warnings": len(context.variables["validation_warnings"])},
                    execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
                )
            
        except Exception as e:
            return StepResult(
                step_id=self.step_id,
                status=StepStatus.FAILED,
                error=str(e),
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )


class EncounterSigningStep(WorkflowStep):
    """Sign encounter if validation passes"""
    
    def __init__(self):
        super().__init__(
            step_id="encounter.sign",
            name="Encounter Signing",
            description="Sign encounter after validation"
        )
    
    async def can_execute(self, context: WorkflowContext) -> bool:
        """Only execute if encounter can be signed"""
        return context.variables.get("can_sign", False)
    
    async def execute(self, context: WorkflowContext) -> StepResult:
        start_time = datetime.utcnow()
        
        try:
            encounter = context.data.get("encounter")
            encounter_id = context.data.get("encounter_id")
            
            if not encounter and not encounter_id:
                raise ValidationException("Encounter or encounter ID is required")
            
            if encounter_id and not encounter:
                # Fetch encounter from database
                encounter = await encounter_repository.get_by_id(encounter_id)
                if not encounter:
                    raise NotFoundError("Encounter", encounter_id)
            
            # Update encounter status
            encounter.status = EncounterStatusEnum.SIGNED
            encounter.signed_at = datetime.utcnow()
            encounter.signed_by = context.user.id if context.user else "system"
            
            # Save encounter
            signed_encounter = await encounter_repository.update(encounter.id, encounter)
            
            # Store signed encounter
            context.data["signed_encounter"] = signed_encounter
            
            logger.info(f"Signed encounter {encounter.id}")
            
            return StepResult(
                step_id=self.step_id,
                status=StepStatus.COMPLETED,
                data={"encounter_id": encounter.id, "signed_at": encounter.signed_at.isoformat()},
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )
            
        except Exception as e:
            return StepResult(
                step_id=self.step_id,
                status=StepStatus.FAILED,
                error=str(e),
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )


class EncounterFHIRSyncStep(WorkflowStep):
    """Sync signed encounter to FHIR"""
    
    def __init__(self):
        super().__init__(
            step_id="encounter.fhir_sync",
            name="Encounter FHIR Sync",
            description="Sync signed encounter to FHIR server",
            retryable=True,
            max_retries=3
        )
    
    async def execute(self, context: WorkflowContext) -> StepResult:
        start_time = datetime.utcnow()
        
        try:
            encounter_id = context.data.get("encounter_id")
            if not encounter_id:
                raise ValidationException("Encounter ID is required")
            
            # Trigger FHIR sync
            sync_response = await fhir_sync_service.auto_sync_on_encounter_sign(encounter_id)
            
            if sync_response.success:
                context.data["encounter_fhir_id"] = sync_response.fhir_id
                
                return StepResult(
                    step_id=self.step_id,
                    status=StepStatus.COMPLETED,
                    data={"fhir_id": sync_response.fhir_id},
                    execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
                )
            else:
                raise ValidationException(f"Encounter FHIR sync failed: {sync_response.errors}")
            
        except Exception as e:
            return StepResult(
                step_id=self.step_id,
                status=StepStatus.FAILED,
                error=str(e),
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )


def register_medical_workflows():
    """Register all predefined medical workflows"""
    
    # Register workflow steps
    workflow_engine.register_step(PatientValidationStep())
    workflow_engine.register_step(PatientDuplicateCheckStep())
    workflow_engine.register_step(PatientCreationStep())
    workflow_engine.register_step(PatientFHIRSyncStep())
    workflow_engine.register_step(EncounterCreationStep())
    workflow_engine.register_step(EncounterValidationStep())
    workflow_engine.register_step(EncounterSigningStep())
    workflow_engine.register_step(EncounterFHIRSyncStep())
    
    # Patient Registration Workflow
    patient_registration_workflow = WorkflowDefinition(
        workflow_id="patient.registration",
        name="Patient Registration Workflow",
        description="Complete patient registration process with validation and FHIR sync",
        version="1.0",
        steps=[
            "patient.validate",
            "patient.duplicate_check", 
            "patient.create",
            "patient.fhir_sync"
        ],
        dependencies={
            "patient.duplicate_check": ["patient.validate"],
            "patient.create": ["patient.duplicate_check"],
            "patient.fhir_sync": ["patient.create"]
        },
        timeout_seconds=300,  # 5 minutes
        default_priority=WorkflowPriority.NORMAL
    )
    
    workflow_engine.register_workflow(patient_registration_workflow)
    
    # Encounter Documentation Workflow
    encounter_documentation_workflow = WorkflowDefinition(
        workflow_id="encounter.documentation",
        name="Encounter Documentation Workflow",
        description="Create encounter and handle documentation validation",
        version="1.0",
        steps=[
            "encounter.create",
            "encounter.validate",
            "encounter.sign",
            "encounter.fhir_sync"
        ],
        dependencies={
            "encounter.validate": ["encounter.create"],
            "encounter.sign": ["encounter.validate"],
            "encounter.fhir_sync": ["encounter.sign"]
        },
        timeout_seconds=600,  # 10 minutes
        default_priority=WorkflowPriority.HIGH
    )
    
    workflow_engine.register_workflow(encounter_documentation_workflow)
    
    # Encounter Signing Workflow (for existing encounters)
    encounter_signing_workflow = WorkflowDefinition(
        workflow_id="encounter.signing",
        name="Encounter Signing Workflow",
        description="Validate and sign existing encounter",
        version="1.0",
        steps=[
            "encounter.validate",
            "encounter.sign",
            "encounter.fhir_sync"
        ],
        dependencies={
            "encounter.sign": ["encounter.validate"],
            "encounter.fhir_sync": ["encounter.sign"]
        },
        timeout_seconds=300,  # 5 minutes
        default_priority=WorkflowPriority.HIGH
    )
    
    workflow_engine.register_workflow(encounter_signing_workflow)
    
    logger.info("Registered medical workflows successfully")


# Initialize workflows on module import
register_medical_workflows()