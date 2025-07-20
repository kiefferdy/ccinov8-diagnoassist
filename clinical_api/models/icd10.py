"""
Pydantic models for ICD-10 related data structures
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class ICD10Code(BaseModel):
    """Model representing an ICD-10 code"""
    code: str = Field(..., description="ICD-10 code (e.g., A00.0)")
    description: str = Field(..., description="Human-readable description")
    category: Optional[str] = Field(None, description="Category/chapter")


class ICD10SearchResponse(BaseModel):
    """Response model for ICD-10 search results"""
    codes: List[ICD10Code]
    total_results: int
    query: str
    search_time_ms: Optional[float] = None


class CategoriesResponse(BaseModel):
    """Response model for categories list"""
    categories: List[str]