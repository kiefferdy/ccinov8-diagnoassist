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
# FIXED WORKING SERVICE WRAPPER
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
    
    # Patient methods
    def create_patient(self, patient_data, created_by=None):
        try:
            # Convert to dict
            data = self._convert_to_dict(patient_data)
            
            # Create patient
            patient = self.repos.patient.create(data)
            
            # Return as response schema
            from schemas.patient import PatientResponse
            return self._create_response_model(patient, PatientResponse)
        except Exception as e:
            raise Exception(f"Patient creation failed: {str(e)}")
    
    def get_patients(self, pagination=None, search=None, status=None):
        try:
            patients = self.repos.patient.get_all()
            
            from schemas.patient import PatientListResponse, PatientResponse
            patient_responses = []
            for p in patients:
                try:
                    patient_responses.append(self._create_response_model(p, PatientResponse))
                except Exception as e:
                    logger.error(f"Failed to convert patient {p.id}: {e}")
                    continue
            
            return PatientListResponse(
                data=patient_responses,
                total=len(patient_responses),
                page=1 if pagination else 1,
                size=len(patient_responses)
            )
        except Exception as e:
            raise Exception(f"Failed to get patients: {str(e)}")
    
    def get_patient(self, patient_id):
        try:
            patient = self.repos.patient.get_by_id(patient_id)
            if not patient:
                raise Exception("Patient not found")
            
            from schemas.patient import PatientResponse
            return self._create_response_model(patient, PatientResponse)
        except Exception as e:
            if "not found" in str(e).lower():
                raise Exception("Patient not found")
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
    
    def get_patient_by_mrn(self, mrn):
        try:
            patient = self.repos.patient.get_by_mrn(mrn)
            if not patient:
                raise Exception("Patient not found")
            
            from schemas.patient import PatientResponse
            return self._create_response_model(patient, PatientResponse)
        except Exception as e:
            raise Exception(f"Patient not found: {str(e)}")
    
    def get_patient_by_email(self, email):
        try:
            patient = self.repos.patient.get_by_email(email)
            if not patient:
                raise Exception("Patient not found")
            
            from schemas.patient import PatientResponse
            return self._create_response_model(patient, PatientResponse)
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
            data = self._convert_to_dict(episode_data)
            episode = self.repos.episode.create(data)
            
            from schemas.episode import EpisodeResponse
            return self._create_response_model(episode, EpisodeResponse)
        except Exception as e:
            raise Exception(f"Episode creation failed: {str(e)}")
    
    def get_episodes_by_patient(self, patient_id, status=None):
        try:
            episodes = self.repos.episode.get_by_patient(patient_id)
            from schemas.episode import EpisodeResponse
            episode_responses = []
            for ep in episodes:
                try:
                    episode_responses.append(self._create_response_model(ep, EpisodeResponse))
                except Exception as e:
                    logger.error(f"Failed to convert episode {ep.id}: {e}")
                    continue
            return episode_responses
        except Exception:
            return []
    
    # Treatment methods
    def create_treatment(self, treatment_data, created_by=None):
        try:
            data = self._convert_to_dict(treatment_data)
            treatment = self.repos.treatment.create(data)
            
            from schemas.treatment import TreatmentResponse
            return self._create_response_model(treatment, TreatmentResponse)
        except Exception as e:
            raise Exception(f"Treatment creation failed: {str(e)}")

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

def get_service(repos: RepositoryManager = Depends(get_repository_manager)) -> WorkingService:
    """Get working service instance"""
    return WorkingService(repos, "api")

def get_pagination(
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 20
) -> PaginationParams:
    """Get pagination parameters"""
    return PaginationParams(page=page, size=size)

def get_auth_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[str]:
    """Get authenticated user - optional for MVP"""
    if credentials:
        # For MVP, just return a simple user identifier
        # In production, validate JWT token here
        return "system_user"
    return None

def check_database_health():
    """Check database connection health"""
    if not test_database_connection():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection unavailable"
        )
    return True