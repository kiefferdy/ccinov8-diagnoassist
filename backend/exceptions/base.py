"""
Base Exception Classes for DiagnoAssist
Foundation exceptions providing common functionality
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
import traceback


class DiagnoAssistException(Exception):
    """
    Base exception for all DiagnoAssist-specific errors
    Provides common functionality for error tracking, logging, and reporting
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None,
        severity: str = "error",
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize base exception
        
        Args:
            message: Technical error message for developers
            error_code: Unique error code for categorization
            details: Additional error details and data
            user_message: User-friendly error message
            severity: Error severity (debug, info, warning, error, critical)
            context: Additional context information
        """
        self.message = message
        self.error_code = error_code or self.__class__.__name__.upper()
        self.details = details or {}
        self.user_message = user_message or self._generate_user_message()
        self.severity = severity
        self.context = context or {}
        
        # Error tracking
        self.error_id = str(uuid.uuid4())
        self.timestamp = datetime.utcnow()
        self.traceback = traceback.format_exc()
        
        super().__init__(self.message)
    
    def _generate_user_message(self) -> str:
        """Generate a user-friendly error message"""
        return "An error occurred while processing your request. Please try again or contact support."
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""
        return {
            "error_id": self.error_id,
            "error_code": self.error_code,
            "message": self.user_message,
            "details": self.details,
            "severity": self.severity,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context
        }
    
    def to_fhir_operation_outcome(self) -> Dict[str, Any]:
        """Convert exception to FHIR OperationOutcome format"""
        severity_mapping = {
            "debug": "information",
            "info": "information", 
            "warning": "warning",
            "error": "error",
            "critical": "fatal"
        }
        
        return {
            "resourceType": "OperationOutcome",
            "id": self.error_id,
            "issue": [
                {
                    "severity": severity_mapping.get(self.severity, "error"),
                    "code": "processing",
                    "details": {
                        "coding": [
                            {
                                "system": "https://diagnoassist.app/error-codes",
                                "code": self.error_code,
                                "display": self.error_code.replace("_", " ").title()
                            }
                        ],
                        "text": self.user_message
                    },
                    "diagnostics": self.message if self.severity == "debug" else None,
                    "expression": list(self.context.keys()) if self.context else None
                }
            ],
            "meta": {
                "lastUpdated": self.timestamp.isoformat(),
                "source": "DiagnoAssist/1.0.0"
            }
        }
    
    def add_context(self, key: str, value: Any) -> None:
        """Add context information to the exception"""
        self.context[key] = value
    
    def add_details(self, key: str, value: Any) -> None:
        """Add detail information to the exception"""
        self.details[key] = value


class APIException(DiagnoAssistException):
    """
    Base exception for API-related errors
    Used for HTTP/REST API specific issues
    """
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        self.status_code = status_code
        self.headers = headers or {}
        
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            user_message=user_message,
            severity="error" if status_code >= 500 else "warning"
        )
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly message based on status code"""
        if self.status_code == 400:
            return "Invalid request. Please check your input and try again."
        elif self.status_code == 401:
            return "Authentication required. Please log in and try again."
        elif self.status_code == 403:
            return "You don't have permission to perform this action."
        elif self.status_code == 404:
            return "The requested resource was not found."
        elif self.status_code == 409:
            return "This action conflicts with existing data."
        elif self.status_code == 429:
            return "Too many requests. Please wait and try again."
        elif self.status_code >= 500:
            return "A server error occurred. Our team has been notified."
        else:
            return "An error occurred while processing your request."


class DatabaseException(DiagnoAssistException):
    """
    Exception for database-related errors
    Handles connection issues, query failures, constraints, etc.
    """
    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        table: Optional[str] = None,
        constraint: Optional[str] = None,
        original_exception: Optional[Exception] = None
    ):
        self.operation = operation  # INSERT, UPDATE, DELETE, SELECT
        self.table = table
        self.constraint = constraint
        self.original_exception = original_exception
        
        details = {}
        if operation:
            details["operation"] = operation
        if table:
            details["table"] = table
        if constraint:
            details["constraint"] = constraint
        if original_exception:
            details["original_error"] = str(original_exception)
        
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details=details,
            severity="error"
        )
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly database error message"""
        if self.constraint:
            if "unique" in self.constraint.lower():
                return "This record already exists. Please check for duplicates."
            elif "foreign" in self.constraint.lower():
                return "Cannot complete operation due to data dependencies."
            elif "check" in self.constraint.lower():
                return "The provided data doesn't meet validation requirements."
        
        if self.operation:
            operation_messages = {
                "INSERT": "Failed to create the record.",
                "UPDATE": "Failed to update the record.", 
                "DELETE": "Failed to delete the record.",
                "SELECT": "Failed to retrieve the requested data."
            }
            return operation_messages.get(self.operation, "Database operation failed.")
        
        return "A database error occurred. Please try again or contact support."


class ExternalServiceException(DiagnoAssistException):
    """
    Exception for external service integration errors
    Handles API calls, third-party services, network issues
    """
    
    def __init__(
        self,
        message: str,
        service_name: str,
        endpoint: Optional[str] = None,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        timeout: bool = False,
        network_error: bool = False
    ):
        self.service_name = service_name
        self.endpoint = endpoint
        self.status_code = status_code
        self.response_body = response_body
        self.timeout = timeout
        self.network_error = network_error
        
        details = {
            "service": service_name,
            "endpoint": endpoint,
            "status_code": status_code,
            "timeout": timeout,
            "network_error": network_error
        }
        
        if response_body:
            details["response"] = response_body[:500]  # Limit response size
        
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details,
            severity="error"
        )
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly external service error message"""
        if self.timeout:
            return f"The {self.service_name} service is taking too long to respond. Please try again."
        elif self.network_error:
            return f"Unable to connect to {self.service_name}. Please check your connection."
        elif self.status_code:
            if self.status_code >= 500:
                return f"The {self.service_name} service is temporarily unavailable."
            elif self.status_code == 429:
                return f"Too many requests to {self.service_name}. Please wait and try again."
            else:
                return f"Error communicating with {self.service_name}."
        else:
            return f"Failed to connect to {self.service_name}. Please try again later."