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
    diagnosis = services.diagnosis.create_diagnosis(diagnosis_data)
    
    return diagnosis


@router.get("/", response_model=DiagnosisListResponse)
async def get_diagnoses(
    services: ServiceDep,
    current_user: CurrentUserDep,
    pagination: PaginationDep,
    episode_id: Optional[UUID] = Query(None, description="Filter by episode ID"),
    patient_id: Optional[UUID] = Query(None, description="Filter by patient ID"),
    status: Optional[str] = Query(None, description="Filter by diagnosis status"),
    confidence_min: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum confidence level")
):
    """
    Get paginated list of diagnoses
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        pagination: Pagination parameters
        episode_id: Episode ID filter
        patient_id: Patient ID filter
        status: Diagnosis status filter
        confidence_min: Minimum confidence threshold
        
    Returns:
        Paginated list of diagnoses
    """
    # Authorization check
    if not current_user:
        raise AuthenticationException(message="Authentication required")
    
    # Get diagnoses through service layer
    diagnoses = services.diagnosis.get_diagnoses(
        pagination=pagination,
        episode_id=str(episode_id) if episode_id else None,
        patient_id=str(patient_id) if patient_id else None,
        status=status,
        confidence_min=confidence_min
    )
    
    return diagnoses


@router.get("/{diagnosis_id}", response_model=DiagnosisResponse)
async def get_diagnosis(
    services: ServiceDep,
    current_user: CurrentUserDep,
    diagnosis_id: UUID = Path(..., description="Diagnosis ID")
):
    """
    Get diagnosis by ID
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        diagnosis_id: Diagnosis UUID
        
    Returns:
        Diagnosis data
    """
    # Authorization check
    if not current_user:
        raise AuthenticationException(message="Authentication required")
    
    # Get diagnosis through service layer
    diagnosis = services.diagnosis.get_diagnosis(str(diagnosis_id))
    
    return diagnosis


@router.put("/{diagnosis_id}", response_model=DiagnosisResponse)
async def update_diagnosis(
    diagnosis_data: DiagnosisUpdate,
    services: ServiceDep,
    current_user: CurrentUserDep,
    diagnosis_id: UUID = Path(..., description="Diagnosis ID")
):
    """
    Update diagnosis information
    
    Args:
        diagnosis_data: Updated diagnosis data
        services: Injected services
        current_user: Current authenticated user
        diagnosis_id: Diagnosis UUID
        
    Returns:
        Updated diagnosis data
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
    services: ServiceDep,
    current_user: CurrentUserDep,
    diagnosis_id: UUID = Path(..., description="Diagnosis ID")
):
    """
    Delete diagnosis (soft delete)
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        diagnosis_id: Diagnosis UUID
        
    Returns:
        Deletion status
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
        success=True,
        message=f"Diagnosis {diagnosis_id} deleted successfully"
    )


# =============================================================================
# AI-Powered Diagnosis Operations
# =============================================================================

@router.post("/analyze-symptoms", response_model=AIAnalysisResult)
async def analyze_symptoms(
    analysis_input: SymptomAnalysisInput,
    services: ServiceDep,
    current_user: CurrentUserDep
):
    """
    AI-powered symptom analysis for differential diagnosis
    
    Args:
        analysis_input: Symptom analysis input data
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        AI analysis results with suggested diagnoses
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("diagnosis.ai_analysis", False):
        raise AuthorizationException(
            message="Insufficient permissions for AI analysis",
            required_permission="diagnosis.ai_analysis"
        )
    
    # Perform AI analysis through service layer
    analysis_result = services.diagnosis.analyze_symptoms(
        analysis_input=analysis_input,
        requested_by=current_user["user_id"]
    )
    
    return analysis_result


@router.post("/{diagnosis_id}/refine", response_model=DiagnosisResponse)
async def refine_diagnosis(
    refinement_data: DiagnosisRefinement,
    services: ServiceDep,
    current_user: CurrentUserDep,
    diagnosis_id: UUID = Path(..., description="Diagnosis ID")
):
    """
    Refine diagnosis using additional clinical data
    
    Args:
        refinement_data: Diagnosis refinement data
        services: Injected services
        current_user: Current authenticated user
        diagnosis_id: Diagnosis UUID
        
    Returns:
        Refined diagnosis data
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("diagnosis.refine", False):
        raise AuthorizationException(
            message="Insufficient permissions to refine diagnoses",
            required_permission="diagnosis.refine"
        )
    
    # Refine diagnosis through service layer
    refined_diagnosis = services.diagnosis.refine_diagnosis(
        diagnosis_id=str(diagnosis_id),
        refinement_data=refinement_data,
        refined_by=current_user["user_id"]
    )
    
    return refined_diagnosis


@router.post("/{diagnosis_id}/confirm", response_model=DiagnosisResponse)
async def confirm_diagnosis(
    confirmation_data: DiagnosisConfirmation,
    services: ServiceDep,
    current_user: CurrentUserDep,
    diagnosis_id: UUID = Path(..., description="Diagnosis ID")
):
    """
    Confirm diagnosis with clinical validation
    
    Args:
        confirmation_data: Diagnosis confirmation data
        services: Injected services
        current_user: Current authenticated user
        diagnosis_id: Diagnosis UUID
        
    Returns:
        Confirmed diagnosis data
    """
    # Authorization check
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


# =============================================================================
# Diagnosis Information and Evidence
# =============================================================================

@router.get("/{diagnosis_id}/evidence")
async def get_diagnosis_evidence(
    services: ServiceDep,
    current_user: CurrentUserDep,
    diagnosis_id: UUID = Path(..., description="Diagnosis ID")
):
    """
    Get supporting evidence for diagnosis
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        diagnosis_id: Diagnosis UUID
        
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
    services: ServiceDep,
    current_user: CurrentUserDep,
    episode_id: UUID = Path(..., description="Episode ID")
):
    """
    Get differential diagnosis for episode
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        episode_id: Episode UUID
        
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
    evidence_data: DiagnosisEvidence,
    services: ServiceDep,
    current_user: CurrentUserDep,
    diagnosis_id: UUID = Path(..., description="Diagnosis ID")
):
    """
    Add supporting evidence to diagnosis
    
    Args:
        evidence_data: Evidence details
        services: Injected services
        current_user: Current authenticated user
        diagnosis_id: Diagnosis UUID
        
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