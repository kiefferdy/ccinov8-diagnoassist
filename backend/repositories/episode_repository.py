"""
Episode Repository for DiagnoAssist
Specialized CRUD operations for Episode model
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from datetime import datetime, date, timedelta
from uuid import UUID
import logging

from models.episode import Episode
from models.patient import Patient
from repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)

class EpisodeRepository(BaseRepository[Episode]):
    """
    Repository for Episode model with specialized operations
    """
    
    def __init__(self, db: Session):
        super().__init__(Episode, db)
    
    def get_by_patient(self, patient_id: str, skip: int = 0, limit: int = 100) -> List[Episode]:
        """
        Get episodes for a specific patient
        
        Args:
            patient_id: Patient UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of episodes for the patient
        """
        try:
            return self.db.query(Episode).filter(
                Episode.patient_id == patient_id
            ).order_by(desc(Episode.start_date)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting episodes for patient {patient_id}: {str(e)}")
            return []
    
    def get_active_by_patient(self, patient_id: str) -> List[Episode]:
        """
        Get active episodes for a specific patient
        
        Args:
            patient_id: Patient UUID
            
        Returns:
            List of active episodes for the patient
        """
        try:
            return self.db.query(Episode).filter(
                and_(
                    Episode.patient_id == patient_id,
                    Episode.status == "active"
                )
            ).order_by(desc(Episode.start_date)).all()
            
        except Exception as e:
            logger.error(f"Error getting active episodes for patient {patient_id}: {str(e)}")
            return []
    
    def get_by_date_range(self, start_date: datetime, end_date: datetime, 
                         skip: int = 0, limit: int = 100) -> List[Episode]:
        """
        Get episodes within a specific date range
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of episodes in the date range
        """
        try:
            return self.db.query(Episode).filter(
                and_(
                    Episode.start_date >= start_date,
                    Episode.start_date <= end_date
                )
            ).order_by(desc(Episode.start_date)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting episodes in date range: {str(e)}")
            return []
    
    def get_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[Episode]:
        """
        Get episodes by status
        
        Args:
            status: Episode status (active, completed, cancelled)
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of episodes with the specified status
        """
        try:
            return self.db.query(Episode).filter(
                Episode.status == status
            ).order_by(desc(Episode.start_date)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting episodes with status {status}: {str(e)}")
            return []
    
    def get_by_encounter_type(self, encounter_type: str, skip: int = 0, limit: int = 100) -> List[Episode]:
        """
        Get episodes by encounter type
        
        Args:
            encounter_type: Type of encounter (inpatient, outpatient, emergency)
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of episodes with the specified encounter type
        """
        try:
            return self.db.query(Episode).filter(
                Episode.encounter_type == encounter_type
            ).order_by(desc(Episode.start_date)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting episodes with encounter type {encounter_type}: {str(e)}")
            return []
    
    def get_by_provider(self, provider_id: str, skip: int = 0, limit: int = 100) -> List[Episode]:
        """
        Get episodes by provider
        
        Args:
            provider_id: Provider identifier
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of episodes for the specified provider
        """
        try:
            return self.db.query(Episode).filter(
                Episode.provider_id == provider_id
            ).order_by(desc(Episode.start_date)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting episodes for provider {provider_id}: {str(e)}")
            return []
    
    def get_ongoing_episodes(self, skip: int = 0, limit: int = 100) -> List[Episode]:
        """
        Get ongoing episodes (started but not ended)
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of ongoing episodes
        """
        try:
            return self.db.query(Episode).filter(
                and_(
                    Episode.start_date <= datetime.utcnow(),
                    Episode.end_date.is_(None),
                    Episode.status == "active"
                )
            ).order_by(desc(Episode.start_date)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting ongoing episodes: {str(e)}")
            return []
    
    def complete_episode(self, episode_id: str, end_date: Optional[datetime] = None) -> bool:
        """
        Complete an episode by setting end date and status
        
        Args:
            episode_id: Episode UUID
            end_date: End date (defaults to current time)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            episode = self.get_by_id(episode_id)
            if not episode:
                return False
            
            episode.end_date = end_date or datetime.utcnow()
            episode.status = "completed"
            episode.updated_at = datetime.utcnow()
            
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error completing episode {episode_id}: {str(e)}")
            self.db.rollback()
            return False
    
    def cancel_episode(self, episode_id: str, reason: Optional[str] = None) -> bool:
        """
        Cancel an episode
        
        Args:
            episode_id: Episode UUID
            reason: Cancellation reason
            
        Returns:
            True if successful, False otherwise
        """
        try:
            episode = self.get_by_id(episode_id)
            if not episode:
                return False
            
            episode.status = "cancelled"
            episode.updated_at = datetime.utcnow()
            
            if reason:
                # Add reason to clinical notes
                if episode.clinical_notes:
                    episode.clinical_notes += f"\n\nCancelled: {reason}"
                else:
                    episode.clinical_notes = f"Cancelled: {reason}"
            
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling episode {episode_id}: {str(e)}")
            self.db.rollback()
            return False
    
    def get_episode_statistics(self) -> Dict[str, Any]:
        """
        Get episode statistics
        
        Returns:
            Dictionary with episode statistics
        """
        try:
            total_episodes = self.db.query(func.count(Episode.id)).scalar()
            active_episodes = self.db.query(func.count(Episode.id)).filter(
                Episode.status == "active"
            ).scalar()
            completed_episodes = self.db.query(func.count(Episode.id)).filter(
                Episode.status == "completed"
            ).scalar()
            
            # Average episode duration for completed episodes
            avg_duration_query = self.db.query(
                func.avg(
                    func.extract('epoch', Episode.end_date - Episode.start_date) / 86400
                )
            ).filter(
                and_(
                    Episode.status == "completed",
                    Episode.end_date.isnot(None)
                )
            )
            avg_duration_days = avg_duration_query.scalar()
            
            return {
                "total_episodes": total_episodes or 0,
                "active_episodes": active_episodes or 0,
                "completed_episodes": completed_episodes or 0,
                "cancelled_episodes": total_episodes - active_episodes - completed_episodes,
                "average_duration_days": round(avg_duration_days, 2) if avg_duration_days else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting episode statistics: {str(e)}")
            return {}
    
    def search_episodes(self, search_term: str, skip: int = 0, limit: int = 100) -> List[Episode]:
        """
        Search episodes by chief complaint or clinical notes
        
        Args:
            search_term: Search term
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching episodes
        """
        try:
            search_pattern = f"%{search_term}%"
            
            return self.db.query(Episode).filter(
                or_(
                    Episode.chief_complaint.ilike(search_pattern),
                    Episode.clinical_notes.ilike(search_pattern),
                    Episode.assessment_notes.ilike(search_pattern),
                    Episode.symptoms.ilike(search_pattern)
                )
            ).order_by(desc(Episode.start_date)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error searching episodes with term '{search_term}': {str(e)}")
            return []
    
    def get_recent_episodes(self, days: int = 7, skip: int = 0, limit: int = 100) -> List[Episode]:
        """
        Get episodes from the last N days
        
        Args:
            days: Number of days to look back
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of recent episodes
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            return self.db.query(Episode).filter(
                Episode.start_date >= cutoff_date
            ).order_by(desc(Episode.start_date)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting recent episodes: {str(e)}")
            return []
    
    def count_by_patient(self, patient_id: str) -> int:
        """
        Count episodes for a specific patient
        
        Args:
            patient_id: Patient UUID
            
        Returns:
            Number of episodes for the patient
        """
        try:
            return self.db.query(func.count(Episode.id)).filter(
                Episode.patient_id == patient_id
            ).scalar() or 0
            
        except Exception as e:
            logger.error(f"Error counting episodes for patient {patient_id}: {str(e)}")
            return 0
    
    def get_patient_latest_episode(self, patient_id: str) -> Optional[Episode]:
        """
        Get the most recent episode for a patient
        
        Args:
            patient_id: Patient UUID
            
        Returns:
            Most recent episode or None if no episodes found
        """
        try:
            return self.db.query(Episode).filter(
                Episode.patient_id == patient_id
            ).order_by(desc(Episode.start_date)).first()
            
        except Exception as e:
            logger.error(f"Error getting latest episode for patient {patient_id}: {str(e)}")
            return None