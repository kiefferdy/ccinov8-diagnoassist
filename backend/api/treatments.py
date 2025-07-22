"""
Treatment API Router for DiagnoAssist
CRUD operations for treatment management with safety monitoring and exception handling
"""

from fastapi import APIRouter, Depends, Query, Path
from typing import List, Optional
from uuid import UUID

# Import dependencies
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
from schemas.clinical_data import (
    TreatmentStart,
    TreatmentCompletion,
    TreatmentDiscontinuation,
    TreatmentMonitoring,
    TreatmentPlanGeneration,
    TreatmentPlanResponse,
    SafetyAlert
)

# Import exceptions - using the global exception system
from exceptions import (
    ValidationException,
    ResourceNotFoundException,
    BusinessRuleException,
    TreatmentException,
    PatientSafetyException,
    ClinicalDataException,
    AuthenticationException,
    AuthorizationException
)

# Create router
router = APIRouter(prefix="/treatments", tags=["treatments"])


# =============================================================================
# Treatment CRUD Operations
# =============================================================================

@router.post("/", response_model=TreatmentResponse, status_code=201)
async def create_treatment(
    treatment_data: TreatmentCreate,
    services: ServiceDep,
    current_user: CurrentUserDep
):
    """
    Create a new treatment
    
    Args:
        treatment_data: Treatment creation data
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Created treatment data
        
    Raises:
        ValidationException: Invalid treatment data
        ResourceNotFoundException: Episode or diagnosis not found
        TreatmentException: Treatment validation error
        PatientSafetyException: Safety rule violation
        AuthorizationException: User lacks permission
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("treatment.create", False):
        raise AuthorizationException(
            message="Insufficient permissions to create treatments",
            required_permission="treatment.create"
        )
    
    # Create treatment through service layer
    treatment = services.treatment.create_treatment(
        treatment_data=treatment_data,
        created_by=current_user["user_id"]
    )
    
    return treatment


@router.get("/", response_model=TreatmentListResponse)
async def get_treatments(
    services: ServiceDep,
    current_user: CurrentUserDep,
    pagination: PaginationDep,
    episode_id: Optional[UUID] = Query(None, description="Filter by episode ID"),
    patient_id: Optional[UUID] = Query(None, description="Filter by patient ID"),
    diagnosis_id: Optional[UUID] = Query(None, description="Filter by diagnosis ID"),
    status: Optional[str] = Query(None, description="Filter by treatment status"),
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
        status: Treatment status filter
        treatment_type: Treatment type filter
        
    Returns:
        Paginated list of treatments
    """
    # Authorization check
    if not current_user:
        raise AuthenticationException(message="Authentication required")
    
    # Get treatments through service layer
    treatments = services.treatment.get_treatments(
        pagination=pagination,
        episode_id=str(episode_id) if episode_id else None,
        patient_id=str(patient_id) if patient_id else None,
        diagnosis_id=str(diagnosis_id) if diagnosis_id else None,
        status=status,
        treatment_type=treatment_type
    )
    
    return treatments


@router.get("/{treatment_id}", response_model=TreatmentResponse)
async def get_treatment(
    services: ServiceDep,
    current_user: CurrentUserDep,
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
        raise AuthenticationException(message="Authentication required")
    
    # Get treatment through service layer
    treatment = services.treatment.get_treatment(str(treatment_id))
    
    return treatment


@router.put("/{treatment_id}", response_model=TreatmentResponse)
async def update_treatment(
    treatment_data: TreatmentUpdate,
    services: ServiceDep,
    current_user: CurrentUserDep,
    treatment_id: UUID = Path(..., description="Treatment ID")
):
    """
    Update treatment information
    
    Args:
        treatment_data: Updated treatment data
        services: Injected services
        current_user: Current authenticated user
        treatment_id: Treatment UUID
        
    Returns:
        Updated treatment data
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("treatment.update", False):
        raise AuthorizationException(
            message="Insufficient permissions to update treatments",
            required_permission="treatment.update"
        )
    
    # Update treatment through service layer
    treatment = services.treatment.update_treatment(
        treatment_id=str(treatment_id),
        treatment_data=treatment_data,
        updated_by=current_user["user_id"]
    )
    
    return treatment


@router.delete("/{treatment_id}", response_model=StatusResponse)
async def delete_treatment(
    services: ServiceDep,
    current_user: CurrentUserDep,
    treatment_id: UUID = Path(..., description="Treatment ID")
):
    """
    Delete treatment (soft delete)
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        treatment_id: Treatment UUID
        
    Returns:
        Deletion status
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("treatment.delete", False):
        raise AuthorizationException(
            message="Insufficient permissions to delete treatments",
            required_permission="treatment.delete"
        )
    
    # Delete treatment through service layer
    services.treatment.delete_treatment(
        treatment_id=str(treatment_id),
        deleted_by=current_user["user_id"]
    )
    
    return StatusResponse(
        success=True,
        message=f"Treatment {treatment_id} deleted successfully"
    )


# =============================================================================
# Treatment Lifecycle Management
# =============================================================================

@router.post("/{treatment_id}/start", response_model=TreatmentResponse)
async def start_treatment(
    start_data: TreatmentStart,
    services: ServiceDep,
    current_user: CurrentUserDep,
    treatment_id: UUID = Path(..., description="Treatment ID")
):
    """
    Start treatment execution
    
    Args:
        start_data: Treatment start parameters
        services: Injected services
        current_user: Current authenticated user
        treatment_id: Treatment UUID
        
    Returns:
        Updated treatment with started status
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("treatment.manage", False):
        raise AuthorizationException(
            message="Insufficient permissions to manage treatments",
            required_permission="treatment.manage"
        )
    
    # Start treatment through service layer
    treatment = services.treatment.start_treatment(
        treatment_id=str(treatment_id),
        start_data=start_data,
        started_by=current_user["user_id"]
    )
    
    return treatment


@router.post("/{treatment_id}/complete", response_model=TreatmentResponse)
async def complete_treatment(
    completion_data: TreatmentCompletion,
    services: ServiceDep,
    current_user: CurrentUserDep,
    treatment_id: UUID = Path(..., description="Treatment ID")
):
    """
    Complete treatment
    
    Args:
        completion_data: Treatment completion data
        services: Injected services
        current_user: Current authenticated user
        treatment_id: Treatment UUID
        
    Returns:
        Completed treatment data
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("treatment.manage", False):
        raise AuthorizationException(
            message="Insufficient permissions to manage treatments",
            required_permission="treatment.manage"
        )
    
    # Complete treatment through service layer
    treatment = services.treatment.complete_treatment(
        treatment_id=str(treatment_id),
        completion_data=completion_data,
        completed_by=current_user["user_id"]
    )
    
    return treatment


@router.post("/{treatment_id}/discontinue", response_model=TreatmentResponse)
async def discontinue_treatment(
    discontinuation_data: TreatmentDiscontinuation,
    services: ServiceDep,
    current_user: CurrentUserDep,
    treatment_id: UUID = Path(..., description="Treatment ID")
):
    """
    Discontinue treatment
    
    Args:
        discontinuation_data: Treatment discontinuation data
        services: Injected services
        current_user: Current authenticated user
        treatment_id: Treatment UUID
        
    Returns:
        Discontinued treatment data
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("treatment.manage", False):
        raise AuthorizationException(
            message="Insufficient permissions to manage treatments",
            required_permission="treatment.manage"
        )
    
    # Discontinue treatment through service layer
    treatment = services.treatment.discontinue_treatment(
        treatment_id=str(treatment_id),
        discontinuation_data=discontinuation_data,
        discontinued_by=current_user["user_id"]
    )
    
    return treatment


@router.post("/{treatment_id}/monitor", response_model=TreatmentResponse)
async def add_monitoring_data(
    monitoring_data: TreatmentMonitoring,
    services: ServiceDep,
    current_user: CurrentUserDep,
    treatment_id: UUID = Path(..., description="Treatment ID")
):
    """
    Add treatment monitoring data
    
    Args:
        monitoring_data: Treatment monitoring information
        services: Injected services
        current_user: Current authenticated user
        treatment_id: Treatment UUID
        
    Returns:
        Updated treatment with monitoring data
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("treatment.monitor", False):
        raise AuthorizationException(
            message="Insufficient permissions to monitor treatments",
            required_permission="treatment.monitor"
        )
    
    # Add monitoring data through service layer
    treatment = services.treatment.add_monitoring_data(
        treatment_id=str(treatment_id),
        monitoring_data=monitoring_data,
        monitored_by=current_user["user_id"]
    )
    
    return treatment


# =============================================================================
# Treatment Planning and Safety
# =============================================================================

@router.post("/generate-plan", response_model=TreatmentPlanResponse)
async def generate_treatment_plan(
    plan_generation_data: TreatmentPlanGeneration,
    services: ServiceDep,
    current_user: CurrentUserDep
):
    """
    Generate AI-assisted treatment plan
    
    Args:
        plan_generation_data: Treatment plan generation parameters
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Generated treatment plan with recommendations
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("treatment.plan", False):
        raise AuthorizationException(
            message="Insufficient permissions to generate treatment plans",
            required_permission="treatment.plan"
        )
    
    # Generate treatment plan through service layer
    treatment_plan = services.treatment.generate_treatment_plan(
        plan_generation_data=plan_generation_data,
        generated_by=current_user["user_id"]
    )
    
    return treatment_plan


@router.get("/{treatment_id}/safety-alerts")
async def get_treatment_safety_alerts(
    services: ServiceDep,
    current_user: CurrentUserDep,
    treatment_id: UUID = Path(..., description="Treatment ID"),
    severity: Optional[str] = Query(None, description="Filter by alert severity"),
    status: Optional[str] = Query(None, description="Filter by alert status")
):
    """
    Get safety alerts for treatment
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        treatment_id: Treatment UUID
        severity: Alert severity filter
        status: Alert status filter
        
    Returns:
        List of safety alerts for the treatment
    """
    # Authorization check
    if not current_user:
        raise AuthenticationException(message="Authentication required")
    
    # Get safety alerts through service layer
    alerts = services.treatment.get_safety_alerts(
        treatment_id=str(treatment_id),
        severity=severity,
        status=status
    )
    
    return alerts


@router.get("/patient/{patient_id}/active")
async def get_active_treatments(
    services: ServiceDep,
    current_user: CurrentUserDep,
    patient_id: UUID = Path(..., description="Patient ID"),
    treatment_type: Optional[str] = Query(None, description="Filter by treatment type")
):
    """
    Get active treatments for a patient
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        patient_id: Patient UUID
        treatment_type: Treatment type filter
        
    Returns:
        List of active treatments for the patient
    """
    # Authorization check
    if not current_user:
        raise AuthenticationException(message="Authentication required")
    
    # Get active treatments through service layer
    treatments = services.treatment.get_active_treatments(
        patient_id=str(patient_id),
        treatment_type=treatment_type
    )
    
    return treatments


@router.get("/episode/{episode_id}/treatments")
async def get_episode_treatments(
    services: ServiceDep,
    current_user: CurrentUserDep,
    episode_id: UUID = Path(..., description="Episode ID"),
    include_completed: bool = Query(False, description="Include completed treatments")
):
    """
    Get treatments for an episode
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        episode_id: Episode UUID
        include_completed: Whether to include completed treatments
        
    Returns:
        List of treatments for the episode
    """
    # Authorization check
    if not current_user:
        raise AuthenticationException(message="Authentication required")
    
    # Get episode treatments through service layer
    treatments = services.treatment.get_episode_treatments(
        episode_id=str(episode_id),
        include_completed=include_completed
    )
    
    return treatments


# Export router
__all__ = ["router"]