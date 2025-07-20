"""
Patient service for DiagnoAssist Backend with business rules integration
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.models.patient import PatientModel
from app.models.auth import UserModel
from app.repositories.patient_repository import patient_repository
from app.core.exceptions import NotFoundError, ConflictException
from app.core.business_rules import business_rules_engine, RuleContext, RuleSeverity

logger = logging.getLogger(__name__)


class PatientService:
    """Service for patient business logic and operations with business rules"""
    
    def __init__(self):
        self.patient_repo = patient_repository
    
    async def register_patient(
        self, 
        patient: PatientModel, 
        user: Optional[UserModel] = None
    ) -> PatientModel:
        """Register a new patient with business rules validation"""
        try:
            # Check for existing patient with same email
            if patient.demographics.email:
                existing_patient = await self.patient_repo.get_by_email(patient.demographics.email)
                if existing_patient:
                    raise ConflictException(
                        f"Patient with email {patient.demographics.email} already exists",
                        "patient",
                        {"email": patient.demographics.email, "existing_id": existing_patient.id}
                    )
            
            # Apply business rules validation
            violations = await business_rules_engine.validate(
                patient, 
                RuleContext.PATIENT_REGISTRATION,
                user=user,
                additional_data={"action": "register_patient"}
            )
            
            # Log warnings but don't block registration
            warnings = [v for v in violations if v.severity == RuleSeverity.WARNING]
            if warnings:
                logger.warning(f"Patient registration warnings: {[w.message for w in warnings]}")
            
            # Raise exception for errors or critical violations
            blocking_violations = [
                v for v in violations 
                if v.severity in [RuleSeverity.ERROR, RuleSeverity.CRITICAL]
            ]
            if blocking_violations:
                from app.core.exceptions import BusinessRuleException
                raise BusinessRuleException(
                    "Patient registration validation failed",
                    violations=blocking_violations
                )
            
            # Create patient
            created_patient = await self.patient_repo.create(patient)
            
            logger.info(f"Registered patient {created_patient.id}: {patient.demographics.name}")
            
            return created_patient
            
        except Exception as e:
            logger.error(f"Error registering patient: {e}")
            raise
    
    async def update_patient(
        self, 
        patient_id: str, 
        patient_updates: PatientModel,
        user: Optional[UserModel] = None
    ) -> PatientModel:
        """Update an existing patient with business rules validation"""
        try:
            # Get existing patient
            existing = await self.patient_repo.get_by_id(patient_id)
            if not existing:
                raise NotFoundError("Patient", patient_id)
            
            # Check for email conflicts if email is being changed
            if (patient_updates.demographics.email and 
                patient_updates.demographics.email != existing.demographics.email):
                
                existing_with_email = await self.patient_repo.get_by_email(patient_updates.demographics.email)
                if existing_with_email and existing_with_email.id != patient_id:
                    raise ConflictException(
                        f"Another patient already has email {patient_updates.demographics.email}",
                        "patient",
                        {"email": patient_updates.demographics.email, "existing_id": existing_with_email.id}
                    )
            
            # Apply business rules validation  
            violations = await business_rules_engine.validate(
                patient_updates, 
                RuleContext.PATIENT_REGISTRATION,  # Reuse registration rules for updates
                user=user,
                additional_data={"action": "update_patient", "existing_patient": existing}
            )
            
            # Log warnings but don't block update
            warnings = [v for v in violations if v.severity == RuleSeverity.WARNING]
            if warnings:
                logger.warning(f"Patient update warnings: {[w.message for w in warnings]}")
            
            # Raise exception for errors or critical violations
            blocking_violations = [
                v for v in violations 
                if v.severity in [RuleSeverity.ERROR, RuleSeverity.CRITICAL]
            ]
            if blocking_violations:
                from app.core.exceptions import BusinessRuleException
                raise BusinessRuleException(
                    "Patient update validation failed",
                    violations=blocking_violations
                )
            
            # Update patient
            updated_patient = await self.patient_repo.update(patient_id, patient_updates)
            
            logger.info(f"Updated patient {patient_id}")
            
            return updated_patient
            
        except Exception as e:
            logger.error(f"Error updating patient {patient_id}: {e}")
            raise
    
    async def get_patient_with_validation(self, patient_id: str) -> PatientModel:
        """Get a patient with existence validation"""
        patient = await self.patient_repo.get_by_id(patient_id)
        if not patient:
            raise NotFoundError("Patient", patient_id)
        return patient
    
    async def search_patients(
        self, 
        search_params: Dict[str, Any],
        skip: int = 0,
        limit: int = 50
    ) -> List[PatientModel]:
        """Search patients with various filters"""
        try:
            # Extract search parameters
            name = search_params.get("name")
            email = search_params.get("email")
            gender = search_params.get("gender")
            age_min = search_params.get("age_min")
            age_max = search_params.get("age_max")
            
            # Use repository search methods
            if email:
                # Exact email search
                patient = await self.patient_repo.get_by_email(email)
                return [patient] if patient else []
            
            # Demographics filter search
            demographics_filter = {}
            if name:
                demographics_filter["name"] = name
            if gender:
                demographics_filter["gender"] = gender
            
            patients = await self.patient_repo.get_by_demographics_filter(
                skip=skip,
                limit=limit,
                **demographics_filter
            )
            
            # Apply age filtering if specified
            if age_min is not None or age_max is not None:
                filtered_patients = []
                for patient in patients:
                    if patient.demographics.date_of_birth:
                        try:
                            birth_date = patient.demographics.date_of_birth
                            if isinstance(birth_date, str):
                                birth_date = datetime.strptime(birth_date, "%Y-%m-%d")
                            age = (datetime.now() - birth_date).days / 365.25
                            
                            if age_min is not None and age < age_min:
                                continue
                            if age_max is not None and age > age_max:
                                continue
                            
                            filtered_patients.append(patient)
                        except (ValueError, TypeError):
                            # Skip patients with invalid birth dates
                            continue
                patients = filtered_patients
            
            return patients
            
        except Exception as e:
            logger.error(f"Error searching patients: {e}")
            return []
    
    async def validate_patient_data(
        self, 
        patient: PatientModel,
        user: Optional[UserModel] = None
    ) -> Dict[str, Any]:
        """Validate patient data using business rules without saving"""
        try:
            # Run business rules validation
            violations = await business_rules_engine.validate(
                patient, 
                RuleContext.PATIENT_REGISTRATION,
                user=user,
                additional_data={"action": "validate_patient"}
            )
            
            # Categorize violations
            errors = [v for v in violations if v.severity in [RuleSeverity.ERROR, RuleSeverity.CRITICAL]]
            warnings = [v for v in violations if v.severity == RuleSeverity.WARNING]
            info = [v for v in violations if v.severity == RuleSeverity.INFO]
            
            validation_result = {
                "is_valid": len(errors) == 0,
                "can_register": len(errors) == 0,
                "violations": {
                    "errors": [v.model_dump() for v in errors],
                    "warnings": [v.model_dump() for v in warnings],
                    "info": [v.model_dump() for v in info]
                },
                "summary": {
                    "total_violations": len(violations),
                    "error_count": len(errors),
                    "warning_count": len(warnings),
                    "info_count": len(info)
                }
            }
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating patient data: {e}")
            return {
                "is_valid": False,
                "can_register": False,
                "violations": {"errors": [], "warnings": [], "info": []},
                "summary": {"total_violations": 0, "error_count": 1, "warning_count": 0, "info_count": 0},
                "error": str(e)
            }
    
    async def delete_patient(
        self, 
        patient_id: str,
        user: Optional[UserModel] = None
    ) -> bool:
        """Delete a patient with proper authorization checks"""
        try:
            # Get existing patient
            patient = await self.patient_repo.get_by_id(patient_id)
            if not patient:
                raise NotFoundError("Patient", patient_id)
            
            # Check authorization (only admins can delete patients)
            if user:
                from app.core.business_rules import business_rules_engine, RuleContext
                await business_rules_engine.validate_and_raise(
                    patient,
                    RuleContext.PATIENT_REGISTRATION,
                    user=user,
                    additional_data={"action": "delete_patient"}
                )
            
            # TODO: Check for existing encounters/episodes before deletion
            # This should be a business rule to prevent orphaned data
            
            # Delete patient
            await self.patient_repo.delete(patient_id)
            
            logger.info(f"Deleted patient {patient_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting patient {patient_id}: {e}")
            raise
    
    async def get_patient_statistics(self) -> Dict[str, Any]:
        """Get patient registration statistics"""
        try:
            # Get basic counts
            total_patients = await self.patient_repo.count()
            
            # Get patients by demographics
            all_patients = await self.patient_repo.get_all(limit=1000)  # Consider pagination for large datasets
            
            stats = {
                "total_patients": total_patients,
                "by_gender": {},
                "by_age_group": {
                    "0-18": 0,
                    "19-35": 0,
                    "36-55": 0,
                    "56-75": 0,
                    "75+": 0,
                    "unknown": 0
                },
                "with_contact_info": {
                    "email": 0,
                    "phone": 0,
                    "both": 0,
                    "none": 0
                },
                "recent_registrations": {
                    "last_24h": 0,
                    "last_week": 0,
                    "last_month": 0
                }
            }
            
            # Process patient data for statistics
            now = datetime.utcnow()
            
            for patient in all_patients:
                # Gender statistics
                gender = patient.demographics.gender or "Unknown"
                stats["by_gender"][gender] = stats["by_gender"].get(gender, 0) + 1
                
                # Age group statistics
                if patient.demographics.date_of_birth:
                    try:
                        birth_date = patient.demographics.date_of_birth
                        if isinstance(birth_date, str):
                            birth_date = datetime.strptime(birth_date, "%Y-%m-%d")
                        age = (now - birth_date).days / 365.25
                        
                        if age <= 18:
                            stats["by_age_group"]["0-18"] += 1
                        elif age <= 35:
                            stats["by_age_group"]["19-35"] += 1
                        elif age <= 55:
                            stats["by_age_group"]["36-55"] += 1
                        elif age <= 75:
                            stats["by_age_group"]["56-75"] += 1
                        else:
                            stats["by_age_group"]["75+"] += 1
                    except (ValueError, TypeError):
                        stats["by_age_group"]["unknown"] += 1
                else:
                    stats["by_age_group"]["unknown"] += 1
                
                # Contact info statistics
                has_email = bool(patient.demographics.email)
                has_phone = bool(patient.demographics.phone)
                
                if has_email and has_phone:
                    stats["with_contact_info"]["both"] += 1
                elif has_email:
                    stats["with_contact_info"]["email"] += 1
                elif has_phone:
                    stats["with_contact_info"]["phone"] += 1
                else:
                    stats["with_contact_info"]["none"] += 1
                
                # Registration timing statistics
                if patient.created_at:
                    time_diff = now - patient.created_at
                    if time_diff.days == 0:
                        stats["recent_registrations"]["last_24h"] += 1
                    if time_diff.days <= 7:
                        stats["recent_registrations"]["last_week"] += 1
                    if time_diff.days <= 30:
                        stats["recent_registrations"]["last_month"] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting patient statistics: {e}")
            return {
                "total_patients": 0,
                "by_gender": {},
                "by_age_group": {},
                "with_contact_info": {},
                "recent_registrations": {},
                "error": str(e)
            }


# Create service instance
patient_service = PatientService()