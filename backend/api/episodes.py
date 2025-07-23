"""
Episode API Router for DiagnoAssist - CLEAN VERSION
CRUD operations for episode management
"""

from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from typing import List, Optional
from uuid import UUID

# Import dependencies - FIXED: Import directly from the module
from api.dependencies import get_service_manager, get_current_user, PaginationParams


# Import schemas
from schemas.episode import (
    EpisodeCreate,
    EpisodeUpdate,
    EpisodeResponse,
    EpisodeListResponse,
    VitalSigns
)
from schemas.common import StatusResponse

# Create router
router = APIRouter(prefix="/episodes", tags=["episodes"])

# Create dependency aliases properly
ServiceDep = Depends(get_service_manager)
CurrentUserDep = Depends(get_current_user)
PaginationDep = Depends(PaginationParams)

# =============================================================================
# Episode CRUD Operations
# =============================================================================

@router.post("/", response_model=EpisodeResponse, status_code=201)
async def create_episode(
    episode_data: EpisodeCreate,
    services = ServiceDep,
    current_user = CurrentUserDep
):
    """
    Create a new episode
    
    Args:
        episode_data: Episode creation data
        services: Injected services
        current_user: Current authenticated user
        
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
        # Create episode through service layer
        episode = services.episode.create_episode(episode_data)
        return episode
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
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
                detail=f"Failed to create episode: {error_message}"
            )


@router.get("/", response_model=EpisodeListResponse)
async def get_episodes(
    services = ServiceDep,
    current_user = CurrentUserDep,
    pagination = PaginationDep,
    patient_id: Optional[UUID] = Query(None, description="Filter by patient ID"),
    status_filter: Optional[str] = Query(None, description="Filter by episode status"),
    encounter_type: Optional[str] = Query(None, description="Filter by encounter type"),
    priority: Optional[str] = Query(None, description="Filter by priority")
):
    """
    Get paginated list of episodes
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        pagination: Pagination parameters
        patient_id: Patient ID filter
        status_filter: Episode status filter
        encounter_type: Encounter type filter
        priority: Priority filter
        
    Returns:
        Paginated list of episodes
    """
    # Authorization check
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        # Get episodes through service layer
        episodes = services.episode.get_episodes(
            pagination=pagination,
            patient_id=str(patient_id) if patient_id else None,
            status=status_filter,
            encounter_type=encounter_type,
            priority=priority
        )
        
        return episodes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve episodes: {str(e)}"
        )


@router.get("/{episode_id}", response_model=EpisodeResponse)
async def get_episode(
    services = ServiceDep,
    current_user = CurrentUserDep,
    episode_id: UUID = Path(..., description="Episode ID")
):
    """
    Get episode by ID
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        episode_id: Episode UUID
        
    Returns:
        Episode data
    """
    # Authorization check
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        # Get episode through service layer
        episode = services.episode.get_episode(str(episode_id))
        return episode
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Episode {episode_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve episode: {error_message}"
            )


@router.put("/{episode_id}", response_model=EpisodeResponse)
async def update_episode(
    episode_data: EpisodeUpdate,
    services = ServiceDep,
    current_user = CurrentUserDep,
    episode_id: UUID = Path(..., description="Episode ID")
):
    """
    Update episode information
    
    Args:
        episode_data: Episode update data
        services: Injected services
        current_user: Current authenticated user
        episode_id: Episode UUID
        
    Returns:
        Updated episode data
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("episode.update", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update episodes"
        )
    
    try:
        # Update episode through service layer
        updated_episode = services.episode.update_episode(
            episode_id=str(episode_id),
            episode_data=episode_data,
            updated_by=current_user["user_id"]
        )
        
        return updated_episode
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Episode {episode_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update episode: {error_message}"
            )


@router.delete("/{episode_id}", response_model=StatusResponse)
async def delete_episode(
    services = ServiceDep,
    current_user = CurrentUserDep,
    episode_id: UUID = Path(..., description="Episode ID")
):
    """
    Delete episode (soft delete)
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        episode_id: Episode UUID
        
    Returns:
        Success status
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("episode.delete", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete episodes"
        )
    
    try:
        # Delete episode through service layer
        services.episode.delete_episode(
            episode_id=str(episode_id),
            deleted_by=current_user["user_id"]
        )
        
        return StatusResponse(
            status="success",
            message=f"Episode {episode_id} deleted successfully"
        )
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Episode {episode_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete episode: {error_message}"
            )


# =============================================================================
# Episode-specific operations
# =============================================================================

@router.get("/{episode_id}/summary")
async def get_episode_summary(
    services = ServiceDep,
    current_user = CurrentUserDep,
    episode_id: UUID = Path(..., description="Episode ID")
):
    """
    Get episode summary with related diagnoses and treatments
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        episode_id: Episode UUID
        
    Returns:
        Episode summary with related data
    """
    # Authorization check
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        # Get episode summary through service layer
        summary = services.episode.get_episode_summary(str(episode_id))
        return summary
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Episode {episode_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve episode summary: {error_message}"
            )


@router.post("/{episode_id}/close", response_model=EpisodeResponse)
async def close_episode(
    services = ServiceDep,
    current_user = CurrentUserDep,
    episode_id: UUID = Path(..., description="Episode ID")
):
    """
    Close an episode
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        episode_id: Episode UUID
        
    Returns:
        Closed episode data
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("episode.update", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to close episodes"
        )
    
    try:
        # Close episode through service layer
        closed_episode = services.episode.close_episode(
            episode_id=str(episode_id),
            closed_by=current_user["user_id"]
        )
        
        return closed_episode
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Episode {episode_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to close episode: {error_message}"
            )

# Export router
__all__ = ["router"]