from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, timedelta
from models.episode import Episode
from schemas.episode import EpisodeCreate, EpisodeUpdate
from .base import BaseRepository
import logging

logger = logging.getLogger(__name__)

class EpisodeRepository(BaseRepository[Episode, EpisodeCreate, EpisodeUpdate]):
    """
    Repository for Episode (medical encounter) data access operations
    """
    
    def __init__(self, db: Session):
        super().__init__(Episode, db)
    
    def get_by_patient_id(
        self, 
        patient_id: str, 
        skip: int = 0, 
        limit: int = 100,
        include_closed: bool = True
    ) -> List[Episode]:
        """
        Get episodes for a specific patient
        
        Args:
            patient_id: Patient identifier
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_closed: Whether to include closed episodes
            
        Returns:
            List of episodes for the patient
        """
        try:
            query = self.db.query(Episode).filter(Episode.patient_id == patient_id)
            
            if not include_closed:
                query = query.filter(Episode.status != 'closed')
            
            return query.order_by(desc(Episode.start_date)).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting episodes for patient {patient_id}: {str(e)}")
            raise
    
    def get_active_episodes(self, patient_id: Optional[str] = None) -> List[Episode]:
        """
        Get active (open) episodes
        
        Args:
            patient_id: Optional patient filter
            
        Returns:
            List of active episodes
        """
        try:
            query = self.db.query(Episode).filter(
                Episode.status.in_(['active', 'in-progress', 'pending'])
            )
            
            if patient_id:
                query = query.filter(Episode.patient_id == patient_id)
            
            return query.order_by(desc(Episode.start_date)).all()
        except Exception as e:
            logger.error(f"Error getting active episodes: {str(e)}")
            raise
    
    def get_episodes_by_status(self, status: str, limit: int = 100) -> List[Episode]:
        """
        Get episodes by status
        
        Args:
            status: Episode status
            limit: Maximum number of records to return
            
        Returns:
            List of episodes with the specified status
        """
        try:
            return self.db.query(Episode).filter(
                Episode.status == status
            ).order_by(desc(Episode.start_date)).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting episodes by status {status}: {str(e)}")
            raise
    
    def get_episodes_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        patient_id: Optional[str] = None
    ) -> List[Episode]:
        """
        Get episodes within a date range
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            patient_id: Optional patient filter
            
        Returns:
            List of episodes within the date range
        """
        try:
            query = self.db.query(Episode).filter(
                and_(
                    Episode.start_date >= start_date,
                    Episode.start_date <= end_date
                )
            )
            
            if patient_id:
                query = query.filter(Episode.patient_id == patient_id)
            
            return query.order_by(desc(Episode.start_date)).all()
        except Exception as e:
            logger.error(f"Error getting episodes by date range: {str(e)}")
            raise
    
    def search_by_chief_complaint(self, complaint_query: str) -> List[Episode]:
        """
        Search episodes by chief complaint
        
        Args:
            complaint_query: Search query for chief complaint
            
        Returns:
            List of episodes matching the complaint search
        """
        try:
            search_term = f"%{complaint_query.lower()}%"
            return self.db.query(Episode).filter(
                func.lower(Episode.chief_complaint).like(search_term)
            ).order_by(desc(Episode.start_date)).all()
        except Exception as e:
            logger.error(f"Error searching episodes by chief complaint '{complaint_query}': {str(e)}")
            raise
    
    def get_episodes_with_diagnoses(self, patient_id: Optional[str] = None) -> List[Episode]:
        """
        Get episodes that have associated diagnoses
        
        Args:
            patient_id: Optional patient filter
            
        Returns:
            List of episodes with diagnoses
        """
        try:
            query = self.db.query(Episode).join(Episode.diagnoses)
            
            if patient_id:
                query = query.filter(Episode.patient_id == patient_id)
            
            return query.order_by(desc(Episode.start_date)).all()
        except Exception as e:
            logger.error(f"Error getting episodes with diagnoses: {str(e)}")
            raise
    
    def get_recent_episodes(self, days: int = 7, limit: int = 50) -> List[Episode]:
        """
        Get recent episodes
        
        Args:
            days: Number of days to look back
            limit: Maximum number of episodes to return
            
        Returns:
            List of recent episodes
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            return self.db.query(Episode).filter(
                Episode.start_date >= cutoff_date
            ).order_by(desc(Episode.start_date)).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting recent episodes: {str(e)}")
            raise
    
    def get_episode_with_related_data(self, episode_id: str) -> Optional[Episode]:
        """
        Get episode with all related data (diagnoses, treatments)
        
        Args:
            episode_id: Episode identifier
            
        Returns:
            Episode with related data or None
        """
        try:
            return self.db.query(Episode).options(
                joinedload(Episode.diagnoses),
                joinedload(Episode.treatments),
                joinedload(Episode.patient)
            ).filter(Episode.id == episode_id).first()
        except Exception as e:
            logger.error(f"Error getting episode with related data {episode_id}: {str(e)}")
            raise
    
    def get_episode_statistics(self, patient_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get episode statistics
        
        Args:
            patient_id: Optional patient filter
            
        Returns:
            Dictionary with episode statistics
        """
        try:
            query = self.db.query(Episode)
            if patient_id:
                query = query.filter(Episode.patient_id == patient_id)
            
            total_episodes = query.count()
            active_episodes = query.filter(Episode.status == 'active').count()
            closed_episodes = query.filter(Episode.status == 'closed').count()
            
            # Average episode duration for closed episodes
            closed_query = query.filter(
                and_(Episode.status == 'closed', Episode.end_date.isnot(None))
            )
            
            avg_duration = None
            if closed_query.count() > 0:
                durations = []
                for episode in closed_query.all():
                    if episode.end_date and episode.start_date:
                        duration = (episode.end_date - episode.start_date).days
                        durations.append(duration)
                
                if durations:
                    avg_duration = sum(durations) / len(durations)
            
            return {
                "total_episodes": total_episodes,
                "active_episodes": active_episodes,
                "closed_episodes": closed_episodes,
                "average_duration_days": avg_duration
            }
        except Exception as e:
            logger.error(f"Error getting episode statistics: {str(e)}")
            raise