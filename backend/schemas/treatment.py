"""
Treatment Pydantic Schemas
"""

from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator
from uuid import UUID

from .common import BaseSchema, PaginatedResponse

class MedicationTreatment(BaseModel):
    """Medication-specific treatment details"""
    medication_name: str = Field(..., max_length=200)
    dosage: str = Field(..., max_length=100)
    frequency: str = Field(..., max_length=100)
    route: str = Field(..., max_length=50, regex="^(oral|IV|IM|subcutaneous|topical|inhalation|rectal|other)$")
    duration: str = Field(..., max_length=100)
    contraindications: Optional[List[str]] = Field(default_factory=list)
    side_effects: Optional[List[str]] = Field(default_factory=list)
    drug_interactions: Optional[List[str]] = Field(default_factory=list)

class NonPharmacologicalTreatment(BaseModel):
    """Non-pharmacological treatment details"""
    lifestyle_modifications: Optional[List[str]] = Field(default_factory=list)
    patient_education: Optional[List[str]] = Field(default_factory=list)
    follow_up_instructions: Optional[str] = None
    monitoring_requirements: Optional[List[str]] = Field(default_factory=list)

class TreatmentBase(BaseSchema):
    """Base treatment schema"""
    treatment_type: str = Field(..., regex="^(medication|procedure|therapy|lifestyle|other)$")
    treatment_name: str = Field(..., min_length=1, max_length=300)
    description: Optional[str] = None
    instructions: Optional[str] = None
    
    # Medication details (optional, used when treatment_type = "medication")
    medication_details: Optional[MedicationTreatment] = None
    
    # Non-pharmacological details
    non_pharm_details: Optional[NonPharmacologicalTreatment] = None
    
    @validator('medication_details')
    def validate_medication_details(cls, v, values):
        if values.get('treatment_type') == 'medication' and not v:
            raise ValueError('Medication details required for medication treatments')
        return v

class TreatmentCreate(TreatmentBase):
    """Schema for creating a new treatment"""
    episode_id: UUID
    diagnosis_id: Optional[UUID] = None
    created_by: Optional[str] = "ai_system"

class TreatmentUpdate(BaseModel):
    """Schema for updating a treatment"""
    treatment_type: Optional[str] = Field(None, regex="^(medication|procedure|therapy|lifestyle|other)$")
    treatment_name: Optional[str] = Field(None, min_length=1, max_length=300)
    description: Optional[str] = None
    instructions: Optional[str] = None
    status: Optional[str] = Field(None, regex="^(planned|approved|active|completed|discontinued)$")
    approved_by: Optional[str] = Field(None, max_length=100)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    medication_details: Optional[MedicationTreatment] = None
    non_pharm_details: Optional[NonPharmacologicalTreatment] = None

class TreatmentResponse(TreatmentBase):
    """Schema for treatment response"""
    id: UUID
    episode_id: UUID
    diagnosis_id: Optional[UUID] = None
    status: str
    approved_by: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: str

class TreatmentListResponse(PaginatedResponse[TreatmentResponse]):
    """Paginated list of treatments"""
    pass