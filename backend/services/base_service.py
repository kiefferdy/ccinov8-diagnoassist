"""
Enhanced Base Service Class for DiagnoAssist
Business Logic Layer Foundation with Medical Exception Handling
BACKWARD COMPATIBLE with existing services
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
    
    def validate_patient_safety(
        self, 
        condition: bool, 
        message: str, 
        patient_id: str, 
        safety_rule: str,
        risk_level: str = "HIGH"
    ) -> None:
        """
        Enhanced patient safety validation
        
        Args:
            condition: If True, raise safety exception
            message: Safety violation message
            patient_id: Patient identifier
            safety_rule: Safety rule violated
            risk_level: Risk level (LOW, MEDIUM, HIGH, CRITICAL)
        """
        if condition:
            if self.enhanced_exceptions:
                raise PatientSafetyException(
                    message=message,
                    patient_id=patient_id,
                    safety_rule=safety_rule,
                    risk_level=risk_level,
                    immediate_action_required=True
                )
            else:
                # Fallback to basic exception
                raise BusinessRuleException(
                    f"PATIENT SAFETY: {message} (Patient: {patient_id})",
                    rule=safety_rule
                )
    
    def validate_clinical_data(
        self,
        data: Dict[str, Any],
        data_type: str,
        patient_id: Optional[str] = None,
        safety_critical: bool = False
    ) -> None:
        """
        Enhanced clinical data validation
        
        Args:
            data: Clinical data to validate
            data_type: Type of clinical data
            patient_id: Patient identifier
            safety_critical: Whether data is safety critical
        """
        if not data or not isinstance(data, dict):
            if self.enhanced_exceptions:
                raise ClinicalDataException(
                    message=f"Invalid {data_type} data format",
                    data_type=data_type,
                    patient_id=patient_id,
                    safety_critical=safety_critical
                )
            else:
                raise ValidationException(f"Invalid {data_type} data format")
    
    def validate_medical_code(
        self,
        code: str,
        code_system: str,
        field_name: str,
        allow_empty: bool = False
    ) -> None:
        """
        Enhanced medical code validation
        
        Args:
            code: Medical code to validate
            code_system: Code system (ICD-10, SNOMED, etc.)
            field_name: Field name for error reporting
            allow_empty: Whether empty codes are allowed
        """
        if not code and not allow_empty:
            if self.enhanced_exceptions:
                raise MedicalValidationException(
                    message=f"Missing {code_system} code",
                    field=field_name,
                    code_system=code_system
                )
            else:
                raise ValidationException(f"Missing {code_system} code", field=field_name)
        
        if code and code_system == "ICD-10":
            # Basic ICD-10 format validation
            if not (len(code) >= 3 and len(code) <= 7):
                if self.enhanced_exceptions:
                    raise MedicalValidationException(
                        message=f"Invalid ICD-10 code format: {code}",
                        field=field_name,
                        value=code,
                        medical_code=code,
                        code_system="ICD-10"
                    )
                else:
                    raise ValidationException(f"Invalid ICD-10 code format: {code}", field=field_name)
    
    def validate_diagnosis_confidence(
        self,
        ai_confidence: Optional[float],
        confidence_level: Optional[str],
        diagnosis_id: Optional[str] = None,
        min_confidence: float = 0.5
    ) -> None:
        """
        Enhanced diagnosis confidence validation
        
        Args:
            ai_confidence: AI confidence score (0.0 to 1.0)
            confidence_level: Human confidence level
            diagnosis_id: Diagnosis identifier
            min_confidence: Minimum acceptable confidence
        """
        if ai_confidence is not None:
            if ai_confidence < min_confidence:
                if self.enhanced_exceptions:
                    raise DiagnosisException(
                        message=f"AI confidence ({ai_confidence:.2f}) below minimum threshold ({min_confidence})",
                        diagnosis_id=diagnosis_id,
                        ai_confidence=ai_confidence,
                        validation_stage="confidence_check"
                    )
                else:
                    raise ValidationException(f"AI confidence too low: {ai_confidence}")
        
        if confidence_level:
            valid_levels = ["very_low", "low", "medium", "high", "very_high"]
            if confidence_level not in valid_levels:
                if self.enhanced_exceptions:
                    raise DiagnosisException(
                        message=f"Invalid confidence level: {confidence_level}",
                        diagnosis_id=diagnosis_id,
                        validation_stage="confidence_level_check"
                    )
                else:
                    raise ValidationException(f"Invalid confidence level: {confidence_level}")
    
    def handle_database_error(self, error: SQLAlchemyError, operation: str = "database operation") -> None:
        """
        Enhanced database error handling with medical context
        
        Args:
            error: SQLAlchemy error
            operation: Operation that failed
            
        Raises:
            DataIntegrityException: For constraint violations
            ValidationException: For other database errors
        """
        error_message = str(error)
        
        if self.enhanced_exceptions:
            # Use enhanced exception system
            from exceptions.base import DatabaseException
            
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
                raise DatabaseException(
                    message=f"Database error during {operation}",
                    operation=operation,
                    original_exception=error
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