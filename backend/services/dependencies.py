"""
Service Dependencies for DiagnoAssist API
FastAPI dependency injection for services layer
"""

from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Generator, Dict, Any
import logging

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

def check_services_health(services: ServiceManager = Depends(get_service_manager)) -> Dict[str, Any]:
    """Check health of all services"""
    return services.health_check()

def check_database_health(db: Session = Depends(get_database_session)) -> Dict[str, Any]:
    """Check database health"""
    try:
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
