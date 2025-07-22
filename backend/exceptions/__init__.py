"""
DiagnoAssist Exception Handling Module
Comprehensive error handling for medical applications
"""

from .base import (
    DiagnoAssistException,
    APIException,
    DatabaseException,
    ExternalServiceException
)

from .validation import (
    ValidationException,
    SchemaValidationException,
    BusinessRuleException,
    DataIntegrityException
)

from .resource import (
    ResourceNotFoundException,
    ResourceConflictException,
    ResourcePermissionException,
    ResourceLockedException
)

from .medical import (
    MedicalValidationException,
    FHIRValidationException,
    ClinicalDataException,
    DiagnosisException,
    TreatmentException,
    PatientSafetyException
)

from .authentication import (
    AuthenticationException,
    AuthorizationException,
    TokenException,
    SessionException
)

from .external import (
    AIServiceException,
    FHIRServerException,
    ThirdPartyAPIException,
    RateLimitException
)

from .handlers import (
    setup_exception_handlers,
    create_error_response,
    log_exception
)

# Exception mapping for HTTP status codes
EXCEPTION_STATUS_MAP = {
    # Client errors (4xx)
    ValidationException: 400,
    SchemaValidationException: 400,
    BusinessRuleException: 400,
    DataIntegrityException: 400,
    MedicalValidationException: 400,
    FHIRValidationException: 400,
    
    # Authentication/Authorization
    AuthenticationException: 401,
    TokenException: 401,
    AuthorizationException: 403,
    ResourcePermissionException: 403,
    SessionException: 403,
    
    # Resource errors
    ResourceNotFoundException: 404,
    ResourceConflictException: 409,
    ResourceLockedException: 423,
    
    # Rate limiting
    RateLimitException: 429,
    
    # Server errors (5xx)
    DatabaseException: 500,
    ExternalServiceException: 502,
    AIServiceException: 502,
    FHIRServerException: 502,
    ThirdPartyAPIException: 502,
    
    # Safety critical
    PatientSafetyException: 500,  # Always treat as critical
    ClinicalDataException: 500,
    DiagnosisException: 500,
    TreatmentException: 500,
}

__all__ = [
    # Base exceptions
    "DiagnoAssistException",
    "APIException", 
    "DatabaseException",
    "ExternalServiceException",
    
    # Validation exceptions
    "ValidationException",
    "SchemaValidationException", 
    "BusinessRuleException",
    "DataIntegrityException",
    
    # Resource exceptions
    "ResourceNotFoundException",
    "ResourceConflictException",
    "ResourcePermissionException",
    "ResourceLockedException",
    
    # Medical exceptions
    "MedicalValidationException",
    "FHIRValidationException",
    "ClinicalDataException", 
    "DiagnosisException",
    "TreatmentException",
    "PatientSafetyException",
    
    # Authentication exceptions
    "AuthenticationException",
    "AuthorizationException",
    "TokenException",
    "SessionException",
    
    # External service exceptions
    "AIServiceException",
    "FHIRServerException", 
    "ThirdPartyAPIException",
    "RateLimitException",
    
    # Handlers
    "setup_exception_handlers",
    "create_error_response",
    "log_exception",
    "EXCEPTION_STATUS_MAP"
]