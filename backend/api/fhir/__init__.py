from fastapi import APIRouter
from .patient import router as patient_router
from .encounter import router as encounter_router
from .observation import router as observation_router
from .diagnostic_report import router as diagnostic_report_router
from .bundle import router as bundle_router
from .metadata import router as metadata_router

# FHIR API router
fhir_router = APIRouter(tags=["FHIR R4"])

# Include all FHIR resource routers
fhir_router.include_router(metadata_router)  # CapabilityStatement first
fhir_router.include_router(patient_router)
fhir_router.include_router(encounter_router)
fhir_router.include_router(observation_router)
fhir_router.include_router(diagnostic_report_router)
fhir_router.include_router(bundle_router)