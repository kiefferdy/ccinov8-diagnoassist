from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from services.patient_service import PatientService
from schemas.patient import PatientCreate, PatientUpdate, PatientResponse, PatientSummary
from api.dependencies import get_patient_service, get_current_user_optional
from api.exceptions import PatientNotFoundException

router = APIRouter(prefix="/patients")

@router.post("/", response_model=PatientResponse, summary="Create Patient")
async def create_patient(
    patient_data: PatientCreate,
    patient_service: PatientService = Depends(get_patient_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Create a new patient using simplified internal format.
    """
    try:
        created_patient = await patient_service.create_patient(patient_data)
        return created_patient
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{patient_id}", response_model=PatientResponse, summary="Get Patient")
async def get_patient(
    patient_id: str,
    patient_service: PatientService = Depends(get_patient_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Get patient by ID using internal format.
    """
    try:
        patient = await patient_service.get_patient(patient_id)
        if not patient:
            raise PatientNotFoundException(patient_id)
        return patient
    except PatientNotFoundException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{patient_id}", response_model=PatientResponse, summary="Update Patient")
async def update_patient(
    patient_id: str,
    patient_data: PatientUpdate,
    patient_service: PatientService = Depends(get_patient_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Update existing patient.
    """
    try:
        updated_patient = await patient_service.update_patient(patient_id, patient_data)
        if not updated_patient:
            raise PatientNotFoundException(patient_id)
        return updated_patient
    except PatientNotFoundException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[PatientResponse], summary="List Patients")
async def list_patients(
    skip: int = Query(0, ge=0, description="Number of patients to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of patients to return"),
    search: Optional[str] = Query(None, description="Search by name"),
    patient_service: PatientService = Depends(get_patient_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    List patients with optional search and pagination.
    """
    try:
        patients = await patient_service.list_patients(
            skip=skip, 
            limit=limit, 
            search=search
        )
        return patients
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{patient_id}/summary", response_model=PatientSummary, summary="Get Patient Summary")
async def get_patient_summary(
    patient_id: str,
    patient_service: PatientService = Depends(get_patient_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Get comprehensive patient summary including recent episodes and statistics.
    """
    try:
        summary = await patient_service.get_patient_summary(patient_id)
        if not summary:
            raise PatientNotFoundException(patient_id)
        return summary
    except PatientNotFoundException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{patient_id}", summary="Delete Patient")
async def delete_patient(
    patient_id: str,
    patient_service: PatientService = Depends(get_patient_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Delete patient and all associated data.
    """
    try:
        success = await patient_service.delete_patient(patient_id)
        if not success:
            raise PatientNotFoundException(patient_id)
        return {"message": "Patient deleted successfully"}
    except PatientNotFoundException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))