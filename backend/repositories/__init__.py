"""
Repositories Module for DiagnoAssist Backend
Data Access Layer with CRUD operations for all models

This module provides:
- Base repository class with common CRUD operations
- Specialized repositories for each model (Patient, Episode, Diagnosis, Treatment, FHIRResource)
- Repository manager for centralized access
- Context managers for transaction handling
- FastAPI dependencies for dependency injection

Usage:
    from repositories import RepositoryManager, get_repositories
    
    # In FastAPI route
    @app.get("/patients/")
    async def get_patients(repos: RepositoryManager = Depends(get_repositories)):
        return repos.patient.get_all()
    
    # With context manager
    with RepositoryContext(db_session) as repos:
        patient = repos.patient.create(patient_data)
        episode = repos.episode.create(episode_data)
        # Auto-commit on success, rollback on exception
"""

from .base_repository import BaseRepository
from .patient_repository import PatientRepository
from .episode_repository import EpisodeRepository
from .diagnosis_repository import DiagnosisRepository
from .treatment_repository import TreatmentRepository
from .fhir_repository import FHIRResourceRepository
from .repository_manager import (
    RepositoryManager,
    get_repository_manager,
    RepositoryContext,
    get_repositories
)

# Version information
__version__ = "1.0.0"
__author__ = "DiagnoAssist Team"

# Export all repository classes and utilities
__all__ = [
    # Base repository
    "BaseRepository",
    
    # Specialized repositories
    "PatientRepository",
    "EpisodeRepository", 
    "DiagnosisRepository",
    "TreatmentRepository",
    "FHIRResourceRepository",
    
    # Repository management
    "RepositoryManager",
    "get_repository_manager",
    "RepositoryContext",
    "get_repositories",
    
    # Version info
    "__version__",
    "__author__"
]

# Convenience function to create all repositories at once
def create_repositories(db_session):
    """
    Convenience function to create all repository instances
    
    Args:
        db_session: SQLAlchemy database session
        
    Returns:
        Dictionary of repository instances
    """
    return {
        'patient': PatientRepository(db_session),
        'episode': EpisodeRepository(db_session),
        'diagnosis': DiagnosisRepository(db_session),
        'treatment': TreatmentRepository(db_session),
        'fhir_resource': FHIRResourceRepository(db_session)
    }

# Repository registry for dynamic access
REPOSITORY_REGISTRY = {
    'patient': PatientRepository,
    'episode': EpisodeRepository,
    'diagnosis': DiagnosisRepository,
    'treatment': TreatmentRepository,
    'fhir_resource': FHIRResourceRepository
}

def get_repository_class(model_name: str):
    """
    Get repository class by model name
    
    Args:
        model_name: Name of the model
        
    Returns:
        Repository class or None if not found
    """
    return REPOSITORY_REGISTRY.get(model_name.lower())

# Import validation - ensure all dependencies are available
try:
    from sqlalchemy.orm import Session
    from sqlalchemy.exc import SQLAlchemyError
    from models.patient import Patient
    from models.episode import Episode
    from models.diagnosis import Diagnosis
    from models.treatment import Treatment
    from models.fhir_resource import FHIRResource
except ImportError as e:
    import warnings
    warnings.warn(f"Repository dependencies not fully available: {e}")

# Module-level logging configuration
import logging
logger = logging.getLogger(__name__)
logger.info("DiagnoAssist Repositories module loaded successfully")