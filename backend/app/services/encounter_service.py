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
from app.services.ai_service import ai_service
from app.models.ai_models import DocumentationCompletionRequest, ClinicalInsights
from app.core.websocket_manager import websocket_manager, MessageType

logger = logging.getLogger(__name__)


class EncounterService:
    """Service for encounter business logic and operations"""
    
    def __init__(self):
        self.encounter_repo = encounter_repository
        self.patient_repo = patient_repository
        self.episode_repo = episode_repository
        self.fhir_sync = fhir_sync_service
    
    async def _broadcast_encounter_update(
        self,
        encounter_id: str,
        update_type: str,
        data: Dict[str, Any],
        user: Optional[UserModel] = None,
        exclude_user: bool = True
    ):
        """Broadcast encounter update to connected clients"""
        try:
            message = {
                "type": MessageType.ENCOUNTER_UPDATE.value,
                "encounter_id": encounter_id,
                "update_type": update_type,
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if user:
                message["user"] = {
                    "id": user.id,
                    "name": user.name,
                    "role": user.role.value
                }
            
            exclude_connection = f"encounter_{encounter_id}_{user.id}" if (user and exclude_user) else None
            
            await websocket_manager.broadcast_to_resource(
                encounter_id,
                message,
                exclude_connection=exclude_connection
            )
            
        except Exception as e:
            logger.warning(f"Failed to broadcast encounter update: {e}")
    
    async def _broadcast_status_update(
        self,
        encounter_id: str,
        status: EncounterStatusEnum,
        message: str,
        user: Optional[UserModel] = None
    ):
        """Broadcast status update to connected clients"""
        try:
            update_message = {
                "type": MessageType.STATUS_UPDATE.value,
                "encounter_id": encounter_id,
                "status": status.value,
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if user:
                update_message["user"] = {
                    "id": user.id,
                    "name": user.name,
                    "role": user.role.value
                }
            
            await websocket_manager.broadcast_to_resource(encounter_id, update_message)
            
        except Exception as e:
            logger.warning(f"Failed to broadcast status update: {e}")
    
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
        soap_data: SOAPModel,
        user: Optional[UserModel] = None
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
            
            # Store old status for comparison
            old_status = encounter.status
            
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
            
            # Broadcast SOAP update to connected clients
            await self._broadcast_encounter_update(
                encounter_id,
                "soap_updated",
                {
                    "soap": soap_data.model_dump(),
                    "version": encounter.workflow.version,
                    "last_saved": encounter.workflow.last_saved.isoformat()
                },
                user
            )
            
            # Broadcast status change if it occurred
            if old_status != encounter.status:
                await self._broadcast_status_update(
                    encounter_id,
                    encounter.status,
                    f"Encounter status changed from {old_status.value} to {encounter.status.value}",
                    user
                )
            
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
            
            # Broadcast encounter signing to connected clients
            await self._broadcast_encounter_update(
                encounter_id,
                "encounter_signed",
                {
                    "signed_by": signed_by,
                    "signed_at": encounter.signed_at.isoformat(),
                    "version": encounter.workflow.signed_version,
                    "notes": notes
                },
                user
            )
            
            # Broadcast status update
            await self._broadcast_status_update(
                encounter_id,
                EncounterStatusEnum.SIGNED,
                f"Encounter signed by {signed_by}",
                user
            )
            
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
        cancelled_by: str,
        user: Optional[UserModel] = None
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
            
            # Broadcast encounter cancellation to connected clients
            await self._broadcast_encounter_update(
                encounter_id,
                "encounter_cancelled",
                {
                    "cancelled_by": cancelled_by,
                    "reason": reason,
                    "cancelled_at": now.isoformat()
                },
                user
            )
            
            # Broadcast status update
            await self._broadcast_status_update(
                encounter_id,
                EncounterStatusEnum.CANCELLED,
                f"Encounter cancelled by {cancelled_by}: {reason}",
                user
            )
            
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
    
    async def generate_ai_documentation_suggestions(
        self,
        encounter_id: str,
        user: Optional[UserModel] = None
    ) -> Dict[str, Any]:
        """
        Generate AI-powered documentation suggestions for encounter
        
        Args:
            encounter_id: ID of the encounter
            user: User requesting suggestions
            
        Returns:
            AI-generated documentation suggestions and completions
        """
        try:
            # Get encounter and patient
            encounter = await self.get_encounter(encounter_id, user)
            patient = await self.patient_repo.get_by_id(encounter.patient_id)
            
            if not patient:
                raise NotFoundError("Patient", encounter.patient_id)
            
            # Build current content from SOAP
            current_content = {}
            if encounter.soap:
                if encounter.soap.subjective:
                    current_content["subjective"] = encounter.soap.subjective.model_dump(exclude_none=True)
                if encounter.soap.objective:
                    current_content["objective"] = encounter.soap.objective.model_dump(exclude_none=True)
                if encounter.soap.assessment:
                    current_content["assessment"] = encounter.soap.assessment.model_dump(exclude_none=True)
                if encounter.soap.plan:
                    current_content["plan"] = encounter.soap.plan.model_dump(exclude_none=True)
            
            # Create documentation completion request
            completion_request = DocumentationCompletionRequest(
                encounter_id=encounter_id,
                current_content=current_content,
                patient_context={
                    "patient_id": patient.id,
                    "demographics": patient.demographics.model_dump() if patient.demographics else None,
                    "medical_background": patient.medical_background.model_dump() if patient.medical_background else None
                }
            )
            
            # Get AI suggestions
            completion_response = await ai_service.complete_documentation(completion_request, patient)
            
            logger.info(f"AI documentation suggestions generated for encounter {encounter_id}")
            
            return {
                "suggestions": [sugg.model_dump() for sugg in completion_response.suggestions],
                "completed_sections": completion_response.completed_sections,
                "quality_score": completion_response.quality_score,
                "missing_elements": completion_response.missing_elements,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating AI documentation suggestions: {e}")
            raise
    
    async def generate_clinical_insights(
        self,
        encounter_id: str,
        user: Optional[UserModel] = None
    ) -> ClinicalInsights:
        """
        Generate AI-powered clinical insights for encounter
        
        Args:
            encounter_id: ID of the encounter
            user: User requesting insights
            
        Returns:
            Clinical insights including diagnoses, treatments, and risk assessments
        """
        try:
            # Get encounter and patient
            encounter = await self.get_encounter(encounter_id, user)
            patient = await self.patient_repo.get_by_id(encounter.patient_id)
            
            if not patient:
                raise NotFoundError("Patient", encounter.patient_id)
            
            # Generate clinical insights
            insights = await ai_service.generate_clinical_insights(patient, encounter)
            
            logger.info(f"Clinical insights generated for encounter {encounter_id}")
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating clinical insights: {e}")
            raise
    
    async def apply_ai_suggestions_to_soap(
        self,
        encounter_id: str,
        suggestions: List[Dict[str, Any]],
        user: Optional[UserModel] = None
    ) -> EncounterModel:
        """
        Apply AI-generated suggestions to encounter SOAP documentation
        
        Args:
            encounter_id: ID of the encounter
            suggestions: List of AI suggestions to apply
            user: User applying suggestions
            
        Returns:
            Updated encounter with applied suggestions
        """
        try:
            encounter = await self.get_encounter(encounter_id, user)
            
            # Only allow applying suggestions to draft encounters
            if encounter.status not in [EncounterStatusEnum.DRAFT, EncounterStatusEnum.IN_PROGRESS]:
                raise ValidationException("Cannot apply AI suggestions to signed encounters")
            
            # Apply business rules validation
            await business_rules_engine.validate_and_raise(
                encounter, 
                RuleContext.ENCOUNTER_MODIFICATION,
                user=user,
                additional_data={
                    "action": "apply_ai_suggestions",
                    "suggestion_count": len(suggestions)
                }
            )
            
            # Initialize SOAP if not exists
            if not encounter.soap:
                encounter.soap = SOAPModel()
            
            # Apply suggestions to appropriate SOAP sections
            for suggestion in suggestions:
                section = suggestion.get("section", "").lower()
                field = suggestion.get("field", "")
                content = suggestion.get("suggestion", "")
                confidence = suggestion.get("confidence", "medium")
                
                # Only apply high and medium confidence suggestions
                if confidence in ["high", "medium"] and content:
                    if section == "subjective" and encounter.soap.subjective:
                        if field == "chief_complaint" and not encounter.soap.subjective.chief_complaint:
                            encounter.soap.subjective.chief_complaint = content
                        elif field == "history_present_illness" and not encounter.soap.subjective.history_present_illness:
                            encounter.soap.subjective.history_present_illness = content
                    
                    elif section == "objective" and encounter.soap.objective:
                        if field == "physical_examination" and not encounter.soap.objective.physical_examination:
                            encounter.soap.objective.physical_examination = content
                    
                    elif section == "assessment" and encounter.soap.assessment:
                        if field == "primary_diagnosis" and not encounter.soap.assessment.primary_diagnosis:
                            encounter.soap.assessment.primary_diagnosis = content
                        elif field == "differential_diagnoses" and not encounter.soap.assessment.differential_diagnoses:
                            encounter.soap.assessment.differential_diagnoses = [content]
                    
                    elif section == "plan" and encounter.soap.plan:
                        if field == "treatment_plan" and not encounter.soap.plan.treatment_plan:
                            encounter.soap.plan.treatment_plan = content
            
            # Add AI consultation metadata
            if not encounter.ai_consultation:
                encounter.ai_consultation = {}
            
            encounter.ai_consultation.setdefault("suggestions_applied", []).extend([
                {
                    "applied_at": datetime.utcnow().isoformat(),
                    "applied_by": user.id if user else None,
                    "suggestion_count": len(suggestions)
                }
            ])
            
            # Update encounter
            updated_encounter = await self.encounter_repo.update(encounter_id, encounter)
            
            logger.info(f"Applied {len(suggestions)} AI suggestions to encounter {encounter_id}")
            
            return updated_encounter
            
        except Exception as e:
            logger.error(f"Error applying AI suggestions: {e}")
            raise
    
    async def get_ai_consultation_history(
        self,
        encounter_id: str,
        user: Optional[UserModel] = None
    ) -> Dict[str, Any]:
        """
        Get AI consultation history for encounter
        
        Args:
            encounter_id: ID of the encounter
            user: User requesting history
            
        Returns:
            AI consultation history and metadata
        """
        try:
            encounter = await self.get_encounter(encounter_id, user)
            
            ai_history = {
                "encounter_id": encounter_id,
                "ai_consultation": encounter.ai_consultation or {},
                "suggestions_applied": [],
                "insights_generated": [],
                "voice_processing": []
            }
            
            # Extract AI activity from consultation data
            if encounter.ai_consultation:
                ai_history["suggestions_applied"] = encounter.ai_consultation.get("suggestions_applied", [])
                ai_history["insights_generated"] = encounter.ai_consultation.get("insights_generated", [])
                ai_history["voice_processing"] = encounter.ai_consultation.get("voice_processing", [])
            
            return ai_history
            
        except Exception as e:
            logger.error(f"Error getting AI consultation history: {e}")
            raise


# Create service instance
encounter_service = EncounterService()