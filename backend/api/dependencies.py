"""
API Dependencies for DiagnoAssist API
FastAPI dependency injection for API layer
Re-exports service dependencies and adds API-specific dependencies
"""

from fastapi import Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Generator, Dict, Any, Optional
import logging

# Import from services layer - this is where ServiceDep is actually defined
try:
    from services.dependencies import (
        get_database_session,
        get_repository_manager,
        get_service_manager,
        ServiceDep,  # This is the key import that was missing
        check_services_health,
        check_database_health
    )
except ImportError as e:
    # Fallback imports if services/dependencies doesn't exist
    from config.database import SessionLocal
    from repositories.repository_manager import RepositoryManager
    from services.service_manager import ServiceManager
    
    logger = logging.getLogger(__name__)
    
    def get_database_session() -> Generator[Session, None, None]:
        """FastAPI dependency for database session"""
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def get_repository_manager(db: Session = Depends(get_database_session)) -> RepositoryManager:
        """FastAPI dependency for repository manager"""
        return RepositoryManager(db)

    def get_service_manager(repos: RepositoryManager = Depends(get_repository_manager)) -> ServiceManager:
        """FastAPI dependency for service manager"""
        return ServiceManager(repos)

    # Service dependencies aliases
    ServiceDep = Depends(get_service_manager)

# Import common schemas for dependencies
from schemas.common import PaginationParams

logger = logging.getLogger(__name__)

# =============================================================================
# API-Specific Dependencies
# =============================================================================

def get_current_user() -> Dict[str, Any]:
    """
    Get current authenticated user (placeholder implementation)
    TODO: Implement proper JWT authentication
    
    Returns:
        Dict with user information
    """
    # Placeholder implementation - return a mock user with all permissions
    return {
        "id": "user_123",
        "username": "admin",
        "email": "admin@diagnoassist.com",
        "permissions": {
            "patient.create": True,
            "patient.read": True,
            "patient.update": True,
            "patient.delete": True,
            "episode.create": True,
            "episode.read": True,
            "episode.update": True,
            "episode.delete": True,
            "diagnosis.create": True,
            "diagnosis.read": True,
            "diagnosis.update": True,
            "diagnosis.delete": True,
            "treatment.create": True,
            "treatment.read": True,
            "treatment.update": True,
            "treatment.delete": True,
            "fhir.create": True,
            "fhir.read": True,
            "fhir.update": True,
            "fhir.delete": True
        }
    }

def require_authentication():
    """
    Require user to be authenticated
    TODO: Implement proper authentication check
    
    Raises:
        HTTPException: If user is not authenticated
    """
    user = get_current_user()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user

def require_permission(permission: str):
    """
    Factory function to create permission-checking dependencies
    
    Args:
        permission: Permission string to check (e.g., "patient.create")
        
    Returns:
        Dependency function that checks the permission
    """
    def permission_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        if not current_user.get("permissions", {}).get(permission, False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions: {permission} required"
            )
        
        return current_user
    
    return Depends(permission_checker)

# =============================================================================
# Query Parameter Dependencies
# =============================================================================

def get_pagination(
    page: int = Query(1, ge=1, description="Page number starting from 1"),
    size: int = Query(10, ge=1, le=100, description="Number of items per page")
) -> PaginationParams:
    """
    Get pagination parameters from query
    
    Args:
        page: Page number (1-based)
        size: Page size (1-100)
        
    Returns:
        PaginationParams object
    """
    return PaginationParams(page=page, size=size)

def get_search_params(
    search: Optional[str] = Query(None, description="Search term"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: Optional[str] = Query("asc", regex="^(asc|desc)$", description="Sort order")
) -> Dict[str, Any]:
    """
    Get search and sorting parameters
    
    Returns:
        Dictionary with search parameters
    """
    return {
        "search": search,
        "sort_by": sort_by,
        "sort_order": sort_order
    }

def get_settings() -> Dict[str, Any]:
    """
    Get application settings (placeholder)
    TODO: Implement proper settings management
    
    Returns:
        Dictionary with application settings
    """
    return {
        "api_version": "1.0.0",
        "debug": True,
        "max_page_size": 100,
        "default_page_size": 10
    }

# =============================================================================
# Dependency Aliases for Easy Use in Routers
# =============================================================================

# Service dependency (imported from services layer)
# ServiceDep is already imported above

# Authentication dependencies
CurrentUserDep = Depends(get_current_user)
AuthUserDep = Depends(require_authentication)

# Query parameter dependencies
PaginationDep = Depends(get_pagination)
SearchDep = Depends(get_search_params)
SettingsDep = Depends(get_settings)

# Permission dependencies (factories)
# Example usage: ReadPatientDep = require_permission("patient.read")

# =============================================================================
# Health Check Dependencies
# =============================================================================

def get_api_health() -> Dict[str, Any]:
    """
    Get API health status
    
    Returns:
        Dictionary with API health information
    """
    return {
        "status": "healthy",
        "api": "running",
        "version": "1.0.0",
        "timestamp": "2025-01-23T00:00:00Z"
    }

# Health check dependency alias
HealthDep = Depends(get_api_health)

# =============================================================================
# Validation Dependencies
# =============================================================================

def validate_uuid(uuid_str: str) -> str:
    """
    Validate UUID format
    
    Args:
        uuid_str: UUID string to validate
        
    Returns:
        Validated UUID string
        
    Raises:
        HTTPException: If UUID format is invalid
    """
    import uuid
    try:
        uuid.UUID(uuid_str)
        return uuid_str
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid UUID format: {uuid_str}"
        )

# Export all dependencies for easy import
__all__ = [
    # Core service dependencies
    "get_database_session",
    "get_repository_manager", 
    "get_service_manager",
    "ServiceDep",
    "check_services_health",
    "check_database_health",
    
    # Authentication dependencies
    "get_current_user",
    "require_authentication",
    "require_permission",
    "CurrentUserDep",
    "AuthUserDep",
    
    # Query parameter dependencies
    "get_pagination",
    "get_search_params",
    "get_settings",
    "PaginationDep",
    "SearchDep", 
    "SettingsDep",
    
    # Health check dependencies
    "get_api_health",
    "HealthDep",
    
    # Validation dependencies
    "validate_uuid"
]