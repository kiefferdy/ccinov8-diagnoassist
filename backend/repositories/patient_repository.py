"""
Patient Repository for DiagnoAssist
Specialized CRUD operations for Patient model
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, date, timedelta
from uuid import UUID
import logging

from models.patient import Patient
from repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)

class PatientRepository(BaseRepository[Patient]):
    """
    Repository for Patient model with specialized operations
    """
    
    def __init__(self, db: Session):
        super().__init__(Patient, db)
    
    def get_by_medical_record_number(self, mrn: str) -> Optional[Patient]:
        """
        Get patient by medical record number
        
        Args:
            mrn: Medical record number
            
        Returns:
            Patient instance or None if not found
        """
        try:
            return self.db.query(Patient).filter(Patient.medical_record_number == mrn).first()
        except Exception as e:
            logger.error(f"Error getting patient by MRN {mrn}: {str(e)}")
            return None
    
    def search_by_name(self, first_name: Optional[str] = None, 
                      last_name: Optional[str] = None, 
                      limit: int = 50) -> List[Patient]:
        """
        Search patients by name (case-insensitive)
        
        Args:
            first_name: Patient's first name (partial match allowed)
            last_name: Patient's last name (partial match allowed)
            limit: Maximum number of results
            
        Returns:
            List of matching patients
        """
        try:
            query = self.db.query(Patient)
            
            if first_name:
                query = query.filter(Patient.first_name.ilike(f'%{first_name}%'))
            
            if last_name:
                query = query.filter(Patient.last_name.ilike(f'%{last_name}%'))
            
            return query.limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error searching patients by name: {str(e)}")
            return []
    
    def get_by_date_of_birth(self, birth_date: date) -> List[Patient]:
        """
        Get patients by date of birth
        
        Args:
            birth_date: Date of birth
            
        Returns:
            List of patients with matching birth date
        """
        try:
            return self.db.query(Patient).filter(Patient.date_of_birth == birth_date).all()
        except Exception as e:
            logger.error(f"Error getting patients by birth date {birth_date}: {str(e)}")
            return []
    
    def get_by_age_range(self, min_age: int, max_age: int) -> List[Patient]:
        """
        Get patients within age range
        
        Args:
            min_age: Minimum age
            max_age: Maximum age
            
        Returns:
            List of patients within age range
        """
        try:
            today = date.today()
            max_birth_date = date(today.year - min_age, today.month, today.day)
            min_birth_date = date(today.year - max_age, today.month, today.day)
            
            return self.db.query(Patient).filter(
                and_(
                    Patient.date_of_birth >= min_birth_date,
                    Patient.date_of_birth <= max_birth_date
                )
            ).all()
            
        except Exception as e:
            logger.error(f"Error getting patients by age range {min_age}-{max_age}: {str(e)}")
            return []
    
    def get_by_gender(self, gender: str, skip: int = 0, limit: int = 100) -> List[Patient]:
        """
        Get patients by gender
        
        Args:
            gender: Patient gender
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of patients with matching gender
        """
        try:
            return self.db.query(Patient).filter(
                Patient.gender == gender
            ).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting patients by gender {gender}: {str(e)}")
            return []
    
    def search_comprehensive(self, search_term: str, limit: int = 50) -> List[Patient]:
        """
        Comprehensive search across multiple patient fields
        
        Args:
            search_term: Search term to match against multiple fields
            limit: Maximum number of results
            
        Returns:
            List of matching patients
        """
        try:
            search_pattern = f'%{search_term}%'
            
            return self.db.query(Patient).filter(
                or_(
                    Patient.first_name.ilike(search_pattern),
                    Patient.last_name.ilike(search_pattern),
                    Patient.medical_record_number.ilike(search_pattern),
                    Patient.email.ilike(search_pattern),
                    Patient.phone.ilike(search_pattern)
                )
            ).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error in comprehensive patient search for '{search_term}': {str(e)}")
            return []
    
    def get_patients_with_episodes(self, skip: int = 0, limit: int = 100) -> List[Patient]:
        """
        Get patients who have associated episodes
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of patients with episodes
        """
        try:
            from models.episode import Episode
            
            return self.db.query(Patient).join(Episode).distinct().offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting patients with episodes: {str(e)}")
            return []
    
    def get_patients_by_emergency_contact(self, contact_name: str) -> List[Patient]:
        """
        Get patients by emergency contact name
        
        Args:
            contact_name: Emergency contact name to search for
            
        Returns:
            List of patients with matching emergency contact
        """
        try:
            return self.db.query(Patient).filter(
                Patient.emergency_contact_name.ilike(f'%{contact_name}%')
            ).all()
            
        except Exception as e:
            logger.error(f"Error getting patients by emergency contact {contact_name}: {str(e)}")
            return []
    
    def get_recently_created(self, days: int = 30, limit: int = 100) -> List[Patient]:
        """
        Get recently created patient records
        
        Args:
            days: Number of days to look back
            limit: Maximum number of records
            
        Returns:
            List of recently created patients
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            return self.db.query(Patient).filter(
                Patient.created_at >= cutoff_date
            ).order_by(Patient.created_at.desc()).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting recently created patients: {str(e)}")
            return []
    
    def update_medical_record_number(self, patient_id: UUID, new_mrn: str) -> Optional[Patient]:
        """
        Update patient's medical record number with validation
        
        Args:
            patient_id: Patient ID
            new_mrn: New medical record number
            
        Returns:
            Updated patient or None if failed
        """
        try:
            # Check if MRN is already in use
            existing = self.get_by_medical_record_number(new_mrn)
            if existing and existing.id != patient_id:
                logger.error(f"Medical record number {new_mrn} already in use")
                return None
            
            return self.update(patient_id, {"medical_record_number": new_mrn})
            
        except Exception as e:
            logger.error(f"Error updating MRN for patient {patient_id}: {str(e)}")
            return None
    
    def get_patient_statistics(self) -> Dict[str, Any]:
        """
        Get patient statistics
        
        Returns:
            Dictionary with patient statistics
        """
        try:
            total_patients = self.count()
            
            gender_stats = self.db.query(
                Patient.gender, 
                func.count(Patient.id).label('count')
            ).group_by(Patient.gender).all()
            
            return {
                "total_patients": total_patients,
                "gender_distribution": {stat.gender: stat.count for stat in gender_stats},
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting patient statistics: {str(e)}")
            return {}
    
    def validate_unique_mrn(self, mrn: str, exclude_patient_id: Optional[UUID] = None) -> bool:
        """
        Validate that medical record number is unique
        
        Args:
            mrn: Medical record number to validate
            exclude_patient_id: Patient ID to exclude from check (for updates)
            
        Returns:
            True if MRN is unique, False otherwise
        """
        try:
            query = self.db.query(Patient).filter(Patient.medical_record_number == mrn)
            
            if exclude_patient_id:
                query = query.filter(Patient.id != exclude_patient_id)
            
            return query.first() is None
            
        except Exception as e:
            logger.error(f"Error validating unique MRN {mrn}: {str(e)}")
            return False
        
    def get_by_mrn(self, mrn: str) -> Optional[Patient]:
        """Get patient by medical record number (alias)"""
        return self.get_by_medical_record_number(mrn)

    def get_by_email(self, email: str) -> Optional[Patient]:
        """Get patient by email address"""
        try:
            return self.db.query(Patient).filter(Patient.email == email).first()
        except Exception as e:
            logger.error(f"Error getting patient by email {email}: {str(e)}")
            return None