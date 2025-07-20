from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from models.patient import Patient
from schemas.patient import PatientCreate, PatientUpdate
from .base import BaseRepository
import logging

logger = logging.getLogger(__name__)

class PatientRepository(BaseRepository[Patient, PatientCreate, PatientUpdate]):
    """
    Repository for Patient data access operations
    """
    
    def __init__(self, db: Session):
        super().__init__(Patient, db)
    
    def get_by_name(self, first_name: str, last_name: str) -> Optional[Patient]:
        """
        Get patient by full name
        
        Args:
            first_name: Patient's first name
            last_name: Patient's last name
            
        Returns:
            Patient instance or None
        """
        try:
            return self.db.query(Patient).filter(
                and_(
                    func.lower(Patient.first_name) == first_name.lower(),
                    func.lower(Patient.last_name) == last_name.lower()
                )
            ).first()
        except Exception as e:
            logger.error(f"Error getting patient by name {first_name} {last_name}: {str(e)}")
            raise
    
    def search_by_name(self, name_query: str) -> List[Patient]:
        """
        Search patients by name (first or last name)
        
        Args:
            name_query: Search query for name
            
        Returns:
            List of matching patients
        """
        try:
            search_term = f"%{name_query.lower()}%"
            return self.db.query(Patient).filter(
                or_(
                    func.lower(Patient.first_name).like(search_term),
                    func.lower(Patient.last_name).like(search_term),
                    func.lower(func.concat(Patient.first_name, ' ', Patient.last_name)).like(search_term)
                )
            ).all()
        except Exception as e:
            logger.error(f"Error searching patients by name '{name_query}': {str(e)}")
            raise
    
    def get_by_date_of_birth(self, date_of_birth: str) -> List[Patient]:
        """
        Get patients by date of birth
        
        Args:
            date_of_birth: Date of birth in YYYY-MM-DD format
            
        Returns:
            List of patients with matching birth date
        """
        try:
            return self.db.query(Patient).filter(
                Patient.date_of_birth == date_of_birth
            ).all()
        except Exception as e:
            logger.error(f"Error getting patients by DOB {date_of_birth}: {str(e)}")
            raise
    
    def get_by_gender(self, gender: str) -> List[Patient]:
        """
        Get patients by gender
        
        Args:
            gender: Patient gender
            
        Returns:
            List of patients with matching gender
        """
        try:
            return self.db.query(Patient).filter(
                func.lower(Patient.gender) == gender.lower()
            ).all()
        except Exception as e:
            logger.error(f"Error getting patients by gender {gender}: {str(e)}")
            raise
    
    def search_comprehensive(
        self,
        name: Optional[str] = None,
        gender: Optional[str] = None,
        birth_year: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Patient]:
        """
        Comprehensive patient search with multiple criteria
        
        Args:
            name: Name search query
            gender: Gender filter
            birth_year: Birth year filter
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching patients
        """
        try:
            query = self.db.query(Patient)
            conditions = []
            
            # Name search
            if name:
                search_term = f"%{name.lower()}%"
                conditions.append(
                    or_(
                        func.lower(Patient.first_name).like(search_term),
                        func.lower(Patient.last_name).like(search_term),
                        func.lower(func.concat(Patient.first_name, ' ', Patient.last_name)).like(search_term)
                    )
                )
            
            # Gender filter
            if gender:
                conditions.append(func.lower(Patient.gender) == gender.lower())
            
            # Birth year filter
            if birth_year:
                conditions.append(func.extract('year', Patient.date_of_birth) == birth_year)
            
            if conditions:
                query = query.filter(and_(*conditions))
            
            return query.order_by(Patient.last_name, Patient.first_name).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error in comprehensive patient search: {str(e)}")
            raise
    
    def get_patients_with_medical_history(self, condition: str) -> List[Patient]:
        """
        Get patients with specific medical history condition
        
        Args:
            condition: Medical condition to search for
            
        Returns:
            List of patients with the condition in their medical history
        """
        try:
            # This uses JSON queries - syntax may vary by database
            if self.db.bind.dialect.name == 'sqlite':
                # SQLite JSON query
                return self.db.query(Patient).filter(
                    Patient.medical_history.like(f'%{condition}%')
                ).all()
            else:
                # PostgreSQL JSON query
                return self.db.query(Patient).filter(
                    Patient.medical_history['chronic_conditions'].astext.like(f'%{condition}%')
                ).all()
        except Exception as e:
            logger.error(f"Error getting patients with medical history '{condition}': {str(e)}")
            raise
    
    def get_patients_by_age_range(self, min_age: int, max_age: int) -> List[Patient]:
        """
        Get patients within an age range
        
        Args:
            min_age: Minimum age
            max_age: Maximum age
            
        Returns:
            List of patients within the age range
        """
        try:
            from datetime import date, timedelta
            today = date.today()
            max_birth_date = today - timedelta(days=min_age * 365.25)
            min_birth_date = today - timedelta(days=(max_age + 1) * 365.25)
            
            return self.db.query(Patient).filter(
                and_(
                    Patient.date_of_birth >= min_birth_date,
                    Patient.date_of_birth <= max_birth_date
                )
            ).all()
        except Exception as e:
            logger.error(f"Error getting patients by age range {min_age}-{max_age}: {str(e)}")
            raise
    
    def get_recent_patients(self, days: int = 30, limit: int = 20) -> List[Patient]:
        """
        Get recently registered patients
        
        Args:
            days: Number of days to look back
            limit: Maximum number of patients to return
            
        Returns:
            List of recently registered patients
        """
        try:
            from datetime import datetime, timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            return self.db.query(Patient).filter(
                Patient.created_at >= cutoff_date
            ).order_by(Patient.created_at.desc()).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting recent patients: {str(e)}")
            raise