"""
Consolidated API Dependencies for DiagnoAssist API
Single source of truth for all FastAPI dependencies
"""

from fastapi import Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Generator, Dict, Any, Optional, Annotated
import logging

# Import database and managers directly
from config.database import SessionLocal
from repositories.repository_manager import RepositoryManager
from services.service_manager import ServiceManager

# Import common schemas
from schemas.common import PaginationParams

logger = logging.getLogger(__name__)

# =============================================================================
# CORE INFRASTRUCTURE DEPENDENCIES
# =============================================================================

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

def check_services_health(services: ServiceManager = Depends(get_service_manager)) -> bool:
    """Check health of all services"""
    try:
        health_status = services.health_check()
        return health_status.get("status") == "healthy"
    except Exception as e:
        logger.error(f"Services health check failed: {e}")
        return False

def check_database_health(db: Session = Depends(get_database_session)) -> bool:
    """Check database health"""
    try:
        db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

# =============================================================================
# FIXED: Authentication Dependencies with proper type annotations
# =============================================================================

def get_current_user() -> Dict[str, Any]:
    """
    Get current authenticated user (placeholder implementation)
    
    Returns:
        Dict with user information - but FastAPI won't use this for response model
    """
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

def require_authentication() -> Dict[str, Any]:
    """
    Require user to be authenticated
    
    Returns:
        User dict if authenticated
        
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
        permission: Permission string to check
        
    Returns:
        Dependency function that checks the permission
    """
    def permission_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
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
# FIXED: Query Parameter Dependencies  
# =============================================================================

def get_pagination(
    page: int = Query(1, ge=1, description="Page number starting from 1"),
    size: int = Query(10, ge=1, le=100, description="Number of items per page")
) -> PaginationParams:
    """Get pagination parameters from query"""
    return PaginationParams(page=page, size=size)

def get_search_params(
    search: Optional[str] = Query(None, description="Search term"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"), 
    sort_order: Optional[str] = Query("asc", pattern="^(asc|desc)$", description="Sort order")
) -> Dict[str, Any]:
    """Get search and sorting parameters"""
    return {
        "search": search,
        "sort_by": sort_by,
        "sort_order": sort_order
    }

def get_settings() -> Dict[str, Any]:
    """Get application settings"""
    return {
        "api_version": "1.0.0",
        "debug": True,
        "max_page_size": 100,
        "default_page_size": 10
    }

def validate_uuid(uuid_str: str) -> str:
    """Validate UUID format"""
    import uuid
    try:
        uuid.UUID(uuid_str)
        return uuid_str
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid UUID format: {uuid_str}"
        )

# =============================================================================
# FIXED: Dependency Aliases - These are the key fixes!
# =============================================================================

# Alias for backward compatibility
get_database = get_database_session

# Database and repository dependencies  
DatabaseDep = Annotated[Session, Depends(get_database_session)]
RepositoryDep = Annotated[RepositoryManager, Depends(get_repository_manager)]

# Service dependencies
ServiceDep = Annotated[ServiceManager, Depends(get_service_manager)]

# FIXED: Authentication dependencies with proper typing
# The key is that these should NOT be used as response model types
CurrentUserDep = Annotated[Dict[str, Any], Depends(get_current_user)]
AuthUserDep = Annotated[Dict[str, Any], Depends(require_authentication)]

# Query parameter dependencies  
PaginationDep = Annotated[PaginationParams, Depends(get_pagination)]
SearchDep = Annotated[Dict[str, Any], Depends(get_search_params)]
SettingsDep = Annotated[Dict[str, Any], Depends(get_settings)]

# Database and service health
DatabaseHealthDep = Annotated[bool, Depends(check_database_health)]
ServicesHealthDep = Annotated[bool, Depends(check_services_health)]

# Export everything
__all__ = [
    # Core service dependencies
    "get_database_session",
    "get_database",  # Alias for backward compatibility
    "get_repository_manager",
    "get_service_manager", 
    "DatabaseDep",
    "RepositoryDep",
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
    
    # Health dependencies
    "DatabaseHealthDep",
    "ServicesHealthDep",
    
    # Validation
    "validate_uuid"
]