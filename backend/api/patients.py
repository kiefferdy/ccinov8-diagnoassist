"""
Patient API Router for DiagnoAssist - IMPORT FIXED VERSION
CRUD operations for patient management with proper FastAPI exceptions
"""

from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from typing import List, Optional
from uuid import UUID

# FIXED: Import dependencies properly from api.dependencies
from api.dependencies import (
    ServiceDep,
    CurrentUserDep,
    PaginationDep,
    SearchDep,
    validate_uuid
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
    services = ServiceDep,
    current_user = CurrentUserDep
):
    """
    Create a new patient
    
    Args:
        patient_data: Patient creation data
        services: Injected services
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
        # Create patient through service layer
        patient = services.patient.create_patient(patient_data)
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
                detail="Internal server error occurred while creating patient"
            )

@router.get("/", response_model=PatientListResponse)
async def list_patients(
    pagination: PaginationParams = PaginationDep,
    search_params: dict = SearchDep,
    services = ServiceDep,
    current_user = CurrentUserDep
):
    """
    List patients with pagination and search
    
    Args:
        pagination: Pagination parameters
        search_params: Search and filter parameters
        services: Injected services
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
        patients = services.patient.list_patients(
            page=pagination.page,
            size=pagination.size,
            search=search_params.get("search"),
            sort_by=search_params.get("sort_by"),
            sort_order=search_params.get("sort_order")
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
    patient_id: str = Path(..., description="Patient ID"),
    services = ServiceDep,
    current_user = CurrentUserDep
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
        # Get patient through service layer
        patient = services.patient.get_patient(patient_id)
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
    patient_id: str = Path(..., description="Patient ID"),
    patient_data: PatientUpdate = ...,
    services = ServiceDep,
    current_user = CurrentUserDep
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
        # Update patient through service layer
        patient = services.patient.update_patient(patient_id, patient_data)
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
    patient_id: str = Path(..., description="Patient ID"),
    services = ServiceDep,
    current_user = CurrentUserDep
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
        # Delete patient through service layer
        success = services.patient.delete_patient(patient_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {patient_id} not found"
            )
        
        return StatusResponse(
            success=True,
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
    patient_id: str = Path(..., description="Patient ID"),
    services = ServiceDep,
    current_user = CurrentUserDep
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
        episodes = services.episode.get_patient_episodes(patient_id)
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
    patient_id: str = Path(..., description="Patient ID"),
    services = ServiceDep,
    current_user = CurrentUserDep
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
        summary = services.clinical.get_patient_health_summary(patient_id)
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