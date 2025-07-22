"""
Diagnosis API Router for DiagnoAssist
CRUD operations for diagnosis management with AI integration and exception handling
"""

from fastapi import APIRouter, Depends, Query, Path
from typing import List, Optional
from uuid import UUID

# Import dependencies
from api.dependencies import ServiceDep, CurrentUserDep, PaginationDep

# Import schemas
from schemas.diagnosis import (
    DiagnosisCreate,
    DiagnosisUpdate,
    DiagnosisResponse,
    DiagnosisListResponse,
    DifferentialDiagnosis,
    AIAnalysisResult
)
from schemas.common import StatusResponse
from schemas.clinical_data import (
    SymptomAnalysisInput,
    DiagnosisRefinement,
    DiagnosisConfirmation,
    DiagnosisEvidence
)

# Import exceptions - using the global exception system
from exceptions import (
    ValidationException,
    ResourceNotFoundException,
    BusinessRuleException,
    DiagnosisException,
    ClinicalDataException,
    PatientSafetyException,
    AuthenticationException,
    AuthorizationException
)

# Create router
router = APIRouter(prefix="/diagnoses", tags=["diagnoses"])


# =============================================================================
# Diagnosis CRUD Operations
# =============================================================================

@router.post("/", response_model=DiagnosisResponse, status_code=201)
async def create_diagnosis(
    diagnosis_data: DiagnosisCreate,
    services: ServiceDep,
    current_user: CurrentUserDep
):
    """
    Create a new diagnosis
    
    Args:
        diagnosis_data: Diagnosis creation data
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Created diagnosis data
        
    Raises:
        ValidationException: Invalid diagnosis data
        ResourceNotFoundException: Episode not found
        DiagnosisException: Diagnosis validation error
        ClinicalDataException: Clinical data validation error
        PatientSafetyException: Safety rule violation
        AuthorizationException: User lacks permission
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("diagnosis.create", False):
        raise AuthorizationException(
            message="Insufficient permissions to create diagnoses",
            required_permission="diagnosis.create"
        )
    
    # Create diagnosis through service layer
    diagnosis = services.diagnosis.create_diagnosis(
        diagnosis_data=diagnosis_data,
        created_by=current_user["user_id"]
    )
    
    return diagnosis


@router.get("/{diagnosis_id}", response_model=DiagnosisResponse)
async def get_diagnosis(
    diagnosis_id: UUID = Path(..., description="Diagnosis ID"),
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Get diagnosis by ID
    
    Args:
        diagnosis_id: Diagnosis UUID
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Diagnosis data with confidence and evidence
        
    Raises:
        ResourceNotFoundException: Diagnosis not found
        AuthorizationException: User lacks permission
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("diagnosis.read", False):
        raise AuthorizationException(
            message="Insufficient permissions to view diagnoses",
            required_permission="diagnosis.read"
        )
    
    # Get diagnosis through service layer
    diagnosis = services.diagnosis.get_diagnosis(str(diagnosis_id))
    
    return diagnosis


@router.get("/", response_model=List[DiagnosisListResponse])
async def list_diagnoses(
    episode_id: Optional[UUID] = Query(None, description="Filter by episode ID"),
    patient_id: Optional[UUID] = Query(None, description="Filter by patient ID"),
    diagnosis_type: Optional[str] = Query(None, description="Filter by diagnosis type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    final_diagnosis: Optional[bool] = Query(None, description="Filter final diagnoses"),
    pagination: PaginationDep = Depends(),
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    List diagnoses with filtering options
    
    Args:
        episode_id: Filter by episode
        patient_id: Filter by patient
        diagnosis_type: Filter by type
        status: Filter by status
        final_diagnosis: Filter final diagnoses
        pagination: Pagination parameters
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        List of diagnoses
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("diagnosis.read", False):
        raise AuthorizationException(
            message="Insufficient permissions to list diagnoses",
            required_permission="diagnosis.read"
        )
    
    # Get diagnoses through service layer
    diagnoses = services.diagnosis.search_diagnoses(
        episode_id=str(episode_id) if episode_id else None,
        patient_id=str(patient_id) if patient_id else None,
        diagnosis_type=diagnosis_type,
        status=status,
        final_diagnosis=final_diagnosis,
        offset=pagination.offset,
        limit=pagination.limit
    )
    
    return diagnoses


@router.put("/{diagnosis_id}", response_model=DiagnosisResponse)
async def update_diagnosis(
    diagnosis_id: UUID = Path(..., description="Diagnosis ID"),
    diagnosis_data: DiagnosisUpdate = ...,
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Update diagnosis information
    
    Args:
        diagnosis_id: Diagnosis UUID
        diagnosis_data: Updated diagnosis data
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Updated diagnosis data
        
    Raises:
        ResourceNotFoundException: Diagnosis not found
        ValidationException: Invalid update data
        DiagnosisException: Diagnosis validation error
        PatientSafetyException: Safety rule violation
        AuthorizationException: User lacks permission
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("diagnosis.update", False):
        raise AuthorizationException(
            message="Insufficient permissions to update diagnoses",
            required_permission="diagnosis.update"
        )
    
    # Update diagnosis through service layer
    diagnosis = services.diagnosis.update_diagnosis(
        diagnosis_id=str(diagnosis_id),
        diagnosis_data=diagnosis_data,
        updated_by=current_user["user_id"]
    )
    
    return diagnosis


@router.delete("/{diagnosis_id}", response_model=StatusResponse)
async def delete_diagnosis(
    diagnosis_id: UUID = Path(..., description="Diagnosis ID"),
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Delete diagnosis (soft delete)
    
    Args:
        diagnosis_id: Diagnosis UUID
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Deletion status
        
    Raises:
        ResourceNotFoundException: Diagnosis not found
        PatientSafetyException: Diagnosis has linked treatments
        AuthorizationException: User lacks permission
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("diagnosis.delete", False):
        raise AuthorizationException(
            message="Insufficient permissions to delete diagnoses",
            required_permission="diagnosis.delete"
        )
    
    # Delete diagnosis through service layer
    services.diagnosis.delete_diagnosis(
        diagnosis_id=str(diagnosis_id),
        deleted_by=current_user["user_id"]
    )
    
    return StatusResponse(
        status="success",
        message=f"Diagnosis {diagnosis_id} deleted successfully"
    )


# =============================================================================
# AI-Powered Diagnosis Operations
# =============================================================================

@router.post("/analyze", response_model=AIAnalysisResult)
async def analyze_symptoms(
    analysis_data: SymptomAnalysisInput = ...,
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Generate AI-powered differential diagnosis
    
    Args:
        analysis_data: Symptoms and clinical data for analysis
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        AI analysis with differential diagnoses
        
    Raises:
        ValidationException: Invalid analysis data
        ClinicalDataException: Insufficient clinical data
        DiagnosisException: AI analysis error
        AuthorizationException: User lacks permission
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("diagnosis.ai_analyze", False):
        raise AuthorizationException(
            message="Insufficient permissions to use AI diagnosis",
            required_permission="diagnosis.ai_analyze"
        )
    
    # Perform AI analysis through service layer
    analysis_result = services.diagnosis.analyze_symptoms(
        analysis_data=analysis_data,
        analyzed_by=current_user["user_id"]
    )
    
    return analysis_result


@router.post("/{episode_id}/generate-differential")
async def generate_differential_diagnosis(
    episode_id: UUID = Path(..., description="Episode ID"),
    include_ai: bool = Query(True, description="Include AI-generated suggestions"),
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Generate differential diagnosis for episode
    
    Args:
        episode_id: Episode UUID
        include_ai: Whether to include AI suggestions
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Differential diagnosis list with confidence scores
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("diagnosis.create", False):
        raise AuthorizationException(
            message="Insufficient permissions to generate differential diagnosis",
            required_permission="diagnosis.create"
        )
    
    # Generate differential through service layer
    differential = services.diagnosis.generate_differential_diagnosis(
        episode_id=str(episode_id),
        include_ai=include_ai,
        generated_by=current_user["user_id"]
    )
    
    return differential


@router.post("/{diagnosis_id}/refine")
async def refine_diagnosis(
    diagnosis_id: UUID = Path(..., description="Diagnosis ID"),
    refinement_data: DiagnosisRefinement = ...,
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Refine diagnosis with additional evidence
    
    Args:
        diagnosis_id: Diagnosis UUID
        refinement_data: Additional clinical evidence
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Refined diagnosis with updated confidence
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("diagnosis.update", False):
        raise AuthorizationException(
            message="Insufficient permissions to refine diagnoses",
            required_permission="diagnosis.update"
        )
    
    # Refine diagnosis through service layer
    refined_diagnosis = services.diagnosis.refine_diagnosis(
        diagnosis_id=str(diagnosis_id),
        refinement_data=refinement_data,
        refined_by=current_user["user_id"]
    )
    
    return refined_diagnosis


# =============================================================================
# Diagnosis Clinical Operations
# =============================================================================

@router.post("/{diagnosis_id}/confirm", response_model=DiagnosisResponse)
async def confirm_diagnosis(
    diagnosis_id: UUID = Path(..., description="Diagnosis ID"),
    confirmation_data: DiagnosisConfirmation = ...,
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Confirm diagnosis as final
    
    Args:
        diagnosis_id: Diagnosis UUID
        confirmation_data: Confirmation details and evidence
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Confirmed diagnosis data
    """
    # Authorization check - requires higher privilege
    if not current_user or not current_user.get("permissions", {}).get("diagnosis.confirm", False):
        raise AuthorizationException(
            message="Insufficient permissions to confirm diagnoses",
            required_permission="diagnosis.confirm"
        )
    
    # Confirm diagnosis through service layer
    confirmed_diagnosis = services.diagnosis.confirm_diagnosis(
        diagnosis_id=str(diagnosis_id),
        confirmation_data=confirmation_data,
        confirmed_by=current_user["user_id"]
    )
    
    return confirmed_diagnosis


@router.get("/{diagnosis_id}/evidence")
async def get_diagnosis_evidence(
    diagnosis_id: UUID = Path(..., description="Diagnosis ID"),
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Get supporting evidence for diagnosis
    
    Args:
        diagnosis_id: Diagnosis UUID
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Evidence summary with sources and confidence
    """
    # Authorization check
    if not current_user:
        raise AuthenticationException(message="Authentication required")
    
    # Get evidence through service layer
    evidence = services.diagnosis.get_diagnosis_evidence(str(diagnosis_id))
    
    return evidence


@router.get("/episode/{episode_id}/differential")
async def get_episode_differential(
    episode_id: UUID = Path(..., description="Episode ID"),
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Get differential diagnosis for episode
    
    Args:
        episode_id: Episode UUID
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Current differential diagnosis list
    """
    # Authorization check
    if not current_user:
        raise AuthenticationException(message="Authentication required")
    
    # Get differential through service layer
    differential = services.diagnosis.get_episode_differential(str(episode_id))
    
    return differential


@router.post("/{diagnosis_id}/add-evidence")
async def add_supporting_evidence(
    diagnosis_id: UUID = Path(..., description="Diagnosis ID"),
    evidence_data: DiagnosisEvidence = ...,
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Add supporting evidence to diagnosis
    
    Args:
        diagnosis_id: Diagnosis UUID
        evidence_data: Evidence details
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Updated diagnosis with new evidence
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("diagnosis.update", False):
        raise AuthorizationException(
            message="Insufficient permissions to add evidence",
            required_permission="diagnosis.update"
        )
    
    # Add evidence through service layer
    updated_diagnosis = services.diagnosis.add_evidence(
        diagnosis_id=str(diagnosis_id),
        evidence_data=evidence_data,
        added_by=current_user["user_id"]
    )
    
    return updated_diagnosis


# Export router
__all__ = ["router"]