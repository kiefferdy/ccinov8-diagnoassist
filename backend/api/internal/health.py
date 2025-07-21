"""
Health check endpoints for DiagnoAssist API
"""

from fastapi import APIRouter
from datetime import datetime
import time

router = APIRouter()

@router.get("/health", summary="Health Check")
async def health_check():
    """
    Basic health check endpoint
    Returns the current status of the DiagnoAssist API
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "DiagnoAssist FHIR Server",
        "version": "1.0.0",
        "fhir_version": "R4"
    }

@router.get("/health/detailed", summary="Detailed Health Check")  
async def detailed_health_check():
    """
    Detailed health check with component status
    """
    start_time = time.time()
    
    # Basic component checks
    components = {
        "api_server": {"status": "healthy", "latency_ms": 0},
        "database": {"status": "checking", "latency_ms": 0},
        "fhir_services": {"status": "available"},
        "ai_services": {"status": "available"}
    }
    
    # Simple database check
    try:
        # This will be replaced with actual database check
        db_start = time.time()
        # Simulate database check
        time.sleep(0.001)
        components["database"]["status"] = "healthy"
        components["database"]["latency_ms"] = round((time.time() - db_start) * 1000, 2)
    except Exception as e:
        components["database"]["status"] = f"unhealthy: {str(e)}"
    
    total_time = round((time.time() - start_time) * 1000, 2)
    
    overall_status = "healthy"
    if any(comp.get("status", "").startswith("unhealthy") for comp in components.values()):
        overall_status = "unhealthy"
    elif any(comp.get("status", "") == "degraded" for comp in components.values()):
        overall_status = "degraded"
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "service": "DiagnoAssist FHIR Server",
        "version": "1.0.0",
        "components": components,
        "total_latency_ms": total_time,
        "endpoints": {
            "fhir_metadata": "/fhir/R4/metadata",
            "fhir_patients": "/fhir/R4/Patient",
            "api_docs": "/docs"
        }
    }

@router.get("/health/fhir", summary="FHIR Service Health")
async def fhir_health_check():
    """
    Check FHIR-specific service health
    """
    return {
        "status": "healthy",
        "fhir_version": "R4",
        "capabilities": [
            "Patient",
            "Encounter", 
            "Observation",
            "DiagnosticReport",
            "Condition",
            "Bundle"
        ],
        "server_base": "http://localhost:8000/fhir/R4",
        "metadata_url": "http://localhost:8000/fhir/R4/metadata"
    }