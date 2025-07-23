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
    
    def get_by_mrn(self, medical_record_number: str) -> Optional[Patient]:
        """
        Get patient by medical record number
        
        Args:
            medical_record_number: Medical record number
            
        Returns:
            Patient instance or None if not found
        """
        try:
            return self.db.query(Patient).filter(
                Patient.medical_record_number == medical_record_number
            ).first()
        except Exception as e:
            logger.error(f"Error getting patient by MRN {medical_record_number}: {str(e)}")
            return None
    
    def get_by_medical_record_number(self, mrn: str) -> Optional[Patient]:
        """
        Alias for get_by_mrn for backward compatibility
        
        Args:
            mrn: Medical record number
            
        Returns:
            Patient instance or None if not found
        """
        return self.get_by_mrn(mrn)
    
    def get_by_email(self, email: str) -> Optional[Patient]:
        """
        Get patient by email address
        
        Args:
            email: Patient's email address
            
        Returns:
            Patient instance or None if not found
        """
        try:
            return self.db.query(Patient).filter(
                Patient.email == email
            ).first()
        except Exception as e:
            logger.error(f"Error getting patient by email {email}: {str(e)}")
            return None
    
    def get_active_patients(self, skip: int = 0, limit: int = 100) -> List[Patient]:
        """
        Get active patients
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of active patients
        """
        try:
            return self.db.query(Patient).filter(
                Patient.status == "active"
            ).order_by(Patient.last_name, Patient.first_name).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting active patients: {str(e)}")
            return []
    
    def get_active_by_patient(self, patient_id: str) -> Optional[Patient]:
        """
        Get active patient by ID
        
        Args:
            patient_id: Patient UUID
            
        Returns:
            Patient instance if active, None otherwise
        """
        try:
            return self.db.query(Patient).filter(
                and_(
                    Patient.id == patient_id,
                    Patient.status == "active"
                )
            ).first()
        except Exception as e:
            logger.error(f"Error getting active patient {patient_id}: {str(e)}")
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
            query = self.db.query(Patient).filter(Patient.status == "active")
            
            if first_name:
                query = query.filter(Patient.first_name.ilike(f'%{first_name}%'))
            
            if last_name:
                query = query.filter(Patient.last_name.ilike(f'%{last_name}%'))
            
            return query.order_by(Patient.last_name, Patient.first_name).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error searching patients by name: {str(e)}")
            return []
    
    def search_patients(self, search_term: str, limit: int = 50) -> List[Patient]:
        """
        Search patients by various criteria (name, email, MRN)
        
        Args:
            search_term: Search term to match against multiple fields
            limit: Maximum number of results
            
        Returns:
            List of matching patients
        """
        try:
            search_pattern = f"%{search_term}%"
            
            return self.db.query(Patient).filter(
                and_(
                    Patient.status == "active",
                    or_(
                        Patient.first_name.ilike(search_pattern),
                        Patient.last_name.ilike(search_pattern),
                        Patient.email.ilike(search_pattern),
                        Patient.medical_record_number.ilike(search_pattern),
                        func.concat(Patient.first_name, ' ', Patient.last_name).ilike(search_pattern)
                    )
                )
            ).order_by(Patient.last_name, Patient.first_name).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error searching patients with term '{search_term}': {str(e)}")
            return []
    
    def get_by_birth_date_range(self, start_date: date, end_date: date, 
                               skip: int = 0, limit: int = 100) -> List[Patient]:
        """
        Get patients born within a specific date range
        
        Args:
            start_date: Start of birth date range
            end_date: End of birth date range
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of patients born in the date range
        """
        try:
            return self.db.query(Patient).filter(
                and_(
                    Patient.status == "active",
                    Patient.date_of_birth >= start_date,
                    Patient.date_of_birth <= end_date
                )
            ).order_by(Patient.last_name, Patient.first_name).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting patients by birth date range: {str(e)}")
            return []
    
    def get_by_age_range(self, min_age: int, max_age: int, 
                        skip: int = 0, limit: int = 100) -> List[Patient]:
        """
        Get patients within a specific age range
        
        Args:
            min_age: Minimum age
            max_age: Maximum age
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of patients in the age range
        """
        try:
            today = date.today()
            max_birth_date = date(today.year - min_age, today.month, today.day)
            min_birth_date = date(today.year - max_age, today.month, today.day)
            
            return self.get_by_birth_date_range(min_birth_date, max_birth_date, skip, limit)
            
        except Exception as e:
            logger.error(f"Error getting patients by age range {min_age}-{max_age}: {str(e)}")
            return []
    
    def get_by_gender(self, gender: str, skip: int = 0, limit: int = 100) -> List[Patient]:
        """
        Get patients by gender
        
        Args:
            gender: Patient gender
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of patients with the specified gender
        """
        try:
            return self.db.query(Patient).filter(
                and_(
                    Patient.status == "active",
                    Patient.gender == gender
                )
            ).order_by(Patient.last_name, Patient.first_name).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting patients by gender {gender}: {str(e)}")
            return []
    
    def deactivate_patient(self, patient_id: str, reason: Optional[str] = None) -> bool:
        """
        Deactivate a patient
        
        Args:
            patient_id: Patient UUID
            reason: Deactivation reason
            
        Returns:
            True if successful, False otherwise
        """
        try:
            patient = self.get_by_id(patient_id)
            if not patient:
                return False
            
            patient.status = "inactive"
            patient.updated_at = datetime.utcnow()
            
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error deactivating patient {patient_id}: {str(e)}")
            self.db.rollback()
            return False
    
    def reactivate_patient(self, patient_id: str) -> bool:
        """
        Reactivate a patient
        
        Args:
            patient_id: Patient UUID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            patient = self.get_by_id(patient_id)
            if not patient:
                return False
            
            patient.status = "active"
            patient.updated_at = datetime.utcnow()
            
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error reactivating patient {patient_id}: {str(e)}")
            self.db.rollback()
            return False
    
    def count_active_patients(self) -> int:
        """
        Count active patients
        
        Returns:
            Number of active patients
        """
        try:
            return self.db.query(func.count(Patient.id)).filter(
                Patient.status == "active"
            ).scalar() or 0
            
        except Exception as e:
            logger.error(f"Error counting active patients: {str(e)}")
            return 0
    
    def get_patient_statistics(self) -> Dict[str, Any]:
        """
        Get patient statistics
        
        Returns:
            Dictionary with patient statistics
        """
        try:
            total_patients = self.db.query(func.count(Patient.id)).scalar()
            active_patients = self.count_active_patients()
            
            # Gender distribution
            gender_stats = self.db.query(
                Patient.gender,
                func.count(Patient.id)
            ).filter(
                Patient.status == "active"
            ).group_by(Patient.gender).all()
            
            gender_distribution = {gender: count for gender, count in gender_stats}
            
            # Age distribution (by decades)
            today = date.today()
            age_ranges = [
                ("0-10", 0, 10),
                ("11-20", 11, 20),
                ("21-30", 21, 30),
                ("31-40", 31, 40),
                ("41-50", 41, 50),
                ("51-60", 51, 60),
                ("61-70", 61, 70),
                ("71-80", 71, 80),
                ("81+", 81, 150)
            ]
            
            age_distribution = {}
            for range_name, min_age, max_age in age_ranges:
                count = len(self.get_by_age_range(min_age, max_age, limit=10000))
                age_distribution[range_name] = count
            
            return {
                "total_patients": total_patients or 0,
                "active_patients": active_patients,
                "inactive_patients": (total_patients or 0) - active_patients,
                "gender_distribution": gender_distribution,
                "age_distribution": age_distribution
            }
            
        except Exception as e:
            logger.error(f"Error getting patient statistics: {str(e)}")
            return {}
    
    def get_patients_with_allergies(self, skip: int = 0, limit: int = 100) -> List[Patient]:
        """
        Get patients who have recorded allergies
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of patients with allergies
        """
        try:
            return self.db.query(Patient).filter(
                and_(
                    Patient.status == "active",
                    Patient.allergies.isnot(None),
                    Patient.allergies != ""
                )
            ).order_by(Patient.last_name, Patient.first_name).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting patients with allergies: {str(e)}")
            return []
    
    def get_patients_with_medical_history(self, skip: int = 0, limit: int = 100) -> List[Patient]:
        """
        Get patients who have recorded medical history
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of patients with medical history
        """
        try:
            return self.db.query(Patient).filter(
                and_(
                    Patient.status == "active",
                    Patient.medical_history.isnot(None),
                    Patient.medical_history != ""
                )
            ).order_by(Patient.last_name, Patient.first_name).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting patients with medical history: {str(e)}")
            return []
    
    def get_recent_patients(self, days: int = 30, skip: int = 0, limit: int = 100) -> List[Patient]:
        """
        Get patients created in the last N days
        
        Args:
            days: Number of days to look back
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of recently created patients
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            return self.db.query(Patient).filter(
                and_(
                    Patient.status == "active",
                    Patient.created_at >= cutoff_date
                )
            ).order_by(Patient.created_at.desc()).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting recent patients: {str(e)}")
            return []