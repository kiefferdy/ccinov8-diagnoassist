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
    services: ServiceDep,
    current_user: CurrentUserDep,
    episode_id: UUID = Path(..., description="Episode ID")
):
    """
    Get episode by ID
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        episode_id: Episode UUID
        
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
    services: ServiceDep,
    current_user: CurrentUserDep,
    pagination: PaginationDep,
    patient_id: Optional[UUID] = Query(None, description="Filter by patient ID"),
    status: Optional[str] = Query(None, description="Filter by episode status"),
    encounter_type: Optional[str] = Query(None, description="Filter by encounter type"),
    provider_id: Optional[str] = Query(None, description="Filter by provider")
):
    """
    List episodes with filtering options
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        pagination: Pagination parameters
        patient_id: Filter by patient
        status: Filter by status
        encounter_type: Filter by encounter type
        provider_id: Filter by provider
        
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
        limit=pagination.page_size
    )
    
    return episodes


@router.put("/{episode_id}", response_model=EpisodeResponse)
async def update_episode(
    episode_data: EpisodeUpdate,
    services: ServiceDep,
    current_user: CurrentUserDep,
    episode_id: UUID = Path(..., description="Episode ID")
):
    """
    Update episode information
    
    Args:
        episode_data: Updated episode data
        services: Injected services
        current_user: Current authenticated user
        episode_id: Episode UUID
        
    Returns:
        Updated episode data
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
    services: ServiceDep,
    current_user: CurrentUserDep,
    episode_id: UUID = Path(..., description="Episode ID")
):
    """
    Delete episode (soft delete)
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        episode_id: Episode UUID
        
    Returns:
        Deletion status
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
        success=True,
        message=f"Episode {episode_id} deleted successfully"
    )


# =============================================================================
# Episode Status Management
# =============================================================================

@router.post("/{episode_id}/start", response_model=EpisodeResponse)
async def start_episode(
    services: ServiceDep,
    current_user: CurrentUserDep,
    episode_id: UUID = Path(..., description="Episode ID")
):
    """
    Start an episode (change status to active)
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        episode_id: Episode UUID
        
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
    services: ServiceDep,
    current_user: CurrentUserDep,
    episode_id: UUID = Path(..., description="Episode ID")
):
    """
    Complete an episode (change status to completed)
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        episode_id: Episode UUID
        
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
    vital_signs: VitalSigns,
    services: ServiceDep,
    current_user: CurrentUserDep,
    episode_id: UUID = Path(..., description="Episode ID")
):
    """
    Update vital signs for episode
    
    Args:
        vital_signs: Vital signs data
        services: Injected services
        current_user: Current authenticated user
        episode_id: Episode UUID
        
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
    exam_findings: PhysicalExamFindings,
    services: ServiceDep,
    current_user: CurrentUserDep,
    episode_id: UUID = Path(..., description="Episode ID")
):
    """
    Update physical exam findings for episode
    
    Args:
        exam_findings: Physical exam findings
        services: Injected services
        current_user: Current authenticated user
        episode_id: Episode UUID
        
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
        exam_findings=exam_findings,
        updated_by=current_user["user_id"]
    )
    
    return episode


@router.post("/{episode_id}/notes", status_code=201)
async def add_clinical_note(
    note_data: ClinicalNoteCreate,
    services: ServiceDep,
    current_user: CurrentUserDep,
    episode_id: UUID = Path(..., description="Episode ID")
):
    """
    Add clinical note to episode
    
    Args:
        note_data: Clinical note data
        services: Injected services
        current_user: Current authenticated user
        episode_id: Episode UUID
        
    Returns:
        Created clinical note
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("episode.note", False):
        raise AuthorizationException(
            message="Insufficient permissions to add clinical notes",
            required_permission="episode.note"
        )
    
    # Add clinical note through service layer
    note = services.episode.add_clinical_note(
        episode_id=str(episode_id),
        note_data=note_data,
        created_by=current_user["user_id"]
    )
    
    return note


@router.get("/{episode_id}/notes")
async def get_clinical_notes(
    services: ServiceDep,
    current_user: CurrentUserDep,
    episode_id: UUID = Path(..., description="Episode ID"),
    note_type: Optional[str] = Query(None, description="Filter by note type")
):
    """
    Get clinical notes for episode
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        episode_id: Episode UUID
        note_type: Filter by note type
        
    Returns:
        List of clinical notes for the episode
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("episode.read", False):
        raise AuthorizationException(
            message="Insufficient permissions to view clinical notes",
            required_permission="episode.read"
        )
    
    # Get clinical notes through service layer
    notes = services.episode.get_clinical_notes(
        episode_id=str(episode_id),
        note_type=note_type
    )
    
    return notes


# =============================================================================
# Episode Summary and Analytics
# =============================================================================

@router.get("/{episode_id}/summary")
async def get_episode_summary(
    services: ServiceDep,
    current_user: CurrentUserDep,
    episode_id: UUID = Path(..., description="Episode ID")
):
    """
    Get comprehensive episode summary
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        episode_id: Episode UUID
        
    Returns:
        Episode summary with diagnoses, treatments, and outcomes
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("episode.read", False):
        raise AuthorizationException(
            message="Insufficient permissions to view episode summary",
            required_permission="episode.read"
        )
    
    # Get episode summary through service layer
    summary = services.episode.get_episode_summary(str(episode_id))
    
    return summary


@router.get("/{episode_id}/timeline")
async def get_episode_timeline(
    services: ServiceDep,
    current_user: CurrentUserDep,
    episode_id: UUID = Path(..., description="Episode ID")
):
    """
    Get episode timeline with chronological events
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        episode_id: Episode UUID
        
    Returns:
        Chronological timeline of episode events
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("episode.read", False):
        raise AuthorizationException(
            message="Insufficient permissions to view episode timeline",
            required_permission="episode.read"
        )
    
    # Get episode timeline through service layer
    timeline = services.episode.get_episode_timeline(str(episode_id))
    
    return timeline


# Export router
__all__ = ["router"]