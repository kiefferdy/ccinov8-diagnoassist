# backend/schemas/fhir_resource.py
"""
FHIR Resource Pydantic Schemas
"""

from typing import Any, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator
from uuid import UUID

from .common import BaseSchema, PaginatedResponse

class FHIRResourceBase(BaseSchema):
    """Base FHIR resource schema"""
    resource_type: str = Field(..., min_length=1, max_length=100)
    resource_id: str = Field(..., min_length=1, max_length=100)
    fhir_data: Dict[str, Any] = Field(..., description="Complete FHIR resource as JSON")
    patient_reference: Optional[str] = Field(None, max_length=100)
    encounter_reference: Optional[str] = Field(None, max_length=100)
    subject_reference: Optional[str] = Field(None, max_length=100)
    source_system: str = Field("diagnoassist", max_length=100)
    
    @validator('fhir_data')
    def validate_fhir_data(cls, v):
        if not isinstance(v, dict):
            raise ValueError('FHIR data must be a dictionary')
        if 'resourceType' not in v:
            raise ValueError('FHIR data must contain resourceType field')
        return v
    
    @validator('resource_type')
    def validate_resource_type(cls, v, values):
        fhir_data = values.get('fhir_data', {})
        if fhir_data.get('resourceType') and fhir_data['resourceType'] != v:
            raise ValueError('resource_type must match fhir_data.resourceType')
        return v

class FHIRResourceCreate(FHIRResourceBase):
    """Schema for creating a new FHIR resource"""
    pass

class FHIRResourceResponse(FHIRResourceBase):
    """Schema for FHIR resource response"""
    id: UUID
    version_id: str
    active: str
    last_updated: datetime
    created_at: datetime

class FHIRResourceListResponse(PaginatedResponse[FHIRResourceResponse]):
    """Paginated list of FHIR resources"""
    pass