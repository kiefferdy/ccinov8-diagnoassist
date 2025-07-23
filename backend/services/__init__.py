"""
Services Module for DiagnoAssist Backend
Business Logic Layer with comprehensive service management

This module provides:
- Core domain services (Patient, Episode, Diagnosis, Treatment)
- Integration services (FHIR)
- Orchestration services (Clinical workflows)
- Service management and dependency injection
- Exception handling and validation
- Business rule enforcement

Usage:
    from services import ServiceManager, get_services
    
    # In FastAPI route
    @app.get("/patients/")
    async def get_patients(services: ServiceManager = Depends(get_services)):
        return services.patient.search_patients()
    
    # With context manager
    with ServiceContext(repository_manager) as services:
        patient = services.patient.create_patient(patient_data)
        episode = services.episode.create_episode(episode_data)
        # Auto-commit on success, rollback on exception
"""

from .base_service import BaseService

from .patient_service import PatientService
from .episode_service import EpisodeService
from .diagnosis_service import DiagnosisService
from .treatment_service import TreatmentService
from .fhir_service import FHIRService
from .clinical_service import ClinicalService

from .service_manager import (
    ServiceManager,
    ServiceContext,
    get_service_manager,
    get_services
)

# Version information
__version__ = "1.0.0"
__author__ = "DiagnoAssist Team"

# Export all service classes and utilities
__all__ = [
    # Base service
    "BaseService",
    
    # Core domain services
    "PatientService",
    "EpisodeService",
    "DiagnosisService",
    "TreatmentService",
    
    # Integration services
    "FHIRService",
    
    # Orchestration services
    "ClinicalService",
    
    # Service management
    "ServiceManager",
    "ServiceContext",
    "get_service_manager",
    "get_services",
    
    # Version info
    "__version__",
    "__author__"
]

# Convenience function to create all services at once
def create_services(repository_manager):
    """
    Convenience function to create service manager instance
    
    Args:
        repository_manager: Repository manager instance
        
    Returns:
        ServiceManager instance with all services initialized
    """
    return ServiceManager(repository_manager)

# Service registry for dynamic access
SERVICE_REGISTRY = {
    'patient': PatientService,
    'episode': EpisodeService,
    'diagnosis': DiagnosisService,
    'treatment': TreatmentService,
    'fhir': FHIRService,
    'clinical': ClinicalService
}

def get_service_class(service_name: str):
    """
    Get service class by name
    
    Args:
        service_name: Name of the service
        
    Returns:
        Service class or None if not found
    """
    return SERVICE_REGISTRY.get(service_name.lower())

# Import validation - ensure all dependencies are available
try:
    from repositories.repository_manager import RepositoryManager
    from schemas.patient import PatientCreate, PatientUpdate, PatientResponse
    from schemas.episode import EpisodeCreate, EpisodeUpdate, EpisodeResponse
    from schemas.diagnosis import DiagnosisCreate, DiagnosisUpdate, DiagnosisResponse
    from schemas.treatment import TreatmentCreate, TreatmentUpdate, TreatmentResponse
    from schemas.fhir_resource import FHIRResourceCreate, FHIRResourceResponse
except ImportError as e:
    import warnings
    warnings.warn(f"Service dependencies not fully available: {e}")

# Module-level logging configuration
import logging
logger = logging.getLogger(__name__)
logger.info("DiagnoAssist Services module loaded successfully")

# Service layer business rules documentation
BUSINESS_RULES = {
    "patient": [
        "Medical record numbers must be unique",
        "Email addresses must be unique if provided",
        "Date of birth cannot be in the future",
        "Age cannot exceed 150 years",
        "Medical record number cannot be changed after creation",
        "Cannot deactivate patient with active episodes"
    ],
    "episode": [
        "End time must be after start time",
        "Cannot create episode for inactive patient", 
        "Cannot modify completed episodes except notes",
        "Episode start time cannot be more than 24 hours in future",
        "Can only complete in-progress episodes",
        "Cannot cancel completed episodes"
    ],
    "diagnosis": [
        "Final diagnosis requires physician confirmation",
        "High probability diagnoses need supporting evidence",
        "Cannot modify final diagnoses except physician notes",
        "Only one final diagnosis per episode",
        "Diagnosis must belong to active episode"
    ],
    "treatment": [
        "Medication treatments require name, dosage, frequency",
        "High-risk medications require physician approval",
        "Cannot modify completed treatments except notes",
        "Drug interactions are checked before activation",
        "Can only approve planned treatments",
        "Can only activate approved treatments"
    ],
    "clinical": [
        "Clinical encounters require active patient",
        "Assessment requires at least one diagnosis or treatment",
        "Final diagnosis must be confirmed before encounter completion",
        "Care plans include all active treatments and conditions"
    ]
}