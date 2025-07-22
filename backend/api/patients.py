"""
Patient API Router for DiagnoAssist - FIXED VERSION
CRUD operations for patient management with proper FastAPI exceptions
"""

from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from typing import List, Optional
from uuid import UUID

# Import dependencies
from api.dependencies import ServiceDep, CurrentUserDep, PaginationDep

# Import schemas
from schemas.patient import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientListResponse
)
from schemas.episode import EpisodeCreate
from schemas.common import StatusResponse

# Create router
router = APIRouter(prefix="/patients", tags=["patients"])


# =============================================================================
# Patient CRUD Operations - FIXED WITH HTTPException
# =============================================================================

@router.post("/", response_model=PatientResponse, status_code=201)
async def create_patient(
    patient_data: PatientCreate,
    services: ServiceDep,
    current_user: CurrentUserDep
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
        patient = services.patient.create_patient(
            patient_data=patient_data,
            created_by=current_user["user_id"]
        )
        
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
    services: ServiceDep,
    current_user: CurrentUserDep,
    pagination: PaginationDep,
    search: Optional[str] = Query(None, description="Search patients by name, MRN, or email"),
    status: Optional[str] = Query(None, description="Filter by patient status")
):
    """
    Get paginated list of patients
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        pagination: Pagination parameters
        search: Search query
        status: Patient status filter
        
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
            status=status
        )
        
        return patients
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve patients: {str(e)}"
        )


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    services: ServiceDep,
    current_user: CurrentUserDep,
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
    services: ServiceDep,
    current_user: CurrentUserDep,
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


@router.delete("/{patient_id}", status_code=204)
async def delete_patient(
    services: ServiceDep,
    current_user: CurrentUserDep,
    patient_id: UUID = Path(..., description="Patient ID")
):
    """
    Delete patient
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        patient_id: Patient UUID
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
        
        # Return 204 No Content (successful deletion)
        return None
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient {patient_id} not found"
            )
        elif "active episodes" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete patient with active episodes"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete patient: {error_message}"
            )


@router.get("/{patient_id}/summary")
async def get_patient_summary(
    services: ServiceDep,
    current_user: CurrentUserDep,
    patient_id: UUID = Path(..., description="Patient ID")
):
    """
    Get comprehensive patient summary
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        patient_id: Patient UUID
        
    Returns:
        Patient summary with episodes, diagnoses, treatments
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("patient.read", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view patient summary"
        )
    
    try:
        # Get patient summary through service layer
        summary = services.patient.get_patient_summary(str(patient_id))
        return summary
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
                detail=f"Failed to get patient summary: {error_message}"
            )


@router.get("/{patient_id}/episodes")
async def get_patient_episodes(
    services: ServiceDep,
    current_user: CurrentUserDep,
    patient_id: UUID = Path(..., description="Patient ID"),
    status: Optional[str] = Query(None, description="Filter by episode status")
):
    """
    Get all episodes for a patient
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        patient_id: Patient UUID
        status: Episode status filter
        
    Returns:
        List of patient episodes
    """
    # Authorization check
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        # Get episodes through episode service
        episodes = services.episode.get_episodes_by_patient(
            patient_id=str(patient_id),
            status=status
        )
        
        return episodes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get patient episodes: {str(e)}"
        )


@router.post("/{patient_id}/episodes", status_code=201)
async def create_patient_episode(
    episode_data: EpisodeCreate,
    services: ServiceDep,
    current_user: CurrentUserDep,
    patient_id: UUID = Path(..., description="Patient ID")
):
    """
    Create new episode for patient
    
    Args:
        episode_data: Episode creation data
        services: Injected services
        current_user: Current authenticated user
        patient_id: Patient UUID
        
    Returns:
        Created episode data
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("episode.create", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create episodes"
        )
    
    try:
        # Verify patient exists first
        services.patient.get_patient(str(patient_id))  # Will raise if not found
        
        # Ensure patient_id is set correctly in episode data
        episode_data.patient_id = patient_id
        
        # Create episode through service layer
        episode = services.episode.create_episode(
            episode_data=episode_data,
            created_by=current_user["user_id"]
        )
        
        return episode
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
                detail=f"Failed to create episode: {error_message}"
            )


# =============================================================================
# Patient Search and Filtering
# =============================================================================

@router.get("/search/by-mrn/{mrn}")
async def get_patient_by_mrn(
    services: ServiceDep,
    current_user: CurrentUserDep,
    mrn: str = Path(..., description="Medical Record Number")
):
    """
    Find patient by Medical Record Number
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        mrn: Medical Record Number
        
    Returns:
        Patient data if found
    """
    # Authorization check
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        # Search by MRN through service layer
        patient = services.patient.get_patient_by_mrn(mrn)
        return patient
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with MRN {mrn} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to search patient: {error_message}"
            )


@router.get("/search/by-email/{email}")
async def get_patient_by_email(
    services: ServiceDep,
    current_user: CurrentUserDep,
    email: str = Path(..., description="Email address")
):
    """
    Find patient by email address
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        email: Email address
        
    Returns:
        Patient data if found
    """
    # Authorization check
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        # Search by email through service layer
        patient = services.patient.get_patient_by_email(email)
        return patient
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with email {email} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to search patient: {error_message}"
            )


# Export router
__all__ = ["router"]