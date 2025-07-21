"""
Episode Repository for DiagnoAssist
Specialized CRUD operations for Episode model
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_, desc
from datetime import datetime, date, timedelta
from uuid import UUID
import logging

from models.episode import Episode
from repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)

class EpisodeRepository(BaseRepository[Episode]):
    """
    Repository for Episode model with specialized operations
    """
    
    def __init__(self, db: Session):
        super().__init__(Episode, db)
    
    def get_by_patient_id(self, patient_id: UUID, skip: int = 0, limit: int = 100) -> List[Episode]:
        """
        Get episodes for a specific patient
        
        Args:
            patient_id: Patient ID
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of episodes for the patient
        """
        try:
            return self.db.query(Episode).filter(
                Episode.patient_id == patient_id
            ).order_by(desc(Episode.start_time)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting episodes for patient {patient_id}: {str(e)}")
            return []
    
    def get_active_episodes(self, skip: int = 0, limit: int = 100) -> List[Episode]:
        """
        Get all active episodes (no end time)
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of active episodes
        """
        try:
            return self.db.query(Episode).filter(
                Episode.end_time.is_(None)
            ).order_by(desc(Episode.start_time)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting active episodes: {str(e)}")
            return []
    
    def get_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[Episode]:
        """
        Get episodes by status
        
        Args:
            status: Episode status (active, completed, cancelled)
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of episodes with matching status
        """
        try:
            return self.db.query(Episode).filter(
                Episode.status == status
            ).order_by(desc(Episode.start_time)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting episodes by status {status}: {str(e)}")
            return []
    
    def get_by_type(self, episode_type: str, skip: int = 0, limit: int = 100) -> List[Episode]:
        """
        Get episodes by type
        
        Args:
            episode_type: Episode type (consultation, emergency, follow-up, etc.)
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of episodes with matching type
        """
        try:
            return self.db.query(Episode).filter(
                Episode.episode_type == episode_type
            ).order_by(desc(Episode.start_time)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting episodes by type {episode_type}: {str(e)}")
            return []
    
    def get_by_date_range(self, start_date: date, end_date: date, 
                         skip: int = 0, limit: int = 100) -> List[Episode]:
        """
        Get episodes within date range
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of episodes within date range
        """
        try:
            return self.db.query(Episode).filter(
                and_(
                    Episode.start_time >= start_date,
                    Episode.start_time <= end_date
                )
            ).order_by(desc(Episode.start_time)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting episodes by date range {start_date} to {end_date}: {str(e)}")
            return []
    
    def get_with_diagnoses(self, episode_id: UUID) -> Optional[Episode]:
        """
        Get episode with all associated diagnoses
        
        Args:
            episode_id: Episode ID
            
        Returns:
            Episode with diagnoses loaded or None if not found
        """
        try:
            return self.db.query(Episode).options(
                joinedload(Episode.diagnoses)
            ).filter(Episode.id == episode_id).first()
            
        except Exception as e:
            logger.error(f"Error getting episode {episode_id} with diagnoses: {str(e)}")
            return None
    
    def get_with_treatments(self, episode_id: UUID) -> Optional[Episode]:
        """
        Get episode with all associated treatments
        
        Args:
            episode_id: Episode ID
            
        Returns:
            Episode with treatments loaded or None if not found
        """
        try:
            return self.db.query(Episode).options(
                joinedload(Episode.treatments)
            ).filter(Episode.id == episode_id).first()
            
        except Exception as e:
            logger.error(f"Error getting episode {episode_id} with treatments: {str(e)}")
            return None
    
    def get_complete_episode(self, episode_id: UUID) -> Optional[Episode]:
        """
        Get episode with all related data (diagnoses, treatments)
        
        Args:
            episode_id: Episode ID
            
        Returns:
            Complete episode with all relationships loaded
        """
        try:
            return self.db.query(Episode).options(
                joinedload(Episode.diagnoses),
                joinedload(Episode.treatments)
            ).filter(Episode.id == episode_id).first()
            
        except Exception as e:
            logger.error(f"Error getting complete episode {episode_id}: {str(e)}")
            return None
    
    def search_by_chief_complaint(self, complaint: str, limit: int = 50) -> List[Episode]:
        """
        Search episodes by chief complaint
        
        Args:
            complaint: Search term for chief complaint
            limit: Maximum number of results
            
        Returns:
            List of episodes matching chief complaint
        """
        try:
            search_pattern = f'%{complaint}%'
            return self.db.query(Episode).filter(
                Episode.chief_complaint.ilike(search_pattern)
            ).order_by(desc(Episode.start_time)).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error searching episodes by chief complaint '{complaint}': {str(e)}")
            return []
    
    def get_recent_episodes(self, days: int = 7, limit: int = 100) -> List[Episode]:
        """
        Get recent episodes within specified days
        
        Args:
            days: Number of days to look back
            limit: Maximum number of records
            
        Returns:
            List of recent episodes
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            return self.db.query(Episode).filter(
                Episode.start_time >= cutoff_date
            ).order_by(desc(Episode.start_time)).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting recent episodes: {str(e)}")
            return []
    
    def get_episodes_by_priority(self, priority: str, skip: int = 0, limit: int = 100) -> List[Episode]:
        """
        Get episodes by priority level
        
        Args:
            priority: Priority level (low, normal, high, urgent)
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of episodes with matching priority
        """
        try:
            return self.db.query(Episode).filter(
                Episode.priority == priority
            ).order_by(desc(Episode.start_time)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting episodes by priority {priority}: {str(e)}")
            return []
    
    def close_episode(self, episode_id: UUID, end_time: Optional[datetime] = None) -> Optional[Episode]:
        """
        Close an episode by setting end time and status
        
        Args:
            episode_id: Episode ID
            end_time: End time (defaults to current time)
            
        Returns:
            Updated episode or None if failed
        """
        try:
            if end_time is None:
                end_time = datetime.utcnow()
            
            return self.update(episode_id, {
                "end_time": end_time,
                "status": "completed"
            })
            
        except Exception as e:
            logger.error(f"Error closing episode {episode_id}: {str(e)}")
            return None
    
    def get_episode_duration_stats(self) -> Dict[str, Any]:
        """
        Get statistics about episode durations
        
        Returns:
            Dictionary with duration statistics
        """
        try:
            # Get completed episodes with duration calculation
            completed_episodes = self.db.query(Episode).filter(
                and_(
                    Episode.end_time.isnot(None),
                    Episode.start_time.isnot(None)
                )
            ).all()
            
            if not completed_episodes:
                return {"message": "No completed episodes found"}
            
            durations = []
            for episode in completed_episodes:
                duration = episode.end_time - episode.start_time
                durations.append(duration.total_seconds() / 3600)  # Convert to hours
            
            avg_duration = sum(durations) / len(durations)
            min_duration = min(durations)
            max_duration = max(durations)
            
            return {
                "total_completed_episodes": len(completed_episodes),
                "average_duration_hours": round(avg_duration, 2),
                "min_duration_hours": round(min_duration, 2),
                "max_duration_hours": round(max_duration, 2),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting episode duration stats: {str(e)}")
            return {}
    
    def get_episode_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive episode statistics
        
        Returns:
            Dictionary with episode statistics
        """
        try:
            total_episodes = self.count()
            
            status_stats = self.db.query(
                Episode.status,
                func.count(Episode.id).label('count')
            ).group_by(Episode.status).all()
            
            type_stats = self.db.query(
                Episode.episode_type,
                func.count(Episode.id).label('count')
            ).group_by(Episode.episode_type).all()
            
            priority_stats = self.db.query(
                Episode.priority,
                func.count(Episode.id).label('count')
            ).group_by(Episode.priority).all()
            
            return {
                "total_episodes": total_episodes,
                "status_distribution": {stat.status: stat.count for stat in status_stats},
                "type_distribution": {stat.episode_type: stat.count for stat in type_stats},
                "priority_distribution": {stat.priority: stat.count for stat in priority_stats},
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting episode statistics: {str(e)}")
            return {}