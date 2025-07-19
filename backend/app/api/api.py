"""
Main API router for DiagnoAssist Backend
"""
from fastapi import APIRouter

from app.api.v1 import patients, episodes, encounters

api_router = APIRouter()

# Include all API v1 routes
api_router.include_router(patients.router, prefix="/patients", tags=["patients"])
api_router.include_router(episodes.router, prefix="/episodes", tags=["episodes"])
api_router.include_router(encounters.router, prefix="/encounters", tags=["encounters"])