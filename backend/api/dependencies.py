"""
API Dependencies for DiagnoAssist
FastAPI dependency injection setup for database, repositories, services, and authentication
"""

from functools import lru_cache
from typing import Annotated, Generator, Optional, Dict, Any
import logging

from fastapi import Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

# Database imports
from config.database import SessionLocal, get_db
from repositories.repository_manager import RepositoryManager
from services.service_manager import ServiceManager

# Schema imports for common dependencies
from schemas.common import PaginationParams

logger = logging.getLogger(__name__)

# Security scheme (placeholder for future auth implementation)
security = HTTPBearer(auto_error=False)

# =============================================================================
# Database Dependencies
# =============================================================================

def get_database() -> Generator[Session, None, None]:
    """
    Database session dependency with automatic cleanup
    
    Yields:
        Database session
        
    Raises:
        HTTPException: If database connection fails
    """
    db = None
    try:
        db = SessionLocal()
        logger.debug("Database session created")
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        if db:
            db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error"
        )
    except Exception as e:
        logger.error(f"Unexpected database error: {str(e)}")
        if db:
            db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    finally:
        if db:
            db.close()
            logger.debug("Database session closed")

# =============================================================================
# Repository Dependencies
# =============================================================================

def get_repository_manager(
    db: Session = Depends(get_database)
) -> RepositoryManager:
    """
    Repository manager dependency
    
    Args:
        db: Database session from dependency injection
        
    Returns:
        RepositoryManager instance
        
    Raises:
        HTTPException: If repository manager creation fails
    """
    try:
        repos = RepositoryManager(db)
        logger.debug("Repository manager created")
        return repos
    except Exception as e:
        logger.error(f"Failed to create repository manager: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize repositories"
        )

# =============================================================================
# Service Dependencies
# =============================================================================

def get_service_manager(
    repos: RepositoryManager = Depends(get_repository_manager)
) -> ServiceManager:
    """
    Service manager dependency
    
    Args:
        repos: Repository manager from dependency injection
        
    Returns:
        ServiceManager instance
        
    Raises:
        HTTPException: If service manager creation fails
    """
    try:
        services = ServiceManager(repos)
        logger.debug("Service manager created")
        return services
    except Exception as e:
        logger.error(f"Failed to create service manager: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize services"
        )

# =============================================================================
# Authentication Dependencies (Placeholder)
# =============================================================================

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """
    Get current authenticated user (placeholder implementation)
    
    Args:
        credentials: Bearer token credentials
        
    Returns:
        User information or None if not authenticated
        
    Note:
        This is a placeholder. In a real implementation, you would:
        1. Validate the JWT token
        2. Extract user information
        3. Check user permissions
        4. Return user object
    """
    if not credentials:
        return None
        
    # TODO: Implement actual JWT validation
    # For now, return a mock user for development
    return {
        "user_id": "dev-user-001",
        "email": "developer@diagnoassist.com",
        "role": "admin",
        "permissions": ["read", "write", "admin"]
    }

def require_authentication(
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Require authentication dependency
    
    Args:
        current_user: Current user from get_current_user dependency
        
    Returns:
        Authenticated user information
        
    Raises:
        HTTPException: If user is not authenticated
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user

def require_permission(permission: str):
    """
    Factory function to create permission-checking dependencies
    
    Args:
        permission: Required permission
        
    Returns:
        Dependency function that checks for the permission
    """
    def check_permission(
        current_user: Dict[str, Any] = Depends(require_authentication)
    ) -> Dict[str, Any]:
        """Check if user has required permission"""
        user_permissions = current_user.get("permissions", [])
        if permission not in user_permissions and "admin" not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        return current_user
    
    return check_permission

# =============================================================================
# Common Query Dependencies
# =============================================================================

def get_pagination(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
) -> PaginationParams:
    """
    Pagination parameters dependency
    
    Args:
        page: Page number (1-based)
        page_size: Items per page (1-100)
        
    Returns:
        PaginationParams object
    """
    return PaginationParams(
        page=page,
        page_size=page_size,
        offset=(page - 1) * page_size
    )

def get_search_params(
    search: Optional[str] = Query(None, description="Search query"),
    sort_by: Optional[str] = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order")
) -> Dict[str, Any]:
    """
    Common search and sorting parameters
    
    Args:
        search: Search query string
        sort_by: Field to sort by
        sort_order: Sort order (asc/desc)
        
    Returns:
        Dictionary of search parameters
    """
    return {
        "search": search,
        "sort_by": sort_by,
        "sort_order": sort_order
    }

# =============================================================================
# Resource Dependencies
# =============================================================================

async def get_patient_or_404(
    patient_id: str,
    services: ServiceManager = Depends(get_service_manager)
):
    """
    Get patient by ID or raise 404
    
    Args:
        patient_id: Patient identifier
        services: Service manager
        
    Returns:
        Patient object
        
    Raises:
        HTTPException: If patient not found
    """
    try:
        patient = await services.patient.get_by_id(patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID '{patient_id}' not found"
            )
        return patient
    except Exception as e:
        logger.error(f"Error fetching patient {patient_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch patient"
        )

async def get_episode_or_404(
    episode_id: str,
    services: ServiceManager = Depends(get_service_manager)
):
    """
    Get episode by ID or raise 404
    
    Args:
        episode_id: Episode identifier
        services: Service manager
        
    Returns:
        Episode object
        
    Raises:
        HTTPException: If episode not found
    """
    try:
        episode = await services.episode.get_by_id(episode_id)
        if not episode:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Episode with ID '{episode_id}' not found"
            )
        return episode
    except Exception as e:
        logger.error(f"Error fetching episode {episode_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch episode"
        )

# =============================================================================
# Configuration Dependencies
# =============================================================================

@lru_cache()
def get_settings():
    """
    Get application settings (cached)
    
    Returns:
        Settings object
    """
    try:
        from config.settings import Settings
        return Settings()
    except ImportError:
        # Fallback settings if config module doesn't exist
        class FallbackSettings:
            app_name = "DiagnoAssist API"
            app_version = "1.0.0"
            debug = True
            fhir_base_url = "http://localhost:8000/fhir"
        
        return FallbackSettings()

# =============================================================================
# Health Check Dependencies
# =============================================================================

async def check_database_health(
    db: Session = Depends(get_database)
) -> bool:
    """
    Check database health
    
    Args:
        db: Database session
        
    Returns:
        True if database is healthy
    """
    try:
        from sqlalchemy import text
        result = db.execute(text("SELECT 1"))
        return result.scalar() == 1
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False

async def check_services_health(
    services: ServiceManager = Depends(get_service_manager)
) -> bool:
    """
    Check services health
    
    Args:
        services: Service manager
        
    Returns:
        True if services are healthy
    """
    try:
        # Check if all core services are available
        required_services = ['patient', 'episode', 'diagnosis', 'treatment']
        for service_name in required_services:
            if not hasattr(services, service_name):
                return False
        return True
    except Exception as e:
        logger.error(f"Services health check failed: {str(e)}")
        return False

# =============================================================================
# Type Annotations for FastAPI Depends
# =============================================================================

# Common dependency types for reuse
DatabaseDep = Annotated[Session, Depends(get_database)]
RepositoryDep = Annotated[RepositoryManager, Depends(get_repository_manager)]
ServiceDep = Annotated[ServiceManager, Depends(get_service_manager)]
CurrentUserDep = Annotated[Optional[Dict[str, Any]], Depends(get_current_user)]
AuthUserDep = Annotated[Dict[str, Any], Depends(require_authentication)]
PaginationDep = Annotated[PaginationParams, Depends(get_pagination)]
SearchDep = Annotated[Dict[str, Any], Depends(get_search_params)]
SettingsDep = Annotated[Any, Depends(get_settings)]

# Permission-specific dependencies
ReadPermissionDep = Annotated[Dict[str, Any], Depends(require_permission("read"))]
WritePermissionDep = Annotated[Dict[str, Any], Depends(require_permission("write"))]
AdminPermissionDep = Annotated[Dict[str, Any], Depends(require_permission("admin"))]

# =============================================================================
# Export commonly used dependencies
# =============================================================================

__all__ = [
    # Core dependencies
    "get_database",
    "get_repository_manager", 
    "get_service_manager",
    
    # Authentication
    "get_current_user",
    "require_authentication",
    "require_permission",
    
    # Common queries
    "get_pagination",
    "get_search_params",
    
    # Resource dependencies
    "get_patient_or_404",
    "get_episode_or_404",
    
    # Configuration
    "get_settings",
    
    # Health checks
    "check_database_health",
    "check_services_health",
    
    # Type annotations
    "DatabaseDep",
    "RepositoryDep", 
    "ServiceDep",
    "CurrentUserDep",
    "AuthUserDep",
    "PaginationDep",
    "SearchDep",
    "SettingsDep",
    "ReadPermissionDep",
    "WritePermissionDep",
    "AdminPermissionDep"
]