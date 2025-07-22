"""
Patient Pydantic Schemas
"""

from pydantic import BaseModel, validator, EmailStr
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID

class PatientBase(BaseModel):
    """Base patient fields"""
    medical_record_number: str
    first_name: str
    last_name: str
    date_of_birth: date
    gender: Optional[str] = "unknown"
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None
    medical_history: Optional[str] = ""
    allergies: Optional[str] = ""
    current_medications: Optional[str] = ""
    
    @validator('gender')
    def validate_gender(cls, v):
        if v and v not in ['male', 'female', 'other', 'unknown']:
            return 'unknown'
        return v or 'unknown'
    
    @validator('date_of_birth')
    def validate_date_of_birth(cls, v):
        if v > date.today():
            raise ValueError('Birth date cannot be in the future')
        return v

class PatientCreate(PatientBase):
    """Schema for creating a patient"""
    pass

class PatientUpdate(BaseModel):
    """Schema for updating a patient"""
    medical_record_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None
    medical_history: Optional[str] = None
    allergies: Optional[str] = None
    current_medications: Optional[str] = None

class PatientResponse(PatientBase):
    """Schema for patient responses"""
    id: UUID
    status: str = "active"
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = "system"
    
    class Config:
        from_attributes = True

class PatientListResponse(BaseModel):
    """Schema for paginated patient list"""
    data: List[PatientResponse]
    total: int
    page: int = 1
    size: int = 20