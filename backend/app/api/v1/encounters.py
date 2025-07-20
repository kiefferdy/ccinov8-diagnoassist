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

# Import service
from app.services.encounter_service import encounter_service


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
    
    # Get filtered encounters from repository (keeping direct access for general listing)
    from app.repositories.encounter_repository import encounter_repository
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
async def create_encounter(
    request: EncounterCreateRequest,
    current_user: CurrentUser = Depends(require_encounter_write)
):
    """Create a new encounter"""
    
    try:
        # Create new encounter
        new_encounter = EncounterModel(
            episode_id=request.episode_id,
            patient_id=request.patient_id,
            type=request.type,
            provider=request.provider,
            soap=SOAPModel(),  # Initialize empty SOAP
            workflow=WorkflowInfo(last_saved=datetime.utcnow())
        )
        
        # Use service to create encounter with validation
        created_encounter = await encounter_service.create_encounter(new_encounter)
        
        return EncounterResponse(data=created_encounter)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except ValidationException as e:
        raise HTTPException(
            status_code=422,
            detail=str(e)
        )


@router.get("/{encounter_id}", response_model=EncounterResponse)
async def get_encounter(
    encounter_id: str,
    current_user: CurrentUser = Depends(require_encounter_read)
):
    """Get an encounter by ID"""
    
    try:
        encounter = await encounter_service.get_encounter_with_validation(encounter_id)
        return EncounterResponse(data=encounter)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.put("/{encounter_id}", response_model=EncounterResponse)
async def update_encounter(
    encounter_id: str, 
    request: EncounterUpdateRequest,
    current_user: CurrentUser = Depends(require_encounter_update)
):
    """Update an existing encounter"""
    
    try:
        # Get encounter first
        encounter = await encounter_service.get_encounter_with_validation(encounter_id)
        
        # Update encounter data
        if request.type is not None:
            encounter.type = request.type
        
        if request.status is not None:
            encounter.status = request.status
        
        if request.provider is not None:
            encounter.provider = request.provider
        
        encounter.updated_at = datetime.utcnow()
        encounter.workflow.last_saved = datetime.utcnow()
        
        # Use service to update with validation
        updated_encounter = await encounter_service.update_encounter(encounter_id, encounter)
        
        return EncounterResponse(data=updated_encounter)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except ValidationException as e:
        raise HTTPException(
            status_code=422,
            detail=str(e)
        )


@router.post("/{encounter_id}/sign", response_model=EncounterResponse)
async def sign_encounter(
    encounter_id: str, 
    request: EncounterSignRequest,
    current_user: CurrentUser = Depends(require_encounter_sign),
):
    """Sign an encounter and trigger FHIR synchronization"""
    
    try:
        # Use service to sign encounter (includes FHIR sync)
        signed_encounter = await encounter_service.sign_encounter(
            encounter_id=encounter_id,
            signed_by=current_user.id,
            notes=getattr(request, 'notes', None)
        )
        
        return EncounterResponse(data=signed_encounter)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except ValidationException as e:
        raise HTTPException(
            status_code=422,
            detail=str(e)
        )


@router.get("/episodes/{episode_id}/encounters", response_model=EncounterListResponse)
async def get_episode_encounters(
    episode_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    status: Optional[EncounterStatusEnum] = Query(None),
    current_user: CurrentUser = Depends(require_encounter_read)
):
    """Get all encounters for a specific episode"""
    
    try:
        # Calculate skip for pagination
        skip = (page - 1) * per_page
        
        # Use service to get episode encounters with validation
        encounters = await encounter_service.get_episode_encounters(
            episode_id=episode_id,
            status=status,
            skip=skip,
            limit=per_page
        )
        
        # Get total count for pagination
        from app.repositories.encounter_repository import encounter_repository
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
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.put("/{encounter_id}/soap", response_model=EncounterResponse)
async def update_encounter_soap(
    encounter_id: str, 
    soap_data: SOAPModel,
    current_user: CurrentUser = Depends(require_encounter_update)
):
    """Update SOAP documentation for an encounter"""
    
    try:
        # Use service to update SOAP with validation
        updated_encounter = await encounter_service.update_soap(encounter_id, soap_data)
        
        return EncounterResponse(data=updated_encounter)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except ValidationException as e:
        raise HTTPException(
            status_code=422,
            detail=str(e)
        )


@router.delete("/{encounter_id}")
async def delete_encounter(
    encounter_id: str,
    current_user: CurrentUser = Depends(require_encounter_delete)
):
    """Delete an encounter (only if not signed)"""
    
    try:
        # Use service to delete encounter with validation
        success = await encounter_service.delete_encounter(encounter_id)
        
        return {
            "success": True,
            "message": f"Encounter {encounter_id} deleted successfully",
            "timestamp": datetime.utcnow()
        }
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except ValidationException as e:
        raise HTTPException(
            status_code=422,
            detail=str(e)
        )


@router.get("/{encounter_id}/validate")
async def validate_encounter_completeness(
    encounter_id: str,
    current_user: CurrentUser = Depends(require_encounter_read)
):
    """Validate encounter documentation completeness"""
    
    try:
        validation_result = await encounter_service.validate_encounter_completeness(encounter_id)
        
        return {
            "success": True,
            "data": validation_result,
            "timestamp": datetime.utcnow()
        }
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.post("/{encounter_id}/cancel")
async def cancel_encounter(
    encounter_id: str,
    reason: str,
    current_user: CurrentUser = Depends(require_encounter_update)
):
    """Cancel an encounter"""
    
    try:
        cancelled_encounter = await encounter_service.cancel_encounter(
            encounter_id=encounter_id,
            reason=reason,
            cancelled_by=current_user.id
        )
        
        return EncounterResponse(data=cancelled_encounter)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except ValidationException as e:
        raise HTTPException(
            status_code=422,
            detail=str(e)
        )


@router.get("/statistics")
async def get_encounter_statistics(current_user: CurrentUser = Depends(require_encounter_read)):
    """Get encounter statistics"""
    
    try:
        stats = await encounter_service.get_encounter_statistics()
        
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get encounter statistics: {str(e)}"
        )