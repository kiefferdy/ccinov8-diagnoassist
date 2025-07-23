"""
Treatment API Router for DiagnoAssist - IMPORT FIXED VERSION
CRUD operations for treatment management
"""

from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from typing import List, Optional
from uuid import UUID

# FIXED: Import dependencies properly
from api.dependencies import ServiceDep, CurrentUserDep, PaginationDep

# Import schemas
from schemas.treatment import (
    TreatmentCreate,
    TreatmentUpdate,
    TreatmentResponse,
    TreatmentListResponse,
    MedicationTreatment,
    NonPharmacologicalTreatment
)
from schemas.common import StatusResponse

# Create router
router = APIRouter(prefix="/treatments", tags=["treatments"])

# =============================================================================
# Treatment CRUD Operations
# =============================================================================

@router.post("/", response_model=TreatmentResponse, status_code=201)
async def create_treatment(
    treatment_data: TreatmentCreate,
    services = ServiceDep,
    current_user = CurrentUserDep
):
    """
    Create a new treatment
    
    Args:
        treatment_data: Treatment creation data
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Created treatment data
    """
    # Authorization check (commented out for MVP)
    # if not current_user or not current_user.get("permissions", {}).get("treatment.create", False):
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Insufficient permissions to create treatments"
    #     )
    
    try:
        # Create treatment through service layer
        treatment = services.treatment.create_treatment(treatment_data)
        return treatment
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
                detail=f"Failed to create treatment: {error_message}"
            )

@router.get("/", response_model=TreatmentListResponse)
async def get_treatments(
    services = ServiceDep,
    current_user = CurrentUserDep,
    pagination = PaginationDep,
    patient_id: Optional[UUID] = Query(None, description="Filter by patient ID"),
    episode_id: Optional[UUID] = Query(None, description="Filter by episode ID"),
    treatment_type: Optional[str] = Query(None, description="Filter by treatment type"),
    status_filter: Optional[str] = Query(None, description="Filter by treatment status")
):
    """
    Get paginated list of treatments
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        pagination: Pagination parameters
        patient_id: Patient ID filter
        episode_id: Episode ID filter
        treatment_type: Treatment type filter
        status_filter: Treatment status filter
        
    Returns:
        Paginated list of treatments
    """
    # Authorization check (commented out for MVP)
    # if not current_user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Authentication required",
    #         headers={"WWW-Authenticate": "Bearer"}
    #     )
    
    try:
        # Get treatments through service layer
        treatments = services.treatment.get_treatments(
            pagination=pagination,
            patient_id=str(patient_id) if patient_id else None,
            episode_id=str(episode_id) if episode_id else None,
            treatment_type=treatment_type,
            status=status_filter
        )
        
        return treatments
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve treatments: {str(e)}"
        )

@router.get("/{treatment_id}", response_model=TreatmentResponse)
async def get_treatment(
    services = ServiceDep,
    current_user = CurrentUserDep,
    treatment_id: UUID = Path(..., description="Treatment ID")
):
    """
    Get treatment by ID
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        treatment_id: Treatment UUID
        
    Returns:
        Treatment data
    """

@router.put("/{treatment_id}", response_model=TreatmentResponse)
async def update_treatment(
    services = ServiceDep,
    current_user = CurrentUserDep,
    treatment_id: UUID = Path(..., description="Treatment ID"),
    treatment_data: TreatmentUpdate = ...
):
    """
    Update treatment
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        treatment_id: Treatment UUID
        treatment_data: Treatment update data
        
    Returns:
        Updated treatment data
    """
    # Authorization check (commented out for MVP)
    # if not current_user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Authentication required",
    #         headers={"WWW-Authenticate": "Bearer"}
    #     )
    
    try:
        # Update treatment through service layer
        treatment = services.treatment.update_treatment(str(treatment_id), treatment_data)
        
        if not treatment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Treatment with ID {treatment_id} not found"
            )
        
        return treatment
    except HTTPException:
        raise
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Treatment with ID {treatment_id} not found"
            )
        elif "validation" in error_message.lower() or "invalid" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error_message
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update treatment: {error_message}"
            )

@router.delete("/{treatment_id}", response_model=StatusResponse)
async def delete_treatment(
    services = ServiceDep,
    current_user = CurrentUserDep,
    treatment_id: UUID = Path(..., description="Treatment ID")
):
    """
    Delete treatment
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        treatment_id: Treatment UUID
        
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
        # Delete treatment through service layer
        success = services.treatment.delete_treatment(str(treatment_id))
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Treatment with ID {treatment_id} not found"
            )
        
        return StatusResponse(
            success=True,
            message=f"Treatment {treatment_id} deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Treatment with ID {treatment_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete treatment: {error_message}"
            )

# =============================================================================
# Treatment-specific endpoints
# =============================================================================

@router.patch("/{treatment_id}/start", response_model=TreatmentResponse)
async def start_treatment(
    services = ServiceDep,
    current_user = CurrentUserDep,
    treatment_id: UUID = Path(..., description="Treatment ID")
):
    """
    Start a treatment
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        treatment_id: Treatment UUID
        
    Returns:
        Updated treatment data
    """
    try:
        # Start treatment through service layer
        treatment = services.treatment.start_treatment(str(treatment_id))
        return treatment
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Treatment with ID {treatment_id} not found"
            )
        elif "cannot start" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to start treatment: {error_message}"
            )

@router.patch("/{treatment_id}/complete", response_model=TreatmentResponse)
async def complete_treatment(
    services = ServiceDep,
    current_user = CurrentUserDep,
    treatment_id: UUID = Path(..., description="Treatment ID"),
    completion_notes: Optional[str] = Query(None, description="Completion notes")
):
    """
    Complete a treatment
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        treatment_id: Treatment UUID
        completion_notes: Optional completion notes
        
    Returns:
        Updated treatment data
    """
    try:
        # Complete treatment through service layer
        treatment = services.treatment.complete_treatment(str(treatment_id), completion_notes)
        return treatment
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Treatment with ID {treatment_id} not found"
            )
        elif "cannot complete" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to complete treatment: {error_message}"
            )

@router.patch("/{treatment_id}/discontinue", response_model=TreatmentResponse)
async def discontinue_treatment(
    services = ServiceDep,
    current_user = CurrentUserDep,
    treatment_id: UUID = Path(..., description="Treatment ID"),
    discontinuation_reason: str = Query(..., description="Reason for discontinuation")
):
    """
    Discontinue a treatment
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        treatment_id: Treatment UUID
        discontinuation_reason: Reason for discontinuation
        
    Returns:
        Updated treatment data
    """
    try:
        # Discontinue treatment through service layer
        treatment = services.treatment.discontinue_treatment(str(treatment_id), discontinuation_reason)
        return treatment
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Treatment with ID {treatment_id} not found"
            )
        elif "cannot discontinue" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to discontinue treatment: {error_message}"
            )

@router.get("/{treatment_id}/monitoring")
async def get_treatment_monitoring(
    services = ServiceDep,
    current_user = CurrentUserDep,
    treatment_id: UUID = Path(..., description="Treatment ID")
):
    """
    Get treatment monitoring data
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        treatment_id: Treatment UUID
        
    Returns:
        Treatment monitoring data
    """
    try:
        # Get treatment monitoring through service layer
        monitoring_data = services.treatment.get_treatment_monitoring(str(treatment_id))
        return monitoring_data
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Treatment with ID {treatment_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve treatment monitoring: {error_message}"
            )