"""
Service Manager for DiagnoAssist
Centralized service layer management and dependency injection
"""

from __future__ import annotations
from typing import Dict, Any, Optional, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from repositories.repository_manager import RepositoryManager

from services.base_service import BaseService
from services.patient_service import PatientService
from services.episode_service import EpisodeService
from services.diagnosis_service import DiagnosisService
from services.treatment_service import TreatmentService
from services.fhir_service import FHIRService
from services.clinical_service import ClinicalService

logger = logging.getLogger(__name__)

class ServiceManager:
    """
    Central manager for all business logic services
    Provides dependency injection and service coordination
    """
    
    def __init__(self, repository_manager):
        """
        Initialize service manager with repository dependencies
        
        Args:
            repository_manager: Repository manager instance
        """
        self.repos = repository_manager
        self._services: Dict[str, BaseService] = {}
        self._initialized = False
        
        # Initialize all services
        self._initialize_services()
        
        # Set up direct attribute access (avoids @property issues with FastAPI)
        self.patient = self._services['patient']
        self.episode = self._services['episode']
        self.diagnosis = self._services['diagnosis']
        self.treatment = self._services['treatment']
        self.fhir = self._services['fhir']
        self.clinical = self._services['clinical']
    
    def _initialize_services(self) -> None:
        """Initialize all service instances"""
        try:
            # Core domain services
            self._services['patient'] = PatientService(self.repos)
            self._services['episode'] = EpisodeService(self.repos)
            self._services['diagnosis'] = DiagnosisService(self.repos)
            self._services['treatment'] = TreatmentService(self.repos)
            
            # Integration services
            self._services['fhir'] = FHIRService(self.repos)
            
            # Orchestration services
            self._services['clinical'] = ClinicalService(self.repos)
            
            self._initialized = True
            logger.info("Service manager initialized with all services")
            
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            raise
    
    # Services are now available as direct attributes (set in __init__)
    # This avoids @property descriptor issues with FastAPI dependency injection
    
    def get_service(self, service_name: str) -> Optional[BaseService]:
        """
        Get service by name
        
        Args:
            service_name: Name of the service
            
        Returns:
            Service instance or None if not found
        """
        return self._services.get(service_name)
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on all services
        
        Returns:
            Dictionary with health check results
        """
        health_status = {
            "services_initialized": self._initialized,
            "total_services": len(self._services),
            "service_status": {},
            "overall_status": "healthy"
        }
        
        failed_services = []
        
        for service_name, service_instance in self._services.items():
            try:
                # Basic health check - verify service can access its repositories
                if hasattr(service_instance, 'repos') and service_instance.repos:
                    health_status["service_status"][service_name] = {
                        "status": "healthy",
                        "class": service_instance.__class__.__name__
                    }
                else:
                    health_status["service_status"][service_name] = {
                        "status": "unhealthy",
                        "error": "No repository manager",
                        "class": service_instance.__class__.__name__
                    }
                    failed_services.append(service_name)
                    
            except Exception as e:
                health_status["service_status"][service_name] = {
                    "status": "unhealthy", 
                    "error": str(e),
                    "class": service_instance.__class__.__name__
                }
                failed_services.append(service_name)
        
        if failed_services:
            health_status["overall_status"] = "unhealthy"
            health_status["failed_services"] = failed_services
        
        return health_status
    
    def commit_all(self) -> None:
        """Commit database transactions"""
        self.repos.commit()
    
    def rollback_all(self) -> None:
        """Rollback database transactions"""
        self.repos.rollback()
    
    def close(self) -> None:
        """Close service manager and cleanup resources"""
        try:
            self.repos.close()
            logger.info("Service manager closed successfully")
        except Exception as e:
            logger.error(f"Error closing service manager: {e}")

class ServiceContext:
    """
    Context manager for service operations with automatic transaction handling
    """
    
    def __init__(self, repository_manager):
        """
        Initialize service context
        
        Args:
            repository_manager: Repository manager instance
        """
        self.repo_manager = repository_manager
        self.service_manager: Optional[ServiceManager] = None
    
    def __enter__(self) -> ServiceManager:
        """Enter context and return service manager"""
        self.service_manager = ServiceManager(self.repo_manager)
        return self.service_manager
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context with automatic transaction handling"""
        if self.service_manager:
            try:
                if exc_type is None:
                    # No exception occurred, commit transaction
                    self.service_manager.commit_all()
                else:
                    # Exception occurred, rollback transaction
                    self.service_manager.rollback_all()
                    logger.error(f"Service context exception: {exc_type.__name__}: {exc_val}")
            finally:
                self.service_manager.close()

# Dependency injection functions for FastAPI
def get_service_manager(repository_manager) -> ServiceManager:
    """
    Factory function to create service manager
    
    Args:
        repository_manager: Repository manager instance
        
    Returns:
        ServiceManager instance
    """
    return ServiceManager(repository_manager)

def get_services(repository_manager) -> ServiceManager:
    """
    Dependency function for FastAPI routes
    
    Args:
        repository_manager: Repository manager from dependency injection
        
    Returns:
        ServiceManager instance
    """
    return get_service_manager(repository_manager)