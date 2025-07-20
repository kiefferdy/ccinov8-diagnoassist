"""
DiagnoAssist API Package
Provides both FHIR-compliant and internal REST APIs
"""

from fastapi import APIRouter
from .fhir import fhir_router
from .internal import internal_router

# Main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(fhir_router, prefix="/fhir")
api_router.include_router(internal_router, prefix="/api")