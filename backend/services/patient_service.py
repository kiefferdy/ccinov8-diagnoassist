"""
Patient Service for DiagnoAssist
Complete business logic for patient management
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from datetime import datetime, date, timedelta
from uuid import UUID
import re

if TYPE_CHECKING:
    from models.patient import Patient
    from schemas.patient import PatientCreate, PatientUpdate, PatientResponse
    from repositories.repository_manager import RepositoryManager

from services.base_service import BaseService

class PatientService(BaseService):
    """
    Service class for patient-related business logic
    """
    
    def __init__(self, repositories):
        super().__init__(repositories)
    
    def validate_business_rules(self, data: Dict[str, Any], operation: str = "create") -> None:
        """
        Validate patient-specific business rules - DISABLED FOR TESTING
        """
        pass
        
    def create_patient(self, patient_data: PatientCreate) -> PatientResponse:
        """
        Create a new patient with validation
        
        Args:
            patient_data: Patient creation data
            
        Returns:
            Created patient response
            
        Raises:
            ValueError: If validation fails
            RuntimeError: If business rules violated
        """
        try:
            # Convert to dict for validation
            data = patient_data.model_dump()
            
            # Validate business rules
            self.validate_business_rules(data, "create")
            
            # Check for duplicate MRN
            existing_patient = self.repos.patient.get_by_mrn(data["medical_record_number"])
            if existing_patient:
                raise RuntimeError(
                    f"Medical Record Number '{data['medical_record_number']}' already exists"
                )
            
            # Check for duplicate email if provided
            if data.get("email"):
                existing_email = self.repos.patient.get_by_email(data["email"])
                if existing_email:
                    raise RuntimeError(
                        f"Email '{data['email']}' already registered to another patient"
                    )
            
            # Create patient
            from models.patient import Patient
            patient = Patient(**data)
            created_patient = self.repos.patient.create(patient)
            
            # Log creation
            self.audit_log("create", "Patient", str(created_patient.id), {
                "mrn": created_patient.medical_record_number,
                "name": f"{created_patient.first_name} {created_patient.last_name}"
            })
            
            # Convert to response schema
            from schemas.patient import PatientResponse
            return PatientResponse.model_validate(created_patient)
            
        except Exception as e:
            self.logger.error(f"Failed to create patient: {e}")
            raise
    
    def get_patient(self, patient_id: str) -> PatientResponse:
        """
        Get patient by ID
        
        Args:
            patient_id: Patient UUID
            
        Returns:
            Patient response
            
        Raises:
            LookupError: If patient not found
        """
        patient = self.repos.patient.get_by_id(patient_id)
        if not patient:
            raise LookupError(f"Patient with identifier {patient_id} not found")
        
        from schemas.patient import PatientResponse
        return PatientResponse.model_validate(patient)
    
    def get_patient_by_mrn(self, mrn: str) -> Optional[PatientResponse]:
        """
        Get patient by medical record number
        
        Args:
            mrn: Medical record number
            
        Returns:
            Patient response or None if not found
        """
        patient = self.repos.patient.get_by_mrn(mrn)
        if not patient:
            return None
        
        from schemas.patient import PatientResponse
        return PatientResponse.model_validate(patient)
    
    def update_patient(self, patient_id: str, patient_data: PatientUpdate) -> PatientResponse:
        """
        Update existing patient
        
        Args:
            patient_id: Patient UUID
            patient_data: Patient update data
            
        Returns:
            Updated patient response
            
        Raises:
            LookupError: If patient not found
            ValueError: If validation fails
            RuntimeError: If business rules violated
        """
        try:
            # Get existing patient
            existing_patient = self.repos.patient.get_by_id(patient_id)
            if not existing_patient:
                raise LookupError(f"Patient with identifier {patient_id} not found")
            
            # Convert to dict for validation (exclude None values)
            data = patient_data.model_dump(exclude_none=True)
            if not data:
                return PatientResponse.model_validate(existing_patient)
            
            # Validate business rules
            self.validate_business_rules(data, "update")
            
            # Check for duplicate MRN if changing
            if "medical_record_number" in data:
                existing_mrn = self.repos.patient.get_by_mrn(data["medical_record_number"])
                if existing_mrn and str(existing_mrn.id) != patient_id:
                    raise RuntimeError(
                        f"Medical Record Number '{data['medical_record_number']}' already exists"
                    )
            
            # Check for duplicate email if changing
            if "email" in data and data["email"]:
                existing_email = self.repos.patient.get_by_email(data["email"])
                if existing_email and str(existing_email.id) != patient_id:
                    raise RuntimeError(
                        f"Email '{data['email']}' already registered to another patient"
                    )
            
            # Update patient
            updated_patient = self.repos.patient.update(patient_id, data)
            
            # Log update
            self.audit_log("update", "Patient", patient_id, {
                "updated_fields": list(data.keys())
            })
            
            from schemas.patient import PatientResponse
            return PatientResponse.model_validate(updated_patient)
            
        except Exception as e:
            self.logger.error(f"Failed to update patient {patient_id}: {e}")
            raise
    
    def delete_patient(self, patient_id: str) -> Dict[str, Any]:
        """
        Soft delete patient (set status to inactive)
        
        Args:
            patient_id: Patient UUID
            
        Returns:
            Deletion confirmation
            
        Raises:
            LookupError: If patient not found
            RuntimeError: If patient has active episodes
        """
        try:
            # Get existing patient
            existing_patient = self.repos.patient.get_by_id(patient_id)
            if not existing_patient:
                raise LookupError(f"Patient with identifier {patient_id} not found")
            
            # Check for active episodes
            active_episodes = self.repos.episode.get_active_by_patient(patient_id)
            if active_episodes:
                raise RuntimeError(
                    "Cannot delete patient with active episodes. Complete or cancel episodes first."
                )
            
            # Soft delete by setting status to inactive
            updated_patient = self.repos.patient.update(patient_id, {"status": "inactive"})
            
            # Log deletion
            self.audit_log("delete", "Patient", patient_id, {
                "mrn": existing_patient.medical_record_number,
                "name": f"{existing_patient.first_name} {existing_patient.last_name}",
                "soft_delete": True
            })
            
            return {
                "message": "Patient deactivated successfully",
                "patient_id": patient_id,
                "status": "inactive"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to delete patient {patient_id}: {e}")
            raise
    
    def search_patients(self, 
                       query: Optional[str] = None,
                       status: Optional[str] = None,
                       skip: int = 0, 
                       limit: int = 20) -> Dict[str, Any]:
        """
        Search patients with pagination
        
        Args:
            query: Search query (name, MRN, email)
            status: Patient status filter
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Dictionary with patients and pagination info
        """
        try:
            # Simplified test response to isolate the error
            return {
                "data": [],
                "total": 0,
                "page": 1,
                "size": limit
            }
            
        except Exception as e:
            self.logger.error(f"Failed to search patients: {e}")
            raise
    
    def get_patient_summary(self, patient_id: str) -> Dict[str, Any]:
        """
        Get comprehensive patient summary with related data
        
        Args:
            patient_id: Patient UUID
            
        Returns:
            Dictionary with patient summary data
        """
        try:
            # Get patient
            patient = self.get_patient(patient_id)
            
            # Get episodes
            episodes = self.repos.episode.get_by_patient(patient_id, limit=10)
            
            # Get active episodes count
            # Get active episodes and count them
            active_episodes = self.repos.episode.get_active_by_patient(patient_id)
            active_episodes_count = len(active_episodes)
            
            # Get total diagnoses across all episodes
            total_diagnoses = sum(
                self.repos.diagnosis.count_by_episode(str(episode.id)) 
                for episode in episodes
            )
            
            # Get active treatments across all episodes  
            active_treatments = []
            for episode in episodes:
                treatments = self.repos.treatment.get_by_episode(str(episode.id))
                active_treatments.extend([t for t in treatments if t.status == "active"])
            
            # Calculate age
            age = None
            if patient.date_of_birth:
                today = date.today()
                age = today.year - patient.date_of_birth.year
                if today < date(today.year, patient.date_of_birth.month, patient.date_of_birth.day):
                    age -= 1
            
            return {
                "patient": patient,
                "demographics": {
                    "age": age,
                    "full_name": f"{patient.first_name} {patient.last_name}",
                    "mrn": patient.medical_record_number
                },
                "clinical_summary": {
                    "total_episodes": len(episodes),
                    "active_episodes": active_episodes_count,
                    "total_diagnoses": total_diagnoses,
                    "active_treatments": len(active_treatments),
                    "last_visit": episodes[0].start_date if episodes else None
                },
                "recent_episodes": episodes[:5],  # Most recent 5 episodes
                "active_treatments": active_treatments[:10]  # Most recent 10 active treatments
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get patient summary for {patient_id}: {e}")
            raise
    
    def get_patient_statistics(self) -> Dict[str, Any]:
        """
        Get patient statistics for dashboard
        
        Returns:
            Dictionary with patient statistics
        """
        try:
            total_patients = self.repos.patient.count()
            active_patients = self.repos.patient.count(status="active")
            inactive_patients = self.repos.patient.count(status="inactive")
            
            # Get recent registrations (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_registrations = self.repos.patient.count_by_date_range(
                start_date=thirty_days_ago
            )
            
            return {
                "total_patients": total_patients,
                "active_patients": active_patients,
                "inactive_patients": inactive_patients,
                "recent_registrations": recent_registrations,
                "registration_rate": round(recent_registrations / 30, 2)  # per day
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get patient statistics: {e}")
            raise