"""
Patient Pydantic Schemas
"""

from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field, validator
from uuid import UUID

from .common import BaseSchema, PaginatedResponse

class PatientBase(BaseSchema):
    """Base patient schema with common fields"""
    medical_record_number: str = Field(..., min_length=1, max_length=50, description="Unique medical record number")
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: date
    gender: Optional[str] = Field(None, regex="^(male|female|other|unknown)$")
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    
    # Emergency contact
    emergency_contact_name: Optional[str] = Field(None, max_length=200)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=50)
    
    # Medical information  
    medical_history: Optional[List[str]] = Field(default_factory=list)
    allergies: Optional[List[str]] = Field(default_factory=list)
    current_medications: Optional[List[str]] = Field(default_factory=list)
    
    @validator('date_of_birth')
    def validate_birth_date(cls, v):
        if v > date.today():
            raise ValueError('Birth date cannot be in the future')
        if v < date(1900, 1, 1):
            raise ValueError('Birth date cannot be before 1900')
        return v
    
    @validator('phone', 'emergency_contact_phone')
    def validate_phone(cls, v):
        if v and not v.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '').isdigit():
            raise ValueError('Phone number must contain only digits and basic formatting')
        return v
    
    @validator('medical_record_number')
    def validate_mrn(cls, v):
        if not v or not v.strip():
            raise ValueError('Medical record number cannot be empty')
        # Remove spaces and validate format (alphanumeric with hyphens allowed)
        clean_mrn = v.strip().upper()
        if not all(c.isalnum() or c in '-_' for c in clean_mrn):
            raise ValueError('Medical record number can only contain letters, numbers, hyphens, and underscores')
        return clean_mrn

class PatientCreate(PatientBase):
    """Schema for creating a new patient"""
    pass

class PatientUpdate(BaseModel):
    """Schema for updating a patient (all fields optional)"""
    medical_record_number: Optional[str] = Field(None, min_length=1, max_length=50)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, regex="^(male|female|other|unknown)$")
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = Field(None, max_length=200)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=50)
    medical_history: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    current_medications: Optional[List[str]] = None
    active: Optional[bool] = None

class PatientResponse(PatientBase):
    """Schema for patient response with additional fields"""
    id: UUID
    full_name: str
    age: Optional[int] = None
    active: bool = True
    created_at: datetime
    updated_at: datetime
    
    # Computed fields
    episodes_count: Optional[int] = 0

class PatientListResponse(PaginatedResponse[PatientResponse]):
    """Paginated list of patients"""
    pass