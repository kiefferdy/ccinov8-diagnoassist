"""
Diagnosis API Router for DiagnoAssist - IMPORT FIXED VERSION
CRUD operations for diagnosis management with AI integration
"""

from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from typing import List, Optional
from uuid import UUID

# Force fresh import to avoid caching issues
from api.dependencies import get_service_manager
from fastapi import Depends

# Create fresh ServiceDep to avoid cached version
ServiceDep = Depends(get_service_manager)

# Import other dependencies normally
from api.dependencies import CurrentUserDep, PaginationDep

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
    # Authorization check (commented out for MVP)
    # if not current_user or not current_user.get("permissions", {}).get("diagnosis.create", False):
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Insufficient permissions to create diagnoses"
    #     )
    
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
    patient_id: Optional[UUID] = Query(None, description="Filter by patient ID"),
    episode_id: Optional[UUID] = Query(None, description="Filter by episode ID"),
    final_only: Optional[bool] = Query(False, description="Show only final diagnoses"),
    confirmed_only: Optional[bool] = Query(False, description="Show only physician-confirmed diagnoses")
):
    """
    Get paginated list of diagnoses
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        pagination: Pagination parameters
        patient_id: Patient ID filter
        episode_id: Episode ID filter
        final_only: Show only final diagnoses
        confirmed_only: Show only physician-confirmed diagnoses
        
    Returns:
        Paginated list of diagnoses
    """
    # Authorization check (commented out for MVP)
    # if not current_user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Authentication required",
    #         headers={"WWW-Authenticate": "Bearer"}
    #     )
    
    try:
        # Get diagnoses through service layer using search_diagnoses method
        diagnoses = services.diagnosis.search_diagnoses(
            query=None,  # No text search query
            episode_id=str(episode_id) if episode_id else None,
            patient_id=str(patient_id) if patient_id else None,
            confidence_level=None,  # All confidence levels
            final_only=final_only,
            skip=getattr(pagination, 'skip', 0) if pagination else 0,
            limit=getattr(pagination, 'limit', 100) if pagination else 100
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
    # Authorization check (commented out for MVP)
    # if not current_user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Authentication required",
    #         headers={"WWW-Authenticate": "Bearer"}
    #     )
    
    try:
        # Get diagnosis through service layer
        diagnosis = services.diagnosis.get_diagnosis(str(diagnosis_id))
        
        if not diagnosis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Diagnosis with ID {diagnosis_id} not found"
            )
        
        return diagnosis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve diagnosis: {str(e)}"
        )

@router.put("/{diagnosis_id}", response_model=DiagnosisResponse)
async def update_diagnosis(
    services = ServiceDep,
    current_user = CurrentUserDep,
    diagnosis_id: UUID = Path(..., description="Diagnosis ID"),
    diagnosis_data: DiagnosisUpdate = ...
):
    """
    Update diagnosis
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        diagnosis_id: Diagnosis UUID
        diagnosis_data: Diagnosis update data
        
    Returns:
        Updated diagnosis data
    """
    # Authorization check (commented out for MVP)
    # if not current_user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Authentication required",
    #         headers={"WWW-Authenticate": "Bearer"}
    #     )
    
    try:
        # Update diagnosis through service layer
        diagnosis = services.diagnosis.update_diagnosis(str(diagnosis_id), diagnosis_data)
        
        if not diagnosis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Diagnosis with ID {diagnosis_id} not found"
            )
        
        return diagnosis
    except HTTPException:
        raise
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Diagnosis with ID {diagnosis_id} not found"
            )
        elif "validation" in error_message.lower() or "invalid" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error_message
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
    Delete diagnosis
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        diagnosis_id: Diagnosis UUID
        
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
        # Delete diagnosis through service layer
        success = services.diagnosis.delete_diagnosis(str(diagnosis_id))
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Diagnosis with ID {diagnosis_id} not found"
            )
        
        return StatusResponse(
            status="success",
            message=f"Diagnosis {diagnosis_id} deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Diagnosis with ID {diagnosis_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete diagnosis: {error_message}"
            )

# =============================================================================
# AI-Enhanced Diagnosis Endpoints
# =============================================================================

@router.post("/analyze-symptoms", response_model=AIAnalysisResult)
async def analyze_symptoms(
    services = ServiceDep,
    current_user = CurrentUserDep,
    symptom_input: SymptomAnalysisInput = ...
):
    """
    Analyze symptoms using AI to suggest diagnoses
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        symptom_input: Symptom analysis input data
        
    Returns:
        AI analysis results with suggested diagnoses
    """
    try:
        # Analyze symptoms through service layer
        analysis = services.diagnosis.analyze_symptoms(symptom_input)
        return analysis
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze symptoms: {str(e)}"
        )

@router.patch("/{diagnosis_id}/confirm", response_model=DiagnosisResponse)
async def confirm_diagnosis(
    services = ServiceDep,
    current_user = CurrentUserDep,
    diagnosis_id: UUID = Path(..., description="Diagnosis ID"),
    confirmation: DiagnosisConfirmation = ...
):
    """
    Confirm a diagnosis (physician confirmation)
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        diagnosis_id: Diagnosis UUID
        confirmation: Diagnosis confirmation data
        
    Returns:
        Updated diagnosis data
    """
    try:
        # Confirm diagnosis through service layer
        diagnosis = services.diagnosis.confirm_diagnosis(str(diagnosis_id), confirmation)
        return diagnosis
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Diagnosis with ID {diagnosis_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to confirm diagnosis: {error_message}"
            )

@router.patch("/{diagnosis_id}/refine", response_model=DiagnosisResponse)
async def refine_diagnosis(
    services = ServiceDep,
    current_user = CurrentUserDep,
    diagnosis_id: UUID = Path(..., description="Diagnosis ID"),
    refinement: DiagnosisRefinement = ...
):
    """
    Refine a diagnosis with additional evidence
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        diagnosis_id: Diagnosis UUID
        refinement: Diagnosis refinement data
        
    Returns:
        Updated diagnosis data
    """
    try:
        # Refine diagnosis through service layer
        diagnosis = services.diagnosis.refine_diagnosis(str(diagnosis_id), refinement)
        return diagnosis
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Diagnosis with ID {diagnosis_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to refine diagnosis: {error_message}"
            )

@router.get("/{diagnosis_id}/differential")
async def get_differential_diagnoses(
    services = ServiceDep,
    current_user = CurrentUserDep,
    diagnosis_id: UUID = Path(..., description="Diagnosis ID")
):
    """
    Get differential diagnoses for a primary diagnosis
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        diagnosis_id: Diagnosis UUID
        
    Returns:
        List of differential diagnoses
    """
    try:
        # Get differential diagnoses through service layer
        differentials = services.diagnosis.get_differential_diagnoses(str(diagnosis_id))
        return differentials
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Diagnosis with ID {diagnosis_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve differential diagnoses: {error_message}"
            )

@router.patch("/{diagnosis_id}/finalize", response_model=DiagnosisResponse)
async def finalize_diagnosis(
    services = ServiceDep,
    current_user = CurrentUserDep,
    diagnosis_id: UUID = Path(..., description="Diagnosis ID")
):
    """
    Finalize a diagnosis (mark as final diagnosis)
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        diagnosis_id: Diagnosis UUID
        
    Returns:
        Updated diagnosis data
    """
    try:
        # Finalize diagnosis through service layer
        diagnosis = services.diagnosis.finalize_diagnosis(str(diagnosis_id))
        return diagnosis
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Diagnosis with ID {diagnosis_id} not found"
            )
        elif "cannot finalize" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to finalize diagnosis: {error_message}"
            )