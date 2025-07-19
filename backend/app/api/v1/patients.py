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

# Import repository
from app.repositories.patient_repository import patient_repository


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
    
    # Calculate skip for pagination
    skip = (page - 1) * per_page
    
    # Get filtered patients from repository
    patients = await patient_repository.get_by_demographics_filter(
        name=name,
        gender=gender,
        email=email,
        skip=skip,
        limit=per_page
    )
    
    # Get total count for pagination
    total = await patient_repository.count()
    
    return PatientListResponse(
        data=patients,
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
        existing_patient = await patient_repository.get_by_email(request.demographics.email)
        if existing_patient:
            raise ValidationException(
                "Patient with this email already exists",
                {"email": request.demographics.email}
            )
    
    # Create new patient
    from app.models.patient import MedicalBackground
    new_patient = PatientModel(
        demographics=request.demographics,
        medical_background=request.medical_background or MedicalBackground(),
    )
    
    # Store patient in database
    created_patient = await patient_repository.create(new_patient)
    
    return PatientResponse(data=created_patient)


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: str,
    current_user: CurrentUser = Depends(require_patient_read),
):
    """Get a patient by ID"""
    
    patient = await patient_repository.get_by_id(patient_id)
    
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
    
    # Get patient
    patient = await patient_repository.get_by_id(patient_id)
    
    if not patient:
        raise NotFoundError("Patient", patient_id)
    
    # Check for email conflicts (if updating email)
    if request.demographics and request.demographics.email:
        existing_patient = await patient_repository.get_by_email(request.demographics.email)
        if existing_patient and existing_patient.id != patient_id:
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
    
    # Update in database
    updated_patient = await patient_repository.update(patient_id, patient)
    
    return PatientResponse(data=updated_patient)


@router.delete("/{patient_id}")
async def delete_patient(
    patient_id: str,
    current_user: CurrentUser = Depends(require_patient_delete),
):
    """Delete a patient"""
    
    # Get patient first to verify it exists
    patient = await patient_repository.get_by_id(patient_id)
    
    if not patient:
        raise NotFoundError("Patient", patient_id)
    
    # Delete patient
    await patient_repository.delete(patient_id)
    
    return {
        "success": True,
        "message": f"Patient {patient.id} deleted successfully",
        "timestamp": datetime.utcnow()
    }