"""
Diagnosis Pydantic Schemas
"""

from typing import List, Optional, Dict, Any
from datetime import datetime  
from pydantic import BaseModel, Field, validator
from uuid import UUID

from .common import BaseSchema, PaginatedResponse

class DifferentialDiagnosis(BaseModel):
    """Single differential diagnosis"""
    condition_name: str
    icd10_code: Optional[str] = None
    probability: float = Field(..., ge=0.0, le=1.0)
    reasoning: Optional[str] = None

class AIAnalysisResult(BaseModel):
    """AI analysis result for diagnosis"""
    primary_diagnosis: str
    probability: float = Field(..., ge=0.0, le=1.0) 
    confidence_level: str = Field(..., regex="^(low|moderate|high)$")
    reasoning: str
    supporting_symptoms: List[str] = Field(default_factory=list)
    differential_diagnoses: List[DifferentialDiagnosis] = Field(default_factory=list)
    red_flags: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)

class DiagnosisBase(BaseSchema):
    """Base diagnosis schema"""
    condition_name: str = Field(..., min_length=1, max_length=300)
    icd10_code: Optional[str] = Field(None, max_length=20)
    snomed_code: Optional[str] = Field(None, max_length=50)
    
    # AI analysis data
    ai_probability: Optional[float] = Field(None, ge=0.0, le=1.0)
    confidence_level: Optional[str] = Field(None, regex="^(low|moderate|high)$")
    ai_reasoning: Optional[str] = None
    
    # Supporting data
    supporting_symptoms: Optional[List[str]] = Field(default_factory=list)
    differential_diagnoses: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    red_flags: Optional[List[str]] = Field(default_factory=list)
    next_steps: Optional[List[str]] = Field(default_factory=list)

class DiagnosisCreate(DiagnosisBase):
    """Schema for creating a new diagnosis"""
    episode_id: UUID
    created_by: Optional[str] = "ai_system"

class DiagnosisUpdate(BaseModel):
    """Schema for updating a diagnosis"""
    condition_name: Optional[str] = Field(None, min_length=1, max_length=300)
    icd10_code: Optional[str] = Field(None, max_length=20)
    snomed_code: Optional[str] = Field(None, max_length=50)
    
    # AI analysis data
    ai_probability: Optional[float] = Field(None, ge=0.0, le=1.0)
    confidence_level: Optional[str] = Field(None, regex="^(low|moderate|high)$")
    ai_reasoning: Optional[str] = None
    
    # Clinical validation
    physician_confirmed: Optional[bool] = None
    physician_notes: Optional[str] = None
    final_diagnosis: Optional[bool] = None
    
    # Supporting data
    supporting_symptoms: Optional[List[str]] = None
    differential_diagnoses: Optional[List[Dict[str, Any]]] = None
    red_flags: Optional[List[str]] = None
    next_steps: Optional[List[str]] = None

class DiagnosisResponse(DiagnosisBase):
    """Schema for diagnosis response"""
    id: UUID
    episode_id: UUID
    
    # Clinical validation
    physician_confirmed: bool
    physician_notes: Optional[str] = None
    final_diagnosis: bool
    confirmed_at: Optional[datetime] = None
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    created_by: str
    
    # Computed fields
    probability_percentage: Optional[float] = None
    
    @validator('probability_percentage', always=True)
    def calculate_percentage(cls, v, values):
        if not v and values.get('ai_probability') is not None:
            return round(values['ai_probability'] * 100, 1)
        return v

class DiagnosisListResponse(PaginatedResponse[DiagnosisResponse]):
    """Paginated list of diagnoses"""
    pass