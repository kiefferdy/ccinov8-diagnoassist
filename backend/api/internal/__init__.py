"""
Internal API Router
Provides simplified internal endpoints for the DiagnoAssist application
"""

from fastapi import APIRouter

# Import all internal routers
from .health import router as health_router
from .patients import router as patients_router
from .episodes import router as episodes_router
from .clinical import router as clinical_router
from .diagnosis import router as diagnosis_router
from .treatment import router as treatment_router

# Internal API router (legacy/convenience endpoints)
internal_router = APIRouter(tags=["Internal API"])

# Include all internal routers
internal_router.include_router(health_router)
internal_router.include_router(patients_router)
internal_router.include_router(episodes_router)
internal_router.include_router(clinical_router)
internal_router.include_router(diagnosis_router)
internal_router.include_router(treatment_router)