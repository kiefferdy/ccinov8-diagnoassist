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
        "authenticated": current_user is not None
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
# Service Status Endpoints
# =============================================================================

@api_router.get("/services/status")
async def services_status(services: ServiceDep):
    """
    Get status of all business services
    
    Returns:
        Status of each service component
    """
    status = {}
    
    # Check each service
    service_names = ['patient', 'episode', 'diagnosis', 'treatment', 'fhir', 'clinical']
    
    for service_name in service_names:
        try:
            service = getattr(services, service_name, None)
            status[service_name] = {
                "available": service is not None,
                "type": type(service).__name__ if service else None
            }
        except Exception as e:
            status[service_name] = {
                "available": False,
                "error": str(e)
            }
    
    return {
        "services": status,
        "total_services": len(service_names),
        "available_services": sum(1 for s in status.values() if s.get("available", False))
    }

# =============================================================================
# Testing Endpoints (Development Only)
# =============================================================================

@api_router.get("/test/dependencies")
async def test_dependencies(
    services: ServiceDep,
    current_user: CurrentUserDep,
    pagination: PaginationDep,
    settings: SettingsDep
):
    """
    Test endpoint to verify all dependencies are working
    This endpoint should only be available in development
    """
    # Only allow in debug mode
    if not getattr(settings, 'debug', False):
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endpoint not available in production"
        )
    
    return {
        "dependencies_test": "success",
        "services": {
            "available": services is not None,
            "type": type(services).__name__,
            "patient_service": hasattr(services, 'patient'),
            "episode_service": hasattr(services, 'episode'),
            "diagnosis_service": hasattr(services, 'diagnosis'),
            "treatment_service": hasattr(services, 'treatment')
        },
        "authentication": {
            "authenticated": current_user is not None,
            "user_info": current_user if current_user else None
        },
        "pagination": {
            "page": pagination.page,
            "size": pagination.size,
            "offset": pagination.offset
        },
        "settings": {
            "app_name": getattr(settings, 'app_name', 'Unknown'),
            "debug_mode": getattr(settings, 'debug', False)
        }
    }

@api_router.get("/test/repositories")
async def test_repositories(services: ServiceDep, settings: SettingsDep):
    """
    Test endpoint to verify repository access through services
    """
    # Only allow in debug mode
    if not getattr(settings, 'debug', False):
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endpoint not available in production"
        )
    
    repository_status = {}
    
    try:
        # Test repository access through services
        if hasattr(services, 'repos'):
            repos = services.repos
            
            # Check each repository
            repo_names = ['patient', 'episode', 'diagnosis', 'treatment', 'fhir_resource']
            
            for repo_name in repo_names:
                try:
                    repo = getattr(repos, repo_name, None)
                    repository_status[repo_name] = {
                        "available": repo is not None,
                        "type": type(repo).__name__ if repo else None
                    }
                except Exception as e:
                    repository_status[repo_name] = {
                        "available": False,
                        "error": str(e)
                    }
        else:
            repository_status["error"] = "Services do not expose repositories"
            
    except Exception as e:
        repository_status["error"] = f"Failed to access repositories: {str(e)}"
    
    return {
        "repositories_test": "completed",
        "repositories": repository_status
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
    return {
        "endpoints": {
            "health": {
                "GET /api/v1/health": "Comprehensive health check",
                "GET /api/v1/health/database": "Database health check",
                "GET /api/v1/health/services": "Services health check"
            },
            "system": {
                "GET /api/v1/info": "System information",
                "GET /api/v1/version": "API version",
                "GET /api/v1/services/status": "Service status"
            },
            "testing": {
                "GET /api/v1/test/dependencies": "Test dependencies (debug only)",
                "GET /api/v1/test/repositories": "Test repositories (debug only)"
            },
            "documentation": {
                "GET /api/v1/docs/endpoints": "This endpoint list"
            }
        },
        "note": "Full CRUD endpoints for patients, episodes, diagnoses, and treatments will be available after Step 8"
    }

# =============================================================================
# Export router
# =============================================================================

__all__ = [
    "api_router"
]