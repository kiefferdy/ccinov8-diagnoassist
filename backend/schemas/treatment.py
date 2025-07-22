"""
Treatment Pydantic Schemas
"""

from pydantic import BaseModel, validator, EmailStr
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID

from .common import BaseSchema, PaginatedResponse

class TreatmentBase(BaseModel):
    """Base treatment fields"""
    episode_id: UUID
    diagnosis_id: Optional[UUID] = None
    treatment_type: str = "medication"
    name: str
    description: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    route: Optional[str] = None
    duration: Optional[str] = None
    instructions: Optional[str] = None
    monitoring_requirements: Optional[str] = ""
    contraindications: Optional[str] = ""
    side_effects: Optional[str] = ""
    drug_interactions: Optional[str] = ""
    lifestyle_modifications: Optional[str] = ""
    follow_up_instructions: Optional[str] = ""
    patient_education: Optional[str] = ""
    prescriber: Optional[str] = None
    approved_by: Optional[str] = None

class TreatmentCreate(TreatmentBase):
    """Schema for creating a treatment"""
    pass

class TreatmentUpdate(BaseModel):
    """Schema for updating a treatment"""
    treatment_type: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    route: Optional[str] = None
    duration: Optional[str] = None
    instructions: Optional[str] = None
    monitoring_requirements: Optional[str] = None
    contraindications: Optional[str] = None
    side_effects: Optional[str] = None
    drug_interactions: Optional[str] = None
    lifestyle_modifications: Optional[str] = None
    follow_up_instructions: Optional[str] = None
    patient_education: Optional[str] = None
    prescriber: Optional[str] = None
    approved_by: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class TreatmentResponse(TreatmentBase):
    """Schema for treatment responses"""
    id: UUID
    status: str = "active"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = "system"
    
    class Config:
        from_attributes = True

class TreatmentListResponse(BaseModel):
    """Schema for paginated treatment list"""
    data: List[TreatmentResponse]
    total: int
    page: int = 1
    size: int = 20