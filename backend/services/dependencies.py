"""
Service Dependencies for DiagnoAssist API
FastAPI dependency injection for services layer - FIXED VERSION
"""

from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import text  # ADDED: Import text for SQL queries
from typing import Generator, Dict, Any, Optional  # ADDED: Optional
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

def check_services_health(services: ServiceManager = Depends(get_service_manager)) -> bool:
    """Check health of all services"""
    try:
        health_status = services.health_check()
        return health_status.get("status") == "healthy"
    except Exception as e:
        logger.error(f"Services health check failed: {e}")
        return False

def check_database_health(db: Session = Depends(get_database_session)) -> bool:
    """Check database health - FIXED"""
    try:
        db.execute(text("SELECT 1"))  # FIXED: Use text() wrapper
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False