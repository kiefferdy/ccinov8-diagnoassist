"""
Common Pydantic Schemas
Shared schemas used across the application
"""

from pydantic import BaseModel, validator, EmailStr, Field
from typing import Optional, List, Any, Generic, TypeVar
from datetime import datetime, date
from uuid import UUID

# Type variable for generic pagination
T = TypeVar('T')

class BaseSchema(BaseModel):
    """Base schema with common configuration"""
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            date: lambda d: d.isoformat(),
            UUID: lambda uuid: str(uuid)
        }

class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response"""
    data: List[T]
    total: int
    page: int = 1
    size: int = 20
    pages: Optional[int] = None
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.total and self.size:
            self.pages = (self.total + self.size - 1) // self.size

class StatusResponse(BaseModel):
    """Generic status response"""
    status: str
    message: str
    data: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    message: str
    details: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
class HealthCheckResponse(BaseModel):
    """Health check response schema"""
    status: str = Field(..., description="Overall system status")
    version: str = Field(default="1.0.0", description="Application version")
    timestamp: datetime = Field(default_factory=datetime.now)
    database: str = Field(default="unknown", description="Database connection status")
    fhir_server: str = Field(default="unknown", description="FHIR server status")
    services: Optional[dict] = Field(default_factory=lambda: {}, description="Individual service statuses")
    uptime: Optional[str] = None

class MessageResponse(BaseModel):
    """Simple message response"""
    message: str
    success: bool = True