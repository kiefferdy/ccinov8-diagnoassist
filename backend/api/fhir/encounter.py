from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import Optional, Dict, Any
from services.fhir_clinical_service import FHIRClinicalService
from api.dependencies import get_fhir_clinical_service, get_current_user_optional
from api.exceptions import EpisodeNotFoundException, FHIRValidationException

router = APIRouter()

@router.post("/R4/Encounter", summary="Create FHIR Encounter")
async def create_encounter(
    encounter_data: Dict[str, Any],
    fhir_service: FHIRClinicalService = Depends(get_fhir_clinical_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Create a new encounter (medical episode) using FHIR Encounter resource format.
    """
    try:
        created_encounter = await fhir_service.create_fhir_encounter(encounter_data)
        return created_encounter.dict()
    except ValueError as e:
        raise FHIRValidationException(str(e), "Encounter")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/R4/Encounter/{encounter_id}", summary="Get FHIR Encounter by ID")
async def get_encounter(
    encounter_id: str = Path(..., description="Encounter resource ID"),
    fhir_service: FHIRClinicalService = Depends(get_fhir_clinical_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Retrieve an encounter by ID in FHIR Encounter resource format.
    """
    try:
        encounter = await fhir_service.get_fhir_encounter(encounter_id)
        if not encounter:
            raise EpisodeNotFoundException(encounter_id)
        return encounter.dict()
    except EpisodeNotFoundException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/R4/Encounter", summary="Search FHIR Encounters")
async def search_encounters(
    patient: Optional[str] = Query(None, description="Patient reference (Patient/[id])"),
    date: Optional[str] = Query(None, description="Encounter date"),
    class_: Optional[str] = Query(None, alias="class", description="Encounter class"),
    status: Optional[str] = Query(None, description="Encounter status"),
    _count: Optional[int] = Query(20, ge=1, le=100, description="Number of results"),
    _offset: Optional[int] = Query(0, ge=0, description="Results offset"),
    fhir_service: FHIRClinicalService = Depends(get_fhir_clinical_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Search for encounters using FHIR search parameters.
    """
    try:
        search_params = {
            "patient": patient,
            "date": date,
            "class": class_,
            "status": status,
            "_count": _count,
            "_offset": _offset
        }
        
        search_params = {k: v for k, v in search_params.items() if v is not None}
        
        bundle = await fhir_service.search_encounters(search_params)
        return bundle.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
