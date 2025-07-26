"""
Custom exception classes for DiagnoAssist Backend
"""
from typing import Any, Dict, Optional


class DiagnoAssistException(Exception):
    """Base exception for DiagnoAssist"""
    
    def __init__(
        self, 
        message: str, 
        error_code: str = "GENERAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(DiagnoAssistException):
    """Data validation errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "VALIDATION_ERROR", details)


class NotFoundError(DiagnoAssistException):
    """Resource not found errors"""
    
    def __init__(self, resource: str, identifier: str):
        message = f"{resource} with id '{identifier}' not found"
        super().__init__(message, "NOT_FOUND", {"resource": resource, "id": identifier})


class DatabaseException(DiagnoAssistException):
    """Database operation errors"""
    
    def __init__(self, message: str, operation: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "DATABASE_ERROR", {"operation": operation, **(details or {})})


class FHIRException(DiagnoAssistException):
    """FHIR integration errors"""
    
    def __init__(self, message: str, fhir_operation: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "FHIR_ERROR", {"fhir_operation": fhir_operation, **(details or {})})


class AIServiceException(DiagnoAssistException):
    """AI service errors"""
    
    def __init__(self, message: str, ai_operation: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "AI_SERVICE_ERROR", {"ai_operation": ai_operation, **(details or {})})


class AuthenticationException(DiagnoAssistException):
    """Authentication errors"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTHENTICATION_ERROR")


class AuthorizationException(DiagnoAssistException):
    """Authorization errors"""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, "AUTHORIZATION_ERROR")


class PermissionDeniedError(DiagnoAssistException):
    """Permission denied errors"""
    
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, "PERMISSION_DENIED")


class ConflictException(DiagnoAssistException):
    """Resource conflict errors"""
    
    def __init__(self, message: str, resource: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "CONFLICT_ERROR", {"resource": resource, **(details or {})})


class RateLimitException(DiagnoAssistException):
    """Rate limiting errors"""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None):
        details = {"retry_after": retry_after} if retry_after else {}
        super().__init__(message, "RATE_LIMIT_ERROR", details)


class BusinessRuleException(DiagnoAssistException):
    """Business rule violation errors"""
    
    def __init__(self, message: str, violations: Optional[list] = None):
        from typing import TYPE_CHECKING
        if TYPE_CHECKING:
            from app.core.business_rules import RuleViolation
        
        details = {"violations": violations or []}
        super().__init__(message, "BUSINESS_RULE_ERROR", details)
        
        # Store violations for easy access
        self.violations = violations or []


class WebSocketException(DiagnoAssistException):
    """WebSocket connection and messaging errors"""
    
    def __init__(self, message: str, connection_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        error_details = {"connection_id": connection_id, **(details or {})}
        super().__init__(message, "WEBSOCKET_ERROR", error_details)