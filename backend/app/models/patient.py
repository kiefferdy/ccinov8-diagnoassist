"""
Patient Pydantic models for DiagnoAssist Backend
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field, validator
from enum import Enum


class GenderEnum(str, Enum):
    """Gender enumeration"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


class ContactInfo(BaseModel):
    """Contact information structure"""
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[Dict[str, Any]] = None


class PatientDemographics(BaseModel):
    """Patient demographic information"""
    name: str = Field(..., min_length=1, max_length=255)
    date_of_birth: date
    gender: GenderEnum
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[Dict[str, Any]] = None
    
    @validator("email")
    def validate_email(cls, v):
        if v and "@" not in v:
            raise ValueError("Invalid email format")
        return v
    
    @validator("phone")
    def validate_phone(cls, v):
        if v and len(v) < 7:
            raise ValueError("Phone number too short")
        return v


class AllergyInfo(BaseModel):
    """Allergy information structure"""
    allergen: str = Field(..., min_length=1)
    reaction: Optional[str] = None
    severity: Optional[str] = Field(None, pattern="^(mild|moderate|severe)$")
    notes: Optional[str] = None


class MedicationInfo(BaseModel):
    """Current medication information"""
    name: str = Field(..., min_length=1)
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    start_date: Optional[date] = None
    prescribing_doctor: Optional[str] = None
    notes: Optional[str] = None


class ChronicCondition(BaseModel):
    """Chronic condition information"""
    condition: str = Field(..., min_length=1)
    diagnosed_date: Optional[date] = None
    severity: Optional[str] = None
    notes: Optional[str] = None


class MedicalBackground(BaseModel):
    """Patient medical background information"""
    allergies: List[AllergyInfo] = Field(default_factory=list)
    medications: List[MedicationInfo] = Field(default_factory=list)
    chronic_conditions: List[ChronicCondition] = Field(default_factory=list)
    past_medical_history: Optional[str] = None
    family_history: Optional[str] = None
    social_history: Optional[str] = None
    
    @validator("allergies", "medications", "chronic_conditions")
    def validate_lists(cls, v):
        # Remove duplicates based on primary field
        if not v:
            return v
        return v  # Additional deduplication logic can be added here


class PatientModel(BaseModel):
    """Complete patient model for database storage"""
    id: Optional[str] = None  # Auto-generated
    demographics: PatientDemographics
    medical_background: MedicalBackground = Field(default_factory=MedicalBackground)
    fhir_patient_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
        }


# API Request/Response Models
class PatientCreateRequest(BaseModel):
    """Request model for creating a new patient"""
    demographics: PatientDemographics
    medical_background: Optional[MedicalBackground] = None


class PatientUpdateRequest(BaseModel):
    """Request model for updating a patient"""
    demographics: Optional[PatientDemographics] = None
    medical_background: Optional[MedicalBackground] = None


class PatientResponse(BaseModel):
    """Response model for patient data"""
    success: bool = True
    data: PatientModel
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PatientListResponse(BaseModel):
    """Response model for patient list"""
    success: bool = True
    data: List[PatientModel]
    total: int
    page: int = 1
    per_page: int = 50
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PatientSearchFilters(BaseModel):
    """Search filters for patient queries"""
    name: Optional[str] = None
    gender: Optional[GenderEnum] = None
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    
    @validator("age_min", "age_max")
    def validate_age(cls, v):
        if v is not None and (v < 0 or v > 150):
            raise ValueError("Age must be between 0 and 150")
        return v