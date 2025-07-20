"""
Encounter service for DiagnoAssist Backend
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.models.encounter import EncounterModel, EncounterStatusEnum, EncounterTypeEnum
from app.models.soap import SOAPModel
from app.models.auth import UserModel
from app.repositories.encounter_repository import encounter_repository
from app.repositories.patient_repository import patient_repository
from app.repositories.episode_repository import episode_repository
from app.services.fhir_sync_service import fhir_sync_service
from app.core.exceptions import NotFoundError, ValidationException
from app.core.business_rules import business_rules_engine, RuleContext, RuleSeverity

logger = logging.getLogger(__name__)


class EncounterService:
    """Service for encounter business logic and operations"""
    
    def __init__(self):
        self.encounter_repo = encounter_repository
        self.patient_repo = patient_repository
        self.episode_repo = episode_repository
        self.fhir_sync = fhir_sync_service
    
    async def create_encounter(
        self, 
        encounter: EncounterModel, 
        user: Optional[UserModel] = None
    ) -> EncounterModel:
        """Create a new encounter with validation"""
        try:
            # Validate patient exists
            patient = await self.patient_repo.get_by_id(encounter.patient_id)
            if not patient:
                raise NotFoundError("Patient", encounter.patient_id)
            
            # Validate episode exists if provided
            if encounter.episode_id:
                episode = await self.episode_repo.get_by_id(encounter.episode_id)
                if not episode:
                    raise NotFoundError("Episode", encounter.episode_id)
                
                # Verify episode belongs to the same patient
                if episode.patient_id != encounter.patient_id:
                    raise ValidationException(
                        "Episode does not belong to the specified patient",
                        {"episode_id": encounter.episode_id, "patient_id": encounter.patient_id}
                    )
            
            # Apply business rules validation
            await business_rules_engine.validate_and_raise(
                encounter, 
                RuleContext.ENCOUNTER_CREATION,
                user=user,
                additional_data={"action": "create_encounter"}
            )
            
            # Create encounter
            created_encounter = await self.encounter_repo.create(encounter)
            
            logger.info(f"Created encounter {created_encounter.id} for patient {encounter.patient_id}")
            
            return created_encounter
            
        except Exception as e:
            logger.error(f"Error creating encounter: {e}")
            raise
    
    async def update_encounter(
        self, 
        encounter_id: str, 
        encounter: EncounterModel,
        user: Optional[UserModel] = None
    ) -> EncounterModel:
        """Update an existing encounter with validation"""
        try:
            # Get existing encounter
            existing = await self.encounter_repo.get_by_id(encounter_id)
            if not existing:
                raise NotFoundError("Encounter", encounter_id)
            
            # Apply business rules validation including state transitions
            await business_rules_engine.validate_and_raise(
                encounter, 
                RuleContext.ENCOUNTER_UPDATE,
                user=user,
                additional_data={
                    "action": "update_encounter",
                    "previous_status": existing.status
                }
            )
            
            # Update encounter
            updated_encounter = await self.encounter_repo.update(encounter_id, encounter)
            
            logger.info(f"Updated encounter {encounter_id}")
            
            return updated_encounter
            
        except Exception as e:
            logger.error(f"Error updating encounter {encounter_id}: {e}")
            raise
    
    async def update_soap(
        self, 
        encounter_id: str, 
        soap_data: SOAPModel
    ) -> EncounterModel:
        """Update SOAP documentation for an encounter"""
        try:
            # Get existing encounter
            encounter = await self.encounter_repo.get_by_id(encounter_id)
            if not encounter:
                raise NotFoundError("Encounter", encounter_id)
            
            # Prevent modifications to signed encounters
            if encounter.status == EncounterStatusEnum.SIGNED:
                raise ValidationException(
                    "Cannot modify SOAP for a signed encounter",
                    {"encounter_id": encounter_id, "status": encounter.status}
                )
            
            # Update SOAP data
            encounter.soap = soap_data
            encounter.updated_at = datetime.utcnow()
            encounter.workflow.last_saved = datetime.utcnow()
            encounter.workflow.version += 1
            
            # Auto-update status to in_progress if it was draft
            if encounter.status == EncounterStatusEnum.DRAFT:
                encounter.status = EncounterStatusEnum.IN_PROGRESS
            
            # Save encounter
            updated_encounter = await self.encounter_repo.update(encounter_id, encounter)
            
            logger.info(f"Updated SOAP for encounter {encounter_id}")
            
            return updated_encounter
            
        except Exception as e:
            logger.error(f"Error updating SOAP for encounter {encounter_id}: {e}")
            raise
    
    async def sign_encounter(
        self, 
        encounter_id: str,
        signed_by: str,
        notes: Optional[str] = None,
        user: Optional[UserModel] = None
    ) -> EncounterModel:
        """Sign an encounter and trigger FHIR synchronization"""
        try:
            # Get existing encounter
            encounter = await self.encounter_repo.get_by_id(encounter_id)
            if not encounter:
                raise NotFoundError("Encounter", encounter_id)
            
            # Create encounter copy for signing validation
            encounter_to_sign = encounter.model_copy()
            encounter_to_sign.status = EncounterStatusEnum.SIGNED
            encounter_to_sign.signed_by = signed_by
            
            # Apply business rules validation for signing
            await business_rules_engine.validate_and_raise(
                encounter_to_sign, 
                RuleContext.ENCOUNTER_SIGNING,
                user=user,
                additional_data={
                    "action": "sign_encounter",
                    "previous_status": encounter.status
                }
            )
            
            # Sign the encounter
            now = datetime.utcnow()
            encounter.status = EncounterStatusEnum.SIGNED
            encounter.signed_at = now
            encounter.signed_by = signed_by
            encounter.updated_at = now
            encounter.workflow.last_saved = now
            encounter.workflow.signed_version = encounter.workflow.version
            
            # Add signing notes if provided
            if notes:
                if not encounter.soap.plan.notes:
                    encounter.soap.plan.notes = notes
                else:
                    encounter.soap.plan.notes += f"\n\nSigning Notes: {notes}"
            
            # Save encounter
            signed_encounter = await self.encounter_repo.update(encounter_id, encounter)
            
            logger.info(f"Signed encounter {encounter_id} by {signed_by}")
            
            # Trigger FHIR synchronization asynchronously
            try:
                sync_response = await self.fhir_sync.auto_sync_on_encounter_sign(encounter_id)
                if sync_response.success:
                    logger.info(f"Successfully synced signed encounter {encounter_id} to FHIR")
                else:
                    logger.warning(f"Failed to sync signed encounter {encounter_id} to FHIR: {sync_response.errors}")
            except Exception as sync_error:
                # Don't fail the signing operation if FHIR sync fails
                logger.error(f"FHIR sync failed for signed encounter {encounter_id}: {sync_error}")
            
            return signed_encounter
            
        except Exception as e:
            logger.error(f"Error signing encounter {encounter_id}: {e}")
            raise
    
    async def cancel_encounter(
        self, 
        encounter_id: str,
        reason: str,
        cancelled_by: str
    ) -> EncounterModel:
        """Cancel an encounter"""
        try:
            # Get existing encounter
            encounter = await self.encounter_repo.get_by_id(encounter_id)
            if not encounter:
                raise NotFoundError("Encounter", encounter_id)
            
            # Prevent cancellation of signed encounters
            if encounter.status == EncounterStatusEnum.SIGNED:
                raise ValidationException(
                    "Cannot cancel a signed encounter",
                    {"encounter_id": encounter_id, "status": encounter.status}
                )
            
            # Cancel the encounter
            now = datetime.utcnow()
            encounter.status = EncounterStatusEnum.CANCELLED
            encounter.updated_at = now
            encounter.workflow.last_saved = now
            
            # Add cancellation notes
            if not encounter.soap.plan.notes:
                encounter.soap.plan.notes = f"Encounter cancelled by {cancelled_by}: {reason}"
            else:
                encounter.soap.plan.notes += f"\n\nEncounter cancelled by {cancelled_by}: {reason}"
            
            # Save encounter
            cancelled_encounter = await self.encounter_repo.update(encounter_id, encounter)
            
            logger.info(f"Cancelled encounter {encounter_id} by {cancelled_by}: {reason}")
            
            return cancelled_encounter
            
        except Exception as e:
            logger.error(f"Error cancelling encounter {encounter_id}: {e}")
            raise
    
    async def delete_encounter(self, encounter_id: str) -> bool:
        """Delete an encounter (only if not signed)"""
        try:
            # Get existing encounter
            encounter = await self.encounter_repo.get_by_id(encounter_id)
            if not encounter:
                raise NotFoundError("Encounter", encounter_id)
            
            # Prevent deletion of signed encounters
            if encounter.status == EncounterStatusEnum.SIGNED:
                raise ValidationException(
                    "Cannot delete a signed encounter",
                    {"encounter_id": encounter_id, "status": encounter.status}
                )
            
            # Delete encounter
            await self.encounter_repo.delete(encounter_id)
            
            logger.info(f"Deleted encounter {encounter_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting encounter {encounter_id}: {e}")
            raise
    
    async def get_encounter_with_validation(self, encounter_id: str) -> EncounterModel:
        """Get an encounter with existence validation"""
        encounter = await self.encounter_repo.get_by_id(encounter_id)
        if not encounter:
            raise NotFoundError("Encounter", encounter_id)
        return encounter
    
    async def get_patient_encounters(
        self, 
        patient_id: str,
        status: Optional[EncounterStatusEnum] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[EncounterModel]:
        """Get all encounters for a patient"""
        # Validate patient exists
        patient = await self.patient_repo.get_by_id(patient_id)
        if not patient:
            raise NotFoundError("Patient", patient_id)
        
        encounters = await self.encounter_repo.get_by_patient(
            patient_id=patient_id,
            status=status,
            skip=skip,
            limit=limit
        )
        
        return encounters
    
    async def get_episode_encounters(
        self, 
        episode_id: str,
        status: Optional[EncounterStatusEnum] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[EncounterModel]:
        """Get all encounters for an episode"""
        # Validate episode exists
        episode = await self.episode_repo.get_by_id(episode_id)
        if not episode:
            raise NotFoundError("Episode", episode_id)
        
        encounters = await self.encounter_repo.get_by_episode(
            episode_id=episode_id,
            status=status,
            skip=skip,
            limit=limit
        )
        
        return encounters
    
    async def validate_encounter_completeness(
        self, 
        encounter_id: str,
        user: Optional[UserModel] = None
    ) -> Dict[str, Any]:
        """Validate encounter documentation completeness using business rules"""
        encounter = await self.get_encounter_with_validation(encounter_id)
        
        # Use business rules engine for validation
        violations = await business_rules_engine.validate(
            encounter, 
            RuleContext.ENCOUNTER_SIGNING,
            user=user,
            additional_data={"action": "validate_completeness"}
        )
        
        # Convert violations to validation result format
        validation_result = {
            "encounter_id": encounter_id,
            "is_complete": True,
            "missing_sections": [],
            "warnings": [],
            "can_be_signed": True,
            "violations": [v.model_dump() for v in violations]
        }
        
        # Process violations
        for violation in violations:
            if violation.severity == RuleSeverity.ERROR or violation.severity == RuleSeverity.CRITICAL:
                validation_result["can_be_signed"] = False
                validation_result["is_complete"] = False
                # Extract field name for missing_sections
                if "chief complaint" in violation.message.lower():
                    validation_result["missing_sections"].append("Chief Complaint")
                elif "primary diagnosis" in violation.message.lower():
                    validation_result["missing_sections"].append("Primary Diagnosis")
                else:
                    validation_result["missing_sections"].append(violation.message)
            elif violation.severity == RuleSeverity.WARNING:
                validation_result["warnings"].append(violation.message)
        
        return validation_result
    
    async def get_encounter_statistics(self) -> Dict[str, Any]:
        """Get encounter statistics"""
        try:
            # Get counts by status
            total_encounters = await self.encounter_repo.count()
            
            stats = {
                "total_encounters": total_encounters,
                "by_status": {},
                "by_type": {},
                "recent_activity": {
                    "last_24h": 0,
                    "last_week": 0
                }
            }
            
            # Count by status
            for status in EncounterStatusEnum:
                count = await self.encounter_repo.count_by_status(status)
                stats["by_status"][status.value] = count
            
            # Count by type
            for encounter_type in EncounterTypeEnum:
                count = await self.encounter_repo.count_by_type(encounter_type)
                stats["by_type"][encounter_type.value] = count
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting encounter statistics: {e}")
            return {
                "total_encounters": 0,
                "by_status": {},
                "by_type": {},
                "recent_activity": {"last_24h": 0, "last_week": 0},
                "error": str(e)
            }


# Create service instance
encounter_service = EncounterService()