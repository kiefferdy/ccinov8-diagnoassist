"""
Encounter API endpoints for DiagnoAssist Backend
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
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
from app.core.exceptions import NotFoundError, ValidationException

router = APIRouter()

# In-memory storage for Phase 1 (will be replaced with database in Phase 3)
encounters_storage: List[EncounterModel] = []
encounter_counter = 1


def generate_encounter_id() -> str:
    """Generate a unique encounter ID"""
    global encounter_counter
    encounter_id = f"ENC{encounter_counter:03d}"
    encounter_counter += 1
    return encounter_id


@router.get("/", response_model=EncounterListResponse)
async def get_encounters(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    patient_id: Optional[str] = Query(None),
    episode_id: Optional[str] = Query(None),
    status: Optional[EncounterStatusEnum] = Query(None),
    type: Optional[EncounterTypeEnum] = Query(None),
):
    """Get list of encounters with optional filtering and pagination"""
    
    # Apply filters
    filtered_encounters = encounters_storage
    
    if patient_id:
        filtered_encounters = [
            e for e in filtered_encounters 
            if e.patient_id == patient_id
        ]
    
    if episode_id:
        filtered_encounters = [
            e for e in filtered_encounters 
            if e.episode_id == episode_id
        ]
    
    if status:
        filtered_encounters = [
            e for e in filtered_encounters 
            if e.status == status
        ]
    
    if type:
        filtered_encounters = [
            e for e in filtered_encounters 
            if e.type == type
        ]
    
    # Sort by created_at descending
    filtered_encounters.sort(key=lambda x: x.created_at or datetime.min, reverse=True)
    
    # Apply pagination
    total = len(filtered_encounters)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_encounters = filtered_encounters[start_idx:end_idx]
    
    return EncounterListResponse(
        data=paginated_encounters,
        total=total,
        page=page,
        per_page=per_page
    )


@router.post("/", response_model=EncounterResponse)
async def create_encounter(request: EncounterCreateRequest):
    """Create a new encounter"""
    
    # TODO: Validate that patient_id and episode_id exist (will be added in Phase 3 with database)
    
    # Create new encounter
    now = datetime.utcnow()
    new_encounter = EncounterModel(
        id=generate_encounter_id(),
        episode_id=request.episode_id,
        patient_id=request.patient_id,
        type=request.type,
        provider=request.provider,
        soap=SOAPModel(),  # Initialize empty SOAP
        workflow=WorkflowInfo(last_saved=now),
        created_at=now,
        updated_at=now
    )
    
    # Store encounter
    encounters_storage.append(new_encounter)
    
    return EncounterResponse(data=new_encounter)


@router.get("/{encounter_id}", response_model=EncounterResponse)
async def get_encounter(encounter_id: str):
    """Get an encounter by ID"""
    
    encounter = next(
        (e for e in encounters_storage if e.id == encounter_id),
        None
    )
    
    if not encounter:
        raise NotFoundError("Encounter", encounter_id)
    
    return EncounterResponse(data=encounter)


@router.put("/{encounter_id}", response_model=EncounterResponse)
async def update_encounter(encounter_id: str, request: EncounterUpdateRequest):
    """Update an existing encounter"""
    
    # Find encounter
    encounter_index = next(
        (i for i, e in enumerate(encounters_storage) if e.id == encounter_id),
        None
    )
    
    if encounter_index is None:
        raise NotFoundError("Encounter", encounter_id)
    
    encounter = encounters_storage[encounter_index]
    
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
    
    # Update in storage
    encounters_storage[encounter_index] = encounter
    
    return EncounterResponse(data=encounter)


@router.post("/{encounter_id}/sign", response_model=EncounterResponse)
async def sign_encounter(encounter_id: str, request: EncounterSignRequest):
    """Sign an encounter"""
    
    # Find encounter
    encounter_index = next(
        (i for i, e in enumerate(encounters_storage) if e.id == encounter_id),
        None
    )
    
    if encounter_index is None:
        raise NotFoundError("Encounter", encounter_id)
    
    encounter = encounters_storage[encounter_index]
    
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
    
    # Update in storage
    encounters_storage[encounter_index] = encounter
    
    return EncounterResponse(data=encounter)


@router.get("/episodes/{episode_id}/encounters", response_model=EncounterListResponse)
async def get_episode_encounters(
    episode_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    status: Optional[EncounterStatusEnum] = Query(None),
):
    """Get all encounters for a specific episode"""
    
    # Filter encounters by episode
    episode_encounters = [
        e for e in encounters_storage 
        if e.episode_id == episode_id
    ]
    
    # Apply status filter if provided
    if status:
        episode_encounters = [
            e for e in episode_encounters 
            if e.status == status
        ]
    
    # Sort by created_at descending
    episode_encounters.sort(key=lambda x: x.created_at or datetime.min, reverse=True)
    
    # Apply pagination
    total = len(episode_encounters)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_encounters = episode_encounters[start_idx:end_idx]
    
    return EncounterListResponse(
        data=paginated_encounters,
        total=total,
        page=page,
        per_page=per_page
    )


@router.put("/{encounter_id}/soap", response_model=EncounterResponse)
async def update_encounter_soap(encounter_id: str, soap_data: SOAPModel):
    """Update SOAP documentation for an encounter"""
    
    # Find encounter
    encounter_index = next(
        (i for i, e in enumerate(encounters_storage) if e.id == encounter_id),
        None
    )
    
    if encounter_index is None:
        raise NotFoundError("Encounter", encounter_id)
    
    encounter = encounters_storage[encounter_index]
    
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
    
    # Update in storage
    encounters_storage[encounter_index] = encounter
    
    return EncounterResponse(data=encounter)


@router.delete("/{encounter_id}")
async def delete_encounter(encounter_id: str):
    """Delete an encounter (only if not signed)"""
    
    # Find encounter
    encounter_index = next(
        (i for i, e in enumerate(encounters_storage) if e.id == encounter_id),
        None
    )
    
    if encounter_index is None:
        raise NotFoundError("Encounter", encounter_id)
    
    encounter = encounters_storage[encounter_index]
    
    # Prevent deletion of signed encounters
    if encounter.status == EncounterStatusEnum.SIGNED:
        raise ValidationException(
            "Cannot delete a signed encounter",
            {"encounter_id": encounter_id, "status": encounter.status}
        )
    
    # Remove encounter
    deleted_encounter = encounters_storage.pop(encounter_index)
    
    return {
        "success": True,
        "message": f"Encounter {deleted_encounter.id} deleted successfully",
        "timestamp": datetime.utcnow()
    }