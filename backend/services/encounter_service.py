"""
Encounter Service for DiagnoAssist
Business logic for encounter management and SOAP documentation
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from datetime import datetime
from uuid import UUID

if TYPE_CHECKING:
    from models.encounter import Encounter
    from schemas.encounter import (
        EncounterCreate, EncounterUpdate, EncounterResponse, 
        SOAPSectionUpdate, EncounterStats
    )
    from repositories.repository_manager import RepositoryManager

from services.base_service import BaseService
from schemas.encounter import EncounterResponse, EncounterStats

class EncounterService(BaseService):
    """
    Service class for encounter-related business logic
    """
    
    def __init__(self, repositories):
        super().__init__(repositories)
    
    def validate_business_rules(self, data: Dict[str, Any], operation: str = "create") -> None:
        """
        Validate encounter-specific business rules
        
        Args:
            data: Encounter data to validate
            operation: Type of operation (create, update)
        """
        # Business rules validation can be implemented here as needed
        pass
    
    def create_encounter(self, encounter_data: EncounterCreate) -> EncounterResponse:
        """
        Create a new encounter
        
        Args:
            encounter_data: Encounter creation data
            
        Returns:
            EncounterResponse: Created encounter data
        """
        try:
            data_dict = encounter_data.model_dump()
            
            # Validate required fields
            self.validate_required_fields(data_dict, [
                "episode_id", "patient_id"
            ])
            
            # Validate UUIDs
            self.validate_uuid(str(data_dict["episode_id"]), "episode_id")
            self.validate_uuid(str(data_dict["patient_id"]), "patient_id")
            
            # Validate episode exists
            episode = self.get_or_raise("Episode", str(data_dict["episode_id"]), 
                                      self.repos.episode.get_by_id)
            
            # Validate patient exists
            patient = self.get_or_raise("Patient", str(data_dict["patient_id"]), 
                                      self.repos.patient.get_by_id)
            
            # Business rule: Patient must be active
            if patient.status != "active":
                raise RuntimeError(
                    "Cannot create encounter for inactive patient"
                )
            
            # Business rule: Episode must be active
            if episode.status not in ["active", "in-progress"]:
                raise RuntimeError(
                    "Cannot create encounter for completed or cancelled episode"
                )
            
            # Validate business rules
            self.validate_business_rules(data_dict, operation="create")
            
            # Process provider information
            if "provider" in data_dict and data_dict["provider"]:
                provider = data_dict.pop("provider")
                data_dict["provider_id"] = provider.get("id")
                data_dict["provider_name"] = provider.get("name")
                data_dict["provider_role"] = provider.get("role")
            
            # Initialize empty SOAP sections if not provided
            soap_sections = ["soap_subjective", "soap_objective", "soap_assessment", "soap_plan"]
            for section in soap_sections:
                if section not in data_dict or data_dict[section] is None:
                    data_dict[section] = {}
            
            # Set default values
            if "status" not in data_dict:
                data_dict["status"] = "draft"
            if "date" not in data_dict:
                data_dict["date"] = datetime.utcnow()
            
            # Create encounter
            encounter = self.repos.encounter.create(data_dict)
            self.safe_commit("encounter creation")
            
            # Update episode's last encounter ID
            self.repos.episode.update(str(episode.id), {"last_encounter_id": str(encounter.id)})
            self.safe_commit("episode update")
            
            # Audit log
            self.audit_log("create", "Encounter", str(encounter.id), {
                "episode_id": str(encounter.episode_id),
                "patient_id": str(encounter.patient_id),
                "type": encounter.type
            })
            
            return self._build_encounter_response(encounter)
            
        except (ValueError):
            self.safe_rollback("encounter creation")
            raise
        except Exception as e:
            self.safe_rollback("encounter creation")
            raise
    
    def update_encounter(self, encounter_id: str, encounter_data: EncounterUpdate) -> EncounterResponse:
        """
        Update an existing encounter
        
        Args:
            encounter_id: Encounter UUID
            encounter_data: Updated encounter data
            
        Returns:
            EncounterResponse: Updated encounter data
        """
        try:
            self.validate_uuid(encounter_id, "encounter_id")
            encounter = self.get_or_raise("Encounter", encounter_id, self.repos.encounter.get_by_id)
            
            update_dict = encounter_data.model_dump(exclude_unset=True)
            
            if not update_dict:
                return self._build_encounter_response(encounter)
            
            # Business rule: Cannot modify signed encounters except for amendments
            if encounter.status == "signed":
                allowed_fields = {"amendments"}
                update_fields = set(update_dict.keys())
                if not update_fields.issubset(allowed_fields):
                    disallowed = update_fields - allowed_fields
                    raise RuntimeError(
                        f"Cannot modify fields {disallowed} on signed encounter"
                    )
            
            # Validate business rules for update
            self.validate_business_rules(update_dict, operation="update")
            
            # Process provider information
            if "provider" in update_dict and update_dict["provider"]:
                provider = update_dict.pop("provider")
                update_dict["provider_id"] = provider.get("id")
                update_dict["provider_name"] = provider.get("name")
                update_dict["provider_role"] = provider.get("role")
            
            # Fix datetime serialization issues in JSON fields
            self._serialize_datetime_fields(update_dict)
            
            # Update encounter
            updated_encounter = self.repos.encounter.update(encounter_id, update_dict)
            self.safe_commit("encounter update")
            
            # Check if update actually succeeded
            if updated_encounter is None:
                self.safe_rollback("encounter update")
                raise RuntimeError("Failed to update encounter - database operation returned None")
            
            # Audit log
            self.audit_log("update", "Encounter", encounter_id, {
                "updated_fields": list(update_dict.keys()),
                "episode_id": str(encounter.episode_id)
            })
            
            return self._build_encounter_response(updated_encounter)
            
        except (ValueError):
            self.safe_rollback("encounter update")
            raise
        except Exception as e:
            self.safe_rollback("encounter update")
            raise
    
    def get_encounter(self, encounter_id: str) -> EncounterResponse:
        """
        Get encounter by ID
        
        Args:
            encounter_id: Encounter UUID
            
        Returns:
            EncounterResponse: Encounter data
        """
        self.validate_uuid(encounter_id, "encounter_id")
        encounter = self.get_or_raise("Encounter", encounter_id, self.repos.encounter.get_by_id)
        return self._build_encounter_response(encounter)
    
    def get_encounters_by_episode(self, episode_id: str, skip: int = 0, limit: int = 100) -> List[EncounterResponse]:
        """
        Get encounters for an episode
        
        Args:
            episode_id: Episode UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of EncounterResponse objects
        """
        self.validate_uuid(episode_id, "episode_id")
        
        # Verify episode exists
        self.get_or_raise("Episode", episode_id, self.repos.episode.get_by_id)
        
        encounters = self.repos.encounter.get_by_episode(episode_id, skip, limit)
        return [self._build_encounter_response(enc) for enc in encounters]
    
    def get_encounters_by_patient(self, patient_id: str, skip: int = 0, limit: int = 100) -> List[EncounterResponse]:
        """
        Get encounters for a patient
        
        Args:
            patient_id: Patient UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of EncounterResponse objects
        """
        self.validate_uuid(patient_id, "patient_id")
        
        # Verify patient exists
        self.get_or_raise("Patient", patient_id, self.repos.patient.get_by_id)
        
        encounters = self.repos.encounter.get_by_patient(patient_id, skip, limit)
        return [self._build_encounter_response(enc) for enc in encounters]
    
    def update_soap_section(self, encounter_id: str, section_update: SOAPSectionUpdate) -> EncounterResponse:
        """
        Update a specific SOAP section
        
        Args:
            encounter_id: Encounter UUID
            section_update: SOAP section update data
            
        Returns:
            EncounterResponse: Updated encounter
        """
        try:
            self.validate_uuid(encounter_id, "encounter_id")
            encounter = self.get_or_raise("Encounter", encounter_id, self.repos.encounter.get_by_id)
            
            # Business rule: Cannot modify signed encounters
            if encounter.status == "signed":
                raise RuntimeError("Cannot modify SOAP sections on signed encounter")
            
            # Update the SOAP section
            updated_encounter = self.repos.encounter.update_soap_section(
                encounter_id, section_update.section, section_update.data
            )
            
            # Audit log
            self.audit_log("update_soap", "Encounter", encounter_id, {
                "section": section_update.section,
                "episode_id": str(encounter.episode_id)
            })
            
            return self._build_encounter_response(updated_encounter)
            
        except Exception as e:
            self.logger.error(f"Error updating SOAP section: {e}")
            raise
    
    def sign_encounter(self, encounter_id: str, provider_name: str) -> EncounterResponse:
        """
        Sign an encounter
        
        Args:
            encounter_id: Encounter UUID
            provider_name: Name of provider signing
            
        Returns:
            EncounterResponse: Signed encounter
        """
        try:
            self.validate_uuid(encounter_id, "encounter_id")
            encounter = self.get_or_raise("Encounter", encounter_id, self.repos.encounter.get_by_id)
            
            # Business rule: Can only sign draft encounters
            if encounter.status != "draft":
                raise RuntimeError(
                    f"Cannot sign encounter with status '{encounter.status}'. Only draft encounters can be signed."
                )
            
            # Business rule: Check if required sections have data
            missing_sections = self._validate_encounter_completeness(encounter)
            if missing_sections:
                raise RuntimeError(
                    f"Cannot sign incomplete encounter. Missing data in: {', '.join(missing_sections)}"
                )
            
            # Sign the encounter
            signed_encounter = self.repos.encounter.sign_encounter(encounter_id, provider_name)
            
            # Audit log
            self.audit_log("sign", "Encounter", encounter_id, {
                "provider": provider_name,
                "episode_id": str(encounter.episode_id)
            })
            
            return self._build_encounter_response(signed_encounter)
            
        except Exception as e:
            self.logger.error(f"Error signing encounter: {e}")
            raise
    
    def get_encounter_stats(self, episode_id: str) -> EncounterStats:
        """
        Get encounter statistics for an episode
        
        Args:
            episode_id: Episode UUID
            
        Returns:
            EncounterStats: Statistics object
        """
        self.validate_uuid(episode_id, "episode_id")
        stats = self.repos.encounter.get_episode_stats(episode_id)
        
        return EncounterStats(
            total=stats["total"],
            draft=stats["draft"],
            signed=stats["signed"],
            lastVisit=stats["lastVisit"]
        )
    
    def copy_forward_from_encounter(self, source_encounter_id: str, target_encounter_id: str, 
                                   sections: List[str]) -> EncounterResponse:
        """
        Copy data from one encounter to another
        
        Args:
            source_encounter_id: Source encounter UUID
            target_encounter_id: Target encounter UUID
            sections: List of sections to copy
            
        Returns:
            EncounterResponse: Updated target encounter
        """
        try:
            self.validate_uuid(source_encounter_id, "source_encounter_id")
            self.validate_uuid(target_encounter_id, "target_encounter_id")
            
            source = self.get_or_raise("Encounter", source_encounter_id, self.repos.encounter.get_by_id)
            target = self.get_or_raise("Encounter", target_encounter_id, self.repos.encounter.get_by_id)
            
            # Business rule: Cannot modify signed encounters
            if target.status == "signed":
                raise RuntimeError("Cannot copy data to signed encounter")
            
            # Copy specified sections
            update_data = {}
            valid_sections = ['subjective', 'objective', 'assessment', 'plan']
            
            for section in sections:
                if section not in valid_sections:
                    continue
                    
                source_field = f"soap_{section}"
                source_data = getattr(source, source_field)
                
                if source_data:
                    # Add lastUpdated timestamp
                    if isinstance(source_data, dict):
                        source_data['lastUpdated'] = datetime.utcnow().isoformat()
                    update_data[source_field] = source_data
            
            if update_data:
                updated_encounter = self.repos.encounter.update(target_encounter_id, update_data)
                self.safe_commit("copy forward")
                
                # Audit log
                self.audit_log("copy_forward", "Encounter", target_encounter_id, {
                    "source_encounter": source_encounter_id,
                    "sections": sections
                })
                
                return self._build_encounter_response(updated_encounter)
            
            return self._build_encounter_response(target)
            
        except Exception as e:
            self.safe_rollback("copy forward")
            raise
    
    def _serialize_datetime_fields(self, data: Dict[str, Any]) -> None:
        """
        Recursively serialize datetime objects in dictionary to ISO format
        
        Args:
            data: Dictionary to process for datetime serialization
        """
        for key, value in data.items():
            if isinstance(value, dict):
                self._serialize_datetime_fields(value)
            elif isinstance(value, datetime):
                data[key] = value.isoformat()
    
    def _build_encounter_response(self, encounter: Encounter) -> EncounterResponse:
        """
        Build EncounterResponse with additional computed fields
        
        Args:
            encounter: Encounter model instance
            
        Returns:
            EncounterResponse with computed fields
        """
        if encounter is None:
            raise ValueError("Cannot build response for None encounter")
            
        # Rebuild provider information
        provider = None
        if encounter.provider_id:
            provider = {
                "id": encounter.provider_id,
                "name": encounter.provider_name or "",
                "role": encounter.provider_role or ""
            }
        
        # Build encounter response
        encounter_dict = {
            "id": encounter.id,
            "episode_id": encounter.episode_id,
            "patient_id": encounter.patient_id,
            "type": encounter.type,
            "date": encounter.date,
            "status": encounter.status,
            "provider_id": encounter.provider_id,
            "provider_name": encounter.provider_name,
            "provider_role": encounter.provider_role,
            "provider": provider,
            "soap_subjective": encounter.soap_subjective or {},
            "soap_objective": encounter.soap_objective or {},
            "soap_assessment": encounter.soap_assessment or {},
            "soap_plan": encounter.soap_plan or {},
            "documents": encounter.documents or [],
            "amendments": encounter.amendments or [],
            "signed_at": encounter.signed_at,
            "signed_by": encounter.signed_by,
            "created_at": encounter.created_at,
            "updated_at": encounter.updated_at,
            "created_by": encounter.created_by,
            "completion_percentage": encounter.completion_percentage,
            "is_signed": encounter.is_signed,
            "chief_complaint": encounter.chief_complaint
        }
        
        return EncounterResponse.model_validate(encounter_dict)
    
    def _validate_encounter_completeness(self, encounter: Encounter) -> List[str]:
        """
        Validate if encounter has minimum required data for signing
        
        Args:
            encounter: Encounter to validate
            
        Returns:
            List of missing sections
        """
        missing = []
        
        # Check subjective - require HPI
        if not encounter.soap_subjective or not encounter.soap_subjective.get('hpi'):
            missing.append('History of Present Illness')
        
        # Check objective - require at least one vital sign
        if not encounter.soap_objective:
            missing.append('Vital Signs')
        else:
            vitals = encounter.soap_objective.get('vitals', {})
            if not any(vitals.values()) if vitals else True:
                missing.append('Vital Signs')
        
        # Check assessment - require clinical impression
        if not encounter.soap_assessment or not encounter.soap_assessment.get('clinicalImpression'):
            missing.append('Clinical Assessment')
        
        # Check plan - require follow-up or treatment
        if not encounter.soap_plan:
            missing.append('Treatment Plan')
        else:
            plan = encounter.soap_plan
            has_plan = (
                plan.get('medications') or 
                plan.get('procedures') or 
                plan.get('followUp', {}).get('timeframe')
            )
            if not has_plan:
                missing.append('Treatment Plan')
        
        return missing
    
    def delete_encounter(self, encounter_id: str) -> Dict[str, Any]:
        """
        Delete an encounter (only if not signed)
        
        Args:
            encounter_id: Encounter UUID
            
        Returns:
            Dict containing deletion status
        """
        try:
            self.validate_uuid(encounter_id, "encounter_id")
            encounter = self.get_or_raise("Encounter", encounter_id, self.repos.encounter.get_by_id)
            
            # Business rule: Cannot delete signed encounters
            if encounter.status == "signed":
                raise RuntimeError("Cannot delete signed encounters")
            
            # Delete encounter
            self.repos.encounter.delete(encounter_id)
            self.safe_commit("encounter deletion")
            
            # Audit log
            self.audit_log("delete", "Encounter", encounter_id, {
                "episode_id": str(encounter.episode_id)
            })
            
            return {
                "status": "success",
                "message": f"Encounter {encounter_id} deleted successfully"
            }
            
        except Exception as e:
            self.safe_rollback("encounter deletion")
            raise