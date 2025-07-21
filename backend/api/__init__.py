"""
API Module for DiagnoAssist Backend
FastAPI routers and endpoints
"""

from fastapi import APIRouter

# Create main API router
api_router = APIRouter(prefix="/api/v1", tags=["api"])

# Simple health check endpoint for testing
@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "DiagnoAssist API is running"}

__all__ = [
    "api_router"
]