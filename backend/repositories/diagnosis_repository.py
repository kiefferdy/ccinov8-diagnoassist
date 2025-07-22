"""
Diagnosis Repository for DiagnoAssist
Specialized CRUD operations for Diagnosis model
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_, desc
from datetime import datetime, date, timedelta
from uuid import UUID
import logging

from models.diagnosis import Diagnosis
from repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)

class DiagnosisRepository(BaseRepository[Diagnosis]):
    """
    Repository for Diagnosis model with specialized operations
    """
    
    def __init__(self, db: Session):
        super().__init__(Diagnosis, db)
    
    def get_by_episode_id(self, episode_id: UUID, skip: int = 0, limit: int = 100) -> List[Diagnosis]:
        """
        Get all diagnoses for a specific episode
        
        Args:
            episode_id: Episode ID
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of diagnoses for the episode
        """
        try:
            return self.db.query(Diagnosis).filter(
                Diagnosis.episode_id == episode_id
            ).order_by(desc(Diagnosis.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting diagnoses for episode {episode_id}: {str(e)}")
            return []
    
    def get_by_condition_name(self, condition_name: str, skip: int = 0, limit: int = 100) -> List[Diagnosis]:
        """
        Get diagnoses by condition name (case-insensitive search)
        
        Args:
            condition_name: Condition name to search for
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of diagnoses matching condition name
        """
        try:
            search_pattern = f'%{condition_name}%'
            return self.db.query(Diagnosis).filter(
                Diagnosis.condition_name.ilike(search_pattern)
            ).order_by(desc(Diagnosis.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting diagnoses by condition '{condition_name}': {str(e)}")
            return []
    
    def get_by_icd10_code(self, icd10_code: str) -> List[Diagnosis]:
        """
        Get diagnoses by ICD-10 code
        
        Args:
            icd10_code: ICD-10 code
            
        Returns:
            List of diagnoses with matching ICD-10 code
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
            List of diagnoses with matching SNOMED code
        """
        try:
            return self.db.query(Diagnosis).filter(
                Diagnosis.snomed_code == snomed_code
            ).order_by(desc(Diagnosis.created_at)).all()
            
        except Exception as e:
            logger.error(f"Error getting diagnoses by SNOMED code {snomed_code}: {str(e)}")
            return []
    
    def get_confirmed_diagnoses(self, skip: int = 0, limit: int = 100) -> List[Diagnosis]:
        """
        Get physician-confirmed diagnoses
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records
            
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
    
    def get_pending_confirmation(self, skip: int = 0, limit: int = 100) -> List[Diagnosis]:
        """
        Get diagnoses pending physician confirmation
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of diagnoses pending confirmation
        """
        try:
            return self.db.query(Diagnosis).filter(
                Diagnosis.physician_confirmed == False
            ).order_by(desc(Diagnosis.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting pending diagnoses: {str(e)}")
            return []
    
    def get_by_confidence_level(self, confidence_level: str, skip: int = 0, limit: int = 100) -> List[Diagnosis]:
        """
        Get diagnoses by AI confidence level
        
        Args:
            confidence_level: Confidence level (low, moderate, high)
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of diagnoses with matching confidence level
        """
        try:
            return self.db.query(Diagnosis).filter(
                Diagnosis.confidence_level == confidence_level
            ).order_by(desc(Diagnosis.ai_probability)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting diagnoses by confidence level {confidence_level}: {str(e)}")
            return []
    
    def get_by_probability_range(self, min_probability: float, max_probability: float) -> List[Diagnosis]:
        """
        Get diagnoses within AI probability range
        
        Args:
            min_probability: Minimum AI probability (0.0 to 1.0)
            max_probability: Maximum AI probability (0.0 to 1.0)
            
        Returns:
            List of diagnoses within probability range
        """
        try:
            return self.db.query(Diagnosis).filter(
                and_(
                    Diagnosis.ai_probability >= min_probability,
                    Diagnosis.ai_probability <= max_probability
                )
            ).order_by(desc(Diagnosis.ai_probability)).all()
            
        except Exception as e:
            logger.error(f"Error getting diagnoses by probability range {min_probability}-{max_probability}: {str(e)}")
            return []
    
    def get_final_diagnoses(self, skip: int = 0, limit: int = 100) -> List[Diagnosis]:
        """
        Get final/primary diagnoses
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records
            
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
    
    def get_by_created_by(self, created_by: str, skip: int = 0, limit: int = 100) -> List[Diagnosis]:
        """
        Get diagnoses by creator (ai_system, physician, etc.)
        
        Args:
            created_by: Creator identifier
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of diagnoses created by specified source
        """
        try:
            return self.db.query(Diagnosis).filter(
                Diagnosis.created_by == created_by
            ).order_by(desc(Diagnosis.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting diagnoses by creator {created_by}: {str(e)}")
            return []
    
    def confirm_diagnosis(self, diagnosis_id: UUID, physician_notes: Optional[str] = None) -> Optional[Diagnosis]:
        """
        Confirm a diagnosis by physician
        
        Args:
            diagnosis_id: Diagnosis ID
            physician_notes: Optional physician notes
            
        Returns:
            Updated diagnosis or None if failed
        """
        try:
            update_data = {
                "physician_confirmed": True,
                "updated_at": datetime.utcnow()
            }
            
            if physician_notes:
                update_data["physician_notes"] = physician_notes
            
            return self.update(diagnosis_id, update_data)
            
        except Exception as e:
            logger.error(f"Error confirming diagnosis {diagnosis_id}: {str(e)}")
            return None
    
    def set_as_final_diagnosis(self, diagnosis_id: UUID) -> Optional[Diagnosis]:
        """
        Set diagnosis as final/primary diagnosis for the episode
        
        Args:
            diagnosis_id: Diagnosis ID
            
        Returns:
            Updated diagnosis or None if failed
        """
        try:
            # First, get the diagnosis to find the episode
            diagnosis = self.get_by_id(diagnosis_id)
            if not diagnosis:
                return None
            
            # Set all other diagnoses for this episode as not final
            self.db.query(Diagnosis).filter(
                and_(
                    Diagnosis.episode_id == diagnosis.episode_id,
                    Diagnosis.id != diagnosis_id
                )
            ).update({"final_diagnosis": False})
            
            # Set this diagnosis as final
            return self.update(diagnosis_id, {
                "final_diagnosis": True,
                "updated_at": datetime.utcnow()
            })
            
        except Exception as e:
            logger.error(f"Error setting final diagnosis {diagnosis_id}: {str(e)}")
            return None
    
    def search_by_symptoms(self, symptoms: List[str], limit: int = 50) -> List[Diagnosis]:
        """
        Search diagnoses by symptoms in supporting_symptoms field
        
        Args:
            symptoms: List of symptoms to search for
            limit: Maximum number of results
            
        Returns:
            List of diagnoses with matching symptoms
        """
        try:
            # This is a simplified search - in practice, you might want more sophisticated JSON querying
            query = self.db.query(Diagnosis)
            
            for symptom in symptoms:
                # Use PostgreSQL JSON contains operator
                query = query.filter(
                    Diagnosis.supporting_symptoms.contains([symptom])
                )
            
            return query.order_by(desc(Diagnosis.ai_probability)).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error searching diagnoses by symptoms {symptoms}: {str(e)}")
            return []
    
    def get_diagnosis_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive diagnosis statistics
        
        Returns:
            Dictionary with diagnosis statistics
        """
        try:
            total_diagnoses = self.count()
            
            confirmed_count = self.db.query(func.count(Diagnosis.id)).filter(
                Diagnosis.physician_confirmed == True
            ).scalar()
            
            final_count = self.db.query(func.count(Diagnosis.id)).filter(
                Diagnosis.final_diagnosis == True
            ).scalar()
            
            confidence_stats = self.db.query(
                Diagnosis.confidence_level,
                func.count(Diagnosis.id).label('count')
            ).group_by(Diagnosis.confidence_level).all()
            
            creator_stats = self.db.query(
                Diagnosis.created_by,
                func.count(Diagnosis.id).label('count')
            ).group_by(Diagnosis.created_by).all()
            
            # Average AI probability
            avg_probability = self.db.query(
                func.avg(Diagnosis.ai_probability)
            ).scalar()
            
            return {
                "total_diagnoses": total_diagnoses,
                "confirmed_diagnoses": confirmed_count,
                "final_diagnoses": final_count,
                "pending_confirmation": total_diagnoses - confirmed_count,
                "average_ai_probability": round(float(avg_probability or 0), 3),
                "confidence_distribution": {stat.confidence_level: stat.count for stat in confidence_stats},
                "creator_distribution": {stat.created_by: stat.count for stat in creator_stats},
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting diagnosis statistics: {str(e)}")
            return {}
    
    def get_most_common_conditions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get most common diagnosed conditions
        
        Args:
            limit: Maximum number of conditions to return
            
        Returns:
            List of conditions with counts
        """
        try:
            conditions = self.db.query(
                Diagnosis.condition_name,
                func.count(Diagnosis.id).label('count')
            ).group_by(Diagnosis.condition_name).order_by(
                desc(func.count(Diagnosis.id))
            ).limit(limit).all()
            
            return [
                {"condition": condition.condition_name, "count": condition.count}
                for condition in conditions
            ]
            
        except Exception as e:
            logger.error(f"Error getting most common conditions: {str(e)}")
            return []
    def get_by_episode(self, episode_id: str, skip: int = 0, limit: int = 100) -> List[Diagnosis]:
        """Get all diagnoses for a specific episode"""
        try:
            from uuid import UUID
            episode_uuid = UUID(episode_id) if isinstance(episode_id, str) else episode_id
            return self.db.query(Diagnosis).filter(
                Diagnosis.episode_id == episode_uuid
            ).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting diagnoses for episode {episode_id}: {str(e)}")
            return []