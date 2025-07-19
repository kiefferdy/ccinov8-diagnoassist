"""
Episode Pydantic models for DiagnoAssist Backend
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class EpisodeCategoryEnum(str, Enum):
    """Episode category enumeration"""
    ACUTE = "acute"
    CHRONIC = "chronic"
    PREVENTIVE = "preventive"
    EMERGENCY = "emergency"
    ROUTINE = "routine"
    FOLLOW_UP = "follow_up"


class EpisodeStatusEnum(str, Enum):
    """Episode status enumeration"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"


class EpisodeModel(BaseModel):
    """Episode model for database storage"""
    id: Optional[str] = None  # Auto-generated
    patient_id: str = Field(..., min_length=1)
    chief_complaint: str = Field(..., min_length=1, max_length=500)
    category: EpisodeCategoryEnum
    status: EpisodeStatusEnum = EpisodeStatusEnum.ACTIVE
    related_episode_ids: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    last_encounter_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    notes: Optional[str] = None
    
    @validator("tags")
    def validate_tags(cls, v):
        """Validate and normalize tags"""
        if not v:
            return v
        # Convert to lowercase and remove duplicates
        return list(set(tag.lower().strip() for tag in v if tag.strip()))
    
    @validator("related_episode_ids")
    def validate_related_episodes(cls, v, values):
        """Ensure episode doesn't reference itself"""
        if "id" in values and values["id"] in v:
            raise ValueError("Episode cannot reference itself")
        return v
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


# API Request/Response Models
class EpisodeCreateRequest(BaseModel):
    """Request model for creating a new episode"""
    patient_id: str = Field(..., min_length=1)
    chief_complaint: str = Field(..., min_length=1, max_length=500)
    category: EpisodeCategoryEnum
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    
    @validator("chief_complaint")
    def validate_chief_complaint(cls, v):
        """Validate chief complaint"""
        return v.strip()


class EpisodeUpdateRequest(BaseModel):
    """Request model for updating an episode"""
    chief_complaint: Optional[str] = Field(None, min_length=1, max_length=500)
    category: Optional[EpisodeCategoryEnum] = None
    status: Optional[EpisodeStatusEnum] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    related_episode_ids: Optional[List[str]] = None


class EpisodeStatusUpdateRequest(BaseModel):
    """Request model for updating episode status"""
    status: EpisodeStatusEnum
    resolved_at: Optional[datetime] = None
    notes: Optional[str] = None
    
    @validator("resolved_at", always=True)
    def validate_resolved_at(cls, v, values):
        """Auto-set resolved_at when status is resolved"""
        if values.get("status") == EpisodeStatusEnum.RESOLVED and not v:
            return datetime.utcnow()
        elif values.get("status") != EpisodeStatusEnum.RESOLVED:
            return None  # Clear resolved_at if not resolved
        return v


class EpisodeResponse(BaseModel):
    """Response model for episode data"""
    success: bool = True
    data: EpisodeModel
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class EpisodeListResponse(BaseModel):
    """Response model for episode list"""
    success: bool = True
    data: List[EpisodeModel]
    total: int
    page: int = 1
    per_page: int = 50
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class EpisodeSearchFilters(BaseModel):
    """Search filters for episode queries"""
    patient_id: Optional[str] = None
    status: Optional[EpisodeStatusEnum] = None
    category: Optional[EpisodeCategoryEnum] = None
    tags: Optional[List[str]] = None
    chief_complaint_search: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    
    @validator("tags")
    def normalize_tags(cls, v):
        """Normalize search tags"""
        if not v:
            return v
        return [tag.lower().strip() for tag in v]


class EpisodeSummary(BaseModel):
    """Summary model for episode overview"""
    id: str
    patient_id: str
    chief_complaint: str
    category: EpisodeCategoryEnum
    status: EpisodeStatusEnum
    encounter_count: int = 0
    last_activity: Optional[datetime] = None
    created_at: datetime