"""
Diagnosis Repository for DiagnoAssist
Specialized CRUD operations for Diagnosis model
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from datetime import datetime, date, timedelta
from uuid import UUID
import logging

from models.diagnosis import Diagnosis
from models.episode import Episode
from repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)

class DiagnosisRepository(BaseRepository[Diagnosis]):
    """
    Repository for Diagnosis model with specialized operations
    """
    
    def __init__(self, db: Session):
        super().__init__(Diagnosis, db)
    
    def get_by_episode(self, episode_id: str) -> List[Diagnosis]:
        """
        Get all diagnoses for a specific episode
        
        Args:
            episode_id: Episode UUID
            
        Returns:
            List of diagnoses for the episode
        """
        try:
            return self.db.query(Diagnosis).filter(
                Diagnosis.episode_id == episode_id
            ).order_by(desc(Diagnosis.created_at)).all()
            
        except Exception as e:
            logger.error(f"Error getting diagnoses for episode {episode_id}: {str(e)}")
            return []
    
    def count_by_episode(self, episode_id: str) -> int:
        """
        Count diagnoses for a specific episode
        
        Args:
            episode_id: Episode UUID
            
        Returns:
            Number of diagnoses for the episode
        """
        try:
            return self.db.query(func.count(Diagnosis.id)).filter(
                Diagnosis.episode_id == episode_id
            ).scalar() or 0
            
        except Exception as e:
            logger.error(f"Error counting diagnoses for episode {episode_id}: {str(e)}")
            return 0
    
    def get_by_patient(self, patient_id: str, skip: int = 0, limit: int = 100) -> List[Diagnosis]:
        """
        Get diagnoses for a specific patient (via episodes)
        
        Args:
            patient_id: Patient UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of diagnoses for the patient
        """
        try:
            return self.db.query(Diagnosis).join(Episode).filter(
                Episode.patient_id == patient_id
            ).order_by(desc(Diagnosis.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting diagnoses for patient {patient_id}: {str(e)}")
            return []
    
    def get_final_diagnoses(self, skip: int = 0, limit: int = 100) -> List[Diagnosis]:
        """
        Get all final diagnoses
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of final diagnoses
        """
        try:
            return self.db.query(Diagnosis).filter(
                Diagnosis.final_diagnosis == True
            ).order_by(desc(Diagnosis.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting final diagnoses: {str(e)}")
            return []
    
    def get_confirmed_diagnoses(self, skip: int = 0, limit: int = 100) -> List[Diagnosis]:
        """
        Get all physician-confirmed diagnoses
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of confirmed diagnoses
        """
        try:
            return self.db.query(Diagnosis).filter(
                Diagnosis.physician_confirmed == True
            ).order_by(desc(Diagnosis.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting confirmed diagnoses: {str(e)}")
            return []
    
    def get_by_condition_name(self, condition_name: str, skip: int = 0, limit: int = 100) -> List[Diagnosis]:
        """
        Get diagnoses by condition name (case-insensitive)
        
        Args:
            condition_name: Condition name to search for
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching diagnoses
        """
        try:
            return self.db.query(Diagnosis).filter(
                Diagnosis.condition_name.ilike(f'%{condition_name}%')
            ).order_by(desc(Diagnosis.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting diagnoses by condition name '{condition_name}': {str(e)}")
            return []
    
    def get_by_icd10_code(self, icd10_code: str) -> List[Diagnosis]:
        """
        Get diagnoses by ICD-10 code
        
        Args:
            icd10_code: ICD-10 code
            
        Returns:
            List of diagnoses with the specified ICD-10 code
        """
        try:
            return self.db.query(Diagnosis).filter(
                Diagnosis.icd10_code == icd10_code
            ).order_by(desc(Diagnosis.created_at)).all()
            
        except Exception as e:
            logger.error(f"Error getting diagnoses by ICD-10 code {icd10_code}: {str(e)}")
            return []
    
    def get_by_snomed_code(self, snomed_code: str) -> List[Diagnosis]:
        """
        Get diagnoses by SNOMED code
        
        Args:
            snomed_code: SNOMED code
            
        Returns:
            List of diagnoses with the specified SNOMED code
        """
        try:
            return self.db.query(Diagnosis).filter(
                Diagnosis.snomed_code == snomed_code
            ).order_by(desc(Diagnosis.created_at)).all()
            
        except Exception as e:
            logger.error(f"Error getting diagnoses by SNOMED code {snomed_code}: {str(e)}")
            return []
    
    def get_by_confidence_level(self, confidence_level: str, skip: int = 0, limit: int = 100) -> List[Diagnosis]:
        """
        Get diagnoses by confidence level
        
        Args:
            confidence_level: Confidence level (low, medium, high)
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of diagnoses with the specified confidence level
        """
        try:
            return self.db.query(Diagnosis).filter(
                Diagnosis.confidence_level == confidence_level
            ).order_by(desc(Diagnosis.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting diagnoses by confidence level {confidence_level}: {str(e)}")
            return []
    
    def get_high_probability_diagnoses(self, threshold: float = 0.8, skip: int = 0, limit: int = 100) -> List[Diagnosis]:
        """
        Get diagnoses with AI probability above threshold
        
        Args:
            threshold: Probability threshold (0.0 to 1.0)
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of high-probability diagnoses
        """
        try:
            return self.db.query(Diagnosis).filter(
                and_(
                    Diagnosis.ai_probability.isnot(None),
                    Diagnosis.ai_probability >= threshold
                )
            ).order_by(desc(Diagnosis.ai_probability)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting high probability diagnoses: {str(e)}")
            return []
    
    def get_pending_confirmation(self, skip: int = 0, limit: int = 100) -> List[Diagnosis]:
        """
        Get diagnoses pending physician confirmation
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of diagnoses pending confirmation
        """
        try:
            return self.db.query(Diagnosis).filter(
                and_(
                    Diagnosis.physician_confirmed == False,
                    Diagnosis.status == "active"
                )
            ).order_by(desc(Diagnosis.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting diagnoses pending confirmation: {str(e)}")
            return []
    
    def confirm_diagnosis(self, diagnosis_id: str, physician_notes: Optional[str] = None, 
                         make_final: bool = False) -> bool:
        """
        Confirm a diagnosis
        
        Args:
            diagnosis_id: Diagnosis UUID
            physician_notes: Optional physician notes
            make_final: Whether to mark as final diagnosis
            
        Returns:
            True if successful, False otherwise
        """
        try:
            diagnosis = self.get_by_id(diagnosis_id)
            if not diagnosis:
                return False
            
            diagnosis.physician_confirmed = True
            diagnosis.updated_at = datetime.utcnow()
            
            if physician_notes:
                diagnosis.physician_notes = physician_notes
            
            if make_final:
                diagnosis.final_diagnosis = True
            
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error confirming diagnosis {diagnosis_id}: {str(e)}")
            self.db.rollback()
            return False
    
    def mark_as_final(self, diagnosis_id: str) -> bool:
        """
        Mark a diagnosis as final
        
        Args:
            diagnosis_id: Diagnosis UUID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            diagnosis = self.get_by_id(diagnosis_id)
            if not diagnosis:
                return False
            
            diagnosis.final_diagnosis = True
            diagnosis.physician_confirmed = True  # Final diagnoses must be confirmed
            diagnosis.updated_at = datetime.utcnow()
            
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error marking diagnosis {diagnosis_id} as final: {str(e)}")
            self.db.rollback()
            return False
    
    def search_diagnoses(self, search_term: str, skip: int = 0, limit: int = 100) -> List[Diagnosis]:
        """
        Search diagnoses by condition name, ICD-10 code, or SNOMED code
        
        Args:
            search_term: Search term
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching diagnoses
        """
        try:
            search_pattern = f"%{search_term}%"
            
            return self.db.query(Diagnosis).filter(
                or_(
                    Diagnosis.condition_name.ilike(search_pattern),
                    Diagnosis.icd10_code.ilike(search_pattern),
                    Diagnosis.snomed_code.ilike(search_pattern),
                    Diagnosis.ai_reasoning.ilike(search_pattern),
                    Diagnosis.supporting_symptoms.ilike(search_pattern)
                )
            ).order_by(desc(Diagnosis.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error searching diagnoses with term '{search_term}': {str(e)}")
            return []
    
    def get_diagnosis_statistics(self) -> Dict[str, Any]:
        """
        Get diagnosis statistics
        
        Returns:
            Dictionary with diagnosis statistics
        """
        try:
            total_diagnoses = self.db.query(func.count(Diagnosis.id)).scalar()
            confirmed_diagnoses = self.db.query(func.count(Diagnosis.id)).filter(
                Diagnosis.physician_confirmed == True
            ).scalar()
            final_diagnoses = self.db.query(func.count(Diagnosis.id)).filter(
                Diagnosis.final_diagnosis == True
            ).scalar()
            
            # Most common conditions
            condition_stats = self.db.query(
                Diagnosis.condition_name,
                func.count(Diagnosis.id)
            ).group_by(Diagnosis.condition_name).order_by(
                desc(func.count(Diagnosis.id))
            ).limit(10).all()
            
            top_conditions = {condition: count for condition, count in condition_stats}
            
            # Confidence level distribution
            confidence_stats = self.db.query(
                Diagnosis.confidence_level,
                func.count(Diagnosis.id)
            ).group_by(Diagnosis.confidence_level).all()
            
            confidence_distribution = {level: count for level, count in confidence_stats}
            
            # Average AI probability
            avg_probability = self.db.query(
                func.avg(Diagnosis.ai_probability)
            ).filter(Diagnosis.ai_probability.isnot(None)).scalar()
            
            return {
                "total_diagnoses": total_diagnoses or 0,
                "confirmed_diagnoses": confirmed_diagnoses or 0,
                "final_diagnoses": final_diagnoses or 0,
                "pending_confirmation": (total_diagnoses or 0) - (confirmed_diagnoses or 0),
                "top_conditions": top_conditions,
                "confidence_distribution": confidence_distribution,
                "average_ai_probability": round(float(avg_probability), 3) if avg_probability else 0.0
            }
            
        except Exception as e:
            logger.error(f"Error getting diagnosis statistics: {str(e)}")
            return {}
    
    def get_recent_diagnoses(self, days: int = 7, skip: int = 0, limit: int = 100) -> List[Diagnosis]:
        """
        Get diagnoses from the last N days
        
        Args:
            days: Number of days to look back
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of recent diagnoses
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            return self.db.query(Diagnosis).filter(
                Diagnosis.created_at >= cutoff_date
            ).order_by(desc(Diagnosis.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting recent diagnoses: {str(e)}")
            return []
    
    def get_active_diagnoses(self, skip: int = 0, limit: int = 100) -> List[Diagnosis]:
        """
        Get active diagnoses
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of active diagnoses
        """
        try:
            return self.db.query(Diagnosis).filter(
                Diagnosis.status == "active"
            ).order_by(desc(Diagnosis.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting active diagnoses: {str(e)}")
            return []
    
    def get_episode_final_diagnosis(self, episode_id: str) -> Optional[Diagnosis]:
        """
        Get the final diagnosis for an episode
        
        Args:
            episode_id: Episode UUID
            
        Returns:
            Final diagnosis for the episode or None if not found
        """
        try:
            return self.db.query(Diagnosis).filter(
                and_(
                    Diagnosis.episode_id == episode_id,
                    Diagnosis.final_diagnosis == True
                )
            ).first()
            
        except Exception as e:
            logger.error(f"Error getting final diagnosis for episode {episode_id}: {str(e)}")
            return None
    
    def count_by_patient(self, patient_id: str) -> int:
        """
        Count diagnoses for a specific patient
        
        Args:
            patient_id: Patient UUID
            
        Returns:
            Number of diagnoses for the patient
        """
        try:
            return self.db.query(func.count(Diagnosis.id)).join(Episode).filter(
                Episode.patient_id == patient_id
            ).scalar() or 0
            
        except Exception as e:
            logger.error(f"Error counting diagnoses for patient {patient_id}: {str(e)}")
            return 0