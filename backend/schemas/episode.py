"""
Episode Pydantic Schemas
"""
from pydantic import BaseModel, validator, EmailStr
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID

from .common import BaseSchema, PaginatedResponse

class VitalSigns(BaseModel):
    """Simplified vital signs"""
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    heart_rate: Optional[int] = None
    temperature: Optional[float] = None
    respiratory_rate: Optional[int] = None
    oxygen_saturation: Optional[int] = None

class EpisodeBase(BaseModel):
    """Base episode fields"""
    patient_id: UUID
    chief_complaint: str
    encounter_type: str = "outpatient"
    priority: str = "routine"
    
    # Vital signs as individual fields
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    heart_rate: Optional[int] = None
    temperature: Optional[float] = None
    respiratory_rate: Optional[int] = None
    oxygen_saturation: Optional[int] = None
    
    # Notes as simple strings
    symptoms: Optional[str] = ""
    physical_exam_findings: Optional[str] = ""
    clinical_notes: Optional[str] = ""
    assessment_notes: Optional[str] = ""
    plan_notes: Optional[str] = ""
    
    # Provider and location
    provider_id: Optional[str] = None
    location: Optional[str] = None
    
    @validator('encounter_type')
    def validate_encounter_type(cls, v):
        valid_types = ['outpatient', 'inpatient', 'emergency']
        if v not in valid_types:
            return 'outpatient'
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        valid_priorities = ['routine', 'urgent', 'emergent']
        if v not in valid_priorities:
            return 'routine'
        return v

class EpisodeCreate(EpisodeBase):
    """Schema for creating an episode"""
    pass

class EpisodeUpdate(BaseModel):
    """Schema for updating an episode"""
    chief_complaint: Optional[str] = None
    encounter_type: Optional[str] = None
    priority: Optional[str] = None
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    heart_rate: Optional[int] = None
    temperature: Optional[float] = None
    respiratory_rate: Optional[int] = None
    oxygen_saturation: Optional[int] = None
    symptoms: Optional[str] = None
    physical_exam_findings: Optional[str] = None
    clinical_notes: Optional[str] = None
    assessment_notes: Optional[str] = None
    plan_notes: Optional[str] = None
    provider_id: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None

class EpisodeResponse(EpisodeBase):
    """Schema for episode responses"""
    id: UUID
    status: str = "active"
    start_date: datetime
    end_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = "system"
    
    class Config:
        from_attributes = True

class EpisodeListResponse(BaseModel):
    """Schema for paginated episode list"""
    data: List[EpisodeResponse]
    total: int
    page: int = 1
    size: int = 20