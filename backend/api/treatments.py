"""
Treatment API Router for DiagnoAssist - CLEAN VERSION
CRUD operations for treatment management with safety monitoring
"""

from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from typing import List, Optional
from uuid import UUID

# Import dependencies - FIXED: Import directly from the module
from api.dependencies import get_service_manager, get_current_user, PaginationParams

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
from schemas.clinical_data import (
    TreatmentStart,
    TreatmentCompletion,
    TreatmentDiscontinuation,
    TreatmentMonitoring,
    TreatmentPlanGeneration,
    TreatmentPlanResponse,
    SafetyAlert
)

# Create router
router = APIRouter(prefix="/treatments", tags=["treatments"])

# Create dependency aliases properly
ServiceDep = Depends(get_service_manager)
CurrentUserDep = Depends(get_current_user)
PaginationDep = Depends(PaginationParams)

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
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("treatment.create", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create treatments"
        )
    
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
        elif "safety" in error_message.lower() or "contraindication" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Safety concern: {error_message}"
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
    episode_id: Optional[UUID] = Query(None, description="Filter by episode ID"),
    patient_id: Optional[UUID] = Query(None, description="Filter by patient ID"),
    diagnosis_id: Optional[UUID] = Query(None, description="Filter by diagnosis ID"),
    status_filter: Optional[str] = Query(None, description="Filter by treatment status"),
    treatment_type: Optional[str] = Query(None, description="Filter by treatment type")
):
    """
    Get paginated list of treatments
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        pagination: Pagination parameters
        episode_id: Episode ID filter
        patient_id: Patient ID filter
        diagnosis_id: Diagnosis ID filter
        status_filter: Treatment status filter
        treatment_type: Treatment type filter
        
    Returns:
        Paginated list of treatments
    """
    # Authorization check
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        # Get treatments through service layer
        treatments = services.treatment.get_treatments(
            pagination=pagination,
            episode_id=str(episode_id) if episode_id else None,
            patient_id=str(patient_id) if patient_id else None,
            diagnosis_id=str(diagnosis_id) if diagnosis_id else None,
            status=status_filter,
            treatment_type=treatment_type
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
    # Authorization check
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        # Get treatment through service layer
        treatment = services.treatment.get_treatment(str(treatment_id))
        return treatment
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Treatment {treatment_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve treatment: {error_message}"
            )


@router.put("/{treatment_id}", response_model=TreatmentResponse)
async def update_treatment(
    treatment_data: TreatmentUpdate,
    services = ServiceDep,
    current_user = CurrentUserDep,
    treatment_id: UUID = Path(..., description="Treatment ID")
):
    """
    Update treatment information
    
    Args:
        treatment_data: Treatment update data
        services: Injected services
        current_user: Current authenticated user
        treatment_id: Treatment UUID
        
    Returns:
        Updated treatment data
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("treatment.update", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update treatments"
        )
    
    try:
        # Update treatment through service layer
        updated_treatment = services.treatment.update_treatment(
            treatment_id=str(treatment_id),
            treatment_data=treatment_data,
            updated_by=current_user["user_id"]
        )
        
        return updated_treatment
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Treatment {treatment_id} not found"
            )
        elif "safety" in error_message.lower() or "contraindication" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Safety concern: {error_message}"
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
    Delete treatment (soft delete)
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        treatment_id: Treatment UUID
        
    Returns:
        Success status
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("treatment.delete", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete treatments"
        )
    
    try:
        # Delete treatment through service layer
        services.treatment.delete_treatment(
            treatment_id=str(treatment_id),
            deleted_by=current_user["user_id"]
        )
        
        return StatusResponse(
            status="success",
            message=f"Treatment {treatment_id} deleted successfully"
        )
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Treatment {treatment_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete treatment: {error_message}"
            )


# =============================================================================
# Treatment Lifecycle Operations
# =============================================================================

@router.post("/{treatment_id}/start", response_model=TreatmentResponse)
async def start_treatment(
    start_data: TreatmentStart,
    services = ServiceDep,
    current_user = CurrentUserDep,
    treatment_id: UUID = Path(..., description="Treatment ID")
):
    """
    Start a treatment
    
    Args:
        start_data: Treatment start data
        services: Injected services
        current_user: Current authenticated user
        treatment_id: Treatment UUID
        
    Returns:
        Started treatment data
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("treatment.update", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to start treatments"
        )
    
    try:
        # Start treatment through service layer
        started_treatment = services.treatment.start_treatment(
            treatment_id=str(treatment_id),
            start_data=start_data,
            started_by=current_user["user_id"]
        )
        
        return started_treatment
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Treatment {treatment_id} not found"
            )
        elif "already started" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to start treatment: {error_message}"
            )


@router.post("/{treatment_id}/complete", response_model=TreatmentResponse)
async def complete_treatment(
    completion_data: TreatmentCompletion,
    services = ServiceDep,
    current_user = CurrentUserDep,
    treatment_id: UUID = Path(..., description="Treatment ID")
):
    """
    Complete a treatment
    
    Args:
        completion_data: Treatment completion data
        services: Injected services
        current_user: Current authenticated user
        treatment_id: Treatment UUID
        
    Returns:
        Completed treatment data
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("treatment.update", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to complete treatments"
        )
    
    try:
        # Complete treatment through service layer
        completed_treatment = services.treatment.complete_treatment(
            treatment_id=str(treatment_id),
            completion_data=completion_data,
            completed_by=current_user["user_id"]
        )
        
        return completed_treatment
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Treatment {treatment_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to complete treatment: {error_message}"
            )


@router.post("/{treatment_id}/discontinue", response_model=TreatmentResponse)
async def discontinue_treatment(
    discontinuation_data: TreatmentDiscontinuation,
    services = ServiceDep,
    current_user = CurrentUserDep,
    treatment_id: UUID = Path(..., description="Treatment ID")
):
    """
    Discontinue a treatment
    
    Args:
        discontinuation_data: Treatment discontinuation data
        services: Injected services
        current_user: Current authenticated user
        treatment_id: Treatment UUID
        
    Returns:
        Discontinued treatment data
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("treatment.update", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to discontinue treatments"
        )
    
    try:
        # Discontinue treatment through service layer
        discontinued_treatment = services.treatment.discontinue_treatment(
            treatment_id=str(treatment_id),
            discontinuation_data=discontinuation_data,
            discontinued_by=current_user["user_id"]
        )
        
        return discontinued_treatment
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Treatment {treatment_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to discontinue treatment: {error_message}"
            )


# =============================================================================
# Treatment Planning and Monitoring
# =============================================================================

@router.post("/plan", response_model=TreatmentPlanResponse)
async def generate_treatment_plan(
    plan_data: TreatmentPlanGeneration,
    services = ServiceDep,
    current_user = CurrentUserDep
):
    """
    Generate a treatment plan based on diagnosis
    
    Args:
        plan_data: Treatment plan generation data
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Generated treatment plan
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("treatment.create", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to generate treatment plans"
        )
    
    try:
        # Generate treatment plan through service layer
        plan = services.treatment.generate_treatment_plan(
            plan_data=plan_data,
            generated_by=current_user["user_id"]
        )
        
        return plan
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_message
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate treatment plan: {error_message}"
            )


@router.post("/{treatment_id}/monitor")
async def add_monitoring_data(
    monitoring_data: TreatmentMonitoring,
    services = ServiceDep,
    current_user = CurrentUserDep,
    treatment_id: UUID = Path(..., description="Treatment ID")
):
    """
    Add monitoring data for a treatment
    
    Args:
        monitoring_data: Treatment monitoring data
        services: Injected services
        current_user: Current authenticated user
        treatment_id: Treatment UUID
        
    Returns:
        Monitoring result with any alerts
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("treatment.update", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to add monitoring data"
        )
    
    try:
        # Add monitoring data through service layer
        monitoring_result = services.treatment.add_monitoring_data(
            treatment_id=str(treatment_id),
            monitoring_data=monitoring_data,
            monitored_by=current_user["user_id"]
        )
        
        return monitoring_result
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Treatment {treatment_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to add monitoring data: {error_message}"
            )


@router.get("/{treatment_id}/safety-alerts")
async def get_safety_alerts(
    services = ServiceDep,
    current_user = CurrentUserDep,
    treatment_id: UUID = Path(..., description="Treatment ID")
):
    """
    Get safety alerts for a treatment
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        treatment_id: Treatment UUID
        
    Returns:
        List of safety alerts
    """
    # Authorization check
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        # Get safety alerts through service layer
        alerts = services.treatment.get_safety_alerts(str(treatment_id))
        return alerts
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Treatment {treatment_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve safety alerts: {error_message}"
            )

# Export router
__all__ = ["router"]