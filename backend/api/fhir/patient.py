from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import Optional, Dict, Any
from services.fhir_patient_service import FHIRPatientService
from api.dependencies import get_fhir_patient_service, get_current_user_optional
from api.exceptions import PatientNotFoundException, FHIRValidationException

router = APIRouter()

@router.post("/R4/Patient", summary="Create FHIR Patient")
async def create_patient(
    patient_data: Dict[str, Any],
    fhir_service: FHIRPatientService = Depends(get_fhir_patient_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Create a new patient using FHIR Patient resource format.
    
    Accepts standard FHIR Patient JSON and returns created patient with server-assigned ID.
    """
    try:
        created_patient = await fhir_service.create_fhir_patient(patient_data)
        return created_patient.dict()
    except ValueError as e:
        raise FHIRValidationException(str(e), "Patient")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/R4/Patient/{patient_id}", summary="Get FHIR Patient by ID")
async def get_patient(
    patient_id: str = Path(..., description="Patient resource ID"),
    fhir_service: FHIRPatientService = Depends(get_fhir_patient_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Retrieve a patient by ID in FHIR Patient resource format.
    """
    try:
        patient = await fhir_service.get_fhir_patient(patient_id)
        if not patient:
            raise PatientNotFoundException(patient_id)
        return patient.dict()
    except PatientNotFoundException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/R4/Patient/{patient_id}", summary="Update FHIR Patient")
async def update_patient(
    patient_id: str = Path(..., description="Patient resource ID"),
    patient_data: Dict[str, Any] = None,
    fhir_service: FHIRPatientService = Depends(get_fhir_patient_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Update an existing patient using FHIR Patient resource format.
    """
    try:
        updated_patient = await fhir_service.update_fhir_patient(patient_id, patient_data)
        if not updated_patient:
            raise PatientNotFoundException(patient_id)
        return updated_patient.dict()
    except PatientNotFoundException:
        raise
    except ValueError as e:
        raise FHIRValidationException(str(e), "Patient")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/R4/Patient", summary="Search FHIR Patients")
async def search_patients(
    name: Optional[str] = Query(None, description="Search by patient name"),
    given: Optional[str] = Query(None, description="Search by given name"),
    family: Optional[str] = Query(None, description="Search by family name"),
    birthdate: Optional[str] = Query(None, description="Search by birth date (YYYY-MM-DD)"),
    gender: Optional[str] = Query(None, description="Search by gender"),
    identifier: Optional[str] = Query(None, description="Search by identifier"),
    _count: Optional[int] = Query(20, ge=1, le=100, description="Number of results to return"),
    _offset: Optional[int] = Query(0, ge=0, description="Number of results to skip"),
    fhir_service: FHIRPatientService = Depends(get_fhir_patient_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Search for patients using FHIR search parameters.
    
    Returns a FHIR Bundle containing matching Patient resources.
    """
    try:
        search_params = {
            "name": name,
            "given": given,
            "family": family,
            "birthdate": birthdate,
            "gender": gender,
            "identifier": identifier,
            "_count": _count,
            "_offset": _offset
        }
        
        # Remove None values
        search_params = {k: v for k, v in search_params.items() if v is not None}
        
        bundle = await fhir_service.search_patients(search_params)
        return bundle.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/R4/Patient/{patient_id}/$everything", summary="Get Patient Everything")
async def get_patient_everything(
    patient_id: str = Path(..., description="Patient resource ID"),
    start: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    fhir_service: FHIRPatientService = Depends(get_fhir_patient_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    FHIR $everything operation - returns all resources related to a patient.
    
    Returns a Bundle containing the patient and all related resources
    (encounters, observations, diagnostic reports, etc.)
    """
    try:
        bundle = await fhir_service.get_patient_everything(
            patient_id, 
            start_date=start, 
            end_date=end
        )
        if not bundle:
            raise PatientNotFoundException(patient_id)
        return bundle.dict()
    except PatientNotFoundException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))