"""
Diagnosis Service for DiagnoAssist
Complete business logic for clinical diagnosis management
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from datetime import datetime, timedelta
from uuid import UUID
import re

if TYPE_CHECKING:
    from models.diagnosis import Diagnosis
    from schemas.diagnosis import DiagnosisCreate, DiagnosisUpdate, DiagnosisResponse
    from repositories.repository_manager import RepositoryManager

from services.base_service import BaseService

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
            operation: Type of operation (create, update)
        """
        # Business rules validation can be implemented here as needed
        pass
    
    def create_diagnosis(self, diagnosis_data: DiagnosisCreate) -> DiagnosisResponse:
        """
        Create a new diagnosis with validation
        
        Args:
            diagnosis_data: Diagnosis creation data
            
        Returns:
            Created diagnosis response
            
        Raises:
            ValueError: If validation fails
            RuntimeError: If business rules violated
        """
        try:
            # Convert to dict for validation
            data = diagnosis_data.model_dump()
            
            # Validate business rules
            self.validate_business_rules(data, "create")
            
            # Verify episode exists
            episode = self.repos.episode.get_by_id(str(data["episode_id"]))
            if not episode:
                raise LookupError("Episode", str(data["episode_id"]))
            
            # If this is AI-generated, set appropriate metadata
            if data.get("ai_probability") and not data.get("created_by"):
                data["created_by"] = "ai_system"
            
            # Create diagnosis
            from models.diagnosis import Diagnosis
            diagnosis = Diagnosis(**data)
            created_diagnosis = self.repos.diagnosis.create(diagnosis)
            
            # If this is set as final diagnosis, update any existing final diagnosis
            if data.get("final_diagnosis"):
                self._handle_final_diagnosis_update(str(data["episode_id"]), str(created_diagnosis.id))
            
            # Log creation
            self.audit_log("create", "Diagnosis", str(created_diagnosis.id), {
                "episode_id": str(created_diagnosis.episode_id),
                "condition": created_diagnosis.condition_name,
                "final_diagnosis": created_diagnosis.final_diagnosis,
                "ai_generated": bool(created_diagnosis.ai_probability)
            })
            
            # Convert to response schema
            from schemas.diagnosis import DiagnosisResponse
            return DiagnosisResponse.model_validate(created_diagnosis)
            
        except Exception as e:
            self.logger.error(f"Failed to create diagnosis: {e}")
            raise
    
    def get_diagnosis(self, diagnosis_id: str) -> DiagnosisResponse:
        """
        Get diagnosis by ID
        
        Args:
            diagnosis_id: Diagnosis UUID
            
        Returns:
            Diagnosis response
            
        Raises:
            LookupError: If diagnosis not found
        """
        diagnosis = self.repos.diagnosis.get_by_id(diagnosis_id)
        if not diagnosis:
            raise LookupError("Diagnosis", diagnosis_id)
        
        from schemas.diagnosis import DiagnosisResponse
        return DiagnosisResponse.model_validate(diagnosis)
    
    def update_diagnosis(self, diagnosis_id: str, diagnosis_data: DiagnosisUpdate) -> DiagnosisResponse:
        """
        Update existing diagnosis
        
        Args:
            diagnosis_id: Diagnosis UUID
            diagnosis_data: Diagnosis update data
            
        Returns:
            Updated diagnosis response
            
        Raises:
            LookupError: If diagnosis not found
            ValueError: If validation fails
            RuntimeError: If business rules violated
        """
        try:
            # Get existing diagnosis
            existing_diagnosis = self.repos.diagnosis.get_by_id(diagnosis_id)
            if not existing_diagnosis:
                raise LookupError("Diagnosis", diagnosis_id)
            
            # Convert to dict for validation (exclude None values)
            data = diagnosis_data.model_dump(exclude_none=True)
            if not data:
                return DiagnosisResponse.model_validate(existing_diagnosis)
            
            # Validate business rules
            self.validate_business_rules(data, "update")
            
            # Handle final diagnosis logic
            if "final_diagnosis" in data and data["final_diagnosis"]:
                episode_id = str(existing_diagnosis.episode_id)
                existing_final = self.repos.diagnosis.get_final_diagnosis_by_episode(episode_id)
                if existing_final and str(existing_final.id) != diagnosis_id:
                    raise RuntimeError(
                        "Episode already has a final diagnosis. Clear existing final diagnosis first"
                    )
            
            # Update diagnosis
            updated_diagnosis = self.repos.diagnosis.update(diagnosis_id, data)
            
            # Handle final diagnosis updates
            if data.get("final_diagnosis"):
                self._handle_final_diagnosis_update(str(updated_diagnosis.episode_id), diagnosis_id)
            
            # Log update
            self.audit_log("update", "Diagnosis", diagnosis_id, {
                "updated_fields": list(data.keys()),
                "episode_id": str(updated_diagnosis.episode_id)
            })
            
            from schemas.diagnosis import DiagnosisResponse
            return DiagnosisResponse.model_validate(updated_diagnosis)
            
        except Exception as e:
            self.logger.error(f"Failed to update diagnosis {diagnosis_id}: {e}")
            raise
    
    def delete_diagnosis(self, diagnosis_id: str) -> Dict[str, Any]:
        """
        Soft delete diagnosis (set status to inactive)
        
        Args:
            diagnosis_id: Diagnosis UUID
            
        Returns:
            Deletion confirmation
            
        Raises:
            LookupError: If diagnosis not found
            RuntimeError: If diagnosis has dependent treatments
        """
        try:
            # Get existing diagnosis
            existing_diagnosis = self.repos.diagnosis.get_by_id(diagnosis_id)
            if not existing_diagnosis:
                raise LookupError("Diagnosis", diagnosis_id)
            
            # Check for dependent treatments
            treatments = self.repos.treatment.get_by_diagnosis_id(diagnosis_id)
            active_treatments = [t for t in treatments if t.status == "active"]
            if active_treatments:
                raise RuntimeError(
                    f"Cannot delete diagnosis with {len(active_treatments)} active treatments. "
                    "Complete or cancel treatments first."
                )
            
            # Soft delete by setting status to inactive
            updated_diagnosis = self.repos.diagnosis.update(diagnosis_id, {"status": "inactive"})
            
            # Log deletion
            self.audit_log("delete", "Diagnosis", diagnosis_id, {
                "episode_id": str(existing_diagnosis.episode_id),
                "condition": existing_diagnosis.condition_name,
                "soft_delete": True
            })
            
            return {
                "message": "Diagnosis deactivated successfully",
                "diagnosis_id": diagnosis_id,
                "status": "inactive"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to delete diagnosis {diagnosis_id}: {e}")
            raise
    
    def get_diagnoses_by_episode(self, episode_id: str) -> List[DiagnosisResponse]:
        """
        Get all diagnoses for an episode
        
        Args:
            episode_id: Episode UUID
            
        Returns:
            List of diagnosis responses
        """
        try:
            diagnoses = self.repos.diagnosis.get_by_episode(episode_id)
            
            from schemas.diagnosis import DiagnosisResponse
            return [DiagnosisResponse.model_validate(d) for d in diagnoses]
            
        except Exception as e:
            self.logger.error(f"Failed to get diagnoses for episode {episode_id}: {e}")
            raise
    
    def get_differential_diagnoses(self, episode_id: str) -> List[DiagnosisResponse]:
        """
        Get differential diagnoses for an episode (non-final diagnoses)
        
        Args:
            episode_id: Episode UUID
            
        Returns:
            List of differential diagnosis responses
        """
        try:
            diagnoses = self.repos.diagnosis.get_differential_by_episode(episode_id)
            
            from schemas.diagnosis import DiagnosisResponse
            return [DiagnosisResponse.model_validate(d) for d in diagnoses]
            
        except Exception as e:
            self.logger.error(f"Failed to get differential diagnoses for episode {episode_id}: {e}")
            raise
    
    def get_final_diagnosis(self, episode_id: str) -> Optional[DiagnosisResponse]:
        """
        Get final diagnosis for an episode
        
        Args:
            episode_id: Episode UUID
            
        Returns:
            Final diagnosis response or None if not set
        """
        try:
            diagnosis = self.repos.diagnosis.get_final_diagnosis_by_episode(episode_id)
            if not diagnosis:
                return None
            
            from schemas.diagnosis import DiagnosisResponse
            return DiagnosisResponse.model_validate(diagnosis)
            
        except Exception as e:
            self.logger.error(f"Failed to get final diagnosis for episode {episode_id}: {e}")
            raise
    
    def set_final_diagnosis(self, episode_id: str, diagnosis_id: str) -> DiagnosisResponse:
        """
        Set a diagnosis as the final diagnosis for an episode
        
        Args:
            episode_id: Episode UUID
            diagnosis_id: Diagnosis UUID to set as final
            
        Returns:
            Updated diagnosis response
            
        Raises:
            LookupError: If diagnosis not found
            RuntimeError: If diagnosis doesn't belong to episode
        """
        try:
            # Get and validate diagnosis
            diagnosis = self.repos.diagnosis.get_by_id(diagnosis_id)
            if not diagnosis:
                raise LookupError("Diagnosis", diagnosis_id)
            
            if str(diagnosis.episode_id) != episode_id:
                raise RuntimeError(
                    "Diagnosis does not belong to the specified episode"
                )
            
            # Clear any existing final diagnosis
            existing_final = self.repos.diagnosis.get_final_diagnosis_by_episode(episode_id)
            if existing_final and str(existing_final.id) != diagnosis_id:
                self.repos.diagnosis.update(str(existing_final.id), {"final_diagnosis": False})
            
            # Set new final diagnosis
            updated_diagnosis = self.repos.diagnosis.update(diagnosis_id, {
                "final_diagnosis": True,
                "physician_confirmed": True
            })
            
            # Log final diagnosis setting
            self.audit_log("set_final", "Diagnosis", diagnosis_id, {
                "episode_id": episode_id,
                "condition": updated_diagnosis.condition_name
            })
            
            from schemas.diagnosis import DiagnosisResponse
            return DiagnosisResponse.model_validate(updated_diagnosis)
            
        except Exception as e:
            self.logger.error(f"Failed to set final diagnosis {diagnosis_id} for episode {episode_id}: {e}")
            raise
    
    def confirm_physician_diagnosis(self, 
                                  diagnosis_id: str, 
                                  physician_notes: Optional[str] = None,
                                  confidence_level: Optional[str] = None) -> DiagnosisResponse:
        """
        Confirm diagnosis by physician
        
        Args:
            diagnosis_id: Diagnosis UUID
            physician_notes: Optional physician notes
            confidence_level: Optional confidence level update
            
        Returns:
            Updated diagnosis response
        """
        try:
            # Prepare update data
            update_data = {"physician_confirmed": True}
            
            if physician_notes:
                update_data["physician_notes"] = physician_notes
            
            if confidence_level:
                if confidence_level not in ["low", "medium", "high"]:
                    raise ValueError(
                        "Confidence level must be low, medium, or high",
                        field="confidence_level",
                        value=confidence_level
                    )
                update_data["confidence_level"] = confidence_level
            
            # Update diagnosis
            updated_diagnosis = self.repos.diagnosis.update(diagnosis_id, update_data)
            
            # Log physician confirmation
            self.audit_log("physician_confirm", "Diagnosis", diagnosis_id, {
                "physician_notes_added": bool(physician_notes),
                "confidence_updated": bool(confidence_level)
            })
            
            from schemas.diagnosis import DiagnosisResponse
            return DiagnosisResponse.model_validate(updated_diagnosis)
            
        except Exception as e:
            self.logger.error(f"Failed to confirm diagnosis {diagnosis_id}: {e}")
            raise
    
    def generate_ai_differential_diagnoses(self, 
                                         episode_id: str,
                                         symptoms: List[str],
                                         patient_data: Dict[str, Any],
                                         limit: int = 5) -> List[DiagnosisResponse]:
        """
        Generate AI-based differential diagnoses
        
        Args:
            episode_id: Episode UUID
            symptoms: List of symptoms
            patient_data: Patient demographic and medical history data
            limit: Maximum number of diagnoses to generate
            
        Returns:
            List of AI-generated diagnosis responses
            
        Note:
            This is a placeholder for AI integration.
            In production, this would call an AI service.
        """
        try:
            # Verify episode exists
            episode = self.repos.episode.get_by_id(episode_id)
            if not episode:
                raise LookupError("Episode", episode_id)
            
            # Placeholder AI differential diagnosis generation
            # In production, this would integrate with medical AI service
            mock_differentials = self._generate_mock_differentials(symptoms, patient_data, limit)
            
            created_diagnoses = []
            for diff_data in mock_differentials:
                diff_data["episode_id"] = UUID(episode_id)
                diff_data["created_by"] = "ai_system"
                diff_data["final_diagnosis"] = False
                
                from schemas.diagnosis import DiagnosisCreate
                diagnosis_create = DiagnosisCreate(**diff_data)
                created_diagnosis = self.create_diagnosis(diagnosis_create)
                created_diagnoses.append(created_diagnosis)
            
            # Log AI generation
            self.audit_log("ai_generate", "Diagnosis", episode_id, {
                "symptoms_count": len(symptoms),
                "diagnoses_generated": len(created_diagnoses),
                "ai_system": "mock_ai"  # Replace with actual AI system name
            })
            
            return created_diagnoses
            
        except Exception as e:
            self.logger.error(f"Failed to generate AI differential diagnoses for episode {episode_id}: {e}")
            raise
    
    def search_diagnoses(self, 
                        query: Optional[str] = None,
                        episode_id: Optional[str] = None,
                        patient_id: Optional[str] = None,
                        confidence_level: Optional[str] = None,
                        final_only: bool = False,
                        skip: int = 0, 
                        limit: int = 20) -> Dict[str, Any]:
        """
        Search diagnoses with various filters
        
        Args:
            query: Search query for condition name
            episode_id: Filter by episode
            patient_id: Filter by patient
            confidence_level: Filter by confidence level
            final_only: Return only final diagnoses
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Dictionary with diagnoses and pagination info
        """
        try:
            # Map service parameters to repository parameters
            search_term = query if query else ""
            diagnoses = self.repos.diagnosis.search_diagnoses(
                search_term=search_term,
                skip=skip,
                limit=limit
            )
            
            # Use simple count for now (can be enhanced later for filtering)
            total_count = self.repos.diagnosis.count()
            
            from schemas.diagnosis import DiagnosisResponse
            diagnosis_responses = [DiagnosisResponse.model_validate(d) for d in diagnoses]
            
            return {
                "data": diagnosis_responses,
                "total": total_count,
                "page": (skip // limit) + 1,
                "size": limit
            }
            
        except Exception as e:
            self.logger.error(f"Failed to search diagnoses: {e}")
            raise
    
    def get_diagnosis_statistics(self) -> Dict[str, Any]:
        """
        Get diagnosis statistics for dashboard
        
        Returns:
            Dictionary with diagnosis statistics
        """
        try:
            total_diagnoses = self.repos.diagnosis.count()
            ai_generated = self.repos.diagnosis.count_ai_generated()
            physician_confirmed = self.repos.diagnosis.count_physician_confirmed()
            final_diagnoses = self.repos.diagnosis.count_final_diagnoses()
            
            # Get recent diagnoses (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_diagnoses = self.repos.diagnosis.count_by_date_range(
                start_date=thirty_days_ago
            )
            
            return {
                "total_diagnoses": total_diagnoses,
                "ai_generated": ai_generated,
                "physician_confirmed": physician_confirmed,
                "final_diagnoses": final_diagnoses,
                "recent_diagnoses": recent_diagnoses,
                "ai_accuracy_rate": round(physician_confirmed / max(ai_generated, 1), 2),
                "final_diagnosis_rate": round(final_diagnoses / max(total_diagnoses, 1), 2)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get diagnosis statistics: {e}")
            raise
    
    def _handle_final_diagnosis_update(self, episode_id: str, diagnosis_id: str) -> None:
        """
        Handle logic when setting a diagnosis as final
        
        Args:
            episode_id: Episode UUID
            diagnosis_id: Diagnosis UUID being set as final
        """
        # Clear any other final diagnoses for this episode
        existing_final = self.repos.diagnosis.get_final_diagnosis_by_episode(episode_id)
        if existing_final and str(existing_final.id) != diagnosis_id:
            self.repos.diagnosis.update(str(existing_final.id), {"final_diagnosis": False})
        
        # Update episode status if needed
        self.repos.episode.update(episode_id, {"status": "diagnosed"})
    
    def _generate_mock_differentials(self, 
                                   symptoms: List[str], 
                                   patient_data: Dict[str, Any], 
                                   limit: int) -> List[Dict[str, Any]]:
        """
        Generate mock differential diagnoses for testing
        
        Args:
            symptoms: List of symptoms
            patient_data: Patient data
            limit: Maximum number of diagnoses
            
        Returns:
            List of mock diagnosis data
            
        Note:
            This is a placeholder. In production, replace with actual AI service.
        """
        # Mock data based on common symptoms
        mock_database = {
            "fever": [
                {"condition_name": "Viral Upper Respiratory Infection", "probability": 0.65, "icd10_code": "J06.9"},
                {"condition_name": "Bacterial Pneumonia", "probability": 0.25, "icd10_code": "J15.9"},
                {"condition_name": "Influenza", "probability": 0.45, "icd10_code": "J11.1"}
            ],
            "chest pain": [
                {"condition_name": "Gastroesophageal Reflux Disease", "probability": 0.55, "icd10_code": "K21.9"},
                {"condition_name": "Costochondritis", "probability": 0.35, "icd10_code": "M94.0"},
                {"condition_name": "Myocardial Infarction", "probability": 0.15, "icd10_code": "I21.9"}
            ],
            "headache": [
                {"condition_name": "Tension Headache", "probability": 0.70, "icd10_code": "G44.2"},
                {"condition_name": "Migraine", "probability": 0.25, "icd10_code": "G43.9"},
                {"condition_name": "Sinusitis", "probability": 0.40, "icd10_code": "J32.9"}
            ]
        }
        
        # Simple matching logic
        candidates = []
        for symptom in symptoms:
            symptom_lower = symptom.lower()
            for key, diagnoses in mock_database.items():
                if key in symptom_lower:
                    candidates.extend(diagnoses)
        
        # Remove duplicates and sort by probability
        seen = set()
        unique_candidates = []
        for candidate in sorted(candidates, key=lambda x: x["probability"], reverse=True):
            condition = candidate["condition_name"]
            if condition not in seen:
                seen.add(condition)
                unique_candidates.append({
                    **candidate,
                    "ai_probability": candidate["probability"],
                    "confidence_level": "medium" if candidate["probability"] > 0.5 else "low",
                    "ai_reasoning": f"Based on symptom pattern: {', '.join(symptoms[:3])}",
                    "supporting_symptoms": "; ".join(symptoms),
                })
        
        return unique_candidates[:limit]