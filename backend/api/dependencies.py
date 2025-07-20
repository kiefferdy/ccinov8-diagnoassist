# ================================
# api/__init__.py
# ================================

"""
DiagnoAssist API Package
Provides both FHIR-compliant and internal REST APIs
"""

from fastapi import APIRouter
from .fhir import fhir_router
from .internal import internal_router

# Main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(fhir_router, prefix="/fhir")
api_router.include_router(internal_router, prefix="/api")


# ================================
# api/dependencies.py
# ================================

from functools import lru_cache
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt

# Database and repository imports
from config.database import get_db
from repositories.patient_repository import PatientRepository
from repositories.episode_repository import EpisodeRepository
from repositories.diagnosis_repository import DiagnosisRepository
from repositories.treatment_repository import TreatmentRepository
from repositories.fhir_patient_repository import FHIRPatientRepository
from repositories.fhir_encounter_repository import FHIREncounterRepository
from repositories.fhir_observation_repository import FHIRObservationRepository

# Service imports
from services.patient_service import PatientService
from services.clinical_service import ClinicalService
from services.diagnosis_service import DiagnosisService
from services.treatment_service import TreatmentService
from services.ai_service import AIService
from services.fhir_patient_service import FHIRPatientService
from services.fhir_clinical_service import FHIRClinicalService
from services.fhir_diagnosis_service import FHIRDiagnosisService
from services.fhir_interop_service import FHIRInteropService

# Configuration
from config.settings import get_settings

# Security
security = HTTPBearer()
settings = get_settings()

# ================================
# Authentication Dependencies
# ================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Validate JWT token and return current user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # In a real app, fetch user from database
    # user = get_user(db, user_id=user_id)
    # if user is None:
    #     raise credentials_exception
    
    return {"user_id": user_id, "sub": user_id}

async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    """Ensure user is active"""
    # Add user status checks here
    return current_user

# Optional authentication for public endpoints
async def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Optional authentication - returns None if no token"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        return {"user_id": user_id, "sub": user_id} if user_id else None
    except JWTError:
        return None

# ================================
# Repository Dependencies
# ================================

def get_patient_repository(db: Session = Depends(get_db)) -> PatientRepository:
    return PatientRepository(db)

def get_episode_repository(db: Session = Depends(get_db)) -> EpisodeRepository:
    return EpisodeRepository(db)

def get_diagnosis_repository(db: Session = Depends(get_db)) -> DiagnosisRepository:
    return DiagnosisRepository(db)

def get_treatment_repository(db: Session = Depends(get_db)) -> TreatmentRepository:
    return TreatmentRepository(db)

# FHIR Repositories
def get_fhir_patient_repository(db: Session = Depends(get_db)) -> FHIRPatientRepository:
    return FHIRPatientRepository(db)

def get_fhir_encounter_repository(db: Session = Depends(get_db)) -> FHIREncounterRepository:
    return FHIREncounterRepository(db)

def get_fhir_observation_repository(db: Session = Depends(get_db)) -> FHIRObservationRepository:
    return FHIRObservationRepository(db)

# ================================
# Service Dependencies
# ================================

@lru_cache()
def get_ai_service() -> AIService:
    return AIService()

def get_patient_service(
    patient_repo: PatientRepository = Depends(get_patient_repository)
) -> PatientService:
    return PatientService(patient_repo)

def get_clinical_service(
    episode_repo: EpisodeRepository = Depends(get_episode_repository),
    ai_service: AIService = Depends(get_ai_service)
) -> ClinicalService:
    return ClinicalService(episode_repo, ai_service)

def get_diagnosis_service(
    diagnosis_repo: DiagnosisRepository = Depends(get_diagnosis_repository),
    ai_service: AIService = Depends(get_ai_service)
) -> DiagnosisService:
    return DiagnosisService(diagnosis_repo, ai_service)

def get_treatment_service(
    treatment_repo: TreatmentRepository = Depends(get_treatment_repository),
    ai_service: AIService = Depends(get_ai_service)
) -> TreatmentService:
    return TreatmentService(treatment_repo, ai_service)

# FHIR Services
def get_fhir_patient_service(
    fhir_patient_repo: FHIRPatientRepository = Depends(get_fhir_patient_repository)
) -> FHIRPatientService:
    return FHIRPatientService(fhir_patient_repo)

def get_fhir_clinical_service(
    fhir_encounter_repo: FHIREncounterRepository = Depends(get_fhir_encounter_repository),
    fhir_observation_repo: FHIRObservationRepository = Depends(get_fhir_observation_repository),
    ai_service: AIService = Depends(get_ai_service)
) -> FHIRClinicalService:
    return FHIRClinicalService(fhir_encounter_repo, fhir_observation_repo, ai_service)

def get_fhir_diagnosis_service(
    fhir_patient_repo: FHIRPatientRepository = Depends(get_fhir_patient_repository),
    fhir_encounter_repo: FHIREncounterRepository = Depends(get_fhir_encounter_repository),
    ai_service: AIService = Depends(get_ai_service)
) -> FHIRDiagnosisService:
    return FHIRDiagnosisService(fhir_patient_repo, fhir_encounter_repo, ai_service)

def get_fhir_interop_service() -> FHIRInteropService:
    return FHIRInteropService()
