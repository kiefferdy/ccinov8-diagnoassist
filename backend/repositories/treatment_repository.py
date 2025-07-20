from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, desc
from models.treatment import Treatment
from schemas.treatment import TreatmentCreate, TreatmentUpdate
from .base import BaseRepository
import logging

logger = logging.getLogger(__name__)

class TreatmentRepository(BaseRepository[Treatment, TreatmentCreate, TreatmentUpdate]):
    """
    Repository for Treatment data access operations
    """
    
    def __init__(self, db: Session):
        super().__init__(Treatment, db)
    
    def get_by_episode_id(self, episode_id: str) -> List[Treatment]:
        """
        Get all treatments for an episode
        
        Args:
            episode_id: Episode identifier
            
        Returns:
            List of treatments for the episode
        """
        try:
            return self.db.query(Treatment).filter(
                Treatment.episode_id == episode_id
            ).order_by(desc(Treatment.created_at)).all()
        except Exception as e:
            logger.error(f"Error getting treatments for episode {episode_id}: {str(e)}")
            raise
    
    def get_by_diagnosis_id(self, diagnosis_id: str) -> List[Treatment]:
        """
        Get treatments for a specific diagnosis
        
        Args:
            diagnosis_id: Diagnosis identifier
            
        Returns:
            List of treatments for the diagnosis
        """
        try:
            return self.db.query(Treatment).filter(
                Treatment.diagnosis_id == diagnosis_id
            ).order_by(desc(Treatment.created_at)).all()
        except Exception as e:
            logger.error(f"Error getting treatments for diagnosis {diagnosis_id}: {str(e)}")
            raise
    
    def get_active_treatments(self, patient_id: Optional[str] = None) -> List[Treatment]:
        """
        Get active treatments
        
        Args:
            patient_id: Optional patient filter
            
        Returns:
            List of active treatments
        """
        try:
            query = self.db.query(Treatment).join(Treatment.episode)
            
            if patient_id:
                query = query.filter(Episode.patient_id == patient_id)
            
            # Filter for active episodes
            query = query.filter(Episode.status == 'active')
            
            return query.order_by(desc(Treatment.created_at)).all()
        except Exception as e:
            logger.error(f"Error getting active treatments: {str(e)}")
            raise