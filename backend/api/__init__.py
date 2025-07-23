"""
API Module for DiagnoAssist Backend
FastAPI routers and endpoints with full dependency injection - COMPLETELY FIXED VERSION
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any

# Import dependencies - FIXED: Remove problematic SettingsDep for now
from api.dependencies import (
    ServiceDep,
    CurrentUserDep,
    PaginationDep,
    check_database_health,
    check_services_health
)

# Import schemas
from schemas.common import HealthCheckResponse, StatusResponse

# Create main API router
api_router = APIRouter(prefix="/api/v1", tags=["api"])

# =============================================================================
# Include all CRUD routers
# =============================================================================

try:
    # Import individual routers
    from api.patients import router as patients_router
    from api.episodes import router as episodes_router  
    from api.treatments import router as treatments_router
    
    # Include routers in main API router
    api_router.include_router(patients_router)
    api_router.include_router(episodes_router)
    api_router.include_router(treatments_router)
    
    print("✅ All CRUD routers included successfully")
    CRUD_ROUTERS_AVAILABLE = True
    
except ImportError as e:
    print(f"⚠️  Some CRUD routers not available: {e}")
    CRUD_ROUTERS_AVAILABLE = False

# Try to include diagnosis router if available
try:
    from api.diagnoses import router as diagnoses_router
    api_router.include_router(diagnoses_router)
    print("✅ Diagnoses router included")
except ImportError:
    print("⚠️  Diagnoses router not available")

# =============================================================================
# Health Check Endpoints - FIXED: Removed SettingsDep
# =============================================================================

@api_router.get("/health", response_model=HealthCheckResponse)
async def health_check(
    db_healthy: bool = Depends(check_database_health),
    services_healthy: bool = Depends(check_services_health)
):
    """
    Comprehensive health check endpoint
    
    Returns:
        Health status of all system components
    """
    return HealthCheckResponse(
        status="healthy" if db_healthy and services_healthy else "degraded",
        version="1.0.0",  # Hardcoded for now to avoid settings dependency issues
        database="connected" if db_healthy else "disconnected",
        fhir_server="running" if services_healthy else "error"
    )

@api_router.get("/health/database", response_model=None)
async def database_health(
    db_healthy: bool = Depends(check_database_health)
):
    """Check database health specifically"""
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected"
    }

@api_router.get("/health/services", response_model=None)
async def services_health(
    services_healthy: bool = Depends(check_services_health)
):
    """Check services health specifically"""
    return {
        "status": "healthy" if services_healthy else "unhealthy",
        "services": "running" if services_healthy else "error"
    }

# =============================================================================
# System Information Endpoints - FIXED: Removed SettingsDep
# =============================================================================

@api_router.get("/info", response_model=None)
async def system_info(
    current_user: CurrentUserDep = None
):
    """
    Get system information
    
    Returns:
        System configuration and status information
    """
    info = {
        "app_name": "DiagnoAssist API",
        "version": "1.0.0",
        "fhir_base_url": "http://localhost:8000/fhir",
        "debug_mode": True,
        "authenticated": current_user is not None,
        "crud_routers_available": CRUD_ROUTERS_AVAILABLE
    }
    
    # Add user info if authenticated
    if current_user:
        info["user"] = {
            "user_id": current_user.get("user_id"),
            "email": current_user.get("email"),
            "role": current_user.get("role")
        }
    
    return info

@api_router.get("/version", response_model=None)
async def get_version():
    """Get API version"""
    return {
        "version": "1.0.0",
        "name": "DiagnoAssist API"
    }

# =============================================================================
# API Documentation Endpoints - FIXED
# =============================================================================

@api_router.get("/docs/endpoints", response_model=None)
async def list_endpoints():
    """
    List all available API endpoints
    
    Returns:
        Summary of all available endpoints
    """
    endpoints = {
        "health": {
            "GET /api/v1/health": "Comprehensive health check",
            "GET /api/v1/health/database": "Database health check",
            "GET /api/v1/health/services": "Services health check"
        },
        "system": {
            "GET /api/v1/info": "System information",
            "GET /api/v1/version": "API version",
            "GET /api/v1/docs/endpoints": "Available endpoints"
        },
        "patients": {
            "GET /api/v1/patients/": "List patients",
            "POST /api/v1/patients/": "Create patient",
            "GET /api/v1/patients/{id}": "Get patient by ID",
            "PUT /api/v1/patients/{id}": "Update patient",
            "DELETE /api/v1/patients/{id}": "Delete patient"
        },
        "episodes": {
            "GET /api/v1/episodes/": "List episodes",
            "POST /api/v1/episodes/": "Create episode",
            "GET /api/v1/episodes/{id}": "Get episode by ID",
            "PUT /api/v1/episodes/{id}": "Update episode",
            "DELETE /api/v1/episodes/{id}": "Delete episode"
        },
        "treatments": {
            "GET /api/v1/treatments/": "List treatments",
            "POST /api/v1/treatments/": "Create treatment",
            "GET /api/v1/treatments/{id}": "Get treatment by ID",
            "PUT /api/v1/treatments/{id}": "Update treatment",
            "DELETE /api/v1/treatments/{id}": "Delete treatment"
        },
        "diagnoses": {
            "GET /api/v1/diagnoses/": "List diagnoses",
            "POST /api/v1/diagnoses/": "Create diagnosis",
            "GET /api/v1/diagnoses/{id}": "Get diagnosis by ID",
            "PUT /api/v1/diagnoses/{id}": "Update diagnosis",
            "DELETE /api/v1/diagnoses/{id}": "Delete diagnosis"
        },
        "fhir": {
            "GET /api/v1/fhir/": "List FHIR resources",
            "POST /api/v1/fhir/": "Create FHIR resource",
            "GET /api/v1/fhir/{id}": "Get FHIR resource by ID",
            "GET /api/v1/fhir/metadata": "FHIR capability statement",
            "GET /api/v1/fhir/Patient/{id}/everything": "Patient everything bundle"
        }
    }
    
    return {
        "message": "DiagnoAssist API Endpoints",
        "total_categories": len(endpoints),
        "endpoints": endpoints,
        "documentation": "/api/docs"
    }

# =============================================================================
# Service Status Endpoints - FIXED
# =============================================================================

@api_router.get("/services/status", response_model=None)
async def get_services_status(
    services = ServiceDep
):
    """
    Get detailed status of all services
    
    Returns:
        Detailed service status information
    """
    try:
        # Get service status through service layer
        status_info = services.health_check()
        return {
            "status": "healthy",
            "services": status_info,
            "timestamp": "2025-01-23T00:00:00Z"
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "error": str(e),
            "timestamp": "2025-01-23T00:00:00Z"
        }

# =============================================================================
# Development Endpoints (for testing) - FIXED
# =============================================================================

@api_router.get("/ping", response_model=None)
async def ping():
    """Simple ping endpoint for testing"""
    return {"message": "pong", "status": "ok"}

@api_router.get("/echo/{message}", response_model=None)
async def echo(message: str):
    """Echo endpoint for testing"""
    return {"echo": message, "timestamp": "2025-01-23T00:00:00Z"}