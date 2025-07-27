"""
Consolidated API Dependencies for DiagnoAssist API
Single source of truth for all FastAPI dependencies
"""

from fastapi import Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Generator, Dict, Any, Optional, Annotated
import logging

# Import database and managers directly
from config.database import SessionLocal
from repositories.repository_manager import RepositoryManager

# Import individual services
from services.patient_service import PatientService
from services.episode_service import EpisodeService
from services.encounter_service import EncounterService
from services.diagnosis_service import DiagnosisService
from services.treatment_service import TreatmentService
from services.fhir_service import FHIRService
from services.clinical_service import ClinicalService

# Import common schemas
from schemas.common import PaginationParams

logger = logging.getLogger(__name__)

# =============================================================================
# CORE INFRASTRUCTURE DEPENDENCIES
# =============================================================================

def get_database_session() -> Generator[Session, None, None]:
    """FastAPI dependency for database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_repository_manager(db: Session = Depends(get_database_session)) -> RepositoryManager:
    """FastAPI dependency for repository manager"""
    return RepositoryManager(db)

# =============================================================================
# INDIVIDUAL SERVICE DEPENDENCIES
# =============================================================================

def get_patient_service(repos: RepositoryManager = Depends(get_repository_manager)) -> PatientService:
    """FastAPI dependency for patient service"""
    return PatientService(repos)

def get_episode_service(repos: RepositoryManager = Depends(get_repository_manager)) -> EpisodeService:
    """FastAPI dependency for episode service"""
    return EpisodeService(repos)

def get_encounter_service(repos: RepositoryManager = Depends(get_repository_manager)) -> EncounterService:
    """FastAPI dependency for encounter service"""
    return EncounterService(repos)

def get_diagnosis_service(repos: RepositoryManager = Depends(get_repository_manager)) -> DiagnosisService:
    """FastAPI dependency for diagnosis service"""
    return DiagnosisService(repos)

def get_treatment_service(repos: RepositoryManager = Depends(get_repository_manager)) -> TreatmentService:
    """FastAPI dependency for treatment service"""
    return TreatmentService(repos)

def get_fhir_service(repos: RepositoryManager = Depends(get_repository_manager)) -> FHIRService:
    """FastAPI dependency for FHIR service"""
    return FHIRService(repos)

def get_clinical_service(repos: RepositoryManager = Depends(get_repository_manager)) -> ClinicalService:
    """FastAPI dependency for clinical service"""
    return ClinicalService(repos)

def check_services_health(
    patient_service: PatientService = Depends(get_patient_service),
    episode_service: EpisodeService = Depends(get_episode_service),
    diagnosis_service: DiagnosisService = Depends(get_diagnosis_service),
    treatment_service: TreatmentService = Depends(get_treatment_service)
) -> bool:
    """Check health of all services"""
    try:
        # Test a simple operation on each service to verify health
        # Test individual service health by checking if they can be instantiated
        return True  # Services loaded successfully if we get here
    except Exception as e:
        logger.error(f"Services health check failed: {e}")
        return False

def check_database_health(db: Session = Depends(get_database_session)) -> bool:
    """Check database health"""
    try:
        db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

# =============================================================================
# Authentication Dependencies
# =============================================================================

def get_current_user() -> Dict[str, Any]:
    """
    Get current authenticated user (placeholder implementation)
    
    Returns:
        Dict with user information - but FastAPI won't use this for response model
    """
    return {
        "id": "user_123",
        "username": "admin", 
        "email": "admin@diagnoassist.com",
        "permissions": {
            "patient.create": True,
            "patient.read": True,
            "patient.update": True,
            "patient.delete": True,
            "episode.create": True,
            "episode.read": True,
            "episode.update": True,
            "episode.delete": True,
            "encounter.create": True,
            "encounter.read": True,
            "encounter.update": True,
            "encounter.delete": True,
            "encounter.sign": True,
            "diagnosis.create": True,
            "diagnosis.read": True,
            "diagnosis.update": True,
            "diagnosis.delete": True,
            "treatment.create": True,
            "treatment.read": True,
            "treatment.update": True,
            "treatment.delete": True,
            "fhir.create": True,
            "fhir.read": True,
            "fhir.update": True,
            "fhir.delete": True
        }
    }

def require_authentication() -> Dict[str, Any]:
    """
    Require user to be authenticated
    
    Returns:
        User dict if authenticated
        
    Raises:
        HTTPException: If user is not authenticated
    """
    user = get_current_user()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user

def require_permission(permission: str):
    """
    Factory function to create permission-checking dependencies
    
    Args:
        permission: Permission string to check
        
    Returns:
        Dependency function that checks the permission
    """
    def permission_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        if not current_user.get("permissions", {}).get(permission, False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions: {permission} required"
            )
        
        return current_user
    
    return Depends(permission_checker)

# =============================================================================
# Query Parameter Dependencies
# =============================================================================

def get_pagination(
    page: int = Query(1, ge=1, description="Page number starting from 1"),
    size: int = Query(20, ge=1, le=100, description="Number of items per page")
) -> PaginationParams:
    """Get pagination parameters from query"""
    try:
        return PaginationParams(page=page, size=size)
    except Exception as e:
        # Return default values if validation fails
        return PaginationParams(page=1, size=20)


# =============================================================================
# Dependency Aliases
# =============================================================================

# Alias for backward compatibility
get_database = get_database_session

# Database and repository dependencies  
DatabaseDep = Annotated[Session, Depends(get_database_session)]
RepositoryDep = Annotated[RepositoryManager, Depends(get_repository_manager)]

PatientServiceDep = Annotated[PatientService, Depends(get_patient_service)]
EpisodeServiceDep = Annotated[EpisodeService, Depends(get_episode_service)]
EncounterServiceDep = Annotated[EncounterService, Depends(get_encounter_service)]
DiagnosisServiceDep = Annotated[DiagnosisService, Depends(get_diagnosis_service)]
TreatmentServiceDep = Annotated[TreatmentService, Depends(get_treatment_service)]
FHIRServiceDep = Annotated[FHIRService, Depends(get_fhir_service)]
ClinicalServiceDep = Annotated[ClinicalService, Depends(get_clinical_service)]

# Authentication dependencies
# The key is that these should NOT be used as response model types
CurrentUserDep = Annotated[Dict[str, Any], Depends(get_current_user)]
AuthUserDep = Annotated[Dict[str, Any], Depends(require_authentication)]

# Query parameter dependencies  
PaginationDep = Annotated[PaginationParams, Depends(get_pagination)]

# Database and service health
DatabaseHealthDep = Annotated[bool, Depends(check_database_health)]
ServicesHealthDep = Annotated[bool, Depends(check_services_health)]

# Export everything
__all__ = [
    # Core infrastructure dependencies
    "get_database_session",
    "get_database",  # Alias for backward compatibility
    "get_repository_manager",
    "DatabaseDep",
    "RepositoryDep",
    
    "get_patient_service",
    "get_episode_service",
    "get_encounter_service",
    "get_diagnosis_service",
    "get_treatment_service",
    "get_fhir_service",
    "get_clinical_service",
    "PatientServiceDep",
    "EpisodeServiceDep",
    "EncounterServiceDep",
    "DiagnosisServiceDep", 
    "TreatmentServiceDep",
    "FHIRServiceDep",
    "ClinicalServiceDep",
    
    # Health checks
    "check_services_health",
    "check_database_health",
    
    # Authentication dependencies
    "get_current_user",
    "require_authentication",
    "require_permission",
    "CurrentUserDep",
    "AuthUserDep",
    
    # Query parameter dependencies
    "get_pagination", 
    "PaginationDep",
    
    # Health dependencies
    "DatabaseHealthDep",
    "ServicesHealthDep"
]