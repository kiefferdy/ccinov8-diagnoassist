"""
Patient API Router for DiagnoAssist
CRUD operations for patient management with comprehensive exception handling
"""

from fastapi import APIRouter, Depends, Query, Path
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
from schemas.common import StatusResponse, PaginatedResponse

# Import exceptions - using the global exception system
from exceptions import (
    ValidationException,
    ResourceNotFoundException,
    ResourceConflictException,
    BusinessRuleException,
    PatientSafetyException,
    AuthenticationException,
    AuthorizationException
)

# Create router
router = APIRouter(prefix="/patients", tags=["patients"])


# =============================================================================
# Patient CRUD Operations
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
        ValidationException: Invalid patient data
        ResourceConflictException: Email/MRN already exists
        BusinessRuleException: Business rule violation
        AuthenticationException: User not authenticated
        AuthorizationException: User lacks permission
    """
    # Authorization check - can create patients
    if not current_user or not current_user.get("permissions", {}).get("patient.create", False):
        raise AuthorizationException(
            message="Insufficient permissions to create patients",
            required_permission="patient.create"
        )
    
    # Create patient through service layer
    patient = services.patient.create_patient(
        patient_data=patient_data,
        created_by=current_user["user_id"]
    )
    
    return patient


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
    # Authorization check
    if not current_user:
        raise AuthenticationException(message="Authentication required")
    
    # Get patients through service layer
    patients = services.patient.get_patients(
        pagination=pagination,
        search=search,
        status=status
    )
    
    return patients


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
        raise AuthenticationException(message="Authentication required")
    
    # Get patient through service layer
    patient = services.patient.get_patient(str(patient_id))
    
    return patient


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
        patient_data: Updated patient data
        services: Injected services
        current_user: Current authenticated user
        patient_id: Patient UUID
        
    Returns:
        Updated patient data
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("patient.update", False):
        raise AuthorizationException(
            message="Insufficient permissions to update patients",
            required_permission="patient.update"
        )
    
    # Update patient through service layer
    patient = services.patient.update_patient(
        patient_id=str(patient_id),
        patient_data=patient_data,
        updated_by=current_user["user_id"]
    )
    
    return patient


@router.delete("/{patient_id}", response_model=StatusResponse)
async def delete_patient(
    services: ServiceDep,
    current_user: CurrentUserDep,
    patient_id: UUID = Path(..., description="Patient ID")
):
    """
    Delete patient (soft delete)
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        patient_id: Patient UUID
        
    Returns:
        Deletion status
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("patient.delete", False):
        raise AuthorizationException(
            message="Insufficient permissions to delete patients",
            required_permission="patient.delete"
        )
    
    # Delete patient through service layer
    services.patient.delete_patient(
        patient_id=str(patient_id),
        deleted_by=current_user["user_id"]
    )
    
    return StatusResponse(
        success=True,
        message=f"Patient {patient_id} deleted successfully"
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
        raise AuthorizationException(
            message="Insufficient permissions to view patient summary",
            required_permission="patient.read"
        )
    
    # Get patient summary through service layer
    summary = services.patient.get_patient_summary(str(patient_id))
    
    return summary


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
        raise AuthenticationException(message="Authentication required")
    
    # Get episodes through episode service
    episodes = services.episode.get_episodes_by_patient(
        patient_id=str(patient_id),
        status=status
    )
    
    return episodes


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
        raise AuthorizationException(
            message="Insufficient permissions to create episodes",
            required_permission="episode.create"
        )
    
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
        raise AuthenticationException(message="Authentication required")
    
    # Search by MRN through service layer
    patient = services.patient.get_patient_by_mrn(mrn)
    
    return patient


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
        raise AuthenticationException(message="Authentication required")
    
    # Search by email through service layer
    patient = services.patient.get_patient_by_email(email)
    
    return patient


# Export router
__all__ = ["router"]