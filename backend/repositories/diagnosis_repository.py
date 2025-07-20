from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, desc, func
from datetime import datetime, timedelta
from models.diagnosis import Diagnosis
from schemas.diagnosis import DiagnosisCreate, DiagnosisUpdate
from .base import BaseRepository
import logging

logger = logging.getLogger(__name__)

class DiagnosisRepository(BaseRepository[Diagnosis, DiagnosisCreate, DiagnosisUpdate]):
    """
    Repository for Diagnosis data access operations
    """
    
    def __init__(self, db: Session):
        super().__init__(Diagnosis, db)
    
    def get_by_episode_id(self, episode_id: str) -> List[Diagnosis]:
        """
        Get all diagnoses for an episode
        
        Args:
            episode_id: Episode identifier
            
        Returns:
            List of diagnoses for the episode
        """
        try:
            return self.db.query(Diagnosis).filter(
                Diagnosis.episode_id == episode_id
            ).order_by(desc(Diagnosis.created_at)).all()
        except Exception as e:
            logger.error(f"Error getting diagnoses for episode {episode_id}: {str(e)}")
            raise
    
    def get_latest_by_episode_id(self, episode_id: str) -> Optional[Diagnosis]:
        """
        Get the most recent diagnosis for an episode
        
        Args:
            episode_id: Episode identifier
            
        Returns:
            Latest diagnosis for the episode or None
        """
        try:
            return self.db.query(Diagnosis).filter(
                Diagnosis.episode_id == episode_id
            ).order_by(desc(Diagnosis.created_at)).first()
        except Exception as e:
            logger.error(f"Error getting latest diagnosis for episode {episode_id}: {str(e)}")
            raise
    
    def get_by_patient_id(self, patient_id: str, limit: int = 50) -> List[Diagnosis]:
        """
        Get diagnoses for a patient across all episodes
        
        Args:
            patient_id: Patient identifier
            limit: Maximum number of diagnoses to return
            
        Returns:
            List of diagnoses for the patient
        """
        try:
            return self.db.query(Diagnosis).join(Diagnosis.episode).filter(
                Episode.patient_id == patient_id
            ).order_by(desc(Diagnosis.created_at)).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting diagnoses for patient {patient_id}: {str(e)}")
            raise
    
    def search_by_condition(self, condition_query: str) -> List[Diagnosis]:
        """
        Search diagnoses by condition/diagnosis text
        
        Args:
            condition_query: Search query for condition
            
        Returns:
            List of diagnoses matching the condition search
        """
        try:
            search_term = f"%{condition_query.lower()}%"
            return self.db.query(Diagnosis).filter(
                or_(
                    func.lower(Diagnosis.final_diagnosis).like(search_term),
                    func.lower(func.cast(Diagnosis.differential_diagnoses, String)).like(search_term)
                )
            ).order_by(desc(Diagnosis.created_at)).all()
        except Exception as e:
            logger.error(f"Error searching diagnoses by condition '{condition_query}': {str(e)}")
            raise
    
    def get_diagnoses_with_high_confidence(
        self, 
        min_confidence: float = 0.8,
        limit: int = 100
    ) -> List[Diagnosis]:
        """
        Get diagnoses with high AI confidence scores
        
        Args:
            min_confidence: Minimum confidence threshold
            limit: Maximum number of diagnoses to return
            
        Returns:
            List of high-confidence diagnoses
        """
        try:
            # This would need to be adapted based on how confidence scores are stored
            # Assuming JSON structure with confidence scores
            return self.db.query(Diagnosis).filter(
                Diagnosis.confidence_scores.isnot(None)
            ).order_by(desc(Diagnosis.created_at)).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting high-confidence diagnoses: {str(e)}")
            raise
    
    def get_diagnoses_requiring_followup(self) -> List[Diagnosis]:
        """
        Get diagnoses that require follow-up
        
        Returns:
            List of diagnoses requiring follow-up
        """
        try:
            # This would be based on specific business logic
            # For now, get diagnoses without final diagnosis or with low confidence
            return self.db.query(Diagnosis).filter(
                or_(
                    Diagnosis.final_diagnosis.is_(None),
                    Diagnosis.final_diagnosis == ""
                )
            ).order_by(desc(Diagnosis.created_at)).all()
        except Exception as e:
            logger.error(f"Error getting diagnoses requiring follow-up: {str(e)}")
            raise
    
    def get_diagnosis_statistics(self) -> Dict[str, Any]:
        """
        Get diagnosis statistics
        
        Returns:
            Dictionary with diagnosis statistics
        """
        try:
            total_diagnoses = self.db.query(Diagnosis).count()
            final_diagnoses = self.db.query(Diagnosis).filter(
                and_(
                    Diagnosis.final_diagnosis.isnot(None),
                    Diagnosis.final_diagnosis != ""
                )
            ).count()
            
            # Most common diagnoses
            # This would need to be adapted based on how diagnoses are stored
            common_diagnoses = self.db.query(
                Diagnosis.final_diagnosis,
                func.count(Diagnosis.final_diagnosis).label('count')
            ).filter(
                and_(
                    Diagnosis.final_diagnosis.isnot(None),
                    Diagnosis.final_diagnosis != ""
                )
            ).group_by(Diagnosis.final_diagnosis).order_by(
                desc('count')
            ).limit(10).all()
            
            return {
                "total_diagnoses": total_diagnoses,
                "finalized_diagnoses": final_diagnoses,
                "pending_diagnoses": total_diagnoses - final_diagnoses,
                "most_common_diagnoses": [
                    {"diagnosis": diag, "count": count} 
                    for diag, count in common_diagnoses
                ]
            }
        except Exception as e:
            logger.error(f"Error getting diagnosis statistics: {str(e)}")
            raise
    
    def get_ai_performance_metrics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get AI diagnosis performance metrics
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with AI performance metrics
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            recent_diagnoses = self.db.query(Diagnosis).filter(
                Diagnosis.created_at >= cutoff_date
            ).all()
            
            if not recent_diagnoses:
                return {"message": "No recent diagnoses found"}
            
            # Calculate average confidence scores
            confidence_scores = []
            for diagnosis in recent_diagnoses:
                if diagnosis.confidence_scores:
                    # Extract confidence scores from JSON
                    scores = diagnosis.confidence_scores
                    if isinstance(scores, list) and scores:
                        confidence_scores.extend([score for score in scores if isinstance(score, (int, float))])
                    elif isinstance(scores, dict):
                        confidence_scores.extend([v for v in scores.values() if isinstance(v, (int, float))])
            
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
            
            return {
                "total_recent_diagnoses": len(recent_diagnoses),
                "average_confidence_score": round(avg_confidence, 3),
                "high_confidence_count": len([s for s in confidence_scores if s >= 0.8]),
                "low_confidence_count": len([s for s in confidence_scores if s < 0.5]),
                "analysis_period_days": days
            }
        except Exception as e:
            logger.error(f"Error getting AI performance metrics: {str(e)}")
            raise
