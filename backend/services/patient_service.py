from typing import List, Optional, Dict, Any
from repositories.patient_repository import PatientRepository
from repositories.episode_repository import EpisodeRepository
from repositories.audit_repository import AuditRepository
from schemas.patient import PatientCreate, PatientUpdate, PatientResponse, PatientSummary
from models.patient import Patient
import logging
from datetime import datetime, date

logger = logging.getLogger(__name__)

class PatientService:
    """
    Service for patient management business logic
    """
    
    def __init__(
        self, 
        patient_repo: PatientRepository,
        episode_repo: Optional[EpisodeRepository] = None,
        audit_repo: Optional[AuditRepository] = None
    ):
        self.patient_repo = patient_repo
        self.episode_repo = episode_repo
        self.audit_repo = audit_repo
    
    async def create_patient(self, patient_data: PatientCreate) -> PatientResponse:
        """
        Create a new patient with business logic validation
        
        Args:
            patient_data: Patient creation data
            
        Returns:
            Created patient response
            
        Raises:
            ValueError: If validation fails
        """
        try:
            # Business logic validations
            await self._validate_patient_data(patient_data)
            
            # Check for potential duplicates
            potential_duplicate = await self._check_for_duplicates(patient_data)
            if potential_duplicate:
                logger.warning(f"Potential duplicate patient detected: {potential_duplicate.id}")
                # In a real system, you might want to return a warning or require confirmation
            
            # Create patient
            patient = self.patient_repo.create(patient_data)
            
            # Log audit trail
            if self.audit_repo:
                await self.audit_repo.log_action(
                    table_name="patients",
                    record_id=patient.id,
                    action="CREATE",
                    new_values=patient_data.dict()
                )
            
            logger.info(f"Created patient: {patient.id}")
            return PatientResponse.from_orm(patient)
            
        except Exception as e:
            logger.error(f"Error creating patient: {str(e)}")
            raise
    
    async def get_patient(self, patient_id: str) -> Optional[PatientResponse]:
        """
        Get patient by ID
        
        Args:
            patient_id: Patient identifier
            
        Returns:
            Patient response or None
        """
        try:
            patient = self.patient_repo.get(patient_id)
            if patient:
                return PatientResponse.from_orm(patient)
            return None
        except Exception as e:
            logger.error(f"Error getting patient {patient_id}: {str(e)}")
            raise
    
    async def update_patient(
        self, 
        patient_id: str, 
        patient_data: PatientUpdate
    ) -> Optional[PatientResponse]:
        """
        Update existing patient
        
        Args:
            patient_id: Patient identifier
            patient_data: Update data
            
        Returns:
            Updated patient response or None
        """
        try:
            # Get existing patient
            existing_patient = self.patient_repo.get(patient_id)
            if not existing_patient:
                return None
            
            # Store old values for audit
            old_values = PatientResponse.from_orm(existing_patient).dict()
            
            # Validate update data
            await self._validate_patient_update(patient_data, existing_patient)
            
            # Update patient
            updated_patient = self.patient_repo.update(existing_patient, patient_data)
            
            # Log audit trail
            if self.audit_repo:
                await self.audit_repo.log_action(
                    table_name="patients",
                    record_id=patient_id,
                    action="UPDATE",
                    old_values=old_values,
                    new_values=patient_data.dict(exclude_unset=True)
                )
            
            logger.info(f"Updated patient: {patient_id}")
            return PatientResponse.from_orm(updated_patient)
            
        except Exception as e:
            logger.error(f"Error updating patient {patient_id}: {str(e)}")
            raise
    
    async def delete_patient(self, patient_id: str) -> bool:
        """
        Delete patient (with business rules)
        
        Args:
            patient_id: Patient identifier
            
        Returns:
            True if deleted, False if not found
        """
        try:
            # Check if patient has active episodes
            if self.episode_repo:
                active_episodes = self.episode_repo.get_active_episodes(patient_id)
                if active_episodes:
                    raise ValueError(
                        f"Cannot delete patient {patient_id}: has {len(active_episodes)} active episodes"
                    )
            
            # Get patient data for audit before deletion
            patient = self.patient_repo.get(patient_id)
            if not patient:
                return False
            
            old_values = PatientResponse.from_orm(patient).dict()
            
            # Delete patient
            success = self.patient_repo.delete(patient_id)
            
            if success and self.audit_repo:
                await self.audit_repo.log_action(
                    table_name="patients",
                    record_id=patient_id,
                    action="DELETE",
                    old_values=old_values
                )
            
            logger.info(f"Deleted patient: {patient_id}")
            return success
            
        except Exception as e:
            logger.error(f"Error deleting patient {patient_id}: {str(e)}")
            raise
    
    async def list_patients(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None
    ) -> List[PatientResponse]:
        """
        List patients with optional search
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            search: Optional search query
            
        Returns:
            List of patient responses
        """
        try:
            if search:
                patients = self.patient_repo.search_by_name(search)
            else:
                patients = self.patient_repo.get_all(skip=skip, limit=limit, order_by="last_name")
            
            return [PatientResponse.from_orm(patient) for patient in patients]
            
        except Exception as e:
            logger.error(f"Error listing patients: {str(e)}")
            raise
    
    async def get_patient_summary(self, patient_id: str) -> Optional[PatientSummary]:
        """
        Get comprehensive patient summary
        
        Args:
            patient_id: Patient identifier
            
        Returns:
            Patient summary or None
        """
        try:
            patient = self.patient_repo.get(patient_id)
            if not patient:
                return None
            
            # Get basic patient info
            summary = PatientSummary(
                basic_info=PatientResponse.from_orm(patient),
                recent_episodes=[],
                medical_alerts=[],
                statistics={}
            )
            
            # Get recent episodes if episode repo is available
            if self.episode_repo:
                recent_episodes = self.episode_repo.get_by_patient_id(
                    patient_id, limit=5
                )
                summary.recent_episodes = [
                    self._episode_to_summary(episode) 
                    for episode in recent_episodes
                ]
                
                # Get episode statistics
                episode_stats = self.episode_repo.get_episode_statistics(patient_id)
                summary.statistics.update(episode_stats)
            
            # Check for medical alerts
            summary.medical_alerts = await self._get_medical_alerts(patient)
            
            # Calculate patient age
            summary.statistics["age"] = self._calculate_age(patient.date_of_birth)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting patient summary {patient_id}: {str(e)}")
            raise
    
    async def search_patients(self, search_criteria: Dict[str, Any]) -> List[PatientResponse]:
        """
        Advanced patient search
        
        Args:
            search_criteria: Search criteria dictionary
            
        Returns:
            List of matching patients
        """
        try:
            patients = self.patient_repo.search_comprehensive(
                name=search_criteria.get("name"),
                gender=search_criteria.get("gender"),
                birth_year=search_criteria.get("birth_year"),
                skip=search_criteria.get("skip", 0),
                limit=search_criteria.get("limit", 100)
            )
            
            return [PatientResponse.from_orm(patient) for patient in patients]
            
        except Exception as e:
            logger.error(f"Error in advanced patient search: {str(e)}")
            raise
    
    # Private helper methods
    
    async def _validate_patient_data(self, patient_data: PatientCreate) -> None:
        """Validate patient creation data"""
        # Age validation
        today = date.today()
        age = today.year - patient_data.date_of_birth.year
        if patient_data.date_of_birth > today:
            raise ValueError("Date of birth cannot be in the future")
        if age > 150:
            raise ValueError("Invalid date of birth: age would be over 150 years")
        
        # Gender validation
        valid_genders = ["male", "female", "other", "unknown"]
        if patient_data.gender.lower() not in valid_genders:
            raise ValueError(f"Invalid gender. Must be one of: {valid_genders}")
        
        # Contact info validation
        if patient_data.contact_info:
            email = patient_data.contact_info.get("email")
            if email and "@" not in email:
                raise ValueError("Invalid email address format")
    
    async def _validate_patient_update(
        self, 
        patient_data: PatientUpdate, 
        existing_patient: Patient
    ) -> None:
        """Validate patient update data"""
        if patient_data.date_of_birth:
            await self._validate_patient_data(
                PatientCreate(
                    first_name=existing_patient.first_name,
                    last_name=existing_patient.last_name,
                    date_of_birth=patient_data.date_of_birth,
                    gender=patient_data.gender or existing_patient.gender
                )
            )
    
    async def _check_for_duplicates(self, patient_data: PatientCreate) -> Optional[Patient]:
        """Check for potential duplicate patients"""
        # Simple duplicate check by name and DOB
        return self.patient_repo.get_by_name(
            patient_data.first_name, 
            patient_data.last_name
        )
    
    async def _get_medical_alerts(self, patient: Patient) -> List[Dict[str, Any]]:
        """Get medical alerts for patient"""
        alerts = []
        
        if patient.medical_history:
            # Check for allergies
            allergies = patient.medical_history.get("allergies", [])
            if allergies:
                alerts.append({
                    "type": "allergy",
                    "severity": "high",
                    "message": f"Allergies: {', '.join(allergies)}"
                })
            
            # Check for chronic conditions
            chronic_conditions = patient.medical_history.get("chronic_conditions", [])
            if chronic_conditions:
                alerts.append({
                    "type": "chronic_condition",
                    "severity": "medium",
                    "message": f"Chronic conditions: {', '.join(chronic_conditions)}"
                })
        
        return alerts
    
    def _calculate_age(self, birth_date: date) -> int:
        """Calculate patient age"""
        today = date.today()
        return today.year - birth_date.year - (
            (today.month, today.day) < (birth_date.month, birth_date.day)
        )
    
    def _episode_to_summary(self, episode) -> Dict[str, Any]:
        """Convert episode to summary format"""
        return {
            "id": episode.id,
            "chief_complaint": episode.chief_complaint,
            "start_date": episode.start_date.isoformat() if episode.start_date else None,
            "status": episode.status
        }