"""
Base Service Class for DiagnoAssist
Business Logic Layer Foundation
"""

from __future__ import annotations
from typing import TypeVar, Generic, Optional, Dict, Any, List, TYPE_CHECKING
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import logging

if TYPE_CHECKING:
    from repositories.repository_manager import RepositoryManager

from repositories.repository_manager import RepositoryManager

logger = logging.getLogger(__name__)

T = TypeVar('T')

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

class BaseService(ABC):
    """
    Abstract base service class providing common functionality
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
    
    def validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]) -> None:
        """
        Validate that required fields are present and not empty
        
        Args:
            data: Data dictionary to validate
            required_fields: List of required field names
            
        Raises:
            ValidationException: If any required field is missing or empty
        """
        missing_fields = []
        empty_fields = []
        
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
            elif data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
                empty_fields.append(field)
        
        if missing_fields:
            raise ValidationException(
                f"Missing required fields: {', '.join(missing_fields)}",
                field="missing_fields",
                value=missing_fields
            )
        
        if empty_fields:
            raise ValidationException(
                f"Empty required fields: {', '.join(empty_fields)}",
                field="empty_fields", 
                value=empty_fields
            )
    
    def validate_uuid(self, uuid_str: str, field_name: str) -> None:
        """
        Validate UUID format
        
        Args:
            uuid_str: UUID string to validate
            field_name: Name of the field for error messages
            
        Raises:
            ValidationException: If UUID format is invalid
        """
        try:
            from uuid import UUID
            UUID(uuid_str)
        except (ValueError, TypeError):
            raise ValidationException(
                f"Invalid UUID format for {field_name}: {uuid_str}",
                field=field_name,
                value=uuid_str
            )
    
    def handle_database_error(self, error: SQLAlchemyError, operation: str) -> None:
        """
        Handle database errors with appropriate logging and exception transformation
        
        Args:
            error: SQLAlchemy error
            operation: Description of the operation that failed
            
        Raises:
            ServiceException: Transformed database error
        """
        self.logger.error(f"Database error during {operation}: {str(error)}")
        
        # Rollback transaction
        try:
            self.db.rollback()
        except Exception as rollback_error:
            self.logger.error(f"Failed to rollback transaction: {rollback_error}")
        
        # Transform specific database errors
        error_message = str(error)
        
        if "duplicate key value" in error_message.lower():
            raise ServiceException(
                f"Duplicate record detected during {operation}",
                "DUPLICATE_RECORD",
                {"operation": operation, "database_error": error_message}
            )
        elif "foreign key constraint" in error_message.lower():
            raise ServiceException(
                f"Reference constraint violation during {operation}",
                "REFERENCE_CONSTRAINT_VIOLATION",
                {"operation": operation, "database_error": error_message}
            )
        elif "not null constraint" in error_message.lower():
            raise ServiceException(
                f"Required field missing during {operation}",
                "REQUIRED_FIELD_MISSING",
                {"operation": operation, "database_error": error_message}
            )
        else:
            raise ServiceException(
                f"Database error during {operation}: {error_message}",
                "DATABASE_ERROR",
                {"operation": operation, "database_error": error_message}
            )
    
    def audit_log(self, action: str, resource_type: str, resource_id: str, details: Optional[Dict] = None) -> None:
        """
        Log service actions for audit purposes
        
        Args:
            action: Action performed (create, update, delete, etc.)
            resource_type: Type of resource
            resource_id: Resource identifier
            details: Additional details to log
        """
        audit_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.__class__.__name__,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details or {}
        }
        
        self.logger.info(f"AUDIT: {action} {resource_type} {resource_id}", extra=audit_data)
    
    def get_or_raise(self, resource_type: str, identifier: str, repository_method) -> Any:
        """
        Get resource or raise ResourceNotFoundException
        
        Args:
            resource_type: Type of resource for error messages
            identifier: Resource identifier
            repository_method: Repository method to call
            
        Returns:
            The found resource
            
        Raises:
            ResourceNotFoundException: If resource not found
        """
        try:
            resource = repository_method(identifier)
            if not resource:
                raise ResourceNotFoundException(resource_type, identifier)
            return resource
        except SQLAlchemyError as e:
            self.handle_database_error(e, f"fetching {resource_type}")
    
    def safe_commit(self, operation_description: str) -> None:
        """
        Safely commit database transaction with error handling
        
        Args:
            operation_description: Description of the operation for error messages
            
        Raises:
            ServiceException: If commit fails
        """
        try:
            self.repos.commit()
            self.logger.debug(f"Successfully committed: {operation_description}")
        except SQLAlchemyError as e:
            self.handle_database_error(e, f"committing {operation_description}")
    
    def safe_rollback(self, operation_description: str) -> None:
        """
        Safely rollback database transaction
        
        Args:
            operation_description: Description of the operation for logging
        """
        try:
            self.repos.rollback()
            self.logger.info(f"Rolled back transaction: {operation_description}")
        except Exception as e:
            self.logger.error(f"Failed to rollback {operation_description}: {e}")
    
    @abstractmethod
    def validate_business_rules(self, data: Dict[str, Any], operation: str = "create") -> None:
        """
        Abstract method to validate business rules specific to each service
        
        Args:
            data: Data to validate
            operation: Operation being performed (create, update, etc.)
            
        Raises:
            BusinessRuleException: If business rules are violated
        """
        pass