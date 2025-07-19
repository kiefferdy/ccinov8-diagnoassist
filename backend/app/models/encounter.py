"""
Encounter Pydantic models for DiagnoAssist Backend
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum

from app.models.soap import SOAPModel


class EncounterTypeEnum(str, Enum):
    """Encounter type enumeration"""
    INITIAL = "initial"
    FOLLOW_UP = "follow_up"
    URGENT = "urgent"
    ROUTINE = "routine"
    CONSULTATION = "consultation"
    TELEMEDICINE = "telemedicine"


class EncounterStatusEnum(str, Enum):
    """Encounter status enumeration"""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SIGNED = "signed"
    AMENDED = "amended"
    CANCELLED = "cancelled"


class ProviderInfo(BaseModel):
    """Healthcare provider information"""
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    role: str = Field(..., min_length=1)
    specialty: Optional[str] = None
    license_number: Optional[str] = None


class AIConsultation(BaseModel):
    """AI consultation data structure"""
    voice_processing: List[Dict[str, Any]] = Field(default_factory=list)
    chat_history: List[Dict[str, Any]] = Field(default_factory=list)
    insights: List[Dict[str, Any]] = Field(default_factory=list)
    differential_diagnoses: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    last_ai_interaction: Optional[datetime] = None


class WorkflowInfo(BaseModel):
    """Workflow management information"""
    auto_save_enabled: bool = True
    last_saved: Optional[datetime] = None
    last_modified_by: Optional[str] = None
    amendments: List[Dict[str, Any]] = Field(default_factory=list)
    version: int = 1
    signed_version: Optional[int] = None


class Amendment(BaseModel):
    """Amendment tracking structure"""
    id: str
    amended_by: str
    amended_at: datetime
    reason: str
    changes: Dict[str, Any]
    previous_version: int


class EncounterModel(BaseModel):
    """Complete encounter model for database storage"""
    id: Optional[str] = None  # Auto-generated
    episode_id: str = Field(..., min_length=1)
    patient_id: str = Field(..., min_length=1)
    type: EncounterTypeEnum
    status: EncounterStatusEnum = EncounterStatusEnum.DRAFT
    provider: ProviderInfo
    soap: Optional[SOAPModel] = None
    ai_consultation: AIConsultation = Field(default_factory=AIConsultation)
    workflow: WorkflowInfo = Field(default_factory=WorkflowInfo)
    fhir_encounter_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    signed_at: Optional[datetime] = None
    signed_by: Optional[str] = None
    
    @validator("signed_at", always=True)
    def validate_signed_at(cls, v, values):
        """Auto-set signed_at when status is signed"""
        if values.get("status") == EncounterStatusEnum.SIGNED and not v:
            return datetime.utcnow()
        return v
    
    @validator("signed_by", always=True)
    def validate_signed_by(cls, v, values):
        """Auto-set signed_by when status is signed"""
        if values.get("status") == EncounterStatusEnum.SIGNED and not v:
            provider = values.get("provider")
            return provider.id if provider else None
        return v
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


# API Request/Response Models
class EncounterCreateRequest(BaseModel):
    """Request model for creating a new encounter"""
    episode_id: str = Field(..., min_length=1)
    patient_id: str = Field(..., min_length=1)
    type: EncounterTypeEnum
    provider: ProviderInfo


class EncounterUpdateRequest(BaseModel):
    """Request model for updating an encounter"""
    type: Optional[EncounterTypeEnum] = None
    status: Optional[EncounterStatusEnum] = None
    provider: Optional[ProviderInfo] = None


class EncounterSignRequest(BaseModel):
    """Request model for signing an encounter"""
    signature_confirmation: bool = Field(..., description="Must be true to sign")
    signing_notes: Optional[str] = None
    
    @validator("signature_confirmation")
    def validate_signature(cls, v):
        if not v:
            raise ValueError("Signature confirmation is required")
        return v


class EncounterAmendRequest(BaseModel):
    """Request model for amending an encounter"""
    reason: str = Field(..., min_length=1, max_length=500)
    changes: Dict[str, Any] = Field(..., min_items=1)
    amended_by: str = Field(..., min_length=1)


class EncounterResponse(BaseModel):
    """Response model for encounter data"""
    success: bool = True
    data: EncounterModel
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class EncounterListResponse(BaseModel):
    """Response model for encounter list"""
    success: bool = True
    data: List[EncounterModel]
    total: int
    page: int = 1
    per_page: int = 50
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class EncounterSearchFilters(BaseModel):
    """Search filters for encounter queries"""
    patient_id: Optional[str] = None
    episode_id: Optional[str] = None
    provider_id: Optional[str] = None
    status: Optional[EncounterStatusEnum] = None
    type: Optional[EncounterTypeEnum] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    signed_after: Optional[datetime] = None
    signed_before: Optional[datetime] = None


class EncounterSummary(BaseModel):
    """Summary model for encounter overview"""
    id: str
    episode_id: str
    patient_id: str
    type: EncounterTypeEnum
    status: EncounterStatusEnum
    provider_name: str
    created_at: datetime
    updated_at: datetime
    signed_at: Optional[datetime] = None
    chief_complaint: Optional[str] = None  # From episode
    
    @validator("chief_complaint", pre=True, always=True)
    def extract_chief_complaint(cls, v):
        """Extract chief complaint from SOAP subjective if available"""
        # This will be populated by the service layer
        return v