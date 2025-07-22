"""
Enhanced Base Service Class for DiagnoAssist - COMPLETE VERSION
Business Logic Layer Foundation with all required methods
"""

from __future__ import annotations
from typing import TypeVar, Generic, Optional, Dict, Any, List, TYPE_CHECKING
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import logging
import uuid

if TYPE_CHECKING:
    from repositories.repository_manager import RepositoryManager

from repositories.repository_manager import RepositoryManager

logger = logging.getLogger(__name__)

T = TypeVar('T')

# Basic exceptions - ALWAYS AVAILABLE for backward compatibility
class ServiceException(Exception):
    """Base exception for service layer errors"""
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict] = None):
        self.message = message
        self.error_code = error_code or "SERVICE_ERROR"
        self.details = details or {}
        super().__init__(self.message)

class ValidationException(ServiceException):
    """Exception for validation errors"""
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        super().__init__(message, "VALIDATION_ERROR", {"field": field, "value": value})

class BusinessRuleException(ServiceException):
    """Exception for business rule violations"""
    def __init__(self, message: str, rule: Optional[str] = None):
        super().__init__(message, "BUSINESS_RULE_VIOLATION", {"rule": rule})

class ResourceNotFoundException(ServiceException):
    """Exception for resource not found errors"""
    def __init__(self, resource_type: str, identifier: str):
        message = f"{resource_type} with identifier '{identifier}' not found"
        super().__init__(message, "RESOURCE_NOT_FOUND", {
            "resource_type": resource_type,
            "identifier": identifier
        })

# Try to import enhanced exception system
try:
    from exceptions.base import DiagnoAssistException
    from exceptions.validation import DataIntegrityException
    from exceptions.medical import (
        PatientSafetyException, 
        ClinicalDataException,
        DiagnosisException,
        TreatmentException,
        MedicalValidationException
    )
    from exceptions.handlers import handle_service_exception, raise_for_patient_safety
    ENHANCED_EXCEPTIONS_AVAILABLE = True
    logger.info("Enhanced medical exception handling loaded")
except ImportError as e:
    logger.info(f"Enhanced exceptions not available, using basic exceptions: {e}")
    ENHANCED_EXCEPTIONS_AVAILABLE = False
    DiagnoAssistException = ServiceException
    DataIntegrityException = ValidationException
    PatientSafetyException = BusinessRuleException
    ClinicalDataException = ValidationException
    DiagnosisException = ValidationException
    TreatmentException = ValidationException
    MedicalValidationException = ValidationException
    
    # Fallback functions
    def handle_service_exception(func):
        return func
    
    def raise_for_patient_safety(condition: bool, message: str, patient_id: str, safety_rule: str):
        if condition:
            raise BusinessRuleException(f"PATIENT SAFETY: {message}", rule=safety_rule)

class BaseService(ABC):
    """
    Enhanced abstract base service class providing common functionality
    with optional medical domain exception handling
    """
    
    def __init__(self, repositories: RepositoryManager):
        """
        Initialize base service with repository manager
        
        Args:
            repositories: Repository manager instance
        """
        self.repos = repositories
        self.db = repositories.db
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        self.enhanced_exceptions = ENHANCED_EXCEPTIONS_AVAILABLE
    
    @abstractmethod
    def validate_business_rules(self, data: Dict[str, Any], operation: str = "create") -> None:
        """
        Validate domain-specific business rules
        
        Args:
            data: Data to validate
            operation: Operation being performed
            
        Raises:
            BusinessRuleException: If business rules are violated
            ValidationException: If validation fails
        """
        pass
    
    def validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]) -> None:
        """
        Validate that required fields are present and not empty
        
        Args:
            data: Data to validate
            required_fields: List of required field names
            
        Raises:
            ValidationException: If required fields are missing
        """
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == "":
                raise ValidationException(
                    f"Required field '{field}' is missing or empty",
                    field=field,
                    value=data.get(field)
                )
    
    def validate_uuid(self, value: str, field_name: str) -> None:
        """
        Validate UUID format
        
        Args:
            value: UUID string to validate
            field_name: Field name for error reporting
            
        Raises:
            ValidationException: If UUID is invalid
        """
        try:
            uuid.UUID(value)
        except (ValueError, TypeError):
            raise ValidationException(
                f"Invalid UUID format for {field_name}: {value}",
                field=field_name,
                value=value
            )
    
    def get_or_raise(self, resource_type: str, resource_id: str, getter_func) -> Any:
        """
        Get resource or raise ResourceNotFoundException
        
        Args:
            resource_type: Type of resource
            resource_id: Resource identifier
            getter_func: Function to get the resource
            
        Returns:
            Resource object
            
        Raises:
            ResourceNotFoundException: If resource not found
        """
        resource = getter_func(resource_id)
        if not resource:
            raise ResourceNotFoundException(resource_type, resource_id)
        return resource
    
    def safe_commit(self, operation: str = "operation") -> None:
        """
        Safely commit database transaction with error handling
        
        Args:
            operation: Description of the operation being committed
        """
        try:
            self.repos.commit()
            self.logger.info(f"Successfully committed {operation}")
        except Exception as e:
            self.logger.error(f"Error committing {operation}: {str(e)}")
            self.safe_rollback(operation)
            raise
    
    def safe_rollback(self, operation: str = "operation") -> None:
        """
        Safely rollback database transaction with error handling
        
        Args:
            operation: Description of the operation being rolled back
        """
        try:
            self.repos.rollback()
            self.logger.warning(f"Rolled back {operation}")
        except Exception as e:
            self.logger.error(f"Error rolling back {operation}: {str(e)}")
    
    def handle_database_error(self, error: SQLAlchemyError, operation: str = "database operation") -> None:
        """
        Handle database errors with enhanced exception system if available
        
        Args:
            error: SQLAlchemy error
            operation: Description of the operation that failed
            
        Raises:
            Various exceptions based on the error type
        """
        error_message = str(error)
        
        if ENHANCED_EXCEPTIONS_AVAILABLE:
            # Use enhanced exception system if available
            if "unique constraint" in error_message.lower():
                raise DataIntegrityException(
                    message=f"Duplicate record detected during {operation}",
                    integrity_type="unique",
                    table_name=self._extract_table_from_error(error_message)
                )
            elif "foreign key constraint" in error_message.lower():
                raise DataIntegrityException(
                    message=f"Reference constraint violation during {operation}",
                    integrity_type="foreign_key",
                    table_name=self._extract_table_from_error(error_message)
                )
            elif "not null constraint" in error_message.lower():
                raise DataIntegrityException(
                    message=f"Required field missing during {operation}",
                    integrity_type="check",
                    table_name=self._extract_table_from_error(error_message)
                )
            else:
                raise ServiceException(
                    f"Database error during {operation}",
                    "DATABASE_ERROR",
                    {"operation": operation, "original_exception": str(error)}
                )
        else:
            # Fallback to basic exceptions
            if "unique constraint" in error_message.lower():
                raise ValidationException(f"Duplicate record detected during {operation}")
            elif "foreign key constraint" in error_message.lower():
                raise ValidationException(f"Reference constraint violation during {operation}")
            elif "not null constraint" in error_message.lower():
                raise ValidationException(f"Required field missing during {operation}")
            else:
                raise ServiceException(
                    f"Database error during {operation}: {error_message}",
                    "DATABASE_ERROR",
                    {"operation": operation, "database_error": error_message}
                )
    
    def _extract_table_from_error(self, error_message: str) -> Optional[str]:
        """Extract table name from database error message"""
        # Simple extraction - could be enhanced
        for word in error_message.split():
            if word.endswith('.'):
                return word.rstrip('.')
        return None
    
    def audit_log(self, action: str, resource_type: str, resource_id: str, details: Optional[Dict] = None) -> None:
        """
        Enhanced audit logging with medical context
        
        Args:
            action: Action performed (create, update, delete, etc.)
            resource_type: Type of resource
            resource_id: Resource identifier
            details: Additional details
        """
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "service": self.__class__.__name__,
            "enhanced_exceptions": self.enhanced_exceptions,
            "details": details or {}
        }
        
        # Log with appropriate level based on action
        if action in ["delete", "deactivate"]:
            self.logger.warning(f"Audit: {action} {resource_type} {resource_id}", extra=audit_entry)
        else:
            self.logger.info(f"Audit: {action} {resource_type} {resource_id}", extra=audit_entry)

# Utility functions for enhanced exception handling
def use_enhanced_exceptions() -> bool:
    """Check if enhanced exception system is available"""
    return ENHANCED_EXCEPTIONS_AVAILABLE

def get_patient_safety_validator():
    """Get patient safety validation function"""
    if ENHANCED_EXCEPTIONS_AVAILABLE:
        return raise_for_patient_safety
    else:
        def basic_safety_check(condition: bool, message: str, patient_id: str, safety_rule: str):
            if condition:
                raise BusinessRuleException(f"PATIENT SAFETY: {message}", rule=safety_rule)
        return basic_safety_check

# Enhanced service decorator
def enhanced_service_method(func):
    """
    Decorator for service methods to provide enhanced exception handling
    """
    if ENHANCED_EXCEPTIONS_AVAILABLE:
        return handle_service_exception(func)
    else:
        # Basic error handling
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Service error in {func.__name__}: {str(e)}")
                raise
        return wrapper