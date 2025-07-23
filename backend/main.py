"""
DiagnoAssist FastAPI Application Entry Point - FIXED VERSION
FHIR R4 Compliant Medical Diagnosis Assistant API
"""

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Print loaded env vars for debugging
print(f"🔍 DATABASE_URL loaded: {'✅ Yes' if os.getenv('DATABASE_URL') else '❌ No'}")
print(f"🔍 SUPABASE_URL loaded: {'✅ Yes' if os.getenv('SUPABASE_URL') else '❌ No'}")

# Simple settings
class Settings:
    app_name = "DiagnoAssist API"
    app_version = "1.0.0"
    debug = True
    cors_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000", 
        "http://127.0.0.1:5173"
    ]

settings = Settings()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="FHIR R4 Compliant Medical Diagnosis Assistant API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Track what's available
components_status = {
    "database": False,
    "api_router": False,
    "patients_router": False,
    "episodes_router": False,
    "treatments_router": False,
    "diagnoses_router": False,
    "fhir_router": False
}

# Startup
logger.info("🚀 DiagnoAssist API starting...")

# Test database
try:
    from config.database import SessionLocal
    db = SessionLocal()
    db.execute("SELECT 1")
    db.close()
    components_status["database"] = True
    logger.info("✅ Database connection successful")
except Exception as e:
    logger.warning(f"⚠️ Database connection failed: {e}")

# Include individual routers directly (skip the problematic main API router for now)
def safe_include_router(router_module: str, router_name: str, prefix: str = "/api/v1"):
    """Safely include a router with error handling"""
    try:
        module = __import__(router_module, fromlist=[router_name])
        router = getattr(module, router_name)
        app.include_router(router, prefix=prefix)
        component_key = router_module.split('.')[-1] + "_router"
        components_status[component_key] = True
        logger.info(f"✅ {router_module} router included successfully")
        return True
    except Exception as e:
        logger.warning(f"⚠️ {router_module} router failed: {e}")
        return False

# Include all routers
routers_to_include = [
    ("api.patients", "router"),
    ("api.episodes", "router"), 
    ("api.treatments", "router"),
    ("api.diagnoses", "router"),
    ("api.fhir", "router")
]

successful_routers = 0
for module_name, router_name in routers_to_include:
    if safe_include_router(module_name, router_name):
        successful_routers += 1

# Try to include the main API router (but don't fail if it doesn't work)
try:
    from api import api_router
    # Only include if we didn't already include individual routers
    if successful_routers == 0:
        app.include_router(api_router)
        components_status["api_router"] = True
        logger.info("✅ Main API router included as fallback")
except Exception as e:
    logger.warning(f"⚠️ Main API router failed (using individual routers instead): {e}")

# Basic endpoints
@app.get("/")
async def root():
    """Root endpoint with system status"""
    return {
        "message": "DiagnoAssist API",
        "version": settings.app_version,
        "status": "running",
        "components": components_status,
        "docs": "/api/docs",
        "endpoints": {
            "patients": "/api/v1/patients/",
            "episodes": "/api/v1/episodes/",
            "treatments": "/api/v1/treatments/",
            "diagnoses": "/api/v1/diagnoses/",
            "fhir": "/api/v1/fhir/"
        }
    }

@app.get("/health")
async def health_check():
    """Simple health check"""
    working_components = sum(1 for status in components_status.values() if status)
    total_components = len(components_status)
    
    return {
        "status": "healthy" if working_components > 0 else "degraded",
        "components": components_status,
        "summary": f"{working_components}/{total_components} components working",
        "database": "connected" if components_status["database"] else "disconnected",
        "routers": f"{successful_routers}/5 routers loaded"
    }

@app.get("/api/status")
async def api_status():
    """Detailed API status"""
    return {
        "api_version": settings.app_version,
        "components": components_status,
        "available_endpoints": {
            "patients": {
                "available": components_status.get("patients_router", False),
                "endpoints": [
                    "GET /api/v1/patients/",
                    "POST /api/v1/patients/",
                    "GET /api/v1/patients/{id}",
                    "PUT /api/v1/patients/{id}",
                    "DELETE /api/v1/patients/{id}"
                ] if components_status.get("patients_router", False) else []
            },
            "episodes": {
                "available": components_status.get("episodes_router", False),
                "endpoints": [
                    "GET /api/v1/episodes/",
                    "POST /api/v1/episodes/",
                    "GET /api/v1/episodes/{id}",
                    "PUT /api/v1/episodes/{id}",
                    "DELETE /api/v1/episodes/{id}",
                    "PATCH /api/v1/episodes/{id}/complete"
                ] if components_status.get("episodes_router", False) else []
            },
            "treatments": {
                "available": components_status.get("treatments_router", False),
                "endpoints": [
                    "GET /api/v1/treatments/",
                    "POST /api/v1/treatments/",
                    "GET /api/v1/treatments/{id}",
                    "PUT /api/v1/treatments/{id}",
                    "DELETE /api/v1/treatments/{id}",
                    "PATCH /api/v1/treatments/{id}/start",
                    "PATCH /api/v1/treatments/{id}/complete"
                ] if components_status.get("treatments_router", False) else []
            },
            "diagnoses": {
                "available": components_status.get("diagnoses_router", False),
                "endpoints": [
                    "GET /api/v1/diagnoses/",
                    "POST /api/v1/diagnoses/",
                    "GET /api/v1/diagnoses/{id}",
                    "PUT /api/v1/diagnoses/{id}",
                    "DELETE /api/v1/diagnoses/{id}",
                    "POST /api/v1/diagnoses/analyze-symptoms",
                    "PATCH /api/v1/diagnoses/{id}/confirm"
                ] if components_status.get("diagnoses_router", False) else []
            },
            "fhir": {
                "available": components_status.get("fhir_router", False),
                "endpoints": [
                    "GET /api/v1/fhir/",
                    "POST /api/v1/fhir/",
                    "GET /api/v1/fhir/{id}",
                    "PUT /api/v1/fhir/{id}",
                    "DELETE /api/v1/fhir/{id}",
                    "GET /api/v1/fhir/metadata"
                ] if components_status.get("fhir_router", False) else []
            }
        }
    }

logger.info(f"📊 Router Summary: {successful_routers}/5 routers loaded")
logger.info("✅ DiagnoAssist API startup completed")

# Development server
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )