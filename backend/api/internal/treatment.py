from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from services.treatment_service import TreatmentService
from schemas.treatment import (
    TreatmentPlanRequest,
    TreatmentPlanResponse,
    MedicationRecommendationRequest,
    MedicationRecommendationResponse
)
from api.dependencies import get_treatment_service, get_current_user_optional
from api.exceptions import InsufficientDataException, AIServiceException

router = APIRouter(prefix="/treatment")

@router.post("/plan", response_model=TreatmentPlanResponse)
async def generate_treatment_plan(
    treatment_request: TreatmentPlanRequest,
    treatment_service: TreatmentService = Depends(get_treatment_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Generate comprehensive treatment plan based on diagnosis.
    
    Provides medication recommendations, follow-up care, patient education,
    and monitoring requirements based on the confirmed diagnosis.
    """
    try:
        treatment_plan = await treatment_service.generate_treatment_plan(treatment_request)
        return treatment_plan
    except ValueError as e:
        raise InsufficientDataException(str(e))
    except Exception as e:
        raise AIServiceException(str(e))

@router.post("/medications", response_model=MedicationRecommendationResponse)
async def get_medication_recommendations(
    medication_request: MedicationRecommendationRequest,
    treatment_service: TreatmentService = Depends(get_treatment_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Get specific medication recommendations with dosing and interactions.
    
    Considers patient allergies, current medications, kidney/liver function,
    and provides appropriate dosing recommendations.
    """
    try:
        recommendations = await treatment_service.get_medication_recommendations(
            medication_request
        )
        return recommendations
    except ValueError as e:
        raise InsufficientDataException(str(e))
    except Exception as e:
        raise AIServiceException(str(e))

@router.post("/interactions/check")
async def check_drug_interactions(
    interaction_data: Dict[str, Any],  # {"medications": [...], "new_medication": "..."}
    treatment_service: TreatmentService = Depends(get_treatment_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Check for drug interactions and contraindications.
    
    Analyzes current medications against new prescriptions and identifies
    potential interactions, contraindications, and safety concerns.
    """
    try:
        if "medications" not in interaction_data:
            raise ValueError("Current medications list is required")
        
        interaction_results = await treatment_service.check_drug_interactions(
            interaction_data
        )
        return interaction_results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))