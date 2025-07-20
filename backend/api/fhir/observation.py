from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import Optional, Dict, Any, List
from services.fhir_clinical_service import FHIRClinicalService
from api.dependencies import get_fhir_clinical_service, get_current_user_optional
from api.exceptions import FHIRValidationException

router = APIRouter()

@router.post("/R4/Observation", summary="Create FHIR Observation")
async def create_observation(
    observation_data: Dict[str, Any],
    fhir_service: FHIRClinicalService = Depends(get_fhir_clinical_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Create a new observation (vital signs, lab results, etc.) using FHIR Observation resource.
    """
    try:
        created_observation = await fhir_service.create_fhir_observation(observation_data)
        return created_observation.dict()
    except ValueError as e:
        raise FHIRValidationException(str(e), "Observation")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/R4/Observation/vital-signs", summary="Create Vital Signs Bundle")
async def create_vital_signs(
    vital_signs_data: Dict[str, Any],
    fhir_service: FHIRClinicalService = Depends(get_fhir_clinical_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Create multiple vital sign observations at once.
    
    Expected format:
    {
        "patient_id": "string",
        "encounter_id": "string",
        "vital_signs": {
            "blood_pressure_systolic": {"value": 120, "unit": "mmHg"},
            "blood_pressure_diastolic": {"value": 80, "unit": "mmHg"},
            "heart_rate": {"value": 72, "unit": "beats/min"},
            "temperature": {"value": 98.6, "unit": "F"}
        },
        "timestamp": "2025-07-20T10:30:00Z"
    }
    """
    try:
        observation_bundle = await fhir_service.create_vital_signs_bundle(vital_signs_data)
        return observation_bundle.dict()
    except ValueError as e:
        raise FHIRValidationException(str(e), "Observation")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/R4/Observation/{observation_id}", summary="Get FHIR Observation by ID")
async def get_observation(
    observation_id: str = Path(..., description="Observation resource ID"),
    fhir_service: FHIRClinicalService = Depends(get_fhir_clinical_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Retrieve an observation by ID in FHIR Observation resource format.
    """
    try:
        observation = await fhir_service.get_fhir_observation(observation_id)
        if not observation:
            raise HTTPException(status_code=404, detail="Observation not found")
        return observation.dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/R4/Observation", summary="Search FHIR Observations")
async def search_observations(
    patient: Optional[str] = Query(None, description="Patient reference"),
    encounter: Optional[str] = Query(None, description="Encounter reference"),
    category: Optional[str] = Query(None, description="Observation category"),
    code: Optional[str] = Query(None, description="Observation code (LOINC)"),
    date: Optional[str] = Query(None, description="Observation date"),
    value_quantity: Optional[str] = Query(None, description="Observation value"),
    _count: Optional[int] = Query(20, ge=1, le=100, description="Number of results"),
    _offset: Optional[int] = Query(0, ge=0, description="Results offset"),
    fhir_service: FHIRClinicalService = Depends(get_fhir_clinical_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Search for observations using FHIR search parameters.
    """
    try:
        search_params = {
            "patient": patient,
            "encounter": encounter,
            "category": category,
            "code": code,
            "date": date,
            "value-quantity": value_quantity,
            "_count": _count,
            "_offset": _offset
        }
        
        search_params = {k: v for k, v in search_params.items() if v is not None}
        
        bundle = await fhir_service.search_observations(search_params)
        return bundle.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))