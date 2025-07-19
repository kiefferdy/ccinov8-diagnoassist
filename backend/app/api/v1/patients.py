"""
Patient API endpoints for DiagnoAssist Backend
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from datetime import datetime

from app.models.patient import (
    PatientModel,
    PatientCreateRequest,
    PatientUpdateRequest,
    PatientResponse,
    PatientListResponse,
    PatientSearchFilters
)
from app.models.auth import CurrentUser
from app.middleware.auth_middleware import (
    require_patient_read, require_patient_write, 
    require_patient_update, require_patient_delete
)
from app.core.exceptions import NotFoundError, ValidationException

router = APIRouter()

# In-memory storage for Phase 1 (will be replaced with database in Phase 3)
patients_storage: List[PatientModel] = []
patient_counter = 1


def generate_patient_id() -> str:
    """Generate a unique patient ID"""
    global patient_counter
    patient_id = f"P{patient_counter:03d}"
    patient_counter += 1
    return patient_id


@router.get("/", response_model=PatientListResponse)
async def get_patients(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    name: Optional[str] = Query(None),
    gender: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    current_user: CurrentUser = Depends(require_patient_read),
):
    """Get list of patients with optional filtering and pagination"""
    
    # Apply filters
    filtered_patients = patients_storage
    
    if name:
        filtered_patients = [
            p for p in filtered_patients 
            if name.lower() in p.demographics.name.lower()
        ]
    
    if gender:
        filtered_patients = [
            p for p in filtered_patients 
            if p.demographics.gender == gender
        ]
    
    if email:
        filtered_patients = [
            p for p in filtered_patients 
            if p.demographics.email and email.lower() in p.demographics.email.lower()
        ]
    
    # Apply pagination
    total = len(filtered_patients)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_patients = filtered_patients[start_idx:end_idx]
    
    return PatientListResponse(
        data=paginated_patients,
        total=total,
        page=page,
        per_page=per_page
    )


@router.post("/", response_model=PatientResponse)
async def create_patient(
    request: PatientCreateRequest,
    current_user: CurrentUser = Depends(require_patient_write),
):
    """Create a new patient"""
    
    # Check for duplicate email
    if request.demographics.email:
        existing_patient = next(
            (p for p in patients_storage if p.demographics.email == request.demographics.email),
            None
        )
        if existing_patient:
            raise ValidationException(
                "Patient with this email already exists",
                {"email": request.demographics.email}
            )
    
    # Create new patient
    now = datetime.utcnow()
    from app.models.patient import MedicalBackground
    new_patient = PatientModel(
        id=generate_patient_id(),
        demographics=request.demographics,
        medical_background=request.medical_background or MedicalBackground(),
        created_at=now,
        updated_at=now
    )
    
    # Store patient
    patients_storage.append(new_patient)
    
    return PatientResponse(data=new_patient)


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: str,
    current_user: CurrentUser = Depends(require_patient_read),
):
    """Get a patient by ID"""
    
    patient = next(
        (p for p in patients_storage if p.id == patient_id),
        None
    )
    
    if not patient:
        raise NotFoundError("Patient", patient_id)
    
    return PatientResponse(data=patient)


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: str, 
    request: PatientUpdateRequest,
    current_user: CurrentUser = Depends(require_patient_update),
):
    """Update an existing patient"""
    
    # Find patient
    patient_index = next(
        (i for i, p in enumerate(patients_storage) if p.id == patient_id),
        None
    )
    
    if patient_index is None:
        raise NotFoundError("Patient", patient_id)
    
    patient = patients_storage[patient_index]
    
    # Check for email conflicts (if updating email)
    if request.demographics and request.demographics.email:
        existing_patient = next(
            (p for p in patients_storage 
             if p.demographics.email == request.demographics.email and p.id != patient_id),
            None
        )
        if existing_patient:
            raise ValidationException(
                "Patient with this email already exists",
                {"email": request.demographics.email}
            )
    
    # Update patient data
    if request.demographics:
        patient.demographics = request.demographics
    
    if request.medical_background:
        patient.medical_background = request.medical_background
    
    patient.updated_at = datetime.utcnow()
    
    # Update in storage
    patients_storage[patient_index] = patient
    
    return PatientResponse(data=patient)


@router.delete("/{patient_id}")
async def delete_patient(
    patient_id: str,
    current_user: CurrentUser = Depends(require_patient_delete),
):
    """Delete a patient"""
    
    # Find patient
    patient_index = next(
        (i for i, p in enumerate(patients_storage) if p.id == patient_id),
        None
    )
    
    if patient_index is None:
        raise NotFoundError("Patient", patient_id)
    
    # Remove patient
    deleted_patient = patients_storage.pop(patient_index)
    
    return {
        "success": True,
        "message": f"Patient {deleted_patient.id} deleted successfully",
        "timestamp": datetime.utcnow()
    }