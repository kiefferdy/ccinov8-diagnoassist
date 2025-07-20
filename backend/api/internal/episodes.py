from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from services.clinical_service import ClinicalService
from schemas.episode import EpisodeCreate, EpisodeUpdate, EpisodeResponse, EpisodeSummary
from api.dependencies import get_clinical_service, get_current_user_optional
from api.exceptions import EpisodeNotFoundException, PatientNotFoundException

router = APIRouter(prefix="/episodes")

@router.post("/", response_model=EpisodeResponse, summary="Create Episode")
async def create_episode(
    episode_data: EpisodeCreate,
    clinical_service: ClinicalService = Depends(get_clinical_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Create a new medical episode for a patient.
    """
    try:
        created_episode = await clinical_service.create_episode(episode_data)
        return created_episode
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{episode_id}", response_model=EpisodeResponse, summary="Get Episode")
async def get_episode(
    episode_id: str,
    clinical_service: ClinicalService = Depends(get_clinical_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Get episode by ID.
    """
    try:
        episode = await clinical_service.get_episode(episode_id)
        if not episode:
            raise EpisodeNotFoundException(episode_id)
        return episode
    except EpisodeNotFoundException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{episode_id}", response_model=EpisodeResponse, summary="Update Episode")
async def update_episode(
    episode_id: str,
    episode_data: EpisodeUpdate,
    clinical_service: ClinicalService = Depends(get_clinical_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Update existing episode.
    """
    try:
        updated_episode = await clinical_service.update_episode(episode_id, episode_data)
        if not updated_episode:
            raise EpisodeNotFoundException(episode_id)
        return updated_episode
    except EpisodeNotFoundException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/patient/{patient_id}", response_model=List[EpisodeResponse])
async def get_patient_episodes(
    patient_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    clinical_service: ClinicalService = Depends(get_clinical_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Get all episodes for a specific patient.
    """
    try:
        episodes = await clinical_service.get_patient_episodes(
            patient_id=patient_id,
            skip=skip,
            limit=limit
        )
        return episodes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{episode_id}/summary", response_model=EpisodeSummary)
async def get_episode_summary(
    episode_id: str,
    clinical_service: ClinicalService = Depends(get_clinical_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Get comprehensive episode summary including all related data.
    """
    try:
        summary = await clinical_service.get_episode_summary(episode_id)
        if not summary:
            raise EpisodeNotFoundException(episode_id)
        return summary
    except EpisodeNotFoundException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))