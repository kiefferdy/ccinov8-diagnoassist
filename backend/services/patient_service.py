"""
Patient Service for DiagnoAssist
Business logic for patient management
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from datetime import datetime, date
from uuid import UUID
import re

if TYPE_CHECKING:
    from models.patient import Patient
    from schemas.patient import PatientCreate, PatientUpdate, PatientResponse
    from repositories.repository_manager import RepositoryManager

from services.base_service import BaseService, ValidationException, BusinessRuleException, ResourceNotFoundException

class PatientService(BaseService):
    """
    Service class for patient-related business logic
    """
    
    def __init__(self, repositories):
        super().__init__(repositories)
    
    def validate_business_rules(self, data: Dict[str, Any], operation: str = "create") -> None:
        """
        Validate patient-specific business rules
        
        Args:
            data: Patient data to validate
            operation: Operation being performed
            
        Raises:
            BusinessRuleException: If business rules are violated
            ValidationException: If validation fails
        """
        # Validate email format
        if "email" in data and data["email"]:
            if not self._is_valid_email(data["email"]):
                raise ValidationException(
                    f"Invalid email format: {data['email']}",
                    field="email",
                    value=data["email"]
                )
        
        # Validate phone format
        if "phone" in data and data["phone"]:
            if not self._is_valid_phone(data["phone"]):
                raise ValidationException(
                    f"Invalid phone format: {data['phone']}",
                    field="phone", 
                    value=data["phone"]
                )
        
        # Validate date of birth
        if "date_of_birth" in data and data["date_of_birth"]:
            dob = data["date_of_birth"]
            if isinstance(dob, str):
                try:
                    dob = datetime.strptime(dob, "%Y-%m-%d").date()
                except ValueError:
                    raise ValidationException(
                        f"Invalid date format: {data['date_of_birth']}. Expected YYYY-MM-DD",
                        field="date_of_birth",
                        value=data["date_of_birth"]
                    )
            
            # Check if date of birth is in the future
            if dob > date.today():
                raise BusinessRuleException(
                    "Date of birth cannot be in the future",
                    rule="future_date_of_birth"
                )
            
            # Check if age is reasonable (not older than 150 years)
            age = (date.today() - dob).days // 365
            if age > 150:
                raise BusinessRuleException(
                    f"Age of {age} years is not reasonable",
                    rule="unreasonable_age"
                )
        
        # Validate gender
        if "gender" in data and data["gender"]:
            valid_genders = ["male", "female", "other", "unknown"]
            if data["gender"].lower() not in valid_genders:
                raise ValidationException(
                    f"Gender must be one of: {', '.join(valid_genders)}",
                    field="gender",
                    value=data["gender"]
                )
        
        # For updates, check if medical record number is being changed
        if operation == "update" and "medical_record_number" in data:
            raise BusinessRuleException(
                "Medical record number cannot be changed after creation",
                rule="immutable_mrn"
            )
    
    def create_patient(self, patient_data: PatientCreate) -> PatientResponse:
        """
        Create a new patient with business rule validation
        
        Args:
            patient_data: Patient creation data
            
        Returns:
            PatientResponse: Created patient data
            
        Raises:
            ValidationException: If validation fails
            BusinessRuleException: If business rules are violated
            ServiceException: If creation fails
        """
        try:
            # Convert Pydantic model to dict for validation
            data_dict = patient_data.model_dump()
            
            # Validate required fields
            self.validate_required_fields(data_dict, [
                "medical_record_number", "first_name", "last_name", 
                "date_of_birth", "gender"
            ])
            
            # Validate business rules
            self.validate_business_rules(data_dict, operation="create")
            
            # Check for duplicate medical record number
            existing_patient = self.repos.patient.get_by_mrn(data_dict["medical_record_number"])
            if existing_patient:
                raise BusinessRuleException(
                    f"Patient with medical record number '{data_dict['medical_record_number']}' already exists",
                    rule="unique_mrn"
                )
            
            # Check for duplicate email if provided
            if data_dict.get("email"):
                existing_email = self.repos.patient.get_by_email(data_dict["email"])
                if existing_email:
                    raise BusinessRuleException(
                        f"Patient with email '{data_dict['email']}' already exists",
                        rule="unique_email"
                    )
            
            # Generate patient identifier if not provided
            if not data_dict.get("patient_identifier"):
                data_dict["patient_identifier"] = self._generate_patient_identifier(data_dict)
            
            # Create patient
            patient = self.repos.patient.create(data_dict)
            self.safe_commit("patient creation")
            
            # Audit log
            self.audit_log("create", "Patient", str(patient.id), {
                "medical_record_number": patient.medical_record_number,
                "name": f"{patient.first_name} {patient.last_name}"
            })
            
            return PatientResponse.model_validate(patient)
            
        except (ValidationException, BusinessRuleException):
            self.safe_rollback("patient creation")
            raise
        except Exception as e:
            self.safe_rollback("patient creation")
            if hasattr(e, 'orig') and 'duplicate key' in str(e.orig):
                raise BusinessRuleException(
                    "Patient with this medical record number already exists",
                    rule="unique_mrn"
                )
            raise
    
    def update_patient(self, patient_id: str, patient_data: PatientUpdate) -> PatientResponse:
        """
        Update an existing patient
        
        Args:
            patient_id: Patient UUID
            patient_data: Updated patient data
            
        Returns:
            PatientResponse: Updated patient data
        """
        try:
            # Validate UUID format
            self.validate_uuid(patient_id, "patient_id")
            
            # Get existing patient
            patient = self.get_or_raise("Patient", patient_id, self.repos.patient.get_by_id)
            
            # Convert update data to dict (excluding None values)
            update_dict = patient_data.model_dump(exclude_unset=True)
            
            if not update_dict:
                # No changes to apply
                return PatientResponse.model_validate(patient)
            
            # Validate business rules for update
            self.validate_business_rules(update_dict, operation="update")
            
            # Check for email uniqueness if email is being updated
            if "email" in update_dict and update_dict["email"]:
                existing_email = self.repos.patient.get_by_email(update_dict["email"])
                if existing_email and str(existing_email.id) != patient_id:
                    raise BusinessRuleException(
                        f"Another patient with email '{update_dict['email']}' already exists",
                        rule="unique_email"
                    )
            
            # Update patient
            updated_patient = self.repos.patient.update(patient_id, update_dict)
            self.safe_commit("patient update")
            
            # Audit log
            self.audit_log("update", "Patient", patient_id, {
                "updated_fields": list(update_dict.keys()),
                "medical_record_number": updated_patient.medical_record_number
            })
            
            return PatientResponse.model_validate(updated_patient)
            
        except (ValidationException, BusinessRuleException, ResourceNotFoundException):
            self.safe_rollback("patient update")
            raise
        except Exception as e:
            self.safe_rollback("patient update")
            raise
    
    def get_patient(self, patient_id: str) -> PatientResponse:
        """
        Get patient by ID
        
        Args:
            patient_id: Patient UUID
            
        Returns:
            PatientResponse: Patient data
        """
        self.validate_uuid(patient_id, "patient_id")
        patient = self.get_or_raise("Patient", patient_id, self.repos.patient.get_by_id)
        return PatientResponse.model_validate(patient)
    
    def get_patient_by_mrn(self, medical_record_number: str) -> Optional[PatientResponse]:
        """
        Get patient by medical record number
        
        Args:
            medical_record_number: Medical record number
            
        Returns:
            PatientResponse or None if not found
        """
        if not medical_record_number.strip():
            raise ValidationException("Medical record number cannot be empty")
        
        patient = self.repos.patient.get_by_mrn(medical_record_number.strip())
        return PatientResponse.model_validate(patient) if patient else None
    
    def search_patients(self, 
                       search_term: Optional[str] = None,
                       skip: int = 0, 
                       limit: int = 100) -> List[PatientResponse]:
        """
        Search patients by various criteria
        
        Args:
            search_term: Search term for name, email, or MRN
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of PatientResponse objects
        """
        patients = self.repos.patient.search_patients(search_term, skip=skip, limit=limit)
        return [PatientResponse.model_validate(p) for p in patients]
    
    def get_patient_summary(self, patient_id: str) -> Dict[str, Any]:
        """
        Get patient summary with episode and diagnosis counts
        
        Args:
            patient_id: Patient UUID
            
        Returns:
            Dictionary with patient summary data
        """
        self.validate_uuid(patient_id, "patient_id")
        patient = self.get_or_raise("Patient", patient_id, self.repos.patient.get_by_id)
        
        # Get related counts
        episodes_count = self.repos.episode.count_by_patient(patient_id)
        active_episodes = self.repos.episode.get_active_by_patient(patient_id)
        recent_episodes = self.repos.episode.get_recent_by_patient(patient_id, limit=5)
        
        return {
            "patient": PatientResponse.model_validate(patient),
            "total_episodes": episodes_count,
            "active_episodes_count": len(active_episodes),
            "recent_episodes": [
                {
                    "id": str(ep.id),
                    "chief_complaint": ep.chief_complaint,
                    "start_time": ep.start_time,
                    "status": ep.status
                } for ep in recent_episodes
            ],
            "last_visit": recent_episodes[0].start_time if recent_episodes else None
        }
    
    def deactivate_patient(self, patient_id: str, reason: str) -> PatientResponse:
        """
        Deactivate a patient (soft delete)
        
        Args:
            patient_id: Patient UUID
            reason: Reason for deactivation
            
        Returns:
            PatientResponse: Updated patient data
        """
        try:
            self.validate_uuid(patient_id, "patient_id")
            patient = self.get_or_raise("Patient", patient_id, self.repos.patient.get_by_id)
            
            # Check if patient has active episodes
            active_episodes = self.repos.episode.get_active_by_patient(patient_id)
            if active_episodes:
                raise BusinessRuleException(
                    "Cannot deactivate patient with active episodes",
                    rule="no_active_episodes_for_deactivation"
                )
            
            # Deactivate patient
            updated_patient = self.repos.patient.update(patient_id, {
                "active": False,
                "updated_at": datetime.utcnow()
            })
            self.safe_commit("patient deactivation")
            
            # Audit log
            self.audit_log("deactivate", "Patient", patient_id, {
                "reason": reason,
                "medical_record_number": patient.medical_record_number
            })
            
            return PatientResponse.model_validate(updated_patient)
            
        except (ValidationException, BusinessRuleException, ResourceNotFoundException):
            self.safe_rollback("patient deactivation")
            raise
        except Exception as e:
            self.safe_rollback("patient deactivation")
            raise
    
    def _generate_patient_identifier(self, patient_data: Dict[str, Any]) -> str:
        """
        Generate a unique patient identifier
        
        Args:
            patient_data: Patient data dictionary
            
        Returns:
            Generated patient identifier
        """
        # Use first 3 letters of last name + first letter of first name + timestamp
        last_name = patient_data.get("last_name", "").upper()[:3]
        first_name = patient_data.get("first_name", "").upper()[:1]
        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        
        return f"PAT{last_name}{first_name}{timestamp}"
    
    def _is_valid_email(self, email: str) -> bool:
        """
        Validate email format using regex
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid, False otherwise
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _is_valid_phone(self, phone: str) -> bool:
        """
        Validate phone number format
        
        Args:
            phone: Phone number to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Remove common separators and check if remaining chars are digits
        cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
        return len(cleaned) >= 10 and cleaned.isdigit()