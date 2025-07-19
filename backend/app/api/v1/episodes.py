"""
Episode API endpoints for DiagnoAssist Backend
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
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
from app.core.exceptions import NotFoundError, ValidationException

router = APIRouter()

# In-memory storage for Phase 1 (will be replaced with database in Phase 3)
episodes_storage: List[EpisodeModel] = []
episode_counter = 1


def generate_episode_id() -> str:
    """Generate a unique episode ID"""
    global episode_counter
    episode_id = f"E{episode_counter:03d}"
    episode_counter += 1
    return episode_id


@router.get("/", response_model=EpisodeListResponse)
async def get_episodes(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    patient_id: Optional[str] = Query(None),
    status: Optional[EpisodeStatusEnum] = Query(None),
    category: Optional[EpisodeCategoryEnum] = Query(None),
):
    """Get list of episodes with optional filtering and pagination"""
    
    # Apply filters
    filtered_episodes = episodes_storage
    
    if patient_id:
        filtered_episodes = [
            e for e in filtered_episodes 
            if e.patient_id == patient_id
        ]
    
    if status:
        filtered_episodes = [
            e for e in filtered_episodes 
            if e.status == status
        ]
    
    if category:
        filtered_episodes = [
            e for e in filtered_episodes 
            if e.category == category
        ]
    
    # Sort by created_at descending
    filtered_episodes.sort(key=lambda x: x.created_at or datetime.min, reverse=True)
    
    # Apply pagination
    total = len(filtered_episodes)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_episodes = filtered_episodes[start_idx:end_idx]
    
    return EpisodeListResponse(
        data=paginated_episodes,
        total=total,
        page=page,
        per_page=per_page
    )


@router.post("/", response_model=EpisodeResponse)
async def create_episode(request: EpisodeCreateRequest):
    """Create a new episode"""
    
    # TODO: Validate that patient_id exists (will be added in Phase 3 with database)
    
    # Create new episode
    now = datetime.utcnow()
    new_episode = EpisodeModel(
        id=generate_episode_id(),
        patient_id=request.patient_id,
        chief_complaint=request.chief_complaint,
        category=request.category,
        tags=request.tags or [],
        notes=request.notes,
        created_at=now,
        updated_at=now
    )
    
    # Store episode
    episodes_storage.append(new_episode)
    
    return EpisodeResponse(data=new_episode)


@router.get("/{episode_id}", response_model=EpisodeResponse)
async def get_episode(episode_id: str):
    """Get an episode by ID"""
    
    episode = next(
        (e for e in episodes_storage if e.id == episode_id),
        None
    )
    
    if not episode:
        raise NotFoundError("Episode", episode_id)
    
    return EpisodeResponse(data=episode)


@router.put("/{episode_id}", response_model=EpisodeResponse)
async def update_episode(episode_id: str, request: EpisodeUpdateRequest):
    """Update an existing episode"""
    
    # Find episode
    episode_index = next(
        (i for i, e in enumerate(episodes_storage) if e.id == episode_id),
        None
    )
    
    if episode_index is None:
        raise NotFoundError("Episode", episode_id)
    
    episode = episodes_storage[episode_index]
    
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
    
    # Update in storage
    episodes_storage[episode_index] = episode
    
    return EpisodeResponse(data=episode)


@router.patch("/{episode_id}/status", response_model=EpisodeResponse)
async def update_episode_status(episode_id: str, request: EpisodeStatusUpdateRequest):
    """Update episode status"""
    
    # Find episode
    episode_index = next(
        (i for i, e in enumerate(episodes_storage) if e.id == episode_id),
        None
    )
    
    if episode_index is None:
        raise NotFoundError("Episode", episode_id)
    
    episode = episodes_storage[episode_index]
    
    # Update status
    episode.status = request.status
    episode.updated_at = datetime.utcnow()
    
    if request.status == EpisodeStatusEnum.RESOLVED:
        episode.resolved_at = request.resolved_at or datetime.utcnow()
    else:
        episode.resolved_at = None
    
    if request.notes:
        episode.notes = request.notes
    
    # Update in storage
    episodes_storage[episode_index] = episode
    
    return EpisodeResponse(data=episode)


@router.get("/patients/{patient_id}/episodes", response_model=EpisodeListResponse)
async def get_patient_episodes(
    patient_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    status: Optional[EpisodeStatusEnum] = Query(None),
):
    """Get all episodes for a specific patient"""
    
    # Filter episodes by patient
    patient_episodes = [
        e for e in episodes_storage 
        if e.patient_id == patient_id
    ]
    
    # Apply status filter if provided
    if status:
        patient_episodes = [
            e for e in patient_episodes 
            if e.status == status
        ]
    
    # Sort by created_at descending
    patient_episodes.sort(key=lambda x: x.created_at or datetime.min, reverse=True)
    
    # Apply pagination
    total = len(patient_episodes)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_episodes = patient_episodes[start_idx:end_idx]
    
    return EpisodeListResponse(
        data=paginated_episodes,
        total=total,
        page=page,
        per_page=per_page
    )


@router.delete("/{episode_id}")
async def delete_episode(episode_id: str):
    """Delete an episode"""
    
    # Find episode
    episode_index = next(
        (i for i, e in enumerate(episodes_storage) if e.id == episode_id),
        None
    )
    
    if episode_index is None:
        raise NotFoundError("Episode", episode_id)
    
    # Remove episode
    deleted_episode = episodes_storage.pop(episode_index)
    
    return {
        "success": True,
        "message": f"Episode {deleted_episode.id} deleted successfully",
        "timestamp": datetime.utcnow()
    }