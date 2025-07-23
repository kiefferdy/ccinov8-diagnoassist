"""
Updated API Dependencies with Services Integration
"""

from fastapi import Depends, Query
from typing import Optional
from sqlalchemy.orm import Session

from services.dependencies import (
    get_service_manager, 
    get_database_session,
    check_services_health,
    check_database_health,
    ServiceManager
)

# Main service dependency
ServiceDep = Depends(get_service_manager)
DatabaseDep = Depends(get_database_session)

class PaginationParams:
    """Pagination parameters for list endpoints"""
    def __init__(
        self,
        skip: int = Query(0, ge=0, description="Number of records to skip"),
        limit: int = Query(20, ge=1, le=100, description="Maximum number of records")
    ):
        self.skip = skip
        self.limit = limit

PaginationDep = Depends(PaginationParams)

class CurrentUser:
    """Current user information (placeholder)"""
    def __init__(self):
        self.id = "system"
        self.username = "system_user"
        self.roles = ["admin"]

def get_current_user() -> CurrentUser:
    """Get current authenticated user"""
    return CurrentUser()

CurrentUserDep = Depends(get_current_user)

def get_settings():
    """Get application settings"""
    from config.settings import get_settings
    return get_settings()

SettingsDep = Depends(get_settings)
