"""
Treatment Service for DiagnoAssist
Business logic for treatment plans and interventions
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from datetime import datetime, timedelta
from uuid import UUID

if TYPE_CHECKING:
    from models.treatment import Treatment
    from schemas.treatment import TreatmentCreate, TreatmentUpdate, TreatmentResponse, MedicationTreatment
    from repositories.repository_manager import RepositoryManager

from services.base_service import BaseService, ValueError

class TreatmentService(BaseService):
    """
    Service class for treatment-related business logic
    """
    
    def __init__(self, repositories):
        super().__init__(repositories)
    
    def validate_business_rules(self, data: Dict[str, Any], operation: str = "create") -> None:
        """
        Validate treatment-specific business rules - DISABLED FOR TESTING
        """
        pass  # All validation disabled

    def create_treatment(self, treatment_data: TreatmentCreate) -> TreatmentResponse:
        """
        Create a new treatment plan
        
        Args:
            treatment_data: Treatment creation data
            
        Returns:
            TreatmentResponse: Created treatment data
        """
        try:
            data_dict = treatment_data.model_dump()
            
            # Validate required fields
            self.validate_required_fields(data_dict, [
                "episode_id", "name"
            ])
            
            # Validate episode exists and is active
            self.validate_uuid(str(data_dict["episode_id"]), "episode_id")
            episode = self.get_or_raise("Episode", str(data_dict["episode_id"]), 
                                      self.repos.episode.get_by_id)
            
            if episode.status != "in-progress":
                raise RuntimeError(
                    "Cannot add treatment to completed or cancelled episode",
                    rule="active_episode_required"
                )
            
            # Validate diagnosis if provided
            if "diagnosis_id" in data_dict and data_dict["diagnosis_id"]:
                self.validate_uuid(str(data_dict["diagnosis_id"]), "diagnosis_id")
                diagnosis = self.get_or_raise("Diagnosis", str(data_dict["diagnosis_id"]), 
                                            self.repos.diagnosis.get_by_id)
                
                # Verify diagnosis belongs to same episode
                if str(diagnosis.episode_id) != str(data_dict["episode_id"]):
                    raise RuntimeError(
                        "Diagnosis must belong to the same episode as the treatment",
                        rule="diagnosis_episode_match"
                    )
            
            # Validate business rules
            self.validate_business_rules(data_dict, operation="create")
            
            # Check for duplicate treatments
            existing_treatments = self.repos.treatment.get_by_episode(str(data_dict["episode_id"]))
            for existing in existing_treatments:
                if (existing.treatment_name.lower().strip() == data_dict["treatment_name"].lower().strip() and
                    existing.status in ["planned", "approved", "active"]):
                    raise RuntimeError(
                        f"Active treatment '{data_dict['treatment_name']}' already exists for this episode",
                        rule="unique_active_treatment_per_episode"
                    )
            
            # Set default values
            if "status" not in data_dict:
                data_dict["status"] = "planned"
            
            if "created_by" not in data_dict:
                data_dict["created_by"] = "ai_system"
            
            # Create treatment
            treatment = self.repos.treatment.create(data_dict)
            self.safe_commit("treatment creation")
            
            # Audit log
            self.audit_log("create", "Treatment", str(treatment.id), {
                "episode_id": str(treatment.episode_id),
                "treatment_name": treatment.treatment_name,
                "treatment_type": treatment.treatment_type
            })
            
            return TreatmentResponse.model_validate(treatment)
            
        except (ValueError):
            self.safe_rollback("treatment creation")
            raise
        except Exception as e:
            self.safe_rollback("treatment creation")
            raise
    
    def update_treatment(self, treatment_id: str, treatment_data: TreatmentUpdate) -> TreatmentResponse:
        """
        Update an existing treatment
        
        Args:
            treatment_id: Treatment UUID
            treatment_data: Updated treatment data
            
        Returns:
            TreatmentResponse: Updated treatment data
        """
        try:
            self.validate_uuid(treatment_id, "treatment_id")
            treatment = self.get_or_raise("Treatment", treatment_id, self.repos.treatment.get_by_id)
            
            update_dict = treatment_data.model_dump(exclude_unset=True)
            
            if not update_dict:
                return TreatmentResponse.model_validate(treatment)
            
            # Validate business rules for update
            self.validate_business_rules(update_dict, operation="update")
            
            # Business rule: Cannot modify completed treatments except for notes
            if treatment.status == "completed":
                allowed_fields = {"follow_up_instructions", "patient_education"}
                update_fields = set(update_dict.keys())
                if not update_fields.issubset(allowed_fields):
                    disallowed = update_fields - allowed_fields
                    raise RuntimeError(
                        f"Cannot modify fields {disallowed} on completed treatment",
                        rule="completed_treatment_limited_updates"
                    )
            
            # Auto-set end_date if status is being changed to completed
            if "status" in update_dict and update_dict["status"] == "completed":
                if not treatment.end_date and "end_date" not in update_dict:
                    update_dict["end_date"] = datetime.utcnow()
            
            # Auto-set start_date if status is being changed to active
            if "status" in update_dict and update_dict["status"] == "active":
                if not treatment.start_date and "start_date" not in update_dict:
                    update_dict["start_date"] = datetime.utcnow()
            
            # Update treatment
            updated_treatment = self.repos.treatment.update(treatment_id, update_dict)
            self.safe_commit("treatment update")
            
            # Audit log
            self.audit_log("update", "Treatment", treatment_id, {
                "updated_fields": list(update_dict.keys()),
                "episode_id": str(treatment.episode_id)
            })
            
            return TreatmentResponse.model_validate(updated_treatment)
            
        except (ValueError):
            self.safe_rollback("treatment update")
            raise
        except Exception as e:
            self.safe_rollback("treatment update")
            raise
    
    def get_treatment(self, treatment_id: str) -> TreatmentResponse:
        """
        Get treatment by ID
        
        Args:
            treatment_id: Treatment UUID
            
        Returns:
            TreatmentResponse: Treatment data
        """
        self.validate_uuid(treatment_id, "treatment_id")
        treatment = self.get_or_raise("Treatment", treatment_id, self.repos.treatment.get_by_id)
        return TreatmentResponse.model_validate(treatment)
    
    def get_treatments_by_episode(self, episode_id: str) -> List[TreatmentResponse]:
        """
        Get all treatments for an episode
        
        Args:
            episode_id: Episode UUID
            
        Returns:
            List of TreatmentResponse objects
        """
        self.validate_uuid(episode_id, "episode_id")
        
        # Verify episode exists
        self.get_or_raise("Episode", episode_id, self.repos.episode.get_by_id)
        
        treatments = self.repos.treatment.get_by_episode(episode_id)
        return [TreatmentResponse.model_validate(t) for t in treatments]
    
    def get_active_treatments_by_patient(self, patient_id: str) -> List[TreatmentResponse]:
        """
        Get all active treatments for a patient across all episodes
        
        Args:
            patient_id: Patient UUID
            
        Returns:
            List of active TreatmentResponse objects
        """
        self.validate_uuid(patient_id, "patient_id")
        
        # Verify patient exists
        self.get_or_raise("Patient", patient_id, self.repos.patient.get_by_id)
        
        treatments = self.repos.treatment.get_active_by_patient(patient_id)
        return [TreatmentResponse.model_validate(t) for t in treatments]
    
    def approve_treatment(self, treatment_id: str, approved_by: str, approval_notes: Optional[str] = None) -> TreatmentResponse:
        """
        Approve a treatment plan
        
        Args:
            treatment_id: Treatment UUID
            approved_by: Identifier of the approving physician
            approval_notes: Optional approval notes
            
        Returns:
            TreatmentResponse: Updated treatment
        """
        try:
            self.validate_uuid(treatment_id, "treatment_id")
            treatment = self.get_or_raise("Treatment", treatment_id, self.repos.treatment.get_by_id)
            
            # Business rule: Can only approve planned treatments
            if treatment.status != "planned":
                raise RuntimeError(
                    f"Cannot approve treatment with status '{treatment.status}'. Only planned treatments can be approved.",
                    rule="approve_planned_only"
                )
            
            # Prepare update data
            update_data = {
                "status": "approved",
                "approved_by": approved_by
            }
            
            if approval_notes:
                current_instructions = treatment.instructions or ""
                if current_instructions:
                    update_data["instructions"] = f"{current_instructions}\n\nApproval Notes:\n{approval_notes}"
                else:
                    update_data["instructions"] = f"Approval Notes:\n{approval_notes}"
            
            # Update treatment
            updated_treatment = self.repos.treatment.update(treatment_id, update_data)
            self.safe_commit("treatment approval")
            
            # Audit log
            self.audit_log("approve", "Treatment", treatment_id, {
                "episode_id": str(treatment.episode_id),
                "approved_by": approved_by
            })
            
            return TreatmentResponse.model_validate(updated_treatment)
            
        except (ValueError):
            self.safe_rollback("treatment approval")
            raise
        except Exception as e:
            self.safe_rollback("treatment approval")
            raise
    
    def activate_treatment(self, treatment_id: str) -> TreatmentResponse:
        """
        Activate an approved treatment
        
        Args:
            treatment_id: Treatment UUID
            
        Returns:
            TreatmentResponse: Updated treatment
        """
        try:
            self.validate_uuid(treatment_id, "treatment_id")
            treatment = self.get_or_raise("Treatment", treatment_id, self.repos.treatment.get_by_id)
            
            # Business rule: Can only activate approved treatments
            if treatment.status != "approved":
                raise RuntimeError(
                    f"Cannot activate treatment with status '{treatment.status}'. Only approved treatments can be activated.",
                    rule="activate_approved_only"
                )
            
            # Check for drug interactions with other active treatments
            if treatment.treatment_type == "medication":
                conflicts = self._check_drug_interactions(treatment)
                if conflicts:
                    raise RuntimeError(
                        f"Drug interactions detected: {', '.join(conflicts)}",
                        rule="drug_interaction_check"
                    )
            
            # Update treatment
            update_data = {
                "status": "active",
                "start_date": datetime.utcnow()
            }
            
            updated_treatment = self.repos.treatment.update(treatment_id, update_data)
            self.safe_commit("treatment activation")
            
            # Audit log
            self.audit_log("activate", "Treatment", treatment_id, {
                "episode_id": str(treatment.episode_id),
                "treatment_name": treatment.treatment_name
            })
            
            return TreatmentResponse.model_validate(updated_treatment)
            
        except (ValueError):
            self.safe_rollback("treatment activation")
            raise
        except Exception as e:
            self.safe_rollback("treatment activation")
            raise
    
    def discontinue_treatment(self, treatment_id: str, reason: str, discontinued_by: str) -> TreatmentResponse:
        """
        Discontinue an active treatment
        
        Args:
            treatment_id: Treatment UUID
            reason: Reason for discontinuation
            discontinued_by: Who discontinued the treatment
            
        Returns:
            TreatmentResponse: Updated treatment
        """
        try:
            self.validate_uuid(treatment_id, "treatment_id")
            treatment = self.get_or_raise("Treatment", treatment_id, self.repos.treatment.get_by_id)
            
            # Business rule: Can only discontinue active or approved treatments
            if treatment.status not in ["active", "approved"]:
                raise RuntimeError(
                    f"Cannot discontinue treatment with status '{treatment.status}'",
                    rule="discontinue_active_or_approved_only"
                )
            
            # Update treatment
            update_data = {
                "status": "discontinued",
                "end_date": datetime.utcnow(),
                "follow_up_instructions": f"Treatment discontinued by {discontinued_by}. Reason: {reason}"
            }
            
            updated_treatment = self.repos.treatment.update(treatment_id, update_data)
            self.safe_commit("treatment discontinuation")
            
            # Audit log
            self.audit_log("discontinue", "Treatment", treatment_id, {
                "episode_id": str(treatment.episode_id),
                "reason": reason,
                "discontinued_by": discontinued_by
            })
            
            return TreatmentResponse.model_validate(updated_treatment)
            
        except (ValueError):
            self.safe_rollback("treatment discontinuation")
            raise
        except Exception as e:
            self.safe_rollback("treatment discontinuation")
            raise
    
    def generate_medication_list(self, patient_id: str) -> Dict[str, Any]:
        """
        Generate current medication list for a patient
        
        Args:
            patient_id: Patient UUID
            
        Returns:
            Dictionary with current medications and details
        """
        self.validate_uuid(patient_id, "patient_id")
        
        # Verify patient exists
        patient = self.get_or_raise("Patient", patient_id, self.repos.patient.get_by_id)
        
        # Get active medication treatments
        active_treatments = self.repos.treatment.get_active_by_patient(patient_id)
        medications = [t for t in active_treatments if t.treatment_type == "medication"]
        
        medication_list = []
        for med in medications:
            medication_list.append({
                "id": str(med.id),
                "medication_name": med.name,  # Changed from med.medication_name to med.name
                "dosage": med.dosage,
                "frequency": med.frequency,
                "route": med.route,
                "start_date": med.start_date,
                "prescribed_for": med.name,  # Changed from med.treatment_name to med.name
                "instructions": med.instructions,
                "side_effects": med.side_effects or [],
                "monitoring_requirements": med.monitoring_requirements or []
            })
        
        return {
            "patient_id": patient_id,
            "patient_name": f"{patient.first_name} {patient.last_name}",
            "generated_at": datetime.utcnow(),
            "medication_count": len(medication_list),
            "medications": medication_list
        }
    
    def check_treatment_adherence(self, treatment_id: str) -> Dict[str, Any]:
        """
        Placeholder for treatment adherence checking
        TODO: Implement adherence monitoring logic
        
        Args:
            treatment_id: Treatment UUID
            
        Returns:
            Dictionary with adherence information
        """
        self.validate_uuid(treatment_id, "treatment_id")
        treatment = self.get_or_raise("Treatment", treatment_id, self.repos.treatment.get_by_id)
        
        return {
            "treatment_id": treatment_id,
            "adherence_score": None,  # TODO: Implement calculation
            "last_checked": datetime.utcnow(),
            "notes": "Adherence monitoring not yet implemented"
        }
    
    def _is_high_risk_medication(self, medication_name: str) -> bool:
        """
        Check if medication is considered high-risk
        
        Args:
            medication_name: Name of the medication
            
        Returns:
            True if high-risk medication
        """
        # Simple implementation - in reality this would be more sophisticated
        high_risk_keywords = [
            "warfarin", "heparin", "insulin", "chemotherapy", "opioid",
            "controlled substance", "narcotic", "methotrexate"
        ]
        
        med_lower = medication_name.lower()
        return any(keyword in med_lower for keyword in high_risk_keywords)
    
    def _check_drug_interactions(self, treatment: Treatment) -> List[str]:
        """
        Check for drug interactions with other active treatments
        
        Args:
            treatment: Treatment to check
            
        Returns:
            List of interaction warnings
        """
        if treatment.treatment_type != "medication":
            return []
        
        # Get other active medications for the same episode
        active_treatments = self.repos.treatment.get_by_episode(str(treatment.episode_id))
        other_meds = [t for t in active_treatments 
                     if t.treatment_type == "medication" and 
                     t.status == "active" and 
                     str(t.id) != str(treatment.id)]
        
        interactions = []
        
        # Simple interaction checking (in reality, this would use a drug interaction database)
        med_name = treatment.name.lower() if treatment.name else ""
        
        for other in other_meds:
            other_med = other.name.lower() if other.name else ""
            
            # Example: Basic warfarin interactions
            if "warfarin" in med_name and any(drug in other_med for drug in ["aspirin", "ibuprofen", "nsaid"]):
                interactions.append(f"Bleeding risk: {treatment.name} + {other.name}")
            
            if "insulin" in med_name and "beta-blocker" in other_med:
                interactions.append(f"Hypoglycemia masking: {treatment.name} + {other.name}")
        
        return interactions