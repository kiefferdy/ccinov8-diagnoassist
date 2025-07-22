"""
Treatment Repository for DiagnoAssist
Specialized CRUD operations for Treatment model
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_, desc
from datetime import datetime, date, timedelta
from uuid import UUID
import logging

from models.treatment import Treatment
from repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)

class TreatmentRepository(BaseRepository[Treatment]):
    """
    Repository for Treatment model with specialized operations
    """
    
    def __init__(self, db: Session):
        super().__init__(Treatment, db)
    
    def get_by_episode_id(self, episode_id: UUID, skip: int = 0, limit: int = 100) -> List[Treatment]:
        """
        Get all treatments for a specific episode
        
        Args:
            episode_id: Episode ID
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of treatments for the episode
        """
        try:
            return self.db.query(Treatment).filter(
                Treatment.episode_id == episode_id
            ).order_by(desc(Treatment.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting treatments for episode {episode_id}: {str(e)}")
            return []
    
    def get_by_diagnosis_id(self, diagnosis_id: UUID) -> List[Treatment]:
        """
        Get treatments for a specific diagnosis
        
        Args:
            diagnosis_id: Diagnosis ID
            
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
            treatment_type: Treatment type (medication, procedure, therapy, etc.)
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of treatments with matching type
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
            status: Treatment status (planned, approved, active, completed, discontinued)
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of treatments with matching status
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
        Get active treatments (status = 'active')
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of active treatments
        """
        try:
            return self.db.query(Treatment).filter(
                Treatment.status == "active"
            ).order_by(desc(Treatment.start_date)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting active treatments: {str(e)}")
            return []
    
    def get_medications(self, skip: int = 0, limit: int = 100) -> List[Treatment]:
        """
        Get medication treatments
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of medication treatments
        """
        try:
            return self.db.query(Treatment).filter(
                Treatment.treatment_type == "medication"
            ).order_by(desc(Treatment.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting medication treatments: {str(e)}")
            return []
    
    def search_by_medication_name(self, medication_name: str, limit: int = 50) -> List[Treatment]:
        """
        Search treatments by medication name
        
        Args:
            medication_name: Medication name to search for
            limit: Maximum number of results
            
        Returns:
            List of treatments with matching medication name
        """
        try:
            search_pattern = f'%{medication_name}%'
            return self.db.query(Treatment).filter(
                Treatment.medication_name.ilike(search_pattern)
            ).order_by(desc(Treatment.created_at)).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error searching treatments by medication '{medication_name}': {str(e)}")
            return []
    
    def search_by_treatment_name(self, treatment_name: str, limit: int = 50) -> List[Treatment]:
        """
        Search treatments by treatment name
        
        Args:
            treatment_name: Treatment name to search for
            limit: Maximum number of results
            
        Returns:
            List of treatments with matching treatment name
        """
        try:
            search_pattern = f'%{treatment_name}%'
            return self.db.query(Treatment).filter(
                Treatment.treatment_name.ilike(search_pattern)
            ).order_by(desc(Treatment.created_at)).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error searching treatments by name '{treatment_name}': {str(e)}")
            return []
    
    def get_by_approved_by(self, approved_by: str, skip: int = 0, limit: int = 100) -> List[Treatment]:
        """
        Get treatments approved by specific healthcare provider
        
        Args:
            approved_by: Healthcare provider identifier
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of treatments approved by the provider
        """
        try:
            return self.db.query(Treatment).filter(
                Treatment.approved_by == approved_by
            ).order_by(desc(Treatment.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting treatments approved by {approved_by}: {str(e)}")
            return []
    
    def get_by_date_range(self, start_date: date, end_date: date, 
                         date_field: str = "start_date") -> List[Treatment]:
        """
        Get treatments within date range
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            date_field: Field to filter on ("start_date" or "end_date")
            
        Returns:
            List of treatments within date range
        """
        try:
            field = getattr(Treatment, date_field)
            return self.db.query(Treatment).filter(
                and_(
                    field >= start_date,
                    field <= end_date
                )
            ).order_by(desc(Treatment.created_at)).all()
            
        except Exception as e:
            logger.error(f"Error getting treatments by {date_field} range {start_date} to {end_date}: {str(e)}")
            return []
    
    def get_by_route(self, route: str, skip: int = 0, limit: int = 100) -> List[Treatment]:
        """
        Get treatments by route of administration
        
        Args:
            route: Route of administration (oral, IV, IM, etc.)
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of treatments with matching route
        """
        try:
            return self.db.query(Treatment).filter(
                Treatment.route == route
            ).order_by(desc(Treatment.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting treatments by route {route}: {str(e)}")
            return []
    
    def approve_treatment(self, treatment_id: UUID, approved_by: str) -> Optional[Treatment]:
        """
        Approve a treatment plan
        
        Args:
            treatment_id: Treatment ID
            approved_by: Healthcare provider who approved the treatment
            
        Returns:
            Updated treatment or None if failed
        """
        try:
            return self.update(treatment_id, {
                "status": "approved",
                "approved_by": approved_by,
                "updated_at": datetime.utcnow()
            })
            
        except Exception as e:
            logger.error(f"Error approving treatment {treatment_id}: {str(e)}")
            return None
    
    def start_treatment(self, treatment_id: UUID, start_date: Optional[datetime] = None) -> Optional[Treatment]:
        """
        Start a treatment (change status to active)
        
        Args:
            treatment_id: Treatment ID
            start_date: Start date (defaults to current time)
            
        Returns:
            Updated treatment or None if failed
        """
        try:
            if start_date is None:
                start_date = datetime.utcnow()
            
            return self.update(treatment_id, {
                "status": "active",
                "start_date": start_date,
                "updated_at": datetime.utcnow()
            })
            
        except Exception as e:
            logger.error(f"Error starting treatment {treatment_id}: {str(e)}")
            return None
    
    def complete_treatment(self, treatment_id: UUID, end_date: Optional[datetime] = None) -> Optional[Treatment]:
        """
        Complete a treatment
        
        Args:
            treatment_id: Treatment ID
            end_date: End date (defaults to current time)
            
        Returns:
            Updated treatment or None if failed
        """
        try:
            if end_date is None:
                end_date = datetime.utcnow()
            
            return self.update(treatment_id, {
                "status": "completed",
                "end_date": end_date,
                "updated_at": datetime.utcnow()
            })
            
        except Exception as e:
            logger.error(f"Error completing treatment {treatment_id}: {str(e)}")
            return None
    
    def discontinue_treatment(self, treatment_id: UUID, end_date: Optional[datetime] = None) -> Optional[Treatment]:
        """
        Discontinue a treatment
        
        Args:
            treatment_id: Treatment ID
            end_date: End date (defaults to current time)
            
        Returns:
            Updated treatment or None if failed
        """
        try:
            if end_date is None:
                end_date = datetime.utcnow()
            
            return self.update(treatment_id, {
                "status": "discontinued",
                "end_date": end_date,
                "updated_at": datetime.utcnow()
            })
            
        except Exception as e:
            logger.error(f"Error discontinuing treatment {treatment_id}: {str(e)}")
            return None
    
    def get_treatment_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive treatment statistics
        
        Returns:
            Dictionary with treatment statistics
        """
        try:
            total_treatments = self.count()
            
            status_stats = self.db.query(
                Treatment.status,
                func.count(Treatment.id).label('count')
            ).group_by(Treatment.status).all()
            
            type_stats = self.db.query(
                Treatment.treatment_type,
                func.count(Treatment.id).label('count')
            ).group_by(Treatment.treatment_type).all()
            
            route_stats = self.db.query(
                Treatment.route,
                func.count(Treatment.id).label('count')
            ).filter(Treatment.route.isnot(None)).group_by(Treatment.route).all()
            
            creator_stats = self.db.query(
                Treatment.created_by,
                func.count(Treatment.id).label('count')
            ).group_by(Treatment.created_by).all()
            
            return {
                "total_treatments": total_treatments,
                "status_distribution": {stat.status: stat.count for stat in status_stats},
                "type_distribution": {stat.treatment_type: stat.count for stat in type_stats},
                "route_distribution": {stat.route: stat.count for stat in route_stats},
                "creator_distribution": {stat.created_by: stat.count for stat in creator_stats},
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting treatment statistics: {str(e)}")
            return {}
    
    def get_most_common_medications(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get most commonly prescribed medications
        
        Args:
            limit: Maximum number of medications to return
            
        Returns:
            List of medications with counts
        """
        try:
            medications = self.db.query(
                Treatment.medication_name,
                func.count(Treatment.id).label('count')
            ).filter(
                Treatment.medication_name.isnot(None)
            ).group_by(Treatment.medication_name).order_by(
                desc(func.count(Treatment.id))
            ).limit(limit).all()
            
            return [
                {"medication": med.medication_name, "count": med.count}
                for med in medications
            ]
            
        except Exception as e:
            logger.error(f"Error getting most common medications: {str(e)}")
            return []
    
    def get_most_common_treatments(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get most common treatment names
        
        Args:
            limit: Maximum number of treatments to return
            
        Returns:
            List of treatments with counts
        """
        try:
            treatments = self.db.query(
                Treatment.treatment_name,
                func.count(Treatment.id).label('count')
            ).group_by(Treatment.treatment_name).order_by(
                desc(func.count(Treatment.id))
            ).limit(limit).all()
            
            return [
                {"treatment": treatment.treatment_name, "count": treatment.count}
                for treatment in treatments
            ]
            
        except Exception as e:
            logger.error(f"Error getting most common treatments: {str(e)}")
            return []
    def get_by_episode(self, episode_id: str, skip: int = 0, limit: int = 100) -> List[Treatment]:
        """Get all treatments for a specific episode"""
        try:
            from uuid import UUID  
            episode_uuid = UUID(episode_id) if isinstance(episode_id, str) else episode_id
            return self.db.query(Treatment).filter(
                Treatment.episode_id == episode_uuid
            ).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting treatments for episode {episode_id}: {str(e)}")
            return []