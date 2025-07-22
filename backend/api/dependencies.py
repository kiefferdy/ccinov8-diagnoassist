"""
API Dependencies for DiagnoAssist - FIXED VERSION
Simple, robust service methods with Pydantic v2 compatibility
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
# FIXED WORKING SERVICE WRAPPER (as fallback)
# =============================================================================

class WorkingService:
    """Simple service that actually works with Pydantic v2"""
    
    def __init__(self, repos, service_name="unknown"):
        self.repos = repos
        self.service_name = service_name
    
    def _convert_to_dict(self, data):
        """Convert data to dict with Pydantic v2 compatibility"""
        if hasattr(data, 'model_dump'):
            return data.model_dump()
        elif hasattr(data, 'dict'):
            return data.dict()  # Pydantic v1 fallback
        else:
            return dict(data)
    
    def _create_response_model(self, data, ResponseClass):
        """Create response model with Pydantic v2 compatibility"""
        try:
            # Try Pydantic v2 first
            if hasattr(ResponseClass, 'model_validate'):
                return ResponseClass.model_validate(data)
            # Fallback to Pydantic v1
            elif hasattr(ResponseClass, 'from_orm'):
                return ResponseClass.from_orm(data)
            else:
                # Last resort - direct instantiation
                return ResponseClass(**data.__dict__ if hasattr(data, '__dict__') else data)
        except Exception as e:
            logger.error(f"Failed to create response model: {e}")
            raise Exception(f"Failed to create response: {str(e)}")
    
    # Patient methods (ADD MISSING METHODS)
    def create_patient(self, patient_data, created_by=None):
        try:
            data = self._convert_to_dict(patient_data)
            patient = self.repos.patient.create(data)
            
            from schemas.patient import PatientResponse
            return self._create_response_model(patient, PatientResponse)
        except Exception as e:
            raise Exception(f"Patient creation failed: {str(e)}")
    
    def get_patient(self, patient_id):
        try:
            patient = self.repos.patient.get_by_id(patient_id)
            if not patient:
                raise Exception("Patient not found")
            
            from schemas.patient import PatientResponse
            return self._create_response_model(patient, PatientResponse)
        except Exception as e:
            raise Exception(f"Failed to get patient: {str(e)}")
    
    def update_patient(self, patient_id, patient_data, updated_by=None):
        try:
            data = self._convert_to_dict(patient_data)
            updated = self.repos.patient.update(patient_id, data)
            
            from schemas.patient import PatientResponse
            return self._create_response_model(updated, PatientResponse)
        except Exception as e:
            raise Exception(f"Failed to update patient: {str(e)}")
    
    def delete_patient(self, patient_id, deleted_by=None):
        try:
            self.repos.patient.delete(patient_id)
            return {"status": "deleted", "patient_id": patient_id}
        except Exception as e:
            raise Exception(f"Failed to delete patient: {str(e)}")
    
    # Episode methods
    def create_episode(self, episode_data, created_by=None):
        try:
            data = self._convert_to_dict(episode_data)
            episode = self.repos.episode.create(data)
            
            from schemas.episode import EpisodeResponse
            return self._create_response_model(episode, EpisodeResponse)
        except Exception as e:
            raise Exception(f"Episode creation failed: {str(e)}")
    
    def get_episode(self, episode_id):
        try:
            episode = self.repos.episode.get_by_id(episode_id)
            if not episode:
                raise Exception("Episode not found")
            
            from schemas.episode import EpisodeResponse
            return self._create_response_model(episode, EpisodeResponse)
        except Exception as e:
            raise Exception(f"Failed to get episode: {str(e)}")
    
    def update_episode(self, episode_id, episode_data, updated_by=None):
        try:
            data = self._convert_to_dict(episode_data)
            updated = self.repos.episode.update(episode_id, data)
            
            from schemas.episode import EpisodeResponse
            return self._create_response_model(updated, EpisodeResponse)
        except Exception as e:
            raise Exception(f"Failed to update episode: {str(e)}")
    
    def delete_episode(self, episode_id, deleted_by=None):
        try:
            self.repos.episode.delete(episode_id)
            return {"status": "deleted", "episode_id": episode_id}
        except Exception as e:
            raise Exception(f"Failed to delete episode: {str(e)}")
    
    # Diagnosis methods
    def create_diagnosis(self, diagnosis_data, created_by=None):
        try:
            data = self._convert_to_dict(diagnosis_data)
            diagnosis = self.repos.diagnosis.create(data)
            
            from schemas.diagnosis import DiagnosisResponse
            return self._create_response_model(diagnosis, DiagnosisResponse)
        except Exception as e:
            raise Exception(f"Diagnosis creation failed: {str(e)}")
    
    def get_diagnosis(self, diagnosis_id):
        try:
            diagnosis = self.repos.diagnosis.get_by_id(diagnosis_id)
            if not diagnosis:
                raise Exception("Diagnosis not found")
            
            from schemas.diagnosis import DiagnosisResponse
            return self._create_response_model(diagnosis, DiagnosisResponse)
        except Exception as e:
            raise Exception(f"Failed to get diagnosis: {str(e)}")
    
    def update_diagnosis(self, diagnosis_id, diagnosis_data, updated_by=None):
        try:
            data = self._convert_to_dict(diagnosis_data)
            updated = self.repos.diagnosis.update(diagnosis_id, data)
            
            from schemas.diagnosis import DiagnosisResponse
            return self._create_response_model(updated, DiagnosisResponse)
        except Exception as e:
            raise Exception(f"Failed to update diagnosis: {str(e)}")
    
    def delete_diagnosis(self, diagnosis_id, deleted_by=None):
        try:
            self.repos.diagnosis.delete(diagnosis_id)
            return {"status": "deleted", "diagnosis_id": diagnosis_id}
        except Exception as e:
            raise Exception(f"Failed to delete diagnosis: {str(e)}")
    
    # Treatment methods
    def create_treatment(self, treatment_data, created_by=None):
        try:
            data = self._convert_to_dict(treatment_data)
            treatment = self.repos.treatment.create(data)
            
            from schemas.treatment import TreatmentResponse
            return self._create_response_model(treatment, TreatmentResponse)
        except Exception as e:
            raise Exception(f"Treatment creation failed: {str(e)}")
    
    def get_treatment(self, treatment_id):
        try:
            treatment = self.repos.treatment.get_by_id(treatment_id)
            if not treatment:
                raise Exception("Treatment not found")
            
            from schemas.treatment import TreatmentResponse
            return self._create_response_model(treatment, TreatmentResponse)
        except Exception as e:
            raise Exception(f"Failed to get treatment: {str(e)}")
    
    def update_treatment(self, treatment_id, treatment_data, updated_by=None):
        try:
            data = self._convert_to_dict(treatment_data)
            updated = self.repos.treatment.update(treatment_id, data)
            
            from schemas.treatment import TreatmentResponse
            return self._create_response_model(updated, TreatmentResponse)
        except Exception as e:
            raise Exception(f"Failed to update treatment: {str(e)}")
    
    def delete_treatment(self, treatment_id, deleted_by=None):
        try:
            self.repos.treatment.delete(treatment_id)
            return {"status": "deleted", "treatment_id": treatment_id}
        except Exception as e:
            raise Exception(f"Failed to delete treatment: {str(e)}")

# =============================================================================
# DEPENDENCY FUNCTIONS
# =============================================================================

def get_database() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_repository_manager(db: Session = Depends(get_database)) -> RepositoryManager:
    """Get repository manager with database session"""
    return RepositoryManager(db)

def get_working_service(repos: RepositoryManager = Depends(get_repository_manager)) -> WorkingService:
    """Get working service instance as fallback"""
    return WorkingService(repos, "api")

def get_pagination(
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 20
) -> PaginationParams:
    """Get pagination parameters"""
    return PaginationParams(page=page, size=size)

def get_auth_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[Dict[str, Any]]:
    """Get authenticated user - MVP version with all permissions"""
    if credentials:
        # For MVP, return a mock user with all permissions
        return {
            "user_id": "system_user",
            "username": "system", 
            "token": credentials.credentials,
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
                "treatment.delete": True
            }
        }
    # For MVP, return anonymous user with read permissions
    return {
        "user_id": "anonymous",
        "username": "anonymous",
        "permissions": {
            "patient.read": True,
            "episode.read": True,
            "diagnosis.read": True,
            "treatment.read": True
        }
    }

def check_database_health():
    """Check database connection health"""
    if not test_database_connection():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection unavailable"
        )
    return True

def check_services_health():
    """Check services health - simple version"""
    try:
        from config.database import SessionLocal
        db = SessionLocal()
        repos = RepositoryManager(db)
        service = WorkingService(repos)
        db.close()
        return True
    except Exception as e:
        logger.error(f"Services health check failed: {e}")
        return False

# =============================================================================
# SERVICE DEPENDENCY SETUP - Try ServiceManager first, fallback to WorkingService
# =============================================================================

# Try to import and use the proper ServiceManager
try:
    from services import get_service_manager, ServiceManager
    
    def get_service_manager_dep(repos: RepositoryManager = Depends(get_repository_manager)) -> ServiceManager:
        """Get service manager for dependency injection"""
        return get_service_manager(repos)
    
    # Use proper ServiceManager if available
    ServiceDep = Annotated[ServiceManager, Depends(get_service_manager_dep)]
    print("✅ Using ServiceManager for dependency injection")
    
except ImportError as e:
    # Fall back to WorkingService if ServiceManager not available
    print(f"⚠️  ServiceManager not available ({e}), using WorkingService fallback")
    ServiceDep = Annotated[WorkingService, Depends(get_working_service)]

# Type annotations for FastAPI dependency injection
CurrentUserDep = Annotated[Optional[Dict[str, Any]], Depends(get_auth_user)]
PaginationDep = Annotated[PaginationParams, Depends(get_pagination)]
DatabaseDep = Annotated[Session, Depends(get_database)]
RepositoryDep = Annotated[RepositoryManager, Depends(get_repository_manager)]
SettingsDep = Annotated[Settings, Depends(lambda: Settings())]

# Export everything
__all__ = [
    "ServiceDep",
    "CurrentUserDep", 
    "PaginationDep",
    "DatabaseDep",
    "RepositoryDep",
    "SettingsDep",
    "check_database_health",
    "check_services_health"
]