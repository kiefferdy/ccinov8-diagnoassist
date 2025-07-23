"""
FHIR Resource Pydantic Schemas - CORRECTED to match SQL schema
"""

from pydantic import BaseModel, validator, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timezone
from uuid import UUID
import json

class FHIRResourceBase(BaseModel):
    """Base FHIR resource fields - matches SQL exactly"""
    resource_type: str = Field(..., description="FHIR resource type")
    resource_id: str = Field(..., description="FHIR resource identifier")
    version_id: str = Field(default="1", description="FHIR resource version")
    fhir_data: str = Field(..., description="FHIR resource data as JSON string")
    patient_reference: Optional[str] = Field(None, description="Patient reference for indexing")
    encounter_reference: Optional[str] = Field(None, description="Encounter reference for indexing")
    subject_reference: Optional[str] = Field(None, description="Subject reference for indexing")
    source_system: str = Field(default="diagnoassist", description="Source system identifier")
    
    @validator('fhir_data')
    def validate_fhir_data(cls, v):
        """Validate that fhir_data is valid JSON"""
        if v:
            try:
                # Ensure it's valid JSON
                json.loads(v)
            except (json.JSONDecodeError, TypeError):
                raise ValueError('fhir_data must be valid JSON string')
        return v
    
    @validator('resource_type')
    def validate_resource_type(cls, v):
        """Validate FHIR resource type"""
        valid_types = [
            'Patient', 'Encounter', 'Observation', 'Condition', 'Procedure',
            'MedicationRequest', 'DiagnosticReport', 'Bundle', 'Organization',
            'Practitioner', 'Location', 'Device', 'Specimen'
        ]
        if v not in valid_types:
            raise ValueError(f'Invalid FHIR resource type: {v}')
        return v

class FHIRResourceCreate(FHIRResourceBase):
    """Schema for creating a FHIR resource"""
    pass

class FHIRResourceUpdate(BaseModel):
    """Schema for updating a FHIR resource"""
    fhir_data: Optional[str] = None
    patient_reference: Optional[str] = None
    encounter_reference: Optional[str] = None
    subject_reference: Optional[str] = None
    status: Optional[str] = None
    
    @validator('fhir_data')
    def validate_fhir_data(cls, v):
        """Validate that fhir_data is valid JSON"""
        if v:
            try:
                json.loads(v)
            except (json.JSONDecodeError, TypeError):
                raise ValueError('fhir_data must be valid JSON string')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        """Validate status values"""
        if v and v not in ['active', 'inactive', 'deleted']:
            raise ValueError('Status must be active, inactive, or deleted')
        return v

class FHIRResourceResponse(FHIRResourceBase):
    """Schema for FHIR resource responses - matches SQL exactly"""
    id: UUID
    status: str = Field(default="active", description="Resource status")
    last_updated: datetime = Field(..., description="Last update timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True
    
    @property
    def fhir_data_dict(self) -> Dict[str, Any]:
        """Get FHIR data as dictionary"""
        try:
            return json.loads(self.fhir_data) if self.fhir_data else {}
        except (json.JSONDecodeError, TypeError):
            return {}

class FHIRResourceListResponse(BaseModel):
    """Schema for paginated FHIR resource list"""
    data: List[FHIRResourceResponse]
    total: int
    page: int = 1
    size: int = 20
    
class FHIRBundleResponse(BaseModel):
    """Schema for FHIR Bundle responses"""
    resource_type: str = "Bundle"
    id: str
    type: str = "collection"
    timestamp: datetime
    total: int
    entry: List[Dict[str, Any]]
    
class FHIRSearchParams(BaseModel):
    """Schema for FHIR search parameters"""
    resource_type: Optional[str] = None
    patient_reference: Optional[str] = None
    encounter_reference: Optional[str] = None
    status: Optional[str] = "active"
    search_term: Optional[str] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)
    
class FHIRResourceStatistics(BaseModel):
    """Schema for FHIR resource statistics"""
    total_resources: int
    active_resources: int
    inactive_resources: int
    resource_type_distribution: Dict[str, int]
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))