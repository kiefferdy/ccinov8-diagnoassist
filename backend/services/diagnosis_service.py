"""
Diagnosis Service for DiagnoAssist
Business logic for medical diagnoses and AI analysis
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from datetime import datetime
from uuid import UUID

if TYPE_CHECKING:
    from models.diagnosis import Diagnosis
    from schemas.diagnosis import DiagnosisCreate, DiagnosisUpdate, DiagnosisResponse, DifferentialDiagnosis
    from repositories.repository_manager import RepositoryManager

from services.base_service import BaseService, ValidationException, BusinessRuleException, ResourceNotFoundException

class DiagnosisService(BaseService):
    """
    Service class for diagnosis-related business logic
    """
    
    def __init__(self, repositories):
        super().__init__(repositories)
    
    def validate_business_rules(self, data: Dict[str, Any], operation: str = "create") -> None:
        """
        Validate diagnosis-specific business rules
        
        Args:
            data: Diagnosis data to validate
            operation: Operation being performed
            
        Raises:
            BusinessRuleException: If business rules are violated
            ValidationException: If validation fails
        """
        # Validate AI probability
        if "ai_probability" in data and data["ai_probability"] is not None:
            prob = data["ai_probability"]
            if not isinstance(prob, (int, float)) or prob < 0 or prob > 1:
                raise ValidationException(
                    "AI probability must be a number between 0 and 1",
                    field="ai_probability",
                    value=prob
                )
        
        # Validate confidence level
        if "confidence_level" in data and data["confidence_level"]:
            valid_levels = ["very_low", "low", "medium", "high", "very_high"]
            if data["confidence_level"] not in valid_levels:
                raise ValidationException(
                    f"Confidence level must be one of: {', '.join(valid_levels)}",
                    field="confidence_level",
                    value=data["confidence_level"]
                )
        
        # Validate ICD-10 code format (basic check)
        if "icd10_code" in data and data["icd10_code"]:
            icd_code = data["icd10_code"].upper()
            if not self._is_valid_icd10_format(icd_code):
                raise ValidationException(
                    f"Invalid ICD-10 code format: {icd_code}",
                    field="icd10_code",
                    value=data["icd10_code"]
                )
        
        # Business rule: Final diagnosis requires physician confirmation
        if data.get("final_diagnosis") and not data.get("physician_confirmed"):
            raise BusinessRuleException(
                "Final diagnosis must be confirmed by a physician",
                rule="final_diagnosis_requires_confirmation"
            )
        
        # Business rule: High probability diagnoses should have supporting evidence
        if (data.get("ai_probability", 0) >= 0.8 and 
            not data.get("supporting_symptoms") and 
            not data.get("ai_reasoning")):
            raise BusinessRuleException(
                "High probability diagnoses must include supporting symptoms or AI reasoning",
                rule="high_probability_requires_evidence"
            )
    
    def create_diagnosis(self, diagnosis_data: DiagnosisCreate) -> DiagnosisResponse:
        """
        Create a new diagnosis
        
        Args:
            diagnosis_data: Diagnosis creation data
            
        Returns:
            DiagnosisResponse: Created diagnosis data
        """
        try:
            data_dict = diagnosis_data.model_dump()
            
            # Validate required fields
            self.validate_required_fields(data_dict, [
                "episode_id", "condition_name"
            ])
            
            # Validate episode exists and is active
            self.validate_uuid(str(data_dict["episode_id"]), "episode_id")
            episode = self.get_or_raise("Episode", str(data_dict["episode_id"]), 
                                      self.repos.episode.get_by_id)
            
            if episode.status != "in-progress":
                raise BusinessRuleException(
                    "Cannot add diagnosis to completed or cancelled episode",
                    rule="active_episode_required"
                )
            
            # Validate business rules
            self.validate_business_rules(data_dict, operation="create")
            
            # Check for duplicate diagnoses (same condition for same episode)
            existing_diagnoses = self.repos.diagnosis.get_by_episode(str(data_dict["episode_id"]))
            for existing in existing_diagnoses:
                if existing.condition_name.lower().strip() == data_dict["condition_name"].lower().strip():
                    raise BusinessRuleException(
                        f"Diagnosis for condition '{data_dict['condition_name']}' already exists for this episode",
                        rule="unique_condition_per_episode"
                    )
            
            # Set default values
            if "ai_probability" not in data_dict and "confidence_level" in data_dict:
                # Convert confidence level to probability estimate
                data_dict["ai_probability"] = self._confidence_to_probability(data_dict["confidence_level"])
            
            if "created_by" not in data_dict:
                data_dict["created_by"] = "ai_system"
            
            # Create diagnosis
            diagnosis = self.repos.diagnosis.create(data_dict)
            self.safe_commit("diagnosis creation")
            
            # Audit log
            self.audit_log("create", "Diagnosis", str(diagnosis.id), {
                "episode_id": str(diagnosis.episode_id),
                "condition_name": diagnosis.condition_name,
                "ai_probability": diagnosis.ai_probability
            })
            
            return DiagnosisResponse.model_validate(diagnosis)
            
        except (ValidationException, BusinessRuleException, ResourceNotFoundException):
            self.safe_rollback("diagnosis creation")
            raise
        except Exception as e:
            self.safe_rollback("diagnosis creation")
            raise
    
    def update_diagnosis(self, diagnosis_id: str, diagnosis_data: DiagnosisUpdate) -> DiagnosisResponse:
        """
        Update an existing diagnosis
        
        Args:
            diagnosis_id: Diagnosis UUID
            diagnosis_data: Updated diagnosis data
            
        Returns:
            DiagnosisResponse: Updated diagnosis data
        """
        try:
            self.validate_uuid(diagnosis_id, "diagnosis_id")
            diagnosis = self.get_or_raise("Diagnosis", diagnosis_id, self.repos.diagnosis.get_by_id)
            
            update_dict = diagnosis_data.model_dump(exclude_unset=True)
            
            if not update_dict:
                return DiagnosisResponse.model_validate(diagnosis)
            
            # Validate business rules for update
            self.validate_business_rules(update_dict, operation="update")
            
            # Business rule: Cannot modify final diagnoses except for physician notes
            if diagnosis.final_diagnosis:
                allowed_fields = {"physician_notes"}
                update_fields = set(update_dict.keys())
                if not update_fields.issubset(allowed_fields):
                    disallowed = update_fields - allowed_fields
                    raise BusinessRuleException(
                        f"Cannot modify fields {disallowed} on final diagnosis",
                        rule="final_diagnosis_limited_updates"
                    )
            
            # Auto-set confirmation timestamp if physician is confirming
            if "physician_confirmed" in update_dict and update_dict["physician_confirmed"]:
                update_dict["confirmed_at"] = datetime.utcnow()
            
            # Update diagnosis
            updated_diagnosis = self.repos.diagnosis.update(diagnosis_id, update_dict)
            self.safe_commit("diagnosis update")
            
            # Audit log
            self.audit_log("update", "Diagnosis", diagnosis_id, {
                "updated_fields": list(update_dict.keys()),
                "episode_id": str(diagnosis.episode_id)
            })
            
            return DiagnosisResponse.model_validate(updated_diagnosis)
            
        except (ValidationException, BusinessRuleException, ResourceNotFoundException):
            self.safe_rollback("diagnosis update")
            raise
        except Exception as e:
            self.safe_rollback("diagnosis update")
            raise
    
    def get_diagnosis(self, diagnosis_id: str) -> DiagnosisResponse:
        """
        Get diagnosis by ID
        
        Args:
            diagnosis_id: Diagnosis UUID
            
        Returns:
            DiagnosisResponse: Diagnosis data
        """
        self.validate_uuid(diagnosis_id, "diagnosis_id")
        diagnosis = self.get_or_raise("Diagnosis", diagnosis_id, self.repos.diagnosis.get_by_id)
        return DiagnosisResponse.model_validate(diagnosis)
    
    def get_diagnoses_by_episode(self, episode_id: str) -> List[DiagnosisResponse]:
        """
        Get all diagnoses for an episode
        
        Args:
            episode_id: Episode UUID
            
        Returns:
            List of DiagnosisResponse objects
        """
        self.validate_uuid(episode_id, "episode_id")
        
        # Verify episode exists
        self.get_or_raise("Episode", episode_id, self.repos.episode.get_by_id)
        
        diagnoses = self.repos.diagnosis.get_by_episode(episode_id)
        return [DiagnosisResponse.model_validate(d) for d in diagnoses]
    
    def confirm_diagnosis(self, diagnosis_id: str, physician_notes: Optional[str] = None) -> DiagnosisResponse:
        """
        Physician confirmation of a diagnosis
        
        Args:
            diagnosis_id: Diagnosis UUID
            physician_notes: Optional physician notes
            
        Returns:
            DiagnosisResponse: Updated diagnosis
        """
        try:
            self.validate_uuid(diagnosis_id, "diagnosis_id")
            diagnosis = self.get_or_raise("Diagnosis", diagnosis_id, self.repos.diagnosis.get_by_id)
            
            # Prepare update data
            update_data = {
                "physician_confirmed": True,
                "confirmed_at": datetime.utcnow()
            }
            
            if physician_notes:
                update_data["physician_notes"] = physician_notes
            
            # Update diagnosis
            updated_diagnosis = self.repos.diagnosis.update(diagnosis_id, update_data)
            self.safe_commit("diagnosis confirmation")
            
            # Audit log
            self.audit_log("confirm", "Diagnosis", diagnosis_id, {
                "episode_id": str(diagnosis.episode_id),
                "condition_name": diagnosis.condition_name
            })
            
            return DiagnosisResponse.model_validate(updated_diagnosis)
            
        except (ValidationException, BusinessRuleException, ResourceNotFoundException):
            self.safe_rollback("diagnosis confirmation")
            raise
        except Exception as e:
            self.safe_rollback("diagnosis confirmation")
            raise
    
    def set_final_diagnosis(self, diagnosis_id: str, physician_notes: Optional[str] = None) -> DiagnosisResponse:
        """
        Set a diagnosis as the final diagnosis for the episode
        
        Args:
            diagnosis_id: Diagnosis UUID
            physician_notes: Optional physician notes
            
        Returns:
            DiagnosisResponse: Updated diagnosis
        """
        try:
            self.validate_uuid(diagnosis_id, "diagnosis_id")
            diagnosis = self.get_or_raise("Diagnosis", diagnosis_id, self.repos.diagnosis.get_by_id)
            
            # Business rule: Must be physician confirmed first
            if not diagnosis.physician_confirmed:
                raise BusinessRuleException(
                    "Diagnosis must be physician confirmed before setting as final",
                    rule="confirmation_required_for_final"
                )
            
            # Clear any existing final diagnoses for this episode
            existing_diagnoses = self.repos.diagnosis.get_by_episode(str(diagnosis.episode_id))
            for existing in existing_diagnoses:
                if existing.final_diagnosis and str(existing.id) != diagnosis_id:
                    self.repos.diagnosis.update(str(existing.id), {"final_diagnosis": False})
            
            # Set as final diagnosis
            update_data = {
                "final_diagnosis": True,
                "confirmed_at": datetime.utcnow()
            }
            
            if physician_notes:
                update_data["physician_notes"] = physician_notes
            
            updated_diagnosis = self.repos.diagnosis.update(diagnosis_id, update_data)
            self.safe_commit("final diagnosis setting")
            
            # Audit log
            self.audit_log("set_final", "Diagnosis", diagnosis_id, {
                "episode_id": str(diagnosis.episode_id),
                "condition_name": diagnosis.condition_name
            })
            
            return DiagnosisResponse.model_validate(updated_diagnosis)
            
        except (ValidationException, BusinessRuleException, ResourceNotFoundException):
            self.safe_rollback("final diagnosis setting")
            raise
        except Exception as e:
            self.safe_rollback("final diagnosis setting")
            raise
    
    def get_differential_diagnoses(self, episode_id: str) -> List[Dict[str, Any]]:
        """
        Get differential diagnoses for an episode, ranked by probability
        
        Args:
            episode_id: Episode UUID
            
        Returns:
            List of diagnosis data ranked by AI probability
        """
        self.validate_uuid(episode_id, "episode_id")
        
        # Verify episode exists
        self.get_or_raise("Episode", episode_id, self.repos.episode.get_by_id)
        
        diagnoses = self.repos.diagnosis.get_by_episode(episode_id)
        
        # Sort by AI probability (descending) and format for differential view
        differential_list = []
        for diagnosis in sorted(diagnoses, key=lambda d: d.ai_probability or 0, reverse=True):
            differential_list.append({
                "id": str(diagnosis.id),
                "condition_name": diagnosis.condition_name,
                "icd10_code": diagnosis.icd10_code,
                "ai_probability": diagnosis.ai_probability,
                "probability_percentage": diagnosis.probability_percentage,
                "confidence_level": diagnosis.confidence_level,
                "physician_confirmed": diagnosis.physician_confirmed,
                "final_diagnosis": diagnosis.final_diagnosis,
                "supporting_symptoms": diagnosis.supporting_symptoms or [],
                "red_flags": diagnosis.red_flags or [],
                "created_at": diagnosis.created_at
            })
        
        return differential_list
    
    def add_supporting_evidence(self, diagnosis_id: str, evidence: Dict[str, Any]) -> DiagnosisResponse:
        """
        Add supporting evidence to a diagnosis
        
        Args:
            diagnosis_id: Diagnosis UUID
            evidence: Evidence data (symptoms, findings, etc.)
            
        Returns:
            DiagnosisResponse: Updated diagnosis
        """
        try:
            self.validate_uuid(diagnosis_id, "diagnosis_id")
            diagnosis = self.get_or_raise("Diagnosis", diagnosis_id, self.repos.diagnosis.get_by_id)
            
            update_data = {}
            
            # Add supporting symptoms
            if "symptoms" in evidence:
                current_symptoms = diagnosis.supporting_symptoms or []
                new_symptoms = evidence["symptoms"]
                if isinstance(new_symptoms, list):
                    current_symptoms.extend(new_symptoms)
                    update_data["supporting_symptoms"] = list(set(current_symptoms))  # Remove duplicates
            
            # Add red flags
            if "red_flags" in evidence:
                current_flags = diagnosis.red_flags or []
                new_flags = evidence["red_flags"]
                if isinstance(new_flags, list):
                    current_flags.extend(new_flags)
                    update_data["red_flags"] = list(set(current_flags))
            
            # Update AI reasoning
            if "reasoning" in evidence:
                current_reasoning = diagnosis.ai_reasoning or ""
                additional_reasoning = evidence["reasoning"]
                if current_reasoning:
                    update_data["ai_reasoning"] = f"{current_reasoning}\n\nAdditional Evidence:\n{additional_reasoning}"
                else:
                    update_data["ai_reasoning"] = additional_reasoning
            
            if not update_data:
                return DiagnosisResponse.model_validate(diagnosis)
            
            # Update diagnosis
            updated_diagnosis = self.repos.diagnosis.update(diagnosis_id, update_data)
            self.safe_commit("evidence addition")
            
            # Audit log
            self.audit_log("add_evidence", "Diagnosis", diagnosis_id, {
                "episode_id": str(diagnosis.episode_id),
                "evidence_types": list(evidence.keys())
            })
            
            return DiagnosisResponse.model_validate(updated_diagnosis)
            
        except (ValidationException, BusinessRuleException, ResourceNotFoundException):
            self.safe_rollback("evidence addition")
            raise
        except Exception as e:
            self.safe_rollback("evidence addition")
            raise
    
    # Placeholder methods for future AI integration
    def analyze_symptoms_for_diagnosis(self, episode_id: str, symptoms: List[str]) -> List[Dict[str, Any]]:
        """
        Placeholder for AI-powered symptom analysis
        TODO: Implement AI integration
        
        Args:
            episode_id: Episode UUID
            symptoms: List of symptoms to analyze
            
        Returns:
            List of potential diagnoses with probabilities
        """
        self.logger.info(f"AI analysis requested for episode {episode_id} with symptoms: {symptoms}")
        
        # Placeholder: Return empty list until AI integration is implemented
        return []
    
    def generate_diagnosis_recommendations(self, episode_id: str) -> Dict[str, Any]:
        """
        Placeholder for AI-powered diagnosis recommendations
        TODO: Implement AI integration
        
        Args:
            episode_id: Episode UUID
            
        Returns:
            Dictionary with diagnosis recommendations
        """
        self.logger.info(f"Diagnosis recommendations requested for episode {episode_id}")
        
        # Placeholder: Return empty recommendations until AI integration is implemented
        return {
            "recommendations": [],
            "confidence": 0.0,
            "reasoning": "AI integration not yet implemented"
        }
    
    def _confidence_to_probability(self, confidence_level: str) -> float:
        """
        Convert confidence level to probability estimate
        
        Args:
            confidence_level: Confidence level string
            
        Returns:
            Probability estimate (0-1)
        """
        mapping = {
            "very_low": 0.2,
            "low": 0.4,
            "medium": 0.6,
            "high": 0.8,
            "very_high": 0.95
        }
        return mapping.get(confidence_level, 0.5)
    
    def _is_valid_icd10_format(self, icd_code: str) -> bool:
        """
        Basic ICD-10 code format validation
        
        Args:
            icd_code: ICD-10 code to validate
            
        Returns:
            True if format appears valid
        """
        import re
        
        # Basic ICD-10 pattern: Letter + 2 digits + optional additional characters
        pattern = r'^[A-Z]\d{2}(\.\d{1,2})?$'
        return bool(re.match(pattern, icd_code))