"""
Diagnosis Pydantic Schemas
"""

from pydantic import BaseModel, validator, EmailStr
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID

from .common import BaseSchema, PaginatedResponse

class DiagnosisBase(BaseModel):
    """Base diagnosis fields"""
    episode_id: UUID
    condition_name: str
    icd10_code: Optional[str] = None
    snomed_code: Optional[str] = None
    ai_probability: Optional[float] = None
    confidence_level: str = "low"
    ai_reasoning: Optional[str] = None
    physician_confirmed: bool = False
    physician_notes: Optional[str] = None
    final_diagnosis: bool = False
    supporting_symptoms: Optional[str] = ""
    differential_diagnoses: Optional[str] = ""
    red_flags: Optional[str] = ""
    next_steps: Optional[str] = ""
    
    @validator('ai_probability')
    def validate_probability(cls, v):
        if v is not None and (v < 0 or v > 1):
            return None
        return v
    
    @validator('confidence_level')
    def validate_confidence(cls, v):
        valid_levels = ['low', 'medium', 'high']
        if v not in valid_levels:
            return 'low'
        return v

class DiagnosisCreate(DiagnosisBase):
    """Schema for creating a diagnosis"""
    pass

class DiagnosisUpdate(BaseModel):
    """Schema for updating a diagnosis"""
    condition_name: Optional[str] = None
    icd10_code: Optional[str] = None
    snomed_code: Optional[str] = None
    ai_probability: Optional[float] = None
    confidence_level: Optional[str] = None
    ai_reasoning: Optional[str] = None
    physician_confirmed: Optional[bool] = None
    physician_notes: Optional[str] = None
    final_diagnosis: Optional[bool] = None
    supporting_symptoms: Optional[str] = None
    differential_diagnoses: Optional[str] = None
    red_flags: Optional[str] = None
    next_steps: Optional[str] = None
    status: Optional[str] = None

class DiagnosisResponse(DiagnosisBase):
    """Schema for diagnosis responses"""
    id: UUID
    status: str = "active"
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = "ai_system"
    
    class Config:
        from_attributes = True

class DiagnosisListResponse(BaseModel):
    """Schema for paginated diagnosis list"""
    data: List[DiagnosisResponse]
    total: int
    page: int = 1
    size: int = 20
