"""
Episode API Router for DiagnoAssist
CRUD operations for episode management
"""

from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from typing import List, Optional
from uuid import UUID

# Import individual service dependencies
from api.dependencies import (
    EpisodeServiceDep,
    CurrentUserDep, 
    PaginationDep
)

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

# =============================================================================
# Episode CRUD Operations
# =============================================================================

@router.post("/", response_model=EpisodeResponse, status_code=201)
async def create_episode(
    episode_data: EpisodeCreate,
    episode_service: EpisodeServiceDep,
    current_user: CurrentUserDep
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
    # Authorization check (commented out for MVP)
    # if not current_user or not current_user.get("permissions", {}).get("episode.create", False):
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Insufficient permissions to create episodes"
    #     )
    
    try:
        # Create episode through service layer
        episode = episode_service.create_episode(episode_data)
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
    episode_service: EpisodeServiceDep,
    current_user: CurrentUserDep,
    pagination: PaginationDep,
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
    # Authorization check (commented out for MVP)
    # if not current_user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Authentication required",
    #         headers={"WWW-Authenticate": "Bearer"}
    #     )
    
    try:
        # Get episodes through service layer
        episodes = episode_service.get_episodes(
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
    episode_service: EpisodeServiceDep,
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
        Episode data
    """
    # Authorization check (commented out for MVP)
    # if not current_user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Authentication required",
    #         headers={"WWW-Authenticate": "Bearer"}
    #     )
    
    try:
        # Get episode through service layer
        episode = episode_service.get_episode(str(episode_id))
        
        if not episode:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Episode with ID {episode_id} not found"
            )
        
        return episode
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve episode: {str(e)}"
        )

@router.put("/{episode_id}", response_model=EpisodeResponse)
async def update_episode(
    episode_service: EpisodeServiceDep,
    current_user: CurrentUserDep,
    episode_id: UUID = Path(..., description="Episode ID"),
    episode_data: EpisodeUpdate = ...
):
    """
    Update episode
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        episode_id: Episode UUID
        episode_data: Episode update data
        
    Returns:
        Updated episode data
    """
    # Authorization check (commented out for MVP)
    # if not current_user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Authentication required",
    #         headers={"WWW-Authenticate": "Bearer"}
    #     )
    
    try:
        # Update episode through service layer
        episode = episode_service.update_episode(str(episode_id), episode_data)
        
        if not episode:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Episode with ID {episode_id} not found"
            )
        
        return episode
    except HTTPException:
        raise
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Episode with ID {episode_id} not found"
            )
        elif "validation" in error_message.lower() or "invalid" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error_message
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update episode: {error_message}"
            )

@router.delete("/{episode_id}", response_model=StatusResponse)
async def delete_episode(
    episode_service: EpisodeServiceDep,
    current_user: CurrentUserDep,
    episode_id: UUID = Path(..., description="Episode ID")
):
    """
    Delete episode
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        episode_id: Episode UUID
        
    Returns:
        Status response
    """
    # Authorization check (commented out for MVP)
    # if not current_user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Authentication required",
    #         headers={"WWW-Authenticate": "Bearer"}
    #     )
    
    try:
        # Delete episode through service layer
        result = episode_service.delete_episode(str(episode_id))
        return result
    except HTTPException:
        raise
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Episode with ID {episode_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete episode: {error_message}"
            )

# =============================================================================
# Episode-specific endpoints
# =============================================================================

@router.patch("/{episode_id}/complete", response_model=EpisodeResponse)
async def complete_episode(
    episode_service: EpisodeServiceDep,
    current_user: CurrentUserDep,
    episode_id: UUID = Path(..., description="Episode ID"),
    completion_notes: Optional[str] = Query(None, description="Completion notes")
):
    """
    Complete an episode
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        episode_id: Episode UUID
        completion_notes: Optional completion notes
        
    Returns:
        Updated episode data
    """
    try:
        # Complete episode through service layer
        episode = episode_service.complete_episode(str(episode_id), completion_notes)
        return episode
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Episode with ID {episode_id} not found"
            )
        elif "cannot complete" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to complete episode: {error_message}"
            )

@router.get("/{episode_id}/timeline")
async def get_episode_timeline(
    episode_service: EpisodeServiceDep,
    current_user: CurrentUserDep,
    episode_id: UUID = Path(..., description="Episode ID")
):
    """
    Get episode timeline with diagnoses and treatments
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        episode_id: Episode UUID
        
    Returns:
        Episode timeline data
    """
    try:
        # Get episode timeline through service layer
        timeline = episode_service.get_episode_timeline(str(episode_id))
        return timeline
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Episode with ID {episode_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve episode timeline: {error_message}"
            )

@router.patch("/{episode_id}/vitals", response_model=EpisodeResponse)
async def update_episode_vitals(
    episode_service: EpisodeServiceDep,
    current_user: CurrentUserDep,
    episode_id: UUID = Path(..., description="Episode ID"),
    vitals: VitalSigns = ...
):
    """
    Update episode vital signs
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        episode_id: Episode UUID
        vitals: Vital signs data
        
    Returns:
        Updated episode data
    """
    try:
        # Update episode vitals through service layer
        episode = episode_service.update_episode_vitals(str(episode_id), vitals)
        return episode
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Episode with ID {episode_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update episode vitals: {error_message}"
            )