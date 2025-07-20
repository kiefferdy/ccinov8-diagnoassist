from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from services.diagnosis_service import DiagnosisService
from schemas.diagnosis import (
    DiagnosisRequest,
    DifferentialDiagnosisResponse,
    DiagnosisRefinementRequest,
    RefinedDiagnosisResponse
)
from api.dependencies import get_diagnosis_service, get_current_user_optional
from api.exceptions import InsufficientDataException, AIServiceException

router = APIRouter(prefix="/diagnosis")

@router.post("/analyze", response_model=DifferentialDiagnosisResponse)
async def generate_differential_diagnosis(
    diagnosis_request: DiagnosisRequest,
    diagnosis_service: DiagnosisService = Depends(get_diagnosis_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Generate differential diagnosis using AI analysis.
    
    Analyzes symptoms, physical exam findings, and vital signs to suggest
    possible diagnoses with confidence scores and supporting evidence.
    """
    try:
        differential = await diagnosis_service.generate_differential_diagnosis(
            episode_id=diagnosis_request.episode_id,
            symptoms=diagnosis_request.symptoms,
            physical_exam=diagnosis_request.physical_exam,
            vital_signs=diagnosis_request.vital_signs
        )
        return differential
    except ValueError as e:
        raise InsufficientDataException(str(e))
    except Exception as e:
        raise AIServiceException(str(e))

@router.post("/refine", response_model=RefinedDiagnosisResponse)
async def refine_diagnosis_with_tests(
    refinement_request: DiagnosisRefinementRequest,
    diagnosis_service: DiagnosisService = Depends(get_diagnosis_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Refine existing diagnosis based on new test results.
    
    Updates confidence scores and diagnosis ranking based on lab results,
    imaging findings, or other diagnostic test outcomes.
    """
    try:
        refined_diagnosis = await diagnosis_service.refine_diagnosis_with_tests(
            diagnosis_id=refinement_request.diagnosis_id,
            test_results=refinement_request.test_results
        )
        return refined_diagnosis
    except ValueError as e:
        raise InsufficientDataException(str(e))
    except Exception as e:
        raise AIServiceException(str(e))

@router.get("/{diagnosis_id}/explanation")
async def get_diagnosis_explanation(
    diagnosis_id: str,
    diagnosis_service: DiagnosisService = Depends(get_diagnosis_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Get detailed explanation of how AI arrived at the diagnosis.
    
    Provides reasoning, key factors considered, and educational information
    about the suggested diagnoses.
    """
    try:
        explanation = await diagnosis_service.get_diagnosis_explanation(diagnosis_id)
        if not explanation:
            raise HTTPException(status_code=404, detail="Diagnosis not found")
        return explanation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate")
async def validate_diagnosis_data(
    validation_data: Dict[str, Any],
    diagnosis_service: DiagnosisService = Depends(get_diagnosis_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Validate diagnosis data for completeness and consistency.
    
    Checks if provided clinical data is sufficient for reliable diagnosis
    and suggests additional information that might be needed.
    """
    try:
        validation_result = await diagnosis_service.validate_diagnosis_data(validation_data)
        return validation_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))