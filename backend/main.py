"""
DiagnoAssist FastAPI Application Entry Point - FIXED VERSION
FHIR R4 Compliant Medical Diagnosis Assistant API
"""

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from sqlalchemy import text


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
    db.execute(text("SELECT 1"))
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

# Debug endpoint to investigate dependency injection issue
from fastapi import Depends
try:
    from api.dependencies import get_service_manager
    
    @app.get("/debug/dependencies")
    async def debug_dependencies(services = Depends(get_service_manager)):
        """Debug endpoint to investigate dependency injection"""
        
        debug_info = {}
        
        # Basic info about the services object
        debug_info["services_type"] = str(type(services))
        debug_info["services_str"] = str(services)
        debug_info["services_dir"] = [attr for attr in dir(services) if not attr.startswith('_')]
        
        # Check the patient attribute specifically
        debug_info["patient_attr_type"] = str(type(services.patient))
        debug_info["patient_attr_str"] = str(services.patient)
        
        # Check if it's a property
        patient_attr = getattr(type(services), 'patient', None)
        debug_info["patient_class_attr_type"] = str(type(patient_attr))
        debug_info["is_property"] = isinstance(patient_attr, property)
        
        # Try to access the property directly from the class
        if isinstance(patient_attr, property):
            debug_info["property_fget"] = str(patient_attr.fget)
            try:
                # Try calling the property getter manually
                actual_service = patient_attr.fget(services)
                debug_info["manual_property_call_type"] = str(type(actual_service))
                debug_info["manual_property_call_str"] = str(actual_service)
                debug_info["manual_call_has_create_patient"] = hasattr(actual_service, 'create_patient')
            except Exception as e:
                debug_info["manual_property_call_error"] = str(e)
        
        # Check the internal _services dict
        if hasattr(services, '_services'):
            debug_info["_services_keys"] = list(services._services.keys())
            if 'patient' in services._services:
                debug_info["_services_patient_type"] = str(type(services._services['patient']))
                debug_info["_services_patient_has_create"] = hasattr(services._services['patient'], 'create_patient')
        
        # Test direct property access vs attribute access
        try:
            debug_info["direct_services_patient_type"] = str(type(services._services.get('patient')))
        except:
            debug_info["direct_services_patient_type"] = "Error accessing _services"
            
        return debug_info
        
    @app.get("/debug/servicedep")
    async def debug_servicedep():
        """Test the ServiceDep annotation specifically"""
        try:
            from api.dependencies import ServiceDep
            # Test if we can import it properly
            return {"ServiceDep_type": str(ServiceDep), "import_success": True}
        except Exception as e:
            return {"import_error": str(e), "import_success": False}
    
    @app.get("/debug/test-patient-creation")
    async def debug_test_patient_creation(services = Depends(get_service_manager)):
        """Test creating a patient with the fixed dependency injection"""
        from schemas.patient import PatientCreate
        
        # Test patient data
        test_data = PatientCreate(
            medical_record_number="DEBUGTEST123",
            first_name="Debug",
            last_name="Test", 
            date_of_birth="1990-01-01",
            gender="male",
            email="debugtest@test.com"
        )
        
        debug_info = {}
        debug_info["services_type"] = str(type(services))
        debug_info["has_patient_attr"] = hasattr(services, 'patient')
        
        if hasattr(services, 'patient'):
            debug_info["patient_type"] = str(type(services.patient))
            debug_info["has_create_method"] = hasattr(services.patient, 'create_patient')
            
            try:
                # Try to create patient like the router does
                patient = services.patient.create_patient(test_data)
                debug_info["creation_success"] = True
                debug_info["patient_id"] = str(patient.id) if patient else "None"
            except Exception as e:
                debug_info["creation_error"] = str(e)
                debug_info["creation_success"] = False
        else:
            debug_info["patient_attr_missing"] = True
            
        return debug_info
    
    @app.get("/debug/test-diagnoses")
    async def debug_test_diagnoses(services = Depends(get_service_manager)):
        """Test diagnoses service directly"""
        try:
            # Try calling search_diagnoses like the router does
            result = services.diagnosis.search_diagnoses(
                query=None,
                episode_id=None,
                patient_id=None,
                confidence_level=None,
                final_only=False,
                skip=0,
                limit=100
            )
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e), "error_type": str(type(e))}
    
    # Test ServiceDep directly - fix the earlier error
    try:
        from api.dependencies import ServiceDep
        
        @app.get("/debug/test-servicedep-syntax")
        async def debug_test_servicedep_syntax(services: ServiceDep):
            """Test using ServiceDep annotation exactly like patient router"""
            debug_info = {}
            
            debug_info["services_type"] = str(type(services))
            debug_info["has_patient_attr"] = hasattr(services, 'patient')
            
            if hasattr(services, 'patient'):
                debug_info["patient_type"] = str(type(services.patient))
                debug_info["has_create_method"] = hasattr(services.patient, 'create_patient')
                
                try:
                    # Try calling get_patient_statistics like original router
                    stats = services.patient.get_patient_statistics()
                    debug_info["method_call_success"] = True
                    debug_info["stats_keys"] = list(stats.keys()) if isinstance(stats, dict) else "Not dict"
                except Exception as e:
                    debug_info["method_call_error"] = str(e)
                    debug_info["method_call_success"] = False
            else:
                debug_info["patient_attr_missing"] = True
                
            return debug_info
            
    except Exception as servicedep_error:
        logger.warning(f"⚠️ Could not create ServiceDep test endpoint: {servicedep_error}")
        
except Exception as e:
    logger.warning(f"⚠️ Could not create debug endpoint: {e}")

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