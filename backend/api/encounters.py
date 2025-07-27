"""
Encounter API Routes for DiagnoAssist
FastAPI endpoints for encounter management and SOAP documentation
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from uuid import UUID

from api.dependencies import get_encounter_service
from services.encounter_service import EncounterService
from schemas.encounter import (
    EncounterCreate,
    EncounterUpdate,
    EncounterResponse,
    EncounterListResponse,
    SOAPSectionUpdate,
    EncounterSignRequest,
    EncounterStats
)
from schemas.common import StatusResponse, PaginationParams
from api.dependencies import get_pagination

router = APIRouter(prefix="/encounters", tags=["encounters"])

@router.post("/", response_model=EncounterResponse, status_code=status.HTTP_201_CREATED)
async def create_encounter(
    encounter_data: EncounterCreate,
    service: EncounterService = Depends(get_encounter_service)
) -> EncounterResponse:
    """
    Create a new encounter
    
    Args:
        encounter_data: Encounter creation data
        service: Encounter service dependency
        
    Returns:
        Created encounter data
        
    Raises:
        HTTPException: If validation fails or encounter creation fails
    """
    try:
        return service.create_encounter(encounter_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create encounter: {str(e)}"
        )

@router.get("/{encounter_id}", response_model=EncounterResponse)
async def get_encounter(
    encounter_id: UUID,
    service: EncounterService = Depends(get_encounter_service)
) -> EncounterResponse:
    """
    Get encounter by ID
    
    Args:
        encounter_id: Encounter UUID
        service: Encounter service dependency
        
    Returns:
        Encounter data
        
    Raises:
        HTTPException: If encounter not found
    """
    try:
        return service.get_encounter(str(encounter_id))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve encounter: {str(e)}"
        )

@router.put("/{encounter_id}", response_model=EncounterResponse)
async def update_encounter(
    encounter_id: UUID,
    encounter_data: EncounterUpdate,
    service: EncounterService = Depends(get_encounter_service)
) -> EncounterResponse:
    """
    Update an existing encounter
    
    Args:
        encounter_id: Encounter UUID
        encounter_data: Updated encounter data
        service: Encounter service dependency
        
    Returns:
        Updated encounter data
        
    Raises:
        HTTPException: If encounter not found or update fails
    """
    try:
        return service.update_encounter(str(encounter_id), encounter_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update encounter: {str(e)}"
        )

@router.patch("/{encounter_id}/soap", response_model=EncounterResponse)
async def update_soap_section(
    encounter_id: UUID,
    section_update: SOAPSectionUpdate,
    service: EncounterService = Depends(get_encounter_service)
) -> EncounterResponse:
    """
    Update a specific SOAP section
    
    Args:
        encounter_id: Encounter UUID
        section_update: SOAP section update data
        service: Encounter service dependency
        
    Returns:
        Updated encounter data
        
    Raises:
        HTTPException: If encounter not found or update fails
    """
    try:
        return service.update_soap_section(str(encounter_id), section_update)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update SOAP section: {str(e)}"
        )

@router.post("/{encounter_id}/sign", response_model=EncounterResponse)
async def sign_encounter(
    encounter_id: UUID,
    sign_request: EncounterSignRequest,
    service: EncounterService = Depends(get_encounter_service)
) -> EncounterResponse:
    """
    Sign an encounter
    
    Args:
        encounter_id: Encounter UUID
        sign_request: Sign request data
        service: Encounter service dependency
        
    Returns:
        Signed encounter data
        
    Raises:
        HTTPException: If encounter not found or signing fails
    """
    try:
        return service.sign_encounter(str(encounter_id), sign_request.provider_name)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sign encounter: {str(e)}"
        )

@router.delete("/{encounter_id}", response_model=StatusResponse)
async def delete_encounter(
    encounter_id: UUID,
    service: EncounterService = Depends(get_encounter_service)
) -> StatusResponse:
    """
    Delete an encounter (only if not signed)
    
    Args:
        encounter_id: Encounter UUID
        service: Encounter service dependency
        
    Returns:
        Status response
        
    Raises:
        HTTPException: If encounter not found or deletion fails
    """
    try:
        result = service.delete_encounter(str(encounter_id))
        return StatusResponse(
            status=result["status"],
            message=result["message"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete encounter: {str(e)}"
        )

@router.get("/episode/{episode_id}", response_model=EncounterListResponse)
async def get_encounters_by_episode(
    episode_id: UUID,
    pagination: PaginationParams = Depends(get_pagination),
    service: EncounterService = Depends(get_encounter_service)
) -> EncounterListResponse:
    """
    Get encounters for a specific episode
    
    Args:
        episode_id: Episode UUID
        pagination: Pagination parameters
        service: Encounter service dependency
        
    Returns:
        List of encounters for the episode
        
    Raises:
        HTTPException: If episode not found
    """
    try:
        encounters = service.get_encounters_by_episode(
            str(episode_id), 
            skip=pagination.offset, 
            limit=pagination.size
        )
        
        # For simplicity, return total as length of encounters
        # In production, you'd want a separate count query
        total = len(encounters)
        
        return EncounterListResponse(
            data=encounters,
            total=total,
            page=pagination.page,
            size=pagination.size
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve encounters: {str(e)}"
        )

@router.get("/patient/{patient_id}", response_model=EncounterListResponse)
async def get_encounters_by_patient(
    patient_id: UUID,
    pagination: PaginationParams = Depends(get_pagination),
    service: EncounterService = Depends(get_encounter_service)
) -> EncounterListResponse:
    """
    Get encounters for a specific patient
    
    Args:
        patient_id: Patient UUID
        pagination: Pagination parameters
        service: Encounter service dependency
        
    Returns:
        List of encounters for the patient
        
    Raises:
        HTTPException: If patient not found
    """
    try:
        encounters = service.get_encounters_by_patient(
            str(patient_id), 
            skip=pagination.offset, 
            limit=pagination.size
        )
        
        # For simplicity, return total as length of encounters
        # In production, you'd want a separate count query
        total = len(encounters)
        
        return EncounterListResponse(
            data=encounters,
            total=total,
            page=pagination.page,
            size=pagination.size
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve encounters: {str(e)}"
        )

@router.get("/episode/{episode_id}/stats", response_model=EncounterStats)
async def get_encounter_stats(
    episode_id: UUID,
    service: EncounterService = Depends(get_encounter_service)
) -> EncounterStats:
    """
    Get encounter statistics for an episode
    
    Args:
        episode_id: Episode UUID
        service: Encounter service dependency
        
    Returns:
        Encounter statistics
        
    Raises:
        HTTPException: If episode not found
    """
    try:
        return service.get_encounter_stats(str(episode_id))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve encounter stats: {str(e)}"
        )

@router.post("/{target_encounter_id}/copy-forward/{source_encounter_id}", response_model=EncounterResponse)
async def copy_forward_from_encounter(
    target_encounter_id: UUID,
    source_encounter_id: UUID,
    sections: List[str] = Query(..., description="List of sections to copy"),
    service: EncounterService = Depends(get_encounter_service)
) -> EncounterResponse:
    """
    Copy data from one encounter to another
    
    Args:
        target_encounter_id: Target encounter UUID
        source_encounter_id: Source encounter UUID
        sections: List of sections to copy (subjective, objective, assessment, plan)
        service: Encounter service dependency
        
    Returns:
        Updated target encounter
        
    Raises:
        HTTPException: If encounters not found or copy fails
    """
    try:
        return service.copy_forward_from_encounter(
            str(source_encounter_id), 
            str(target_encounter_id), 
            sections
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to copy encounter data: {str(e)}"
        )

@router.get("/", response_model=EncounterListResponse)
async def get_encounters(
    episode_id: Optional[UUID] = Query(None, description="Filter by episode"),
    patient_id: Optional[UUID] = Query(None, description="Filter by patient"),
    status: Optional[str] = Query(None, description="Filter by status"),
    encounter_type: Optional[str] = Query(None, description="Filter by type"),
    pagination: PaginationParams = Depends(get_pagination),
    service: EncounterService = Depends(get_encounter_service)
) -> EncounterListResponse:
    """
    Get encounters with optional filters
    
    Args:
        episode_id: Filter by episode (optional)
        patient_id: Filter by patient (optional)
        status: Filter by status (optional)
        encounter_type: Filter by type (optional)
        pagination: Pagination parameters
        service: Encounter service dependency
        
    Returns:
        Filtered list of encounters
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        # Route to appropriate service method based on filters
        if episode_id:
            encounters = service.get_encounters_by_episode(
                str(episode_id), pagination.offset, pagination.size
            )
        elif patient_id:
            encounters = service.get_encounters_by_patient(
                str(patient_id), pagination.offset, pagination.size
            )
        else:
            # For now, return empty list if no specific filter
            # In production, you'd implement a general get_all method
            encounters = []
        
        total = len(encounters)
        
        return EncounterListResponse(
            data=encounters,
            total=total,
            page=pagination.page,
            size=pagination.size
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve encounters: {str(e)}"
        )