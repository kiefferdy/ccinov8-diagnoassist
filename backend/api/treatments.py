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


@router.get("/{treatment_id}", response_model=TreatmentResponse)
async def get_treatment(
    treatment_id: UUID = Path(..., description="Treatment ID"),
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Get treatment by ID
    
    Args:
        treatment_id: Treatment UUID
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Treatment data with monitoring information
        
    Raises:
        ResourceNotFoundException: Treatment not found
        AuthorizationException: User lacks permission
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("treatment.read", False):
        raise AuthorizationException(
            message="Insufficient permissions to view treatments",
            required_permission="treatment.read"
        )
    
    # Get treatment through service layer
    treatment = services.treatment.get_treatment(str(treatment_id))
    
    return treatment


@router.get("/", response_model=List[TreatmentListResponse])
async def list_treatments(
    episode_id: Optional[UUID] = Query(None, description="Filter by episode ID"),
    patient_id: Optional[UUID] = Query(None, description="Filter by patient ID"),
    diagnosis_id: Optional[UUID] = Query(None, description="Filter by diagnosis ID"),
    treatment_type: Optional[str] = Query(None, description="Filter by treatment type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    active_only: bool = Query(False, description="Show only active treatments"),
    pagination: PaginationDep = Depends(),
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    List treatments with filtering options
    
    Args:
        episode_id: Filter by episode
        patient_id: Filter by patient
        diagnosis_id: Filter by diagnosis
        treatment_type: Filter by type
        status: Filter by status
        active_only: Show only active treatments
        pagination: Pagination parameters
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        List of treatments
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("treatment.read", False):
        raise AuthorizationException(
            message="Insufficient permissions to list treatments",
            required_permission="treatment.read"
        )
    
    # Get treatments through service layer
    treatments = services.treatment.search_treatments(
        episode_id=str(episode_id) if episode_id else None,
        patient_id=str(patient_id) if patient_id else None,
        diagnosis_id=str(diagnosis_id) if diagnosis_id else None,
        treatment_type=treatment_type,
        status=status,
        active_only=active_only,
        offset=pagination.offset,
        limit=pagination.limit
    )
    
    return treatments


@router.put("/{treatment_id}", response_model=TreatmentResponse)
async def update_treatment(
    treatment_id: UUID = Path(..., description="Treatment ID"),
    treatment_data: TreatmentUpdate = ...,
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Update treatment information
    
    Args:
        treatment_id: Treatment UUID
        treatment_data: Updated treatment data
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Updated treatment data
        
    Raises:
        ResourceNotFoundException: Treatment not found
        ValidationException: Invalid update data
        TreatmentException: Treatment validation error
        PatientSafetyException: Safety rule violation
        AuthorizationException: User lacks permission
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
    treatment_id: UUID = Path(..., description="Treatment ID"),
    reason: Optional[str] = Query(None, description="Reason for deletion"),
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Delete treatment (soft delete with safety checks)
    
    Args:
        treatment_id: Treatment UUID
        reason: Reason for deletion
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Deletion status
        
    Raises:
        ResourceNotFoundException: Treatment not found
        PatientSafetyException: Treatment is critical for patient
        TreatmentException: Treatment cannot be safely discontinued
        AuthorizationException: User lacks permission
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
        reason=reason,
        deleted_by=current_user["user_id"]
    )
    
    return StatusResponse(
        status="success",
        message=f"Treatment {treatment_id} deleted successfully"
    )


# =============================================================================
# Treatment Clinical Operations
# =============================================================================

@router.post("/{treatment_id}/start", response_model=TreatmentResponse)
async def start_treatment(
    treatment_id: UUID = Path(..., description="Treatment ID"),
    start_data: TreatmentStart = ...,
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Start a treatment (change status to active)
    
    Args:
        treatment_id: Treatment UUID
        start_data: Treatment start parameters
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Updated treatment data
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("treatment.update", False):
        raise AuthorizationException(
            message="Insufficient permissions to start treatments",
            required_permission="treatment.update"
        )
    
    # Start treatment through service layer
    treatment = services.treatment.start_treatment(
        treatment_id=str(treatment_id),
        start_data=start_data.model_dump(),
        started_by=current_user["user_id"]
    )
    
    return treatment


@router.post("/{treatment_id}/complete", response_model=TreatmentResponse)
async def complete_treatment(
    treatment_id: UUID = Path(..., description="Treatment ID"),
    completion_data: TreatmentCompletion = ...,
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Complete a treatment (change status to completed)
    
    Args:
        treatment_id: Treatment UUID
        completion_data: Treatment completion details
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Updated treatment data
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("treatment.update", False):
        raise AuthorizationException(
            message="Insufficient permissions to complete treatments",
            required_permission="treatment.update"
        )
    
    # Complete treatment through service layer
    treatment = services.treatment.complete_treatment(
        treatment_id=str(treatment_id),
        completion_data=completion_data.model_dump(),
        completed_by=current_user["user_id"]
    )
    
    return treatment


@router.post("/{treatment_id}/discontinue", response_model=TreatmentResponse)
async def discontinue_treatment(
    treatment_id: UUID = Path(..., description="Treatment ID"),
    discontinuation_data: TreatmentDiscontinuation = ...,
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Discontinue a treatment with safety checks
    
    Args:
        treatment_id: Treatment UUID
        discontinuation_data: Discontinuation reason and details
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Updated treatment data
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("treatment.discontinue", False):
        raise AuthorizationException(
            message="Insufficient permissions to discontinue treatments",
            required_permission="treatment.discontinue"
        )
    
    # Discontinue treatment through service layer
    treatment = services.treatment.discontinue_treatment(
        treatment_id=str(treatment_id),
        discontinuation_data=discontinuation_data.model_dump(),
        discontinued_by=current_user["user_id"]
    )
    
    return treatment


# =============================================================================
# Treatment Monitoring and Safety
# =============================================================================

@router.get("/{treatment_id}/monitoring")
async def get_treatment_monitoring(
    treatment_id: UUID = Path(..., description="Treatment ID"),
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Get treatment monitoring data and safety alerts
    
    Args:
        treatment_id: Treatment UUID
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Monitoring data with safety indicators
    """
    # Authorization check
    if not current_user:
        raise AuthenticationException(message="Authentication required")
    
    # Get monitoring data through service layer
    monitoring = services.treatment.get_treatment_monitoring(str(treatment_id))
    
    return monitoring


@router.post("/{treatment_id}/monitor")
async def record_monitoring_data(
    treatment_id: UUID = Path(..., description="Treatment ID"),
    monitoring_data: TreatmentMonitoring = ...,
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Record monitoring data for treatment
    
    Args:
        treatment_id: Treatment UUID
        monitoring_data: Monitoring measurements and observations
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Updated treatment with monitoring data
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("treatment.monitor", False):
        raise AuthorizationException(
            message="Insufficient permissions to record monitoring data",
            required_permission="treatment.monitor"
        )
    
    # Record monitoring through service layer
    treatment = services.treatment.record_monitoring(
        treatment_id=str(treatment_id),
        monitoring_data=monitoring_data,
        recorded_by=current_user["user_id"]
    )
    
    return treatment


@router.get("/patient/{patient_id}/active")
async def get_active_treatments(
    patient_id: UUID = Path(..., description="Patient ID"),
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Get all active treatments for a patient
    
    Args:
        patient_id: Patient UUID
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        List of active treatments for patient
    """
    # Authorization check
    if not current_user:
        raise AuthenticationException(message="Authentication required")
    
    # Get active treatments through service layer
    treatments = services.treatment.get_active_treatments_by_patient(str(patient_id))
    
    return treatments


@router.get("/safety/alerts")
async def get_treatment_safety_alerts(
    patient_id: Optional[UUID] = Query(None, description="Filter by patient ID"),
    severity: Optional[str] = Query(None, description="Filter by alert severity"),
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Get treatment safety alerts
    
    Args:
        patient_id: Optional patient filter
        severity: Optional severity filter
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        List of safety alerts
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("treatment.safety", False):
        raise AuthorizationException(
            message="Insufficient permissions to view safety alerts",
            required_permission="treatment.safety"
        )
    
    # Get safety alerts through service layer
    alerts = services.treatment.get_safety_alerts(
        patient_id=str(patient_id) if patient_id else None,
        severity=severity
    )
    
    return alerts


# =============================================================================
# Treatment Planning and Recommendations
# =============================================================================

@router.post("/plan/generate", response_model=TreatmentPlanResponse)
async def generate_treatment_plan(
    plan_data: TreatmentPlanGeneration = ...,
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Generate AI-powered treatment plan recommendations
    
    Args:
        plan_data: Patient and diagnosis data for plan generation
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
    plan = services.treatment.generate_treatment_plan(
        plan_data=plan_data,
        generated_by=current_user["user_id"]
    )
    
    return plan


@router.get("/interactions/check")
async def check_treatment_interactions(
    treatment_ids: List[UUID] = Query(..., description="Treatment IDs to check"),
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Check for treatment interactions and contraindications
    
    Args:
        treatment_ids: List of treatment IDs to check
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Interaction analysis and warnings
    """
    # Authorization check
    if not current_user:
        raise AuthenticationException(message="Authentication required")
    
    # Check interactions through service layer
    interactions = services.treatment.check_interactions(
        treatment_ids=[str(t_id) for t_id in treatment_ids]
    )
    
    return interactions


# Export router
__all__ = ["router"]