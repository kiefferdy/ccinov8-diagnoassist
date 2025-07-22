"""
API Module for DiagnoAssist Backend
FastAPI routers and endpoints with full dependency injection
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any

# Import dependencies
from api.dependencies import (
    ServiceDep,
    CurrentUserDep,
    PaginationDep,
    SettingsDep,
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
# Health Check Endpoints
# =============================================================================

@api_router.get("/health", response_model=HealthCheckResponse)
async def health_check(
    settings: SettingsDep,
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
        version=getattr(settings, 'app_version', '1.0.0'),
        database="connected" if db_healthy else "disconnected",
        fhir_server="running" if services_healthy else "error"
    )

@api_router.get("/health/database")
async def database_health(
    db_healthy: bool = Depends(check_database_health)
):
    """Check database health specifically"""
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected"
    }

@api_router.get("/health/services")
async def services_health(
    services_healthy: bool = Depends(check_services_health)
):
    """Check services health specifically"""
    return {
        "status": "healthy" if services_healthy else "unhealthy",
        "services": "running" if services_healthy else "error"
    }

# =============================================================================
# System Information Endpoints
# =============================================================================

@api_router.get("/info")
async def system_info(
    settings: SettingsDep,
    current_user: CurrentUserDep = None
):
    """
    Get system information
    
    Returns:
        System configuration and status information
    """
    info = {
        "app_name": getattr(settings, 'app_name', 'DiagnoAssist API'),
        "version": getattr(settings, 'app_version', '1.0.0'),
        "fhir_base_url": getattr(settings, 'fhir_base_url', 'http://localhost:8000/fhir'),
        "debug_mode": getattr(settings, 'debug', False),
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

@api_router.get("/version")
async def get_version(settings: SettingsDep):
    """Get API version"""
    return {
        "version": getattr(settings, 'app_version', '1.0.0'),
        "name": getattr(settings, 'app_name', 'DiagnoAssist API')
    }

# =============================================================================
# API Documentation Endpoints  
# =============================================================================

@api_router.get("/docs/endpoints")
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
            "GET /api/v1/version": "API version"
        },
        "documentation": {
            "GET /api/v1/docs/endpoints": "This endpoint list"
        }
    }
    
    # Add CRUD endpoints if available
    if CRUD_ROUTERS_AVAILABLE:
        endpoints["patients"] = {
            "POST /api/v1/patients/": "Create patient",
            "GET /api/v1/patients/": "List patients", 
            "GET /api/v1/patients/{id}": "Get patient",
            "PUT /api/v1/patients/{id}": "Update patient",
            "DELETE /api/v1/patients/{id}": "Delete patient"
        }
        endpoints["episodes"] = {
            "POST /api/v1/episodes/": "Create episode",
            "GET /api/v1/episodes/": "List episodes",
            "GET /api/v1/episodes/{id}": "Get episode", 
            "PUT /api/v1/episodes/{id}": "Update episode",
            "DELETE /api/v1/episodes/{id}": "Delete episode"
        }
        endpoints["treatments"] = {
            "POST /api/v1/treatments/": "Create treatment",
            "GET /api/v1/treatments/": "List treatments",
            "GET /api/v1/treatments/{id}": "Get treatment",
            "PUT /api/v1/treatments/{id}": "Update treatment", 
            "DELETE /api/v1/treatments/{id}": "Delete treatment"
        }
    
    return {
        "endpoints": endpoints,
        "crud_available": CRUD_ROUTERS_AVAILABLE,
        "note": "CRUD endpoints are now available!" if CRUD_ROUTERS_AVAILABLE else "CRUD endpoints need router integration"
    }

# =============================================================================
# Export router
# =============================================================================

__all__ = [
    "api_router"
]
