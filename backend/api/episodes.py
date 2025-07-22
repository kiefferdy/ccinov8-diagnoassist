"""
Episode API Router for DiagnoAssist
CRUD operations for clinical episode management with exception handling
"""

from fastapi import APIRouter, Depends, Query, Path
from typing import List, Optional
from uuid import UUID

# Import dependencies
from api.dependencies import ServiceDep, CurrentUserDep, PaginationDep

# Import schemas
from schemas.episode import (
    EpisodeCreate,
    EpisodeUpdate,
    EpisodeResponse,
    EpisodeListResponse,
    VitalSigns,
    PhysicalExamFindings
)
from schemas.common import StatusResponse
from schemas.clinical_data import ClinicalNoteCreate
from schemas.clinical_data import ClinicalNoteCreate

# Import exceptions - using the global exception system
from exceptions import (
    ValidationException,
    ResourceNotFoundException,
    BusinessRuleException,
    PatientSafetyException,
    ClinicalDataException,
    AuthenticationException,
    AuthorizationException
)

# Create router
router = APIRouter(prefix="/episodes", tags=["episodes"])


# =============================================================================
# Episode CRUD Operations
# =============================================================================

@router.post("/", response_model=EpisodeResponse, status_code=201)
async def create_episode(
    episode_data: EpisodeCreate,
    services: ServiceDep,
    current_user: CurrentUserDep
):
    """
    Create a new clinical episode
    
    Args:
        episode_data: Episode creation data
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Created episode data
        
    Raises:
        ValidationException: Invalid episode data
        ResourceNotFoundException: Patient not found
        BusinessRuleException: Business rule violation
        ClinicalDataException: Clinical data validation error
        AuthorizationException: User lacks permission
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("episode.create", False):
        raise AuthorizationException(
            message="Insufficient permissions to create episodes",
            required_permission="episode.create"
        )
    
    # Create episode through service layer
    episode = services.episode.create_episode(
        episode_data=episode_data,
        created_by=current_user["user_id"]
    )
    
    return episode


@router.get("/{episode_id}", response_model=EpisodeResponse)
async def get_episode(
    episode_id: UUID = Path(..., description="Episode ID"),
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Get episode by ID
    
    Args:
        episode_id: Episode UUID
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Episode data with related information
        
    Raises:
        ResourceNotFoundException: Episode not found
        AuthorizationException: User lacks permission
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("episode.read", False):
        raise AuthorizationException(
            message="Insufficient permissions to view episodes",
            required_permission="episode.read"
        )
    
    # Get episode through service layer
    episode = services.episode.get_episode(str(episode_id))
    
    return episode


@router.get("/", response_model=List[EpisodeListResponse])
async def list_episodes(
    patient_id: Optional[UUID] = Query(None, description="Filter by patient ID"),
    status: Optional[str] = Query(None, description="Filter by episode status"),
    encounter_type: Optional[str] = Query(None, description="Filter by encounter type"),
    provider_id: Optional[str] = Query(None, description="Filter by provider"),
    pagination: PaginationDep = Depends(),
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    List episodes with filtering options
    
    Args:
        patient_id: Filter by patient
        status: Filter by status
        encounter_type: Filter by encounter type
        provider_id: Filter by provider
        pagination: Pagination parameters
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        List of episodes
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("episode.read", False):
        raise AuthorizationException(
            message="Insufficient permissions to list episodes",
            required_permission="episode.read"
        )
    
    # Get episodes through service layer
    episodes = services.episode.search_episodes(
        patient_id=str(patient_id) if patient_id else None,
        status=status,
        encounter_type=encounter_type,
        provider_id=provider_id,
        offset=pagination.offset,
        limit=pagination.limit
    )
    
    return episodes


@router.put("/{episode_id}", response_model=EpisodeResponse)
async def update_episode(
    episode_id: UUID = Path(..., description="Episode ID"),
    episode_data: EpisodeUpdate = ...,
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Update episode information
    
    Args:
        episode_id: Episode UUID
        episode_data: Updated episode data
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Updated episode data
        
    Raises:
        ResourceNotFoundException: Episode not found
        ValidationException: Invalid update data
        ClinicalDataException: Clinical validation error
        PatientSafetyException: Safety rule violation
        AuthorizationException: User lacks permission
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("episode.update", False):
        raise AuthorizationException(
            message="Insufficient permissions to update episodes",
            required_permission="episode.update"
        )
    
    # Update episode through service layer
    episode = services.episode.update_episode(
        episode_id=str(episode_id),
        episode_data=episode_data,
        updated_by=current_user["user_id"]
    )
    
    return episode


@router.delete("/{episode_id}", response_model=StatusResponse)
async def delete_episode(
    episode_id: UUID = Path(..., description="Episode ID"),
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Delete episode (soft delete)
    
    Args:
        episode_id: Episode UUID
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Deletion status
        
    Raises:
        ResourceNotFoundException: Episode not found
        PatientSafetyException: Episode has active treatments
        AuthorizationException: User lacks permission
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("episode.delete", False):
        raise AuthorizationException(
            message="Insufficient permissions to delete episodes",
            required_permission="episode.delete"
        )
    
    # Delete episode through service layer
    services.episode.delete_episode(
        episode_id=str(episode_id),
        deleted_by=current_user["user_id"]
    )
    
    return StatusResponse(
        status="success",
        message=f"Episode {episode_id} deleted successfully"
    )


# =============================================================================
# Episode Clinical Operations
# =============================================================================

@router.get("/{episode_id}/timeline")
async def get_episode_timeline(
    episode_id: UUID = Path(..., description="Episode ID"),
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Get complete clinical timeline for episode
    
    Args:
        episode_id: Episode UUID
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Episode timeline with diagnoses and treatments
    """
    # Authorization check
    if not current_user:
        raise AuthenticationException(message="Authentication required")
    
    # Get timeline through service layer
    timeline = services.episode.get_episode_timeline(str(episode_id))
    
    return timeline


@router.get("/{episode_id}/summary")
async def get_episode_summary(
    episode_id: UUID = Path(..., description="Episode ID"),
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Get episode summary with clinical insights
    
    Args:
        episode_id: Episode UUID
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Episode summary with insights
    """
    # Authorization check
    if not current_user:
        raise AuthenticationException(message="Authentication required")
    
    # Get summary through clinical service
    summary = services.clinical.get_episode_summary(str(episode_id))
    
    return summary


@router.post("/{episode_id}/start", response_model=EpisodeResponse)
async def start_episode(
    episode_id: UUID = Path(..., description="Episode ID"),
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Start an episode (change status to active)
    
    Args:
        episode_id: Episode UUID
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Updated episode data
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("episode.update", False):
        raise AuthorizationException(
            message="Insufficient permissions to start episodes",
            required_permission="episode.update"
        )
    
    # Start episode through service layer
    episode = services.episode.start_episode(
        episode_id=str(episode_id),
        started_by=current_user["user_id"]
    )
    
    return episode


@router.post("/{episode_id}/complete", response_model=EpisodeResponse)
async def complete_episode(
    episode_id: UUID = Path(..., description="Episode ID"),
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Complete an episode (change status to completed)
    
    Args:
        episode_id: Episode UUID
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Updated episode data
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("episode.update", False):
        raise AuthorizationException(
            message="Insufficient permissions to complete episodes",
            required_permission="episode.update"
        )
    
    # Complete episode through service layer
    episode = services.episode.complete_episode(
        episode_id=str(episode_id),
        completed_by=current_user["user_id"]
    )
    
    return episode


# =============================================================================
# Episode Vital Signs and Clinical Data
# =============================================================================

@router.put("/{episode_id}/vital-signs", response_model=EpisodeResponse)
async def update_vital_signs(
    episode_id: UUID = Path(..., description="Episode ID"),
    vital_signs: VitalSigns = ...,
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Update vital signs for episode
    
    Args:
        episode_id: Episode UUID
        vital_signs: Vital signs data
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Updated episode data
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("episode.update", False):
        raise AuthorizationException(
            message="Insufficient permissions to update vital signs",
            required_permission="episode.update"
        )
    
    # Update vital signs through service layer
    episode = services.episode.update_vital_signs(
        episode_id=str(episode_id),
        vital_signs=vital_signs,
        updated_by=current_user["user_id"]
    )
    
    return episode


@router.put("/{episode_id}/physical-exam", response_model=EpisodeResponse)
async def update_physical_exam(
    episode_id: UUID = Path(..., description="Episode ID"),
    physical_exam: PhysicalExamFindings = ...,
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Update physical examination findings for episode
    
    Args:
        episode_id: Episode UUID
        physical_exam: Physical exam findings
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Updated episode data
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("episode.update", False):
        raise AuthorizationException(
            message="Insufficient permissions to update physical exam",
            required_permission="episode.update"
        )
    
    # Update physical exam through service layer
    episode = services.episode.update_physical_exam(
        episode_id=str(episode_id),
        physical_exam=physical_exam,
        updated_by=current_user["user_id"]
    )
    
    return episode


@router.post("/{episode_id}/notes")
async def add_clinical_note(
    episode_id: UUID = Path(..., description="Episode ID"),
    note_data: ClinicalNoteCreate = ...,
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Add clinical note to episode
    
    Args:
        episode_id: Episode UUID
        note_data: Clinical note data
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Updated episode with note
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("episode.update", False):
        raise AuthorizationException(
            message="Insufficient permissions to add clinical notes",
            required_permission="episode.update"
        )
    
    # Add note through service layer
    episode = services.episode.add_clinical_note(
        episode_id=str(episode_id),
        note_data=note_data,
        author=current_user["user_id"]
    )
    
    return episode


# Export router
__all__ = ["router"]