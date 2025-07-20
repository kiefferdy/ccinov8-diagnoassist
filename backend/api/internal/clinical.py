from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from services.clinical_service import ClinicalService
from schemas.clinical import (
    ClinicalAssessmentRequest, 
    DynamicQuestionsResponse,
    ClinicalDataRequest,
    ClinicalAnalysisResponse
)
from api.dependencies import get_clinical_service, get_current_user_optional
from api.exceptions import InsufficientDataException, AIServiceException

router = APIRouter(prefix="/clinical")

@router.post("/assessment/questions", response_model=DynamicQuestionsResponse)
async def get_dynamic_questions(
    assessment_data: ClinicalAssessmentRequest,
    clinical_service: ClinicalService = Depends(get_clinical_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Generate dynamic questions based on chief complaint and existing data.
    
    Uses AI to determine the most relevant follow-up questions.
    """
    try:
        questions = await clinical_service.generate_dynamic_questions(assessment_data)
        return questions
    except ValueError as e:
        raise InsufficientDataException(str(e))
    except Exception as e:
        raise AIServiceException(str(e))

@router.post("/assessment/analyze", response_model=ClinicalAnalysisResponse)
async def analyze_clinical_data(
    clinical_data: ClinicalDataRequest,
    clinical_service: ClinicalService = Depends(get_clinical_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Analyze clinical assessment data and provide insights.
    
    Identifies patterns, suggests additional questions, and highlights important findings.
    """
    try:
        analysis = await clinical_service.analyze_clinical_data(clinical_data)
        return analysis
    except ValueError as e:
        raise InsufficientDataException(str(e))
    except Exception as e:
        raise AIServiceException(str(e))

@router.post("/symptoms/extract")
async def extract_symptoms_from_text(
    text_data: Dict[str, str],  # {"text": "patient complains of..."}
    clinical_service: ClinicalService = Depends(get_clinical_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Extract structured symptoms from free text using NLP.
    
    Useful for processing transcribed patient interviews or clinical notes.
    """
    try:
        if "text" not in text_data:
            raise ValueError("Text field is required")
        
        extracted_symptoms = await clinical_service.extract_symptoms_from_text(
            text_data["text"]
        )
        return extracted_symptoms
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise AIServiceException(str(e))