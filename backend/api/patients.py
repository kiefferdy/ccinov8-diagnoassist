"""
Patient API Router for DiagnoAssist - CLEAN VERSION
CRUD operations for patient management with proper FastAPI exceptions
"""

from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from typing import List, Optional
from uuid import UUID

# Import dependencies - FIXED: Import directly from the module
from api.dependencies import get_service_manager, get_current_user, PaginationParams

# Import schemas
from schemas.patient import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientListResponse
)
from schemas.common import StatusResponse

# Create router
router = APIRouter(prefix="/patients", tags=["patients"])

# Create dependency aliases properly
ServiceDep = Depends(get_service_manager)
CurrentUserDep = Depends(get_current_user)
PaginationDep = Depends(PaginationParams)

# =============================================================================
# Patient CRUD Operations - CLEAN VERSION
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
    # Authorization check - can create patients
    if not current_user or not current_user.get("permissions", {}).get("patient.create", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create patients"
        )
    
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
                detail=f"Failed to create patient: {error_message}"
            )


@router.get("/", response_model=PatientListResponse)
async def get_patients(
    services = ServiceDep,
    current_user = CurrentUserDep,
    pagination = PaginationDep,
    search: Optional[str] = Query(None, description="Search patients by name, MRN, or email"),
    status_filter: Optional[str] = Query(None, description="Filter by patient status")
):
    """
    Get paginated list of patients
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        pagination: Pagination parameters
        search: Search query
        status_filter: Patient status filter
        
    Returns:
        Paginated list of patients
    """
    # Authorization check - FIXED to use HTTPException
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        # Get patients through service layer
        patients = services.patient.get_patients(
            pagination=pagination,
            search=search,
            status=status_filter
        )
        
        return patients
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve patients: {str(e)}"
        )


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    services = ServiceDep,
    current_user = CurrentUserDep,
    patient_id: UUID = Path(..., description="Patient ID")
):
    """
    Get patient by ID
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        patient_id: Patient UUID
        
    Returns:
        Patient data
    """
    # Authorization check
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        # Get patient through service layer
        patient = services.patient.get_patient(str(patient_id))
        return patient
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient {patient_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve patient: {error_message}"
            )


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_data: PatientUpdate,
    services = ServiceDep,
    current_user = CurrentUserDep,
    patient_id: UUID = Path(..., description="Patient ID")
):
    """
    Update patient information
    
    Args:
        patient_data: Patient update data
        services: Injected services
        current_user: Current authenticated user
        patient_id: Patient UUID
        
    Returns:
        Updated patient data
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("patient.update", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update patients"
        )
    
    try:
        # Update patient through service layer
        updated_patient = services.patient.update_patient(
            patient_id=str(patient_id),
            patient_data=patient_data,
            updated_by=current_user["user_id"]
        )
        
        return updated_patient
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient {patient_id} not found"
            )
        elif "already exists" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_message
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update patient: {error_message}"
            )


@router.delete("/{patient_id}", response_model=StatusResponse)
async def delete_patient(
    services = ServiceDep,
    current_user = CurrentUserDep,
    patient_id: UUID = Path(..., description="Patient ID")
):
    """
    Delete patient (soft delete)
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        patient_id: Patient UUID
        
    Returns:
        Success status
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("patient.delete", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete patients"
        )
    
    try:
        # Delete patient through service layer
        services.patient.delete_patient(
            patient_id=str(patient_id),
            deleted_by=current_user["user_id"]
        )
        
        return StatusResponse(
            status="success",
            message=f"Patient {patient_id} deleted successfully"
        )
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient {patient_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete patient: {error_message}"
            )

# Export router
__all__ = ["router"]