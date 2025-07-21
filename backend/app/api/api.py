"""
Main API router for DiagnoAssist Backend
"""
from fastapi import APIRouter

from app.api.v1 import auth, patients, episodes, encounters, fhir, ai, realtime, chat, collaboration, status

api_router = APIRouter()

# Include all API v1 routes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(patients.router, prefix="/patients", tags=["patients"])
api_router.include_router(episodes.router, prefix="/episodes", tags=["episodes"])
api_router.include_router(encounters.router, prefix="/encounters", tags=["encounters"])
api_router.include_router(fhir.router, prefix="/fhir", tags=["fhir"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(realtime.router, prefix="/realtime", tags=["realtime"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(collaboration.router, prefix="/collaboration", tags=["collaboration"])
api_router.include_router(status.router, prefix="/status", tags=["status"])