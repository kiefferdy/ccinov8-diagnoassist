"""
Diagnosis API Router for DiagnoAssist - CLEAN VERSION
CRUD operations for diagnosis management with AI integration
"""

from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from typing import List, Optional
from uuid import UUID

# Import dependencies - FIXED: Import directly from the module
from api.dependencies import get_service_manager, get_current_user, PaginationParams

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

# Create router
router = APIRouter(prefix="/diagnoses", tags=["diagnoses"])

# Create dependency aliases properly
ServiceDep = Depends(get_service_manager)
CurrentUserDep = Depends(get_current_user)
PaginationDep = Depends(PaginationParams)

# =============================================================================
# Diagnosis CRUD Operations
# =============================================================================

@router.post("/", response_model=DiagnosisResponse, status_code=201)
async def create_diagnosis(
    diagnosis_data: DiagnosisCreate,
    services = ServiceDep,
    current_user = CurrentUserDep
):
    """
    Create a new diagnosis
    
    Args:
        diagnosis_data: Diagnosis creation data
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Created diagnosis data
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("diagnosis.create", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create diagnoses"
        )
    
    try:
        # Create diagnosis through service layer
        diagnosis = services.diagnosis.create_diagnosis(diagnosis_data)
        return diagnosis
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
                detail=f"Failed to create diagnosis: {error_message}"
            )


@router.get("/", response_model=DiagnosisListResponse)
async def get_diagnoses(
    services = ServiceDep,
    current_user = CurrentUserDep,
    pagination = PaginationDep,
    episode_id: Optional[UUID] = Query(None, description="Filter by episode ID"),
    patient_id: Optional[UUID] = Query(None, description="Filter by patient ID"),
    status_filter: Optional[str] = Query(None, description="Filter by diagnosis status"),
    confidence_min: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum confidence level"),
    final_only: Optional[bool] = Query(False, description="Only final diagnoses")
):
    """
    Get paginated list of diagnoses
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        pagination: Pagination parameters
        episode_id: Episode ID filter
        patient_id: Patient ID filter
        status_filter: Diagnosis status filter
        confidence_min: Minimum confidence threshold
        final_only: Only return final diagnoses
        
    Returns:
        Paginated list of diagnoses
    """
    # Authorization check
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        # Get diagnoses through service layer
        diagnoses = services.diagnosis.get_diagnoses(
            pagination=pagination,
            episode_id=str(episode_id) if episode_id else None,
            patient_id=str(patient_id) if patient_id else None,
            status=status_filter,
            confidence_min=confidence_min,
            final_only=final_only
        )
        
        return diagnoses
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve diagnoses: {str(e)}"
        )


@router.get("/{diagnosis_id}", response_model=DiagnosisResponse)
async def get_diagnosis(
    services = ServiceDep,
    current_user = CurrentUserDep,
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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        # Get diagnosis through service layer
        diagnosis = services.diagnosis.get_diagnosis(str(diagnosis_id))
        return diagnosis
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Diagnosis {diagnosis_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve diagnosis: {error_message}"
            )


@router.put("/{diagnosis_id}", response_model=DiagnosisResponse)
async def update_diagnosis(
    diagnosis_data: DiagnosisUpdate,
    services = ServiceDep,
    current_user = CurrentUserDep,
    diagnosis_id: UUID = Path(..., description="Diagnosis ID")
):
    """
    Update diagnosis information
    
    Args:
        diagnosis_data: Diagnosis update data
        services: Injected services
        current_user: Current authenticated user
        diagnosis_id: Diagnosis UUID
        
    Returns:
        Updated diagnosis data
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("diagnosis.update", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update diagnoses"
        )
    
    try:
        # Update diagnosis through service layer
        updated_diagnosis = services.diagnosis.update_diagnosis(
            diagnosis_id=str(diagnosis_id),
            diagnosis_data=diagnosis_data,
            updated_by=current_user["user_id"]
        )
        
        return updated_diagnosis
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Diagnosis {diagnosis_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update diagnosis: {error_message}"
            )


@router.delete("/{diagnosis_id}", response_model=StatusResponse)
async def delete_diagnosis(
    services = ServiceDep,
    current_user = CurrentUserDep,
    diagnosis_id: UUID = Path(..., description="Diagnosis ID")
):
    """
    Delete diagnosis (soft delete)
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        diagnosis_id: Diagnosis UUID
        
    Returns:
        Success status
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("diagnosis.delete", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete diagnoses"
        )
    
    try:
        # Delete diagnosis through service layer
        services.diagnosis.delete_diagnosis(
            diagnosis_id=str(diagnosis_id),
            deleted_by=current_user["user_id"]
        )
        
        return StatusResponse(
            status="success",
            message=f"Diagnosis {diagnosis_id} deleted successfully"
        )
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Diagnosis {diagnosis_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete diagnosis: {error_message}"
            )


# =============================================================================
# AI-powered Diagnosis Operations
# =============================================================================

@router.post("/analyze-symptoms", response_model=AIAnalysisResult)
async def analyze_symptoms(
    symptom_data: SymptomAnalysisInput,
    services = ServiceDep,
    current_user = CurrentUserDep
):
    """
    Analyze symptoms using AI to suggest diagnoses
    
    Args:
        symptom_data: Symptom analysis input
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        AI analysis results with suggested diagnoses
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("diagnosis.create", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to analyze symptoms"
        )
    
    try:
        # Analyze symptoms through service layer
        analysis = services.diagnosis.analyze_symptoms(symptom_data)
        return analysis
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
                detail=f"Failed to analyze symptoms: {error_message}"
            )


@router.post("/{diagnosis_id}/confirm", response_model=DiagnosisResponse)
async def confirm_diagnosis(
    confirmation_data: DiagnosisConfirmation,
    services = ServiceDep,
    current_user = CurrentUserDep,
    diagnosis_id: UUID = Path(..., description="Diagnosis ID")
):
    """
    Confirm a diagnosis as final
    
    Args:
        confirmation_data: Diagnosis confirmation data
        services: Injected services
        current_user: Current authenticated user
        diagnosis_id: Diagnosis UUID
        
    Returns:
        Confirmed diagnosis data
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("diagnosis.update", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to confirm diagnoses"
        )
    
    try:
        # Confirm diagnosis through service layer
        confirmed_diagnosis = services.diagnosis.confirm_diagnosis(
            diagnosis_id=str(diagnosis_id),
            confirmation_data=confirmation_data,
            confirmed_by=current_user["user_id"]
        )
        
        return confirmed_diagnosis
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Diagnosis {diagnosis_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to confirm diagnosis: {error_message}"
            )


@router.post("/{diagnosis_id}/refine", response_model=DiagnosisResponse)
async def refine_diagnosis(
    refinement_data: DiagnosisRefinement,
    services = ServiceDep,
    current_user = CurrentUserDep,
    diagnosis_id: UUID = Path(..., description="Diagnosis ID")
):
    """
    Refine a diagnosis with additional evidence
    
    Args:
        refinement_data: Diagnosis refinement data
        services: Injected services
        current_user: Current authenticated user
        diagnosis_id: Diagnosis UUID
        
    Returns:
        Refined diagnosis data
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("diagnosis.update", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to refine diagnoses"
        )
    
    try:
        # Refine diagnosis through service layer
        refined_diagnosis = services.diagnosis.refine_diagnosis(
            diagnosis_id=str(diagnosis_id),
            refinement_data=refinement_data,
            refined_by=current_user["user_id"]
        )
        
        return refined_diagnosis
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Diagnosis {diagnosis_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to refine diagnosis: {error_message}"
            )

# Export router
__all__ = ["router"]