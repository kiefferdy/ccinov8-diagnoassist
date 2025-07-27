"""
Repository Manager for DiagnoAssist
Centralized access to all repositories with dependency management
"""

from sqlalchemy.orm import Session
from typing import Optional
import logging

from repositories.base_repository import BaseRepository
from repositories.patient_repository import PatientRepository
from repositories.episode_repository import EpisodeRepository
from repositories.encounter_repository import EncounterRepository
from repositories.diagnosis_repository import DiagnosisRepository
from repositories.treatment_repository import TreatmentRepository
from repositories.fhir_repository import FHIRResourceRepository

logger = logging.getLogger(__name__)

class RepositoryManager:
    """
    Centralized manager for all repositories
    Provides singleton access and dependency injection
    """
    
    def __init__(self, db: Session):
        """
        Initialize repository manager with database session
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self._repositories = {}
    
    @property
    def patient(self) -> PatientRepository:
        """Get Patient repository instance"""
        if 'patient' not in self._repositories:
            self._repositories['patient'] = PatientRepository(self.db)
        return self._repositories['patient']
    
    @property
    def episode(self) -> EpisodeRepository:
        """Get Episode repository instance"""
        if 'episode' not in self._repositories:
            self._repositories['episode'] = EpisodeRepository(self.db)
        return self._repositories['episode']
    
    @property
    def encounter(self) -> EncounterRepository:
        """Get Encounter repository instance"""
        if 'encounter' not in self._repositories:
            self._repositories['encounter'] = EncounterRepository(self.db)
        return self._repositories['encounter']
    
    @property
    def diagnosis(self) -> DiagnosisRepository:
        """Get Diagnosis repository instance"""
        if 'diagnosis' not in self._repositories:
            self._repositories['diagnosis'] = DiagnosisRepository(self.db)
        return self._repositories['diagnosis']
    
    @property
    def treatment(self) -> TreatmentRepository:
        """Get Treatment repository instance"""
        if 'treatment' not in self._repositories:
            self._repositories['treatment'] = TreatmentRepository(self.db)
        return self._repositories['treatment']
    
    @property
    def fhir_resource(self) -> FHIRResourceRepository:
        """Get FHIR Resource repository instance"""
        if 'fhir_resource' not in self._repositories:
            self._repositories['fhir_resource'] = FHIRResourceRepository(self.db)
        return self._repositories['fhir_resource']
    
    def get_repository(self, model_name: str) -> Optional[BaseRepository]:
        """
        Get repository by model name
        
        Args:
            model_name: Name of the model/repository
            
        Returns:
            Repository instance or None if not found
        """
        repository_map = {
            'patient': self.patient,
            'episode': self.episode,
            'encounter': self.encounter,
            'diagnosis': self.diagnosis,
            'treatment': self.treatment,
            'fhir_resource': self.fhir_resource
        }
        
        return repository_map.get(model_name.lower())
    
    def close(self):
        """
        Close database session and cleanup resources
        """
        try:
            if self.db:
                self.db.close()
            self._repositories.clear()
            logger.info("Repository manager closed successfully")
        except Exception as e:
            logger.error(f"Error closing repository manager: {str(e)}")
    
    def rollback(self):
        """
        Rollback current transaction across all repositories
        """
        try:
            self.db.rollback()
            logger.info("Transaction rolled back")
        except Exception as e:
            logger.error(f"Error rolling back transaction: {str(e)}")
    
    def commit(self):
        """
        Commit current transaction across all repositories
        """
        try:
            self.db.commit()
            logger.info("Transaction committed")
        except Exception as e:
            logger.error(f"Error committing transaction: {str(e)}")
            self.rollback()
            raise
    
    def refresh_all(self):
        """
        Refresh all repository instances (clear cache)
        """
        self._repositories.clear()
        logger.info("All repositories refreshed")


def get_repository_manager(db: Session) -> RepositoryManager:
    """
    Factory function to create repository manager
    
    Args:
        db: Database session
        
    Returns:
        Repository manager instance
    """
    return RepositoryManager(db)


# Context manager for repository operations
class RepositoryContext:
    """
    Context manager for repository operations with automatic cleanup
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.repo_manager = None
    
    def __enter__(self) -> RepositoryManager:
        self.repo_manager = RepositoryManager(self.db)
        return self.repo_manager
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.repo_manager:
            if exc_type is not None:
                # Exception occurred, rollback
                self.repo_manager.rollback()
            else:
                # Success, commit
                try:
                    self.repo_manager.commit()
                except Exception:
                    self.repo_manager.rollback()
                    raise
            
            self.repo_manager.close()


# Repository dependency for FastAPI
async def get_repositories(db: Session) -> RepositoryManager:
    """
    FastAPI dependency for repository manager
    
    Args:
        db: Database session from FastAPI dependency
        
    Returns:
        Repository manager instance
    """
    return RepositoryManager(db)