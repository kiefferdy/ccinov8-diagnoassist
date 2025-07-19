"""
Encounter API endpoints for DiagnoAssist Backend
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from datetime import datetime

from app.models.encounter import (
    EncounterModel,
    EncounterCreateRequest,
    EncounterUpdateRequest,
    EncounterSignRequest,
    EncounterResponse,
    EncounterListResponse,
    EncounterTypeEnum,
    EncounterStatusEnum,
    WorkflowInfo
)
from app.models.soap import SOAPModel
from app.models.auth import CurrentUser
from app.middleware.auth_middleware import (
    require_encounter_read, require_encounter_write, 
    require_encounter_update, require_encounter_delete, require_encounter_sign
)
from app.core.exceptions import NotFoundError, ValidationException

router = APIRouter()

# Import repository
from app.repositories.encounter_repository import encounter_repository


@router.get("/", response_model=EncounterListResponse)
async def get_encounters(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    patient_id: Optional[str] = Query(None),
    episode_id: Optional[str] = Query(None),
    status: Optional[EncounterStatusEnum] = Query(None),
    type: Optional[EncounterTypeEnum] = Query(None),
    current_user: CurrentUser = Depends(require_encounter_read),
):
    """Get list of encounters with optional filtering and pagination"""
    
    # Calculate skip for pagination
    skip = (page - 1) * per_page
    
    # Get filtered encounters from repository
    encounters = await encounter_repository.get_by_filters(
        patient_id=patient_id,
        episode_id=episode_id,
        status=status,
        encounter_type=type,
        skip=skip,
        limit=per_page
    )
    
    # Get total count for pagination
    total = await encounter_repository.count_by_filters(
        patient_id=patient_id,
        episode_id=episode_id,
        status=status,
        encounter_type=type
    )
    
    return EncounterListResponse(
        data=encounters,
        total=total,
        page=page,
        per_page=per_page
    )


@router.post("/", response_model=EncounterResponse)
async def create_encounter(request: EncounterCreateRequest):
    """Create a new encounter"""
    
    # Create new encounter
    new_encounter = EncounterModel(
        episode_id=request.episode_id,
        patient_id=request.patient_id,
        type=request.type,
        provider=request.provider,
        soap=SOAPModel(),  # Initialize empty SOAP
        workflow=WorkflowInfo(last_saved=datetime.utcnow())
    )
    
    # Store encounter in database
    created_encounter = await encounter_repository.create(new_encounter)
    
    return EncounterResponse(data=created_encounter)


@router.get("/{encounter_id}", response_model=EncounterResponse)
async def get_encounter(encounter_id: str):
    """Get an encounter by ID"""
    
    encounter = await encounter_repository.get_by_id(encounter_id)
    
    if not encounter:
        raise NotFoundError("Encounter", encounter_id)
    
    return EncounterResponse(data=encounter)


@router.put("/{encounter_id}", response_model=EncounterResponse)
async def update_encounter(encounter_id: str, request: EncounterUpdateRequest):
    """Update an existing encounter"""
    
    # Get encounter
    encounter = await encounter_repository.get_by_id(encounter_id)
    
    if not encounter:
        raise NotFoundError("Encounter", encounter_id)
    
    # Check if encounter is signed (prevent modifications)
    if encounter.status == EncounterStatusEnum.SIGNED:
        raise ValidationException(
            "Cannot modify a signed encounter",
            {"encounter_id": encounter_id, "status": encounter.status}
        )
    
    # Update encounter data
    if request.type is not None:
        encounter.type = request.type
    
    if request.status is not None:
        encounter.status = request.status
    
    if request.provider is not None:
        encounter.provider = request.provider
    
    encounter.updated_at = datetime.utcnow()
    encounter.workflow.last_saved = datetime.utcnow()
    
    # Update in database
    updated_encounter = await encounter_repository.update(encounter_id, encounter)
    
    return EncounterResponse(data=updated_encounter)


@router.post("/{encounter_id}/sign", response_model=EncounterResponse)
async def sign_encounter(
    encounter_id: str, 
    request: EncounterSignRequest,
    current_user: CurrentUser = Depends(require_encounter_sign),
):
    """Sign an encounter"""
    
    # Get encounter
    encounter = await encounter_repository.get_by_id(encounter_id)
    
    if not encounter:
        raise NotFoundError("Encounter", encounter_id)
    
    # Validate encounter can be signed
    if encounter.status == EncounterStatusEnum.SIGNED:
        raise ValidationException(
            "Encounter is already signed",
            {"encounter_id": encounter_id}
        )
    
    if encounter.status == EncounterStatusEnum.CANCELLED:
        raise ValidationException(
            "Cannot sign a cancelled encounter",
            {"encounter_id": encounter_id}
        )
    
    # Sign the encounter
    now = datetime.utcnow()
    encounter.status = EncounterStatusEnum.SIGNED
    encounter.signed_at = now
    encounter.signed_by = encounter.provider.id
    encounter.updated_at = now
    encounter.workflow.last_saved = now
    encounter.workflow.signed_version = encounter.workflow.version
    
    # Update in database
    updated_encounter = await encounter_repository.update(encounter_id, encounter)
    
    return EncounterResponse(data=updated_encounter)


@router.get("/episodes/{episode_id}/encounters", response_model=EncounterListResponse)
async def get_episode_encounters(
    episode_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    status: Optional[EncounterStatusEnum] = Query(None),
):
    """Get all encounters for a specific episode"""
    
    # Calculate skip for pagination
    skip = (page - 1) * per_page
    
    # Get episode encounters from repository
    encounters = await encounter_repository.get_by_episode(
        episode_id=episode_id,
        status=status,
        skip=skip,
        limit=per_page
    )
    
    # Get total count for pagination
    total = await encounter_repository.count_by_episode(
        episode_id=episode_id,
        status=status
    )
    
    return EncounterListResponse(
        data=encounters,
        total=total,
        page=page,
        per_page=per_page
    )


@router.put("/{encounter_id}/soap", response_model=EncounterResponse)
async def update_encounter_soap(encounter_id: str, soap_data: SOAPModel):
    """Update SOAP documentation for an encounter"""
    
    # Get encounter
    encounter = await encounter_repository.get_by_id(encounter_id)
    
    if not encounter:
        raise NotFoundError("Encounter", encounter_id)
    
    # Check if encounter is signed (prevent modifications)
    if encounter.status == EncounterStatusEnum.SIGNED:
        raise ValidationException(
            "Cannot modify SOAP for a signed encounter",
            {"encounter_id": encounter_id, "status": encounter.status}
        )
    
    # Update SOAP data
    encounter.soap = soap_data
    encounter.updated_at = datetime.utcnow()
    encounter.workflow.last_saved = datetime.utcnow()
    encounter.workflow.version += 1
    
    # Auto-update status to in_progress if it was draft
    if encounter.status == EncounterStatusEnum.DRAFT:
        encounter.status = EncounterStatusEnum.IN_PROGRESS
    
    # Update in database
    updated_encounter = await encounter_repository.update(encounter_id, encounter)
    
    return EncounterResponse(data=updated_encounter)


@router.delete("/{encounter_id}")
async def delete_encounter(encounter_id: str):
    """Delete an encounter (only if not signed)"""
    
    # Get encounter first to verify it exists
    encounter = await encounter_repository.get_by_id(encounter_id)
    
    if not encounter:
        raise NotFoundError("Encounter", encounter_id)
    
    # Prevent deletion of signed encounters
    if encounter.status == EncounterStatusEnum.SIGNED:
        raise ValidationException(
            "Cannot delete a signed encounter",
            {"encounter_id": encounter_id, "status": encounter.status}
        )
    
    # Delete encounter
    await encounter_repository.delete(encounter_id)
    
    return {
        "success": True,
        "message": f"Encounter {encounter.id} deleted successfully",
        "timestamp": datetime.utcnow()
    }