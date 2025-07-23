"""
Clean API Dependencies for DiagnoAssist
Functions only - no pre-created Depends objects to avoid circular imports
"""

from fastapi import Depends, Query
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

# Database session dependency
def get_database_session():
    """Get database session"""
    from config.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Repository manager dependency
def get_repository_manager(db: Session = Depends(get_database_session)):
    """Get repository manager"""
    from repositories.repository_manager import RepositoryManager
    return RepositoryManager(db)

# Service manager dependency
def get_service_manager(repos = Depends(get_repository_manager)):
    """Get service manager"""
    from services.service_manager import ServiceManager
    return ServiceManager(repos)

# Pagination parameters
class PaginationParams:
    """Pagination parameters for list endpoints"""
    def __init__(
        self,
        skip: int = Query(0, ge=0, description="Number of records to skip"),
        limit: int = Query(20, ge=1, le=100, description="Maximum number of records")
    ):
        self.skip = skip
        self.limit = limit

# Mock user for development
def get_current_user() -> Dict[str, Any]:
    """Get current authenticated user (mock implementation)"""
    return {
        "user_id": "system",
        "username": "system_user",
        "roles": ["admin"],
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
        }
    }

# Settings dependency
def get_settings():
    """Get application settings"""
    try:
        from config.settings import get_settings
        return get_settings()
    except ImportError:
        # Fallback simple settings
        class SimpleSettings:
            app_name = "DiagnoAssist API"
            app_version = "1.0.0"
            debug = True
        return SimpleSettings()

# Health check functions
def check_database_health(db: Session = Depends(get_database_session)) -> Dict[str, Any]:
    """Check database health"""
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

def check_services_health(services = Depends(get_service_manager)) -> Dict[str, Any]:
    """Check health of all services"""
    try:
        return services.health_check()
    except Exception as e:
        return {"status": "unhealthy", "services": "unavailable", "error": str(e)}

# Note: ServiceDep, CurrentUserDep, PaginationDep are created locally in each router
# to avoid circular import issues