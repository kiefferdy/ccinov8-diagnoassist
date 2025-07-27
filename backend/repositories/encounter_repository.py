"""
Encounter Repository for DiagnoAssist
Database operations for encounter management
"""

from __future__ import annotations
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from uuid import UUID
from datetime import datetime, timedelta

if TYPE_CHECKING:
    from models.encounter import Encounter
    from schemas.encounter import EncounterCreate, EncounterUpdate

from repositories.base_repository import BaseRepository
from models.encounter import Encounter
from sqlalchemy.orm import joinedload
from sqlalchemy import and_, desc, asc
import logging

logger = logging.getLogger(__name__)

class EncounterRepository(BaseRepository[Encounter]):
    """
    Repository for encounter-related database operations
    """
    
    def __init__(self, db):
        super().__init__(Encounter, db)
    
    def get_by_episode(self, episode_id: str, skip: int = 0, limit: int = 100) -> List[Encounter]:
        """
        Get encounters for a specific episode
        
        Args:
            episode_id: Episode UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of encounters ordered by date descending
        """
        try:
            self.validate_uuid(episode_id)
            return (self.db.query(self.model)
                    .filter(self.model.episode_id == episode_id)
                    .options(joinedload(self.model.episode), joinedload(self.model.patient))
                    .order_by(desc(self.model.date))
                    .offset(skip)
                    .limit(limit)
                    .all())
        except Exception as e:
            logger.error(f"Error getting encounters by episode {episode_id}: {e}")
            raise
    
    def get_by_patient(self, patient_id: str, skip: int = 0, limit: int = 100) -> List[Encounter]:
        """
        Get encounters for a specific patient
        
        Args:
            patient_id: Patient UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of encounters ordered by date descending
        """
        try:
            self.validate_uuid(patient_id)
            return (self.db.query(self.model)
                    .filter(self.model.patient_id == patient_id)
                    .options(joinedload(self.model.episode), joinedload(self.model.patient))
                    .order_by(desc(self.model.date))
                    .offset(skip)
                    .limit(limit)
                    .all())
        except Exception as e:
            logger.error(f"Error getting encounters by patient {patient_id}: {e}")
            raise
    
    def get_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[Encounter]:
        """
        Get encounters by status
        
        Args:
            status: Encounter status (draft, signed)
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of encounters
        """
        try:
            return (self.db.query(self.model)
                    .filter(self.model.status == status)
                    .options(joinedload(self.model.episode), joinedload(self.model.patient))
                    .order_by(desc(self.model.date))
                    .offset(skip)
                    .limit(limit)
                    .all())
        except Exception as e:
            logger.error(f"Error getting encounters by status {status}: {e}")
            raise
    
    def get_by_type(self, encounter_type: str, skip: int = 0, limit: int = 100) -> List[Encounter]:
        """
        Get encounters by type
        
        Args:
            encounter_type: Type of encounter
            skip: Number of records to skip  
            limit: Maximum number of records to return
            
        Returns:
            List of encounters
        """
        try:
            return (self.db.query(self.model)
                    .filter(self.model.type == encounter_type)
                    .options(joinedload(self.model.episode), joinedload(self.model.patient))
                    .order_by(desc(self.model.date))
                    .offset(skip)
                    .limit(limit)
                    .all())
        except Exception as e:
            logger.error(f"Error getting encounters by type {encounter_type}: {e}")
            raise
    
    def get_signed_encounters(self, skip: int = 0, limit: int = 100) -> List[Encounter]:
        """
        Get all signed encounters
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of signed encounters
        """
        return self.get_by_status("signed", skip, limit)
    
    def get_draft_encounters(self, skip: int = 0, limit: int = 100) -> List[Encounter]:
        """
        Get all draft encounters
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of draft encounters
        """
        return self.get_by_status("draft", skip, limit)
    
    def count_by_episode(self, episode_id: str) -> int:
        """
        Count encounters for an episode
        
        Args:
            episode_id: Episode UUID
            
        Returns:
            Number of encounters
        """
        try:
            self.validate_uuid(episode_id)
            return self.db.query(self.model).filter(self.model.episode_id == episode_id).count()
        except Exception as e:
            logger.error(f"Error counting encounters by episode {episode_id}: {e}")
            raise
    
    def count_by_patient(self, patient_id: str) -> int:
        """
        Count encounters for a patient
        
        Args:
            patient_id: Patient UUID
            
        Returns:
            Number of encounters
        """
        try:
            self.validate_uuid(patient_id)
            return self.db.query(self.model).filter(self.model.patient_id == patient_id).count()
        except Exception as e:
            logger.error(f"Error counting encounters by patient {patient_id}: {e}")
            raise
    
    def count_by_status(self, status: str) -> int:
        """
        Count encounters by status
        
        Args:
            status: Encounter status
            
        Returns:
            Number of encounters
        """
        try:
            return self.db.query(self.model).filter(self.model.status == status).count()
        except Exception as e:
            logger.error(f"Error counting encounters by status {status}: {e}")
            raise
    
    def get_episode_stats(self, episode_id: str) -> Dict[str, Any]:
        """
        Get encounter statistics for an episode
        
        Args:
            episode_id: Episode UUID
            
        Returns:
            Dictionary with encounter statistics
        """
        try:
            self.validate_uuid(episode_id)
            encounters = self.get_by_episode(episode_id)
            
            total = len(encounters)
            draft = len([e for e in encounters if e.status == "draft"])
            signed = len([e for e in encounters if e.status == "signed"])
            last_visit = encounters[0].date if encounters else None
            
            return {
                "total": total,
                "draft": draft, 
                "signed": signed,
                "lastVisit": last_visit
            }
        except Exception as e:
            logger.error(f"Error getting episode stats for {episode_id}: {e}")
            raise
    
    def get_recent_encounters(self, days: int = 30, skip: int = 0, limit: int = 100) -> List[Encounter]:
        """
        Get recent encounters within specified days
        
        Args:
            days: Number of days to look back
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of recent encounters
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            return (self.db.query(self.model)
                    .filter(self.model.date >= cutoff_date)
                    .options(joinedload(self.model.episode), joinedload(self.model.patient))
                    .order_by(desc(self.model.date))
                    .offset(skip)
                    .limit(limit)
                    .all())
        except Exception as e:
            logger.error(f"Error getting recent encounters: {e}")
            raise
    
    def update_soap_section(self, encounter_id: str, section: str, data: Dict[str, Any]) -> Encounter:
        """
        Update a specific SOAP section
        
        Args:
            encounter_id: Encounter UUID
            section: SOAP section name (subjective, objective, assessment, plan)
            data: Section data to update
            
        Returns:
            Updated encounter
        """
        try:
            self.validate_uuid(encounter_id)
            encounter = self.get_by_id(encounter_id)
            if not encounter:
                raise ValueError(f"Encounter {encounter_id} not found")
            
            # Validate section name
            valid_sections = ['subjective', 'objective', 'assessment', 'plan']
            if section not in valid_sections:
                raise ValueError(f"Invalid SOAP section: {section}")
            
            # Update the specific section
            field_name = f"soap_{section}"
            current_data = getattr(encounter, field_name) or {}
            
            # Merge the new data with existing data
            if isinstance(current_data, dict) and isinstance(data, dict):
                current_data.update(data)
                current_data['lastUpdated'] = datetime.utcnow().isoformat()
            else:
                current_data = data
                current_data['lastUpdated'] = datetime.utcnow().isoformat()
            
            # Update the encounter
            setattr(encounter, field_name, current_data)
            self.db.commit()
            self.db.refresh(encounter)
            
            return encounter
            
        except Exception as e:
            logger.error(f"Error updating SOAP section {section} for encounter {encounter_id}: {e}")
            self.db.rollback()
            raise
    
    def sign_encounter(self, encounter_id: str, provider_name: str) -> Encounter:
        """
        Sign an encounter
        
        Args:
            encounter_id: Encounter UUID
            provider_name: Name of provider signing
            
        Returns:
            Signed encounter
        """
        try:
            self.validate_uuid(encounter_id)
            encounter = self.get_by_id(encounter_id)
            if not encounter:
                raise ValueError(f"Encounter {encounter_id} not found")
            
            if encounter.status == "signed":
                raise ValueError("Encounter is already signed")
            
            # Update signing fields
            update_data = {
                "status": "signed",
                "signed_at": datetime.utcnow(),
                "signed_by": provider_name
            }
            
            return self.update(encounter_id, update_data)
            
        except Exception as e:
            logger.error(f"Error signing encounter {encounter_id}: {e}")
            raise
    
    def get_with_filters(self, episode_id: Optional[str] = None, patient_id: Optional[str] = None,
                        status: Optional[str] = None, encounter_type: Optional[str] = None,
                        skip: int = 0, limit: int = 100) -> List[Encounter]:
        """
        Get encounters with multiple filters
        
        Args:
            episode_id: Filter by episode
            patient_id: Filter by patient  
            status: Filter by status
            encounter_type: Filter by type
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of filtered encounters
        """
        try:
            query = self.db.query(self.model)
            
            # Apply filters
            if episode_id:
                self.validate_uuid(episode_id)
                query = query.filter(self.model.episode_id == episode_id)
            
            if patient_id:
                self.validate_uuid(patient_id)
                query = query.filter(self.model.patient_id == patient_id)
            
            if status:
                query = query.filter(self.model.status == status)
            
            if encounter_type:
                query = query.filter(self.model.type == encounter_type)
            
            # Add joins and ordering
            query = (query.options(joinedload(self.model.episode), joinedload(self.model.patient))
                    .order_by(desc(self.model.date))
                    .offset(skip)
                    .limit(limit))
            
            return query.all()
            
        except Exception as e:
            logger.error(f"Error getting encounters with filters: {e}")
            raise