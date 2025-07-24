"""
Patient API Router for DiagnoAssist
CRUD operations for patient management with proper FastAPI exceptions
"""

from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from typing import List, Optional
from uuid import UUID

# Import individual service dependencies
from api.dependencies import (
    PatientServiceDep,
    EpisodeServiceDep, 
    ClinicalServiceDep,
    CurrentUserDep,
    PaginationDep
)

# Import schemas
from schemas.patient import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientListResponse
)
from schemas.common import StatusResponse, PaginationParams

# Create router
router = APIRouter(prefix="/patients", tags=["patients"])

# =============================================================================
# Patient CRUD Operations - COMPREHENSIVE VERSION
# =============================================================================

@router.post("/", response_model=PatientResponse, status_code=201)
async def create_patient(
    patient_data: PatientCreate,
    patient_service: PatientServiceDep,
    current_user: CurrentUserDep
):
    """
    Create a new patient
    
    Args:
        patient_data: Patient creation data
        patient_service: Injected patient service
        current_user: Current authenticated user
        
    Returns:
        Created patient data
        
    Raises:
        HTTPException: Various HTTP errors based on the issue
    """
    # Authorization check - can create patients (commented out for MVP)
    # if not current_user or not current_user.get("permissions", {}).get("patient.create", False):
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Insufficient permissions to create patients"
    #     )
    
    try:
        patient = patient_service.create_patient(patient_data)
        return patient
    except Exception as e:
        # Convert service exceptions to HTTP exceptions
        error_message = str(e)
        
        if "already exists" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_message
            )
        elif "validation" in error_message.lower() or "invalid" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error_message
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error occurred while creating patient: {error_message}"
            )

@router.get("/", response_model=PatientListResponse)
async def list_patients(
    patient_service: PatientServiceDep,
    current_user: CurrentUserDep,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search term")
):
    """
    List patients with pagination and search
    
    Args:
        page: Page number
        size: Page size
        search: Search term
        patient_service: Injected patient service
        current_user: Current authenticated user
        
    Returns:
        List of patients with pagination metadata
    """
    # Authorization check (commented out for MVP)
    # if not current_user or not current_user.get("permissions", {}).get("patient.read", False):
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Insufficient permissions to read patients"
    #     )
    
    try:
        # Get patients through service layer
        patients = patient_service.list_patients(
            page=page,
            size=size,
            search=search,
            sort_by=None,
            sort_order=None
        )
        return patients
    except Exception as e:
        error_message = str(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while listing patients"
        )

@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_service: PatientServiceDep,
    current_user: CurrentUserDep,
    patient_id: str = Path(..., description="Patient ID")
):
    """
    Get a specific patient by ID
    
    Args:
        patient_id: Patient UUID
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Patient data
        
    Raises:
        HTTPException: If patient not found or permission denied
    """
    # Validate UUID format (commented out for MVP, keeping for later)
    # validate_uuid(patient_id)
    
    # Authorization check (commented out for MVP)
    # if not current_user or not current_user.get("permissions", {}).get("patient.read", False):
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Insufficient permissions to read patients"
    #     )
    
    try:
        patient = patient_service.get_patient(patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {patient_id} not found"
            )
        return patient
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        error_message = str(e)
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {patient_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error occurred while retrieving patient"
            )

@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_service: PatientServiceDep,
    current_user: CurrentUserDep,
    patient_id: str = Path(..., description="Patient ID"),
    patient_data: PatientUpdate = ...
):
    """
    Update a specific patient
    
    Args:
        patient_id: Patient UUID
        patient_data: Updated patient data
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Updated patient data
    """
    # Validate UUID format (commented out for MVP)
    # validate_uuid(patient_id)
    
    # Authorization check (commented out for MVP)
    # if not current_user or not current_user.get("permissions", {}).get("patient.update", False):
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Insufficient permissions to update patients"
    #     )
    
    try:
        patient = patient_service.update_patient(patient_id, patient_data)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {patient_id} not found"
            )
        return patient
    except HTTPException:
        raise
    except Exception as e:
        error_message = str(e)
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {patient_id} not found"
            )
        elif "validation" in error_message.lower() or "invalid" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error_message
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error occurred while updating patient"
            )

@router.delete("/{patient_id}", response_model=StatusResponse)
async def delete_patient(
    patient_service: PatientServiceDep,
    current_user: CurrentUserDep,
    patient_id: str = Path(..., description="Patient ID")
):
    """
    Delete a specific patient
    
    Args:
        patient_id: Patient UUID
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Status response
    """
    # Validate UUID format (commented out for MVP)
    # validate_uuid(patient_id)
    
    # Authorization check (commented out for MVP)
    # if not current_user or not current_user.get("permissions", {}).get("patient.delete", False):
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Insufficient permissions to delete patients"
    #     )
    
    try:
        result = patient_service.delete_patient(patient_id)
        
        return StatusResponse(
            status="success",
            message=f"Patient {patient_id} deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        error_message = str(e)
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {patient_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error occurred while deleting patient"
            )

# =============================================================================
# Additional Patient Endpoints
# =============================================================================

@router.get("/{patient_id}/episodes", response_model=List[dict])
async def get_patient_episodes(
    episode_service: EpisodeServiceDep,
    current_user: CurrentUserDep,
    patient_id: str = Path(..., description="Patient ID")
):
    """
    Get all episodes for a specific patient
    
    Args:
        patient_id: Patient UUID
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        List of patient episodes
    """
    # Validate UUID format (commented out for MVP)
    # validate_uuid(patient_id)
    
    # Authorization check (commented out for MVP)
    # if not current_user or not current_user.get("permissions", {}).get("patient.read", False):
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Insufficient permissions to read patient episodes"
    #     )
    
    try:
        # Get patient episodes through service layer
        episodes = episode_service.get_patient_episodes(patient_id)
        return episodes
    except Exception as e:
        error_message = str(e)
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {patient_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error occurred while retrieving patient episodes"
            )

@router.get("/{patient_id}/health-summary")
async def get_patient_health_summary(
    clinical_service: ClinicalServiceDep,
    current_user: CurrentUserDep,
    patient_id: str = Path(..., description="Patient ID")
):
    """
    Get health summary for a patient
    
    Args:
        patient_id: Patient UUID
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Patient health summary
    """
    # Validate UUID format (commented out for MVP)
    # validate_uuid(patient_id)
    
    # Authorization check (commented out for MVP)
    # if not current_user or not current_user.get("permissions", {}).get("patient.read", False):
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Insufficient permissions to read patient health summary"
    #     )
    
    try:
        # Get patient health summary through service layer
        summary = clinical_service.get_patient_health_summary(patient_id)
        return summary
    except Exception as e:
        error_message = str(e)
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {patient_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error occurred while retrieving patient health summary"
            )