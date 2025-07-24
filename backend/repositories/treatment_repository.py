"""
Treatment Repository for DiagnoAssist
Specialized CRUD operations for Treatment model
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from datetime import datetime, date, timedelta
from uuid import UUID
import logging

from models.treatment import Treatment
from models.episode import Episode
from models.diagnosis import Diagnosis
from repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)

class TreatmentRepository(BaseRepository[Treatment]):
    """
    Repository for Treatment model with specialized operations
    """
    
    def __init__(self, db: Session):
        super().__init__(Treatment, db)
    
    def get_by_episode(self, episode_id: str) -> List[Treatment]:
        """
        Get all treatments for a specific episode
        
        Args:
            episode_id: Episode UUID
            
        Returns:
            List of treatments for the episode
        """
        try:
            return self.db.query(Treatment).filter(
                Treatment.episode_id == episode_id
            ).order_by(desc(Treatment.created_at)).all()
            
        except Exception as e:
            logger.error(f"Error getting treatments for episode {episode_id}: {str(e)}")
            return []
    
    def count_by_episode(self, episode_id: str) -> int:
        """
        Count treatments for a specific episode
        
        Args:
            episode_id: Episode UUID
            
        Returns:
            Number of treatments for the episode
        """
        try:
            return self.db.query(func.count(Treatment.id)).filter(
                Treatment.episode_id == episode_id
            ).scalar() or 0
            
        except Exception as e:
            logger.error(f"Error counting treatments for episode {episode_id}: {str(e)}")
            return 0
    
    def get_by_patient(self, patient_id: str, skip: int = 0, limit: int = 100) -> List[Treatment]:
        """
        Get treatments for a specific patient (via episodes)
        
        Args:
            patient_id: Patient UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of treatments for the patient
        """
        try:
            return self.db.query(Treatment).join(Episode).filter(
                Episode.patient_id == patient_id
            ).order_by(desc(Treatment.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting treatments for patient {patient_id}: {str(e)}")
            return []
    
    def get_active_by_patient(self, patient_id: str) -> List[Treatment]:
        """
        Get active treatments for a specific patient
        
        Args:
            patient_id: Patient UUID
            
        Returns:
            List of active treatments for the patient
        """
        try:
            return self.db.query(Treatment).join(Episode).filter(
                and_(
                    Episode.patient_id == patient_id,
                    Treatment.status == "active"
                )
            ).order_by(desc(Treatment.created_at)).all()
            
        except Exception as e:
            logger.error(f"Error getting active treatments for patient {patient_id}: {str(e)}")
            return []
    
    def get_by_diagnosis(self, diagnosis_id: str) -> List[Treatment]:
        """
        Get treatments for a specific diagnosis
        
        Args:
            diagnosis_id: Diagnosis UUID
            
        Returns:
            List of treatments for the diagnosis
        """
        try:
            return self.db.query(Treatment).filter(
                Treatment.diagnosis_id == diagnosis_id
            ).order_by(desc(Treatment.created_at)).all()
            
        except Exception as e:
            logger.error(f"Error getting treatments for diagnosis {diagnosis_id}: {str(e)}")
            return []
    
    def get_by_treatment_type(self, treatment_type: str, skip: int = 0, limit: int = 100) -> List[Treatment]:
        """
        Get treatments by type
        
        Args:
            treatment_type: Type of treatment (medication, procedure, etc.)
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of treatments with the specified type
        """
        try:
            return self.db.query(Treatment).filter(
                Treatment.treatment_type == treatment_type
            ).order_by(desc(Treatment.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting treatments by type {treatment_type}: {str(e)}")
            return []
    
    def get_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[Treatment]:
        """
        Get treatments by status
        
        Args:
            status: Treatment status (active, completed, discontinued, etc.)
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of treatments with the specified status
        """
        try:
            return self.db.query(Treatment).filter(
                Treatment.status == status
            ).order_by(desc(Treatment.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting treatments by status {status}: {str(e)}")
            return []
    
    def get_active_treatments(self, skip: int = 0, limit: int = 100) -> List[Treatment]:
        """
        Get all active treatments
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of active treatments
        """
        try:
            return self.db.query(Treatment).filter(
                Treatment.status == "active"
            ).order_by(desc(Treatment.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting active treatments: {str(e)}")
            return []
    
    def get_by_prescriber(self, prescriber: str, skip: int = 0, limit: int = 100) -> List[Treatment]:
        """
        Get treatments by prescriber
        
        Args:
            prescriber: Prescriber identifier
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of treatments by the specified prescriber
        """
        try:
            return self.db.query(Treatment).filter(
                Treatment.prescriber == prescriber
            ).order_by(desc(Treatment.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting treatments by prescriber {prescriber}: {str(e)}")
            return []
    
    def get_medications(self, skip: int = 0, limit: int = 100) -> List[Treatment]:
        """
        Get all medication treatments
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of medication treatments
        """
        try:
            return self.db.query(Treatment).filter(
                Treatment.treatment_type == "medication"
            ).order_by(desc(Treatment.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting medications: {str(e)}")
            return []
    
    def get_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[Treatment]:
        """
        Get treatments by name (case-insensitive)
        
        Args:
            name: Treatment name to search for
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching treatments
        """
        try:
            return self.db.query(Treatment).filter(
                Treatment.name.ilike(f'%{name}%')
            ).order_by(desc(Treatment.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting treatments by name '{name}': {str(e)}")
            return []
    
    def get_by_date_range(self, start_date: datetime, end_date: datetime, 
                         skip: int = 0, limit: int = 100) -> List[Treatment]:
        """
        Get treatments within a specific date range
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of treatments in the date range
        """
        try:
            return self.db.query(Treatment).filter(
                and_(
                    Treatment.start_date >= start_date,
                    Treatment.start_date <= end_date
                )
            ).order_by(desc(Treatment.start_date)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting treatments in date range: {str(e)}")
            return []
    
    def get_ongoing_treatments(self, skip: int = 0, limit: int = 100) -> List[Treatment]:
        """
        Get ongoing treatments (started but not ended)
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of ongoing treatments
        """
        try:
            return self.db.query(Treatment).filter(
                and_(
                    Treatment.start_date <= datetime.utcnow(),
                    Treatment.end_date.is_(None),
                    Treatment.status == "active"
                )
            ).order_by(desc(Treatment.start_date)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting ongoing treatments: {str(e)}")
            return []
    
    def complete_treatment(self, treatment_id: str, end_date: Optional[datetime] = None) -> bool:
        """
        Complete a treatment by setting end date and status
        
        Args:
            treatment_id: Treatment UUID
            end_date: End date (defaults to current time)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            treatment = self.get_by_id(treatment_id)
            if not treatment:
                return False
            
            treatment.end_date = end_date or datetime.utcnow()
            treatment.status = "completed"
            treatment.updated_at = datetime.utcnow()
            
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error completing treatment {treatment_id}: {str(e)}")
            self.db.rollback()
            return False
    
    def discontinue_treatment(self, treatment_id: str, reason: Optional[str] = None) -> bool:
        """
        Discontinue a treatment
        
        Args:
            treatment_id: Treatment UUID
            reason: Discontinuation reason
            
        Returns:
            True if successful, False otherwise
        """
        try:
            treatment = self.get_by_id(treatment_id)
            if not treatment:
                return False
            
            treatment.status = "discontinued"
            treatment.end_date = datetime.utcnow()
            treatment.updated_at = datetime.utcnow()
            
            if reason:
                # Add reason to instructions
                if treatment.instructions:
                    treatment.instructions += f"\n\nDiscontinued: {reason}"
                else:
                    treatment.instructions = f"Discontinued: {reason}"
            
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error discontinuing treatment {treatment_id}: {str(e)}")
            self.db.rollback()
            return False
    
    def search_treatments(self, search_term: str, skip: int = 0, limit: int = 100) -> List[Treatment]:
        """
        Search treatments by name, description, or instructions
        
        Args:
            search_term: Search term
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching treatments
        """
        try:
            search_pattern = f"%{search_term}%"
            
            return self.db.query(Treatment).filter(
                or_(
                    Treatment.name.ilike(search_pattern),
                    Treatment.description.ilike(search_pattern),
                    Treatment.instructions.ilike(search_pattern),
                    Treatment.dosage.ilike(search_pattern)
                )
            ).order_by(desc(Treatment.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error searching treatments with term '{search_term}': {str(e)}")
            return []
    
    def get_treatment_statistics(self) -> Dict[str, Any]:
        """
        Get treatment statistics
        
        Returns:
            Dictionary with treatment statistics
        """
        try:
            total_treatments = self.db.query(func.count(Treatment.id)).scalar()
            active_treatments = self.db.query(func.count(Treatment.id)).filter(
                Treatment.status == "active"
            ).scalar()
            completed_treatments = self.db.query(func.count(Treatment.id)).filter(
                Treatment.status == "completed"
            ).scalar()
            
            # Most common treatment types
            type_stats = self.db.query(
                Treatment.treatment_type,
                func.count(Treatment.id)
            ).group_by(Treatment.treatment_type).order_by(
                desc(func.count(Treatment.id))
            ).all()
            
            type_distribution = {treatment_type: count for treatment_type, count in type_stats}
            
            # Most common treatments
            treatment_stats = self.db.query(
                Treatment.name,
                func.count(Treatment.id)
            ).group_by(Treatment.name).order_by(
                desc(func.count(Treatment.id))
            ).limit(10).all()
            
            top_treatments = {name: count for name, count in treatment_stats}
            
            # Status distribution
            status_stats = self.db.query(
                Treatment.status,
                func.count(Treatment.id)
            ).group_by(Treatment.status).all()
            
            status_distribution = {status: count for status, count in status_stats}
            
            return {
                "total_treatments": total_treatments or 0,
                "active_treatments": active_treatments or 0,
                "completed_treatments": completed_treatments or 0,
                "discontinued_treatments": status_distribution.get("discontinued", 0),
                "type_distribution": type_distribution,
                "top_treatments": top_treatments,
                "status_distribution": status_distribution
            }
            
        except Exception as e:
            logger.error(f"Error getting treatment statistics: {str(e)}")
            return {}
    
    def get_recent_treatments(self, days: int = 7, skip: int = 0, limit: int = 100) -> List[Treatment]:
        """
        Get treatments from the last N days
        
        Args:
            days: Number of days to look back
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of recent treatments
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            return self.db.query(Treatment).filter(
                Treatment.created_at >= cutoff_date
            ).order_by(desc(Treatment.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting recent treatments: {str(e)}")
            return []
    
    def count_by_patient(self, patient_id: str) -> int:
        """
        Count treatments for a specific patient
        
        Args:
            patient_id: Patient UUID
            
        Returns:
            Number of treatments for the patient
        """
        try:
            return self.db.query(func.count(Treatment.id)).join(Episode).filter(
                Episode.patient_id == patient_id
            ).scalar() or 0
            
        except Exception as e:
            logger.error(f"Error counting treatments for patient {patient_id}: {str(e)}")
            return 0
    
    def get_patient_medication_history(self, patient_id: str, skip: int = 0, limit: int = 100) -> List[Treatment]:
        """
        Get medication history for a specific patient
        
        Args:
            patient_id: Patient UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of medication treatments for the patient
        """
        try:
            return self.db.query(Treatment).join(Episode).filter(
                and_(
                    Episode.patient_id == patient_id,
                    Treatment.treatment_type == "medication"
                )
            ).order_by(desc(Treatment.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting medication history for patient {patient_id}: {str(e)}")
            return []
    
    def get_treatments_requiring_monitoring(self, skip: int = 0, limit: int = 100) -> List[Treatment]:
        """
        Get treatments that have monitoring requirements
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of treatments requiring monitoring
        """
        try:
            return self.db.query(Treatment).filter(
                and_(
                    Treatment.monitoring_requirements.isnot(None),
                    Treatment.monitoring_requirements != "",
                    Treatment.status == "active"
                )
            ).order_by(desc(Treatment.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting treatments requiring monitoring: {str(e)}")
            return []
    
    def get_treatments_with_interactions(self, skip: int = 0, limit: int = 100) -> List[Treatment]:
        """
        Get treatments that have drug interactions noted
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of treatments with interactions
        """
        try:
            return self.db.query(Treatment).filter(
                and_(
                    Treatment.drug_interactions.isnot(None),
                    Treatment.drug_interactions != "",
                    Treatment.status == "active"
                )
            ).order_by(desc(Treatment.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting treatments with interactions: {str(e)}")
            return []
    
    def get_by_diagnosis_id(self, diagnosis_id: str) -> List[Treatment]:
        """
        Get treatments for a specific diagnosis
        
        Args:
            diagnosis_id: Diagnosis UUID
            
        Returns:
            List of treatments for the diagnosis
        """
        try:
            return self.db.query(Treatment).filter(
                Treatment.diagnosis_id == diagnosis_id
            ).order_by(desc(Treatment.created_at)).all()
            
        except Exception as e:
            logger.error(f"Error getting treatments for diagnosis {diagnosis_id}: {str(e)}")
            return []