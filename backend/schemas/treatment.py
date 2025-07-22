"""
Treatment Pydantic Schemas - Matches SQL Schema Exactly
"""

from pydantic import BaseModel, validator, Field
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID

class TreatmentBase(BaseModel):
    """Base treatment fields - matches SQL exactly"""
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
    
    # Simple text fields as per SQL schema
    monitoring_requirements: Optional[str] = ""
    contraindications: Optional[str] = ""
    side_effects: Optional[str] = ""
    drug_interactions: Optional[str] = ""
    lifestyle_modifications: Optional[str] = ""
    follow_up_instructions: Optional[str] = ""
    patient_education: Optional[str] = ""
    
    # Additional fields from SQL
    prescriber: Optional[str] = None
    approved_by: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class TreatmentCreate(TreatmentBase):
    """Schema for creating a treatment"""
    pass

class TreatmentUpdate(BaseModel):
    """Schema for updating a treatment"""
    diagnosis_id: Optional[UUID] = None
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
    """Schema for treatment responses - matches SQL exactly"""
    id: UUID
    status: str = "active"
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

# Specific treatment type schemas for compatibility
class MedicationTreatment(BaseModel):
    """Schema for medication-specific treatments"""
    name: str  # Changed from medication_name to match SQL schema
    dosage: str
    frequency: str
    route: str = "oral"
    duration: Optional[str] = None
    instructions: Optional[str] = None
    side_effects: Optional[str] = None
    contraindications: Optional[str] = None
    drug_interactions: Optional[str] = None

class NonPharmacologicalTreatment(BaseModel):
    """Schema for non-medication treatments"""
    name: str  # Changed from treatment_name to match SQL schema
    treatment_type: str = Field(..., pattern="^(therapy|procedure|lifestyle|education|monitoring)$")  # FIXED: regex -> pattern
    description: str
    instructions: Optional[str] = None
    duration: Optional[str] = None
    frequency: Optional[str] = None
    goals: Optional[str] = None
    lifestyle_modifications: Optional[str] = None
    patient_education: Optional[str] = None
    follow_up_requirements: Optional[str] = None