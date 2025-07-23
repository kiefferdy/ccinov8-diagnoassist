"""
Enhanced Base Service Class for DiagnoAssist - COMPLETE VERSION
Business Logic Layer Foundation with all required methods
"""

from __future__ import annotations
from typing import TypeVar, Optional, Dict, Any, List, TYPE_CHECKING
from abc import ABC, abstractmethod
from datetime import datetime, timezone
try:
    from sqlalchemy.exc import SQLAlchemyError
except ImportError:
    # Fallback for when SQLAlchemy is not available
    class SQLAlchemyError(Exception):
        pass
import logging
import uuid

if TYPE_CHECKING:
    from repositories.repository_manager import RepositoryManager

from repositories.repository_manager import RepositoryManager

logger = logging.getLogger(__name__)

T = TypeVar('T')

# Use standard Python exceptions

# Fallback functions for compatibility
def handle_service_exception(func):
    return func

def raise_for_patient_safety(condition: bool, message: str, patient_id: str = None, safety_rule: str = None):
    if condition:
        raise RuntimeError(f"PATIENT SAFETY: {message} (Rule: {safety_rule})")

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
        pass  # Simplified initialization
    
    @abstractmethod
    def validate_business_rules(self, data: Dict[str, Any], operation: str = "create") -> None:
        """
        Validate domain-specific business rules
        
        Args:
            data: Data to validate
            operation: Operation being performed
            
        Raises:
            RuntimeError: If business rules are violated
            ValueError: If validation fails
        """
        pass
    
    def validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]) -> None:
        """
        Validate that required fields are present and not empty
        
        Args:
            data: Data to validate
            required_fields: List of required field names
            
        Raises:
            ValueError: If required fields are missing
        """
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == "":
                raise ValueError(f"Required field '{field}' is missing or empty")
    
    def validate_uuid(self, value: str, field_name: str) -> None:
        """
        Validate UUID format
        
        Args:
            value: UUID string to validate
            field_name: Field name for error reporting
            
        Raises:
            ValueError: If UUID is invalid
        """
        try:
            uuid.UUID(value)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid UUID format for {field_name}: {value}")
    
    def get_or_raise(self, resource_type: str, resource_id: str, getter_func) -> Any:
        """
        Get resource or raise LookupError
        
        Args:
            resource_type: Type of resource
            resource_id: Resource identifier
            getter_func: Function to get the resource
            
        Returns:
            Resource object
            
        Raises:
            LookupError: If resource not found
        """
        resource = getter_func(resource_id)
        if not resource:
            raise LookupError(f"{resource_type} with identifier '{resource_id}' not found")
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
        
        # Handle database errors with standard exceptions
        if "unique constraint" in error_message.lower():
            raise ValueError(f"Duplicate record detected during {operation}")
        elif "foreign key constraint" in error_message.lower():
            raise ValueError(f"Reference constraint violation during {operation}")
        elif "not null constraint" in error_message.lower():
            raise ValueError(f"Required field missing during {operation}")
        else:
            raise RuntimeError(f"Database error during {operation}: {error_message}")
    
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
            "timestamp": datetime.now(timezone.utc).isoformat(),
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

# Utility functions for patient safety

def get_patient_safety_validator():
    """Get patient safety validation function"""
    return raise_for_patient_safety

# Service method decorator
def enhanced_service_method(func):
    """
    Decorator for service methods to provide basic error handling
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Service error in {func.__name__}: {str(e)}")
            raise
    return wrapper