"""
FHIR Resource Pydantic Schemas
"""

from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID

class FHIRResourceBase(BaseModel):
    """Base FHIR resource fields"""
    resource_type: str
    resource_id: str
    version_id: str = "1"
    fhir_data: str  # JSON as string for simplicity
    patient_reference: Optional[str] = None
    encounter_reference: Optional[str] = None
    subject_reference: Optional[str] = None
    source_system: str = "diagnoassist"

class FHIRResourceCreate(FHIRResourceBase):
    """Schema for creating a FHIR resource"""
    pass

class FHIRResourceResponse(FHIRResourceBase):
    """Schema for FHIR resource responses"""
    id: UUID
    status: str = "active"
    last_updated: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

class FHIRResourceListResponse(BaseModel):
    """Schema for paginated FHIR resource list"""
    data: List[FHIRResourceResponse]
    total: int
    page: int = 1
    size: int = 20