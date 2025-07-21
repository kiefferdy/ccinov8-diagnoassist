"""
Episode Pydantic Schemas
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from uuid import UUID

from .common import BaseSchema, PaginatedResponse

class VitalSigns(BaseModel):
    """Vital signs sub-schema"""
    blood_pressure_systolic: Optional[int] = Field(None, ge=50, le=300)
    blood_pressure_diastolic: Optional[int] = Field(None, ge=30, le=200) 
    heart_rate: Optional[int] = Field(None, ge=30, le=250)
    respiratory_rate: Optional[int] = Field(None, ge=5, le=60)
    temperature: Optional[float] = Field(None, ge=30.0, le=45.0)  # Celsius
    oxygen_saturation: Optional[int] = Field(None, ge=50, le=100)
    weight: Optional[float] = Field(None, ge=0, le=1000)  # kg
    height: Optional[float] = Field(None, ge=0, le=300)  # cm
    bmi: Optional[float] = Field(None, ge=10, le=100)
    
    @validator('bmi', always=True)
    def calculate_bmi(cls, v, values):
        if not v and values.get('weight') and values.get('height'):
            weight_kg = values['weight']
            height_m = values['height'] / 100
            return round(weight_kg / (height_m ** 2), 1)
        return v

class PhysicalExamFindings(BaseModel):
    """Physical examination findings sub-schema"""
    general_appearance: Optional[str] = None
    skin: Optional[str] = None
    head_neck: Optional[str] = None
    cardiovascular: Optional[str] = None
    respiratory: Optional[str] = None
    abdominal: Optional[str] = None
    neurological: Optional[str] = None
    musculoskeletal: Optional[str] = None
    psychiatric: Optional[str] = None
    additional_findings: Optional[Dict[str, Any]] = Field(default_factory=dict)

class EpisodeBase(BaseSchema):
    """Base episode schema"""
    chief_complaint: str = Field(..., min_length=1, max_length=500)
    encounter_type: str = Field("outpatient", regex="^(outpatient|inpatient|emergency)$")
    priority: str = Field("routine", regex="^(routine|urgent|emergent)$")
    provider_id: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=200)
    
    # Clinical data
    vital_signs: Optional[VitalSigns] = None
    symptoms: Optional[List[str]] = Field(default_factory=list)
    physical_exam_findings: Optional[PhysicalExamFindings] = None
    
    # Notes
    clinical_notes: Optional[str] = None
    assessment_notes: Optional[str] = None  
    plan_notes: Optional[str] = None

class EpisodeCreate(EpisodeBase):
    """Schema for creating a new episode"""
    patient_id: UUID

class EpisodeUpdate(BaseModel):
    """Schema for updating an episode"""
    chief_complaint: Optional[str] = Field(None, min_length=1, max_length=500)
    status: Optional[str] = Field(None, regex="^(in-progress|completed|cancelled)$")
    encounter_type: Optional[str] = Field(None, regex="^(outpatient|inpatient|emergency)$")
    priority: Optional[str] = Field(None, regex="^(routine|urgent|emergent)$") 
    provider_id: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=200)
    end_time: Optional[datetime] = None
    vital_signs: Optional[VitalSigns] = None
    symptoms: Optional[List[str]] = None
    physical_exam_findings: Optional[PhysicalExamFindings] = None
    clinical_notes: Optional[str] = None
    assessment_notes: Optional[str] = None
    plan_notes: Optional[str] = None

class EpisodeResponse(EpisodeBase):
    """Schema for episode response"""
    id: UUID
    patient_id: UUID
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # Counts for related data
    diagnoses_count: Optional[int] = 0
    treatments_count: Optional[int] = 0

class EpisodeListResponse(PaginatedResponse[EpisodeResponse]):
    """Paginated list of episodes"""
    pass