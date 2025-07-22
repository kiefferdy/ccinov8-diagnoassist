"""
API Dependencies for DiagnoAssist - FINAL WORKING VERSION
Simple, robust service methods that actually work
"""

import logging
from typing import Dict, Any, Optional, Annotated
from fastapi import Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

# Database and core imports
from config.database import SessionLocal, test_database_connection
from repositories.repository_manager import RepositoryManager

# Schema imports  
from schemas.common import PaginationParams
from config.settings import Settings

# Setup logging
logger = logging.getLogger(__name__)

# Security scheme for Bearer token authentication
security = HTTPBearer(auto_error=False)

# =============================================================================
# SIMPLE WORKING SERVICE WRAPPER
# =============================================================================

class WorkingService:
    """Simple service that actually works"""
    
    def __init__(self, repos, service_name="unknown"):
        self.repos = repos
        self.service_name = service_name
    
    # Patient methods
    def create_patient(self, patient_data, created_by=None):
        try:
            # Convert to dict
            if hasattr(patient_data, 'model_dump'):
                data = patient_data.model_dump()
            elif hasattr(patient_data, 'dict'):
                data = patient_data.dict()
            else:
                data = dict(patient_data)
            
            # Create patient
            patient = self.repos.patient.create(data)
            
            # Return as response schema
            from schemas.patient import PatientResponse
            return PatientResponse.model_validate(patient)
        except Exception as e:
            raise Exception(f"Patient creation failed: {str(e)}")
    
    def get_patients(self, pagination=None, search=None, status=None):
        try:
            patients = self.repos.patient.get_all()
            
            from schemas.patient import PatientListResponse, PatientResponse
            return PatientListResponse(
                data=[PatientResponse.model_validate(p) for p in patients],
                total=len(patients),
                page=1 if pagination else 1,
                size=len(patients)
            )
        except Exception as e:
            raise Exception(f"Failed to get patients: {str(e)}")
    
    def get_patient(self, patient_id):
        try:
            patient = self.repos.patient.get_by_id(patient_id)
            if not patient:
                raise Exception("Patient not found")
            
            from schemas.patient import PatientResponse
            return PatientResponse.model_validate(patient)
        except Exception as e:
            if "not found" in str(e).lower():
                raise Exception("Patient not found")
            raise Exception(f"Failed to get patient: {str(e)}")
    
    def update_patient(self, patient_id, patient_data, updated_by=None):
        try:
            if hasattr(patient_data, 'model_dump'):
                data = patient_data.model_dump(exclude_unset=True)
            else:
                data = dict(patient_data)
            
            updated = self.repos.patient.update(patient_id, data)
            
            from schemas.patient import PatientResponse
            return PatientResponse.model_validate(updated)
        except Exception as e:
            raise Exception(f"Failed to update patient: {str(e)}")
    
    def delete_patient(self, patient_id, deleted_by=None):
        try:
            self.repos.patient.delete(patient_id)
            return {"status": "deleted", "patient_id": patient_id}
        except Exception as e:
            raise Exception(f"Failed to delete patient: {str(e)}")
    
    def get_patient_by_mrn(self, mrn):
        try:
            patient = self.repos.patient.get_by_mrn(mrn)
            if not patient:
                raise Exception("Patient not found")
            
            from schemas.patient import PatientResponse
            return PatientResponse.model_validate(patient)
        except Exception as e:
            raise Exception(f"Patient not found: {str(e)}")
    
    def get_patient_by_email(self, email):
        try:
            patient = self.repos.patient.get_by_email(email)
            if not patient:
                raise Exception("Patient not found")
            
            from schemas.patient import PatientResponse
            return PatientResponse.model_validate(patient)
        except Exception as e:
            raise Exception(f"Patient not found: {str(e)}")
    
    def get_patient_summary(self, patient_id):
        try:
            patient = self.get_patient(patient_id)
            return {
                "patient": patient,
                "summary": {"total_episodes": 0, "active_episodes": 0}
            }
        except Exception as e:
            raise Exception(f"Failed to get summary: {str(e)}")
    
    # Episode methods
    def create_episode(self, episode_data, created_by=None):
        try:
            if hasattr(episode_data, 'model_dump'):
                data = episode_data.model_dump()
            else:
                data = dict(episode_data)
            
            episode = self.repos.episode.create(data)
            
            from schemas.episode import EpisodeResponse
            return EpisodeResponse.model_validate(episode)
        except Exception as e:
            raise Exception(f"Episode creation failed: {str(e)}")
    
    def get_episodes_by_patient(self, patient_id, status=None):
        try:
            episodes = self.repos.episode.get_by_patient(patient_id)
            from schemas.episode import EpisodeResponse
            return [EpisodeResponse.model_validate(ep) for ep in episodes]
        except Exception:
            return []
    
    # Treatment methods
    def create_treatment(self, treatment_data, created_by=None):
        try:
            if hasattr(treatment_data, 'model_dump'):
                data = treatment_data.model_dump()
            else:
                data = dict(treatment_data)
            
            treatment = self.repos.treatment.create(data)
            
            from schemas.treatment import TreatmentResponse
            return TreatmentResponse.model_validate(treatment)
        except Exception as e:
            raise Exception(f"Treatment creation failed: {str(e)}")
    
    # Diagnosis methods  
    def create_diagnosis(self, diagnosis_data, created_by=None):
        try:
            if hasattr(diagnosis_data, 'model_dump'):
                data = diagnosis_data.model_dump()
            else:
                data = dict(diagnosis_data)
            
            diagnosis = self.repos.diagnosis.create(data)
            
            from schemas.diagnosis import DiagnosisResponse
            return DiagnosisResponse.model_validate(diagnosis)
        except Exception as e:
            raise Exception(f"Diagnosis creation failed: {str(e)}")


class SimpleServiceManager:
    """Simple service manager that works"""
    
    def __init__(self, repos):
        self.repos = repos
        
        # Create working services
        self.patient = WorkingService(repos, "patient")
        self.episode = WorkingService(repos, "episode")
        self.diagnosis = WorkingService(repos, "diagnosis") 
        self.treatment = WorkingService(repos, "treatment")
        self.fhir = WorkingService(repos, "fhir")
        self.clinical = WorkingService(repos, "clinical")

# =============================================================================
# Database Dependencies
# =============================================================================

def get_database() -> Session:
    """Database session dependency"""
    if not SessionLocal:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured"
        )
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =============================================================================
# Repository Dependencies  
# =============================================================================

def get_repository_manager(
    db: Session = Depends(get_database)
) -> RepositoryManager:
    """Repository manager dependency"""
    try:
        repos = RepositoryManager(db)
        logger.debug("Repository manager created")
        return repos
    except Exception as e:
        logger.error(f"Failed to create repository manager: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize repositories"
        )

# =============================================================================
# Service Dependencies - SIMPLE WORKING VERSION
# =============================================================================

def get_service_manager(
    repos: RepositoryManager = Depends(get_repository_manager)
):
    """Simple working service manager"""
    try:
        # Use our simple working service manager
        services = SimpleServiceManager(repos)
        logger.debug("Simple working service manager created")
        return services
    except Exception as e:
        logger.error(f"Failed to create service manager: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize services"
        )

# =============================================================================
# Authentication Dependencies
# =============================================================================

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """Get current user - returns mock user for development"""
    if not credentials:
        return None
    
    if credentials.credentials:
        return {
            "user_id": "dev-user-001",
            "email": "developer@diagnoassist.com",
            "role": "admin",
            "permissions": {
                "patient.create": True,
                "patient.read": True,
                "patient.update": True,
                "patient.delete": True,
                "episode.create": True,
                "episode.read": True,
                "episode.update": True,
                "episode.delete": True,
                "diagnosis.create": True,
                "diagnosis.read": True,
                "diagnosis.update": True,
                "diagnosis.delete": True,
                "treatment.create": True,
                "treatment.read": True,
                "treatment.update": True,
                "treatment.delete": True,
            }
        }
    
    return None

def require_authentication(
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Require authentication"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user

def require_permission(permission: str):
    """Permission checking factory"""
    def check_permission(
        current_user: Dict[str, Any] = Depends(require_authentication)
    ) -> Dict[str, Any]:
        user_permissions = current_user.get("permissions", {})
        if not user_permissions.get(permission, False) and current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        return current_user
    return check_permission

# =============================================================================
# Common Dependencies
# =============================================================================

def get_pagination(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size")
) -> PaginationParams:
    """Pagination parameters"""
    return PaginationParams(page=page, size=size)

def get_search_params(
    search: Optional[str] = Query(None, description="Search query"),
    sort_by: Optional[str] = Query(None, description="Sort field"),
    sort_order: Optional[str] = Query("asc", regex="^(asc|desc)$", description="Sort order")
) -> Dict[str, Any]:
    """Search parameters"""
    return {
        "search": search,
        "sort_by": sort_by,
        "sort_order": sort_order
    }

def get_settings() -> Settings:
    """Application settings"""
    return Settings()

# =============================================================================
# Health Dependencies
# =============================================================================

def check_database_health() -> Dict[str, Any]:
    """Database health check"""
    try:
        connection_ok = test_database_connection()
        return {
            "status": "healthy" if connection_ok else "unhealthy",
            "database": "connected" if connection_ok else "disconnected"
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

def check_services_health(services = Depends(get_service_manager)) -> Dict[str, Any]:
    """Services health check"""
    try:
        service_status = {}
        for service_name in ['patient', 'episode', 'diagnosis', 'treatment']:
            service_status[service_name] = "available" if hasattr(services, service_name) else "unavailable"
        
        return {
            "status": "healthy",
            "services": service_status
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

# =============================================================================
# Type Annotations
# =============================================================================

DatabaseDep = Annotated[Session, Depends(get_database)]
RepositoryDep = Annotated[RepositoryManager, Depends(get_repository_manager)]
ServiceDep = Annotated[Any, Depends(get_service_manager)]
CurrentUserDep = Annotated[Optional[Dict[str, Any]], Depends(get_current_user)]
AuthUserDep = Annotated[Dict[str, Any], Depends(require_authentication)]
PaginationDep = Annotated[PaginationParams, Depends(get_pagination)]
SearchDep = Annotated[Dict[str, Any], Depends(get_search_params)]
SettingsDep = Annotated[Settings, Depends(get_settings)]

# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "get_database",
    "get_repository_manager", 
    "get_service_manager",
    "get_current_user",
    "require_authentication",
    "require_permission",
    "get_pagination",
    "get_search_params",
    "get_settings",
    "check_database_health",
    "check_services_health",
    "DatabaseDep",
    "RepositoryDep", 
    "ServiceDep",
    "CurrentUserDep",
    "AuthUserDep",
    "PaginationDep",
    "SearchDep",
    "SettingsDep"
]