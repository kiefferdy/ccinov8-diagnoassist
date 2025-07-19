"""
Episode API endpoints for DiagnoAssist Backend
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from datetime import datetime

from app.models.episode import (
    EpisodeModel,
    EpisodeCreateRequest,
    EpisodeUpdateRequest,
    EpisodeStatusUpdateRequest,
    EpisodeResponse,
    EpisodeListResponse,
    EpisodeCategoryEnum,
    EpisodeStatusEnum
)
from app.models.auth import CurrentUser
from app.middleware.auth_middleware import (
    require_episode_read, require_episode_write, 
    require_episode_update, require_episode_delete
)
from app.core.exceptions import NotFoundError, ValidationException

router = APIRouter()

# Import repository
from app.repositories.episode_repository import episode_repository


@router.get("/", response_model=EpisodeListResponse)
async def get_episodes(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    patient_id: Optional[str] = Query(None),
    status: Optional[EpisodeStatusEnum] = Query(None),
    category: Optional[EpisodeCategoryEnum] = Query(None),
    current_user: CurrentUser = Depends(require_episode_read),
):
    """Get list of episodes with optional filtering and pagination"""
    
    # Calculate skip for pagination
    skip = (page - 1) * per_page
    
    # Get filtered episodes from repository
    episodes = await episode_repository.get_by_filters(
        patient_id=patient_id,
        status=status,
        category=category,
        skip=skip,
        limit=per_page
    )
    
    # Get total count for pagination
    total = await episode_repository.count_by_filters(
        patient_id=patient_id,
        status=status,
        category=category
    )
    
    return EpisodeListResponse(
        data=episodes,
        total=total,
        page=page,
        per_page=per_page
    )


@router.post("/", response_model=EpisodeResponse)
async def create_episode(
    request: EpisodeCreateRequest,
    current_user: CurrentUser = Depends(require_episode_write),
):
    """Create a new episode"""
    
    # Create new episode
    new_episode = EpisodeModel(
        patient_id=request.patient_id,
        chief_complaint=request.chief_complaint,
        category=request.category,
        tags=request.tags or [],
        notes=request.notes
    )
    
    # Store episode in database
    created_episode = await episode_repository.create(new_episode)
    
    return EpisodeResponse(data=created_episode)


@router.get("/{episode_id}", response_model=EpisodeResponse)
async def get_episode(episode_id: str):
    """Get an episode by ID"""
    
    episode = await episode_repository.get_by_id(episode_id)
    
    if not episode:
        raise NotFoundError("Episode", episode_id)
    
    return EpisodeResponse(data=episode)


@router.put("/{episode_id}", response_model=EpisodeResponse)
async def update_episode(episode_id: str, request: EpisodeUpdateRequest):
    """Update an existing episode"""
    
    # Get episode
    episode = await episode_repository.get_by_id(episode_id)
    
    if not episode:
        raise NotFoundError("Episode", episode_id)
    
    # Update episode data
    if request.chief_complaint is not None:
        episode.chief_complaint = request.chief_complaint
    
    if request.category is not None:
        episode.category = request.category
    
    if request.status is not None:
        episode.status = request.status
        if request.status == EpisodeStatusEnum.RESOLVED:
            episode.resolved_at = datetime.utcnow()
        else:
            episode.resolved_at = None
    
    if request.tags is not None:
        episode.tags = request.tags
    
    if request.notes is not None:
        episode.notes = request.notes
    
    if request.related_episode_ids is not None:
        # Validate that episode doesn't reference itself
        if episode_id in request.related_episode_ids:
            raise ValidationException(
                "Episode cannot reference itself",
                {"episode_id": episode_id}
            )
        episode.related_episode_ids = request.related_episode_ids
    
    episode.updated_at = datetime.utcnow()
    
    # Update in database
    updated_episode = await episode_repository.update(episode_id, episode)
    
    return EpisodeResponse(data=updated_episode)


@router.patch("/{episode_id}/status", response_model=EpisodeResponse)
async def update_episode_status(episode_id: str, request: EpisodeStatusUpdateRequest):
    """Update episode status"""
    
    # Get episode
    episode = await episode_repository.get_by_id(episode_id)
    
    if not episode:
        raise NotFoundError("Episode", episode_id)
    
    # Update status
    episode.status = request.status
    episode.updated_at = datetime.utcnow()
    
    if request.status == EpisodeStatusEnum.RESOLVED:
        episode.resolved_at = request.resolved_at or datetime.utcnow()
    else:
        episode.resolved_at = None
    
    if request.notes:
        episode.notes = request.notes
    
    # Update in database
    updated_episode = await episode_repository.update(episode_id, episode)
    
    return EpisodeResponse(data=updated_episode)


@router.get("/patients/{patient_id}/episodes", response_model=EpisodeListResponse)
async def get_patient_episodes(
    patient_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    status: Optional[EpisodeStatusEnum] = Query(None),
):
    """Get all episodes for a specific patient"""
    
    # Calculate skip for pagination
    skip = (page - 1) * per_page
    
    # Get patient episodes from repository
    episodes = await episode_repository.get_by_patient(
        patient_id=patient_id,
        status=status,
        skip=skip,
        limit=per_page
    )
    
    # Get total count for pagination
    total = await episode_repository.count_by_patient(
        patient_id=patient_id,
        status=status
    )
    
    return EpisodeListResponse(
        data=episodes,
        total=total,
        page=page,
        per_page=per_page
    )


@router.delete("/{episode_id}")
async def delete_episode(episode_id: str):
    """Delete an episode"""
    
    # Get episode first to verify it exists
    episode = await episode_repository.get_by_id(episode_id)
    
    if not episode:
        raise NotFoundError("Episode", episode_id)
    
    # Delete episode
    await episode_repository.delete(episode_id)
    
    return {
        "success": True,
        "message": f"Episode {episode.id} deleted successfully",
        "timestamp": datetime.utcnow()
    }