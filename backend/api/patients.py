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
            required_permission="patient.create",
            user_id=current_user.get("user_id") if current_user else None
        )
    
    # Create patient through service layer
    # Service will handle validation and business rules
    patient = services.patient.create_patient(
        patient_data=patient_data,
        created_by=current_user["user_id"]
    )
    
    return patient


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: UUID = Path(..., description="Patient ID"),
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Get patient by ID
    
    Args:
        patient_id: Patient UUID
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Patient data
        
    Raises:
        ResourceNotFoundException: Patient not found
        AuthorizationException: User lacks permission
    """
    # Authorization check - can read patients
    if not current_user or not current_user.get("permissions", {}).get("patient.read", False):
        raise AuthorizationException(
            message="Insufficient permissions to view patients",
            required_permission="patient.read"
        )
    
    # Get patient through service layer
    # Service will raise ResourceNotFoundException if not found
    patient = services.patient.get_patient(str(patient_id))
    
    return patient


@router.get("/", response_model=PaginatedResponse[PatientListResponse])
async def list_patients(
    pagination: PaginationDep = Depends(),
    search: Optional[str] = Query(None, description="Search by name, email, or MRN"),
    status: Optional[str] = Query(None, description="Filter by patient status"),
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    List patients with filtering and pagination
    
    Args:
        pagination: Pagination parameters
        search: Search query
        status: Status filter
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Paginated list of patients
        
    Raises:
        ValidationException: Invalid query parameters
        AuthorizationException: User lacks permission
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("patient.read", False):
        raise AuthorizationException(
            message="Insufficient permissions to list patients",
            required_permission="patient.read"
        )
    
    # Search patients through service layer
    result = services.patient.search_patients(
        search_query=search,
        status_filter=status,
        offset=pagination.offset,
        limit=pagination.limit
    )
    
    return result


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: UUID = Path(..., description="Patient ID"),
    patient_data: PatientUpdate = ...,
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Update patient information
    
    Args:
        patient_id: Patient UUID
        patient_data: Updated patient data
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Updated patient data
        
    Raises:
        ResourceNotFoundException: Patient not found
        ValidationException: Invalid update data
        BusinessRuleException: Business rule violation
        AuthorizationException: User lacks permission
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
    patient_id: UUID = Path(..., description="Patient ID"),
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Delete patient (soft delete)
    
    Args:
        patient_id: Patient UUID
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Deletion status
        
    Raises:
        ResourceNotFoundException: Patient not found
        PatientSafetyException: Patient has active episodes
        AuthorizationException: User lacks permission
    """
    # Authorization check - requires admin or delete permission
    if not current_user or not current_user.get("permissions", {}).get("patient.delete", False):
        raise AuthorizationException(
            message="Insufficient permissions to delete patients",
            required_permission="patient.delete"
        )
    
    # Delete patient through service layer
    # Service will check for active episodes and patient safety
    services.patient.delete_patient(
        patient_id=str(patient_id),
        deleted_by=current_user["user_id"]
    )
    
    return StatusResponse(
        status="success",
        message=f"Patient {patient_id} deleted successfully"
    )


# =============================================================================
# Patient Summary and Clinical Operations
# =============================================================================

@router.get("/{patient_id}/summary")
async def get_patient_summary(
    patient_id: UUID = Path(..., description="Patient ID"),
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Get comprehensive patient summary including episodes and conditions
    
    Args:
        patient_id: Patient UUID
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Patient summary with clinical data
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
    patient_id: UUID = Path(..., description="Patient ID"),
    status: Optional[str] = Query(None, description="Filter by episode status"),
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Get all episodes for a patient
    
    Args:
        patient_id: Patient UUID
        status: Episode status filter
        services: Injected services
        current_user: Current authenticated user
        
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
    patient_id: UUID = Path(..., description="Patient ID"),
    episode_data: EpisodeCreate = ...,
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Create new episode for patient
    
    Args:
        patient_id: Patient UUID
        episode_data: Episode creation data
        services: Injected services
        current_user: Current authenticated user
        
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
    mrn: str = Path(..., description="Medical Record Number"),
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Find patient by Medical Record Number
    
    Args:
        mrn: Medical Record Number
        services: Injected services
        current_user: Current authenticated user
        
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
    email: str = Path(..., description="Email address"),
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Find patient by email address
    
    Args:
        email: Email address
        services: Injected services
        current_user: Current authenticated user
        
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