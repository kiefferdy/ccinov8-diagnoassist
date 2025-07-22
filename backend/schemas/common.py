"""
Common Pydantic Schemas
Shared schemas used across the application
"""

from pydantic import BaseModel, validator, EmailStr
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID

class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = 1
    size: int = 20
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size

class StatusResponse(BaseModel):
    """Generic status response"""
    status: str
    message: str
    data: Optional[dict] = None