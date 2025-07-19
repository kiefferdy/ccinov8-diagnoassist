"""
Encounter repository for DiagnoAssist Backend
"""
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.repositories.base_repository import BaseRepository
from app.models.encounter import (
    EncounterModel, EncounterTypeEnum, EncounterStatusEnum, 
    ProviderInfo, AIConsultation, WorkflowInfo
)
from app.models.soap import SOAPModel
from app.core.exceptions import DatabaseException


class EncounterRepository(BaseRepository[EncounterModel]):
    """Repository for Encounter entities"""
    
    def __init__(self):
        super().__init__("encounters")
        self._id_counter = 1
    
    def _to_dict(self, encounter: EncounterModel) -> Dict[str, Any]:
        """Convert EncounterModel to dictionary for MongoDB storage"""
        return {
            "id": encounter.id,
            "episode_id": encounter.episode_id,
            "patient_id": encounter.patient_id,
            "type": encounter.type.value,
            "status": encounter.status.value,
            "provider": {
                "id": encounter.provider.id,
                "name": encounter.provider.name,
                "role": encounter.provider.role,
                "specialty": encounter.provider.specialty,
                "license_number": encounter.provider.license_number
            },
            "soap": self._soap_to_dict(encounter.soap) if encounter.soap else None,
            "ai_consultation": {
                "voice_processing": encounter.ai_consultation.voice_processing,
                "chat_history": encounter.ai_consultation.chat_history,
                "insights": encounter.ai_consultation.insights,
                "differential_diagnoses": encounter.ai_consultation.differential_diagnoses,
                "recommendations": encounter.ai_consultation.recommendations,
                "last_ai_interaction": encounter.ai_consultation.last_ai_interaction
            },
            "workflow": {
                "auto_save_enabled": encounter.workflow.auto_save_enabled,
                "last_saved": encounter.workflow.last_saved,
                "last_modified_by": encounter.workflow.last_modified_by,
                "amendments": encounter.workflow.amendments,
                "version": encounter.workflow.version,
                "signed_version": encounter.workflow.signed_version
            },
            "fhir_encounter_id": encounter.fhir_encounter_id,
            "created_at": encounter.created_at,
            "updated_at": encounter.updated_at,
            "signed_at": encounter.signed_at,
            "signed_by": encounter.signed_by
        }
    
    def _soap_to_dict(self, soap: SOAPModel) -> Dict[str, Any]:
        """Convert SOAP model to dictionary"""
        if not soap:
            return None
        
        return {
            "subjective": self._subjective_to_dict(soap.subjective) if soap.subjective else None,
            "objective": self._objective_to_dict(soap.objective) if soap.objective else None,
            "assessment": self._assessment_to_dict(soap.assessment) if soap.assessment else None,
            "plan": self._plan_to_dict(soap.plan) if soap.plan else None,
            "overall_completion_percentage": soap.overall_completion_percentage,
            "last_updated": soap.last_updated
        }
    
    def _subjective_to_dict(self, subjective) -> Dict[str, Any]:
        """Convert subjective section to dictionary"""
        return {
            "chief_complaint": subjective.chief_complaint,
            "history_of_present_illness": subjective.history_of_present_illness,
            "symptoms": [
                {
                    "name": symptom.name,
                    "duration": symptom.duration,
                    "severity": symptom.severity.value if symptom.severity else None,
                    "description": symptom.description,
                    "associated_factors": symptom.associated_factors,
                    "alleviating_factors": symptom.alleviating_factors,
                    "aggravating_factors": symptom.aggravating_factors
                } for symptom in subjective.symptoms
            ],
            "review_of_systems": subjective.review_of_systems.dict() if subjective.review_of_systems else None,
            "social_history": subjective.social_history,
            "family_history": subjective.family_history,
            "past_medical_history": subjective.past_medical_history,
            "medications": subjective.medications,
            "allergies": subjective.allergies,
            "last_updated": subjective.last_updated,
            "completion_percentage": subjective.completion_percentage
        }
    
    def _objective_to_dict(self, objective) -> Dict[str, Any]:
        """Convert objective section to dictionary"""
        return {
            "vital_signs": objective.vital_signs.dict() if objective.vital_signs else None,
            "physical_exam": objective.physical_exam.dict() if objective.physical_exam else None,
            "lab_results": [result.dict() for result in objective.lab_results],
            "imaging_results": objective.imaging_results,
            "other_tests": objective.other_tests,
            "last_updated": objective.last_updated,
            "completion_percentage": objective.completion_percentage
        }
    
    def _assessment_to_dict(self, assessment) -> Dict[str, Any]:
        """Convert assessment section to dictionary"""
        return {
            "primary_diagnosis": assessment.primary_diagnosis.dict() if assessment.primary_diagnosis else None,
            "secondary_diagnoses": [diag.dict() for diag in assessment.secondary_diagnoses],
            "differential_diagnoses": [diag.dict() for diag in assessment.differential_diagnoses],
            "clinical_impression": assessment.clinical_impression,
            "prognosis": assessment.prognosis,
            "risk_factors": assessment.risk_factors,
            "last_updated": assessment.last_updated,
            "completion_percentage": assessment.completion_percentage
        }
    
    def _plan_to_dict(self, plan) -> Dict[str, Any]:
        """Convert plan section to dictionary"""
        return {
            "medications": [med.dict() for med in plan.medications],
            "procedures": [proc.dict() for proc in plan.procedures],
            "diagnostic_tests": plan.diagnostic_tests,
            "follow_up": plan.follow_up.dict() if plan.follow_up else None,
            "patient_education": plan.patient_education,
            "lifestyle_modifications": plan.lifestyle_modifications,
            "referrals": plan.referrals,
            "other_interventions": plan.other_interventions,
            "last_updated": plan.last_updated,
            "completion_percentage": plan.completion_percentage
        }
    
    def _from_dict(self, data: Dict[str, Any]) -> EncounterModel:
        """Convert dictionary from MongoDB to EncounterModel"""
        # Parse provider
        provider_data = data.get("provider", {})
        provider = ProviderInfo(
            id=provider_data.get("id", ""),
            name=provider_data.get("name", ""),
            role=provider_data.get("role", ""),
            specialty=provider_data.get("specialty"),
            license_number=provider_data.get("license_number")
        )
        
        # Parse SOAP (simplified for Phase 3)
        soap_data = data.get("soap")
        soap = None
        if soap_data:
            # For now, store as SOAPModel() - will be enhanced in later phases
            soap = SOAPModel()
        
        # Parse AI consultation
        ai_data = data.get("ai_consultation", {})
        ai_consultation = AIConsultation(
            voice_processing=ai_data.get("voice_processing", []),
            chat_history=ai_data.get("chat_history", []),
            insights=ai_data.get("insights", []),
            differential_diagnoses=ai_data.get("differential_diagnoses", []),
            recommendations=ai_data.get("recommendations", []),
            last_ai_interaction=ai_data.get("last_ai_interaction")
        )
        
        # Parse workflow
        workflow_data = data.get("workflow", {})
        workflow = WorkflowInfo(
            auto_save_enabled=workflow_data.get("auto_save_enabled", True),
            last_saved=workflow_data.get("last_saved"),
            last_modified_by=workflow_data.get("last_modified_by"),
            amendments=workflow_data.get("amendments", []),
            version=workflow_data.get("version", 1),
            signed_version=workflow_data.get("signed_version")
        )
        
        return EncounterModel(
            id=data.get("id"),
            episode_id=data.get("episode_id", ""),
            patient_id=data.get("patient_id", ""),
            type=EncounterTypeEnum(data.get("type", "routine")),
            status=EncounterStatusEnum(data.get("status", "draft")),
            provider=provider,
            soap=soap,
            ai_consultation=ai_consultation,
            workflow=workflow,
            fhir_encounter_id=data.get("fhir_encounter_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            signed_at=data.get("signed_at"),
            signed_by=data.get("signed_by")
        )
    
    def _get_entity_name(self) -> str:
        """Get entity name for error messages"""
        return "Encounter"
    
    def _generate_id(self) -> str:
        """Generate unique encounter ID"""
        encounter_id = f"ENC{self._id_counter:03d}"
        self._id_counter += 1
        return encounter_id
    
    async def get_by_episode_id(
        self,
        episode_id: str,
        status: Optional[EncounterStatusEnum] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[EncounterModel]:
        """Get encounters for a specific episode"""
        try:
            filter_dict = {"episode_id": episode_id}
            
            if status:
                filter_dict["status"] = status.value
            
            return await self.get_all(
                filter_dict=filter_dict,
                skip=skip,
                limit=limit,
                sort_field="created_at",
                sort_direction=-1
            )
            
        except Exception as e:
            raise DatabaseException(
                f"Database error while retrieving encounters for episode {episode_id}: {str(e)}",
                "read"
            )
    
    async def get_by_patient_id(
        self,
        patient_id: str,
        status: Optional[EncounterStatusEnum] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[EncounterModel]:
        """Get encounters for a specific patient"""
        try:
            filter_dict = {"patient_id": patient_id}
            
            if status:
                filter_dict["status"] = status.value
            
            return await self.get_all(
                filter_dict=filter_dict,
                skip=skip,
                limit=limit,
                sort_field="created_at",
                sort_direction=-1
            )
            
        except Exception as e:
            raise DatabaseException(
                f"Database error while retrieving encounters for patient {patient_id}: {str(e)}",
                "read"
            )
    
    async def get_by_provider_id(
        self,
        provider_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[EncounterModel]:
        """Get encounters for a specific provider"""
        filter_dict = {"provider.id": provider_id}
        return await self.get_all(
            filter_dict=filter_dict,
            skip=skip,
            limit=limit
        )
    
    async def get_by_status(
        self,
        status: EncounterStatusEnum,
        skip: int = 0,
        limit: int = 50
    ) -> List[EncounterModel]:
        """Get encounters by status"""
        filter_dict = {"status": status.value}
        return await self.get_all(
            filter_dict=filter_dict,
            skip=skip,
            limit=limit
        )
    
    async def get_signed_encounters(
        self,
        signed_after: Optional[datetime] = None,
        signed_before: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[EncounterModel]:
        """Get signed encounters with optional date filtering"""
        try:
            filter_dict = {"status": EncounterStatusEnum.SIGNED.value}
            
            if signed_after or signed_before:
                date_filter = {}
                if signed_after:
                    date_filter["$gte"] = signed_after
                if signed_before:
                    date_filter["$lte"] = signed_before
                filter_dict["signed_at"] = date_filter
            
            return await self.get_all(
                filter_dict=filter_dict,
                skip=skip,
                limit=limit,
                sort_field="signed_at",
                sort_direction=-1
            )
            
        except Exception as e:
            raise DatabaseException(
                f"Database error while retrieving signed encounters: {str(e)}",
                "read"
            )
    
    async def update_status(self, encounter_id: str, status: EncounterStatusEnum) -> EncounterModel:
        """Update encounter status"""
        update_fields = {"status": status.value}
        
        # Set signed_at if status is signed
        if status == EncounterStatusEnum.SIGNED:
            update_fields["signed_at"] = datetime.utcnow()
        
        return await self.update_fields(encounter_id, update_fields)
    
    async def sign_encounter(self, encounter_id: str, signed_by: str) -> EncounterModel:
        """Sign an encounter"""
        now = datetime.utcnow()
        update_fields = {
            "status": EncounterStatusEnum.SIGNED.value,
            "signed_at": now,
            "signed_by": signed_by,
            "workflow.signed_version": await self._get_current_version(encounter_id)
        }
        
        return await self.update_fields(encounter_id, update_fields)
    
    async def _get_current_version(self, encounter_id: str) -> int:
        """Get current version of encounter"""
        encounter = await self.get_by_id(encounter_id)
        return encounter.workflow.version if encounter else 1
    
    async def update_soap(self, encounter_id: str, soap: SOAPModel) -> EncounterModel:
        """Update SOAP documentation"""
        update_fields = {
            "soap": self._soap_to_dict(soap),
            "workflow.last_saved": datetime.utcnow(),
            "workflow.version": await self._get_current_version(encounter_id) + 1
        }
        
        return await self.update_fields(encounter_id, update_fields)
    
    async def update_fhir_reference(self, encounter_id: str, fhir_encounter_id: str) -> EncounterModel:
        """Update FHIR encounter reference"""
        return await self.update_fields(encounter_id, {"fhir_encounter_id": fhir_encounter_id})
    
    async def get_draft_encounters_for_user(self, user_id: str) -> List[EncounterModel]:
        """Get draft encounters for a specific user"""
        filter_dict = {
            "provider.id": user_id,
            "status": EncounterStatusEnum.DRAFT.value
        }
        return await self.get_all(filter_dict=filter_dict)
    
    async def get_encounter_statistics(self) -> Dict[str, Any]:
        """Get encounter statistics"""
        try:
            collection = await self.get_collection()
            
            # Count by status
            status_counts = {}
            for status in EncounterStatusEnum:
                count = await collection.count_documents({"status": status.value})
                status_counts[status.value] = count
            
            # Count by type
            type_counts = {}
            for encounter_type in EncounterTypeEnum:
                count = await collection.count_documents({"type": encounter_type.value})
                type_counts[encounter_type.value] = count
            
            # Total count
            total_count = await collection.count_documents({})
            
            # Signed encounters count
            signed_count = await collection.count_documents({
                "status": EncounterStatusEnum.SIGNED.value
            })
            
            return {
                "total_encounters": total_count,
                "signed_encounters": signed_count,
                "by_status": status_counts,
                "by_type": type_counts
            }
            
        except Exception as e:
            raise DatabaseException(
                f"Database error while retrieving encounter statistics: {str(e)}",
                "read"
            )


# Create repository instance
encounter_repository = EncounterRepository()