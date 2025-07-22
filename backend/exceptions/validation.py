"""
Validation Exception Classes for DiagnoAssist
Handles data validation, schema validation, and business rule violations
"""

from typing import Optional, Dict, Any, List, Union
from .base import DiagnoAssistException


class ValidationException(DiagnoAssistException):
    """
    General validation exception for input data validation
    """
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Any = None,
        expected_type: Optional[str] = None,
        validation_rule: Optional[str] = None
    ):
        self.field = field
        self.value = value
        self.expected_type = expected_type
        self.validation_rule = validation_rule
        
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)[:100]  # Limit value length
        if expected_type:
            details["expected_type"] = expected_type
        if validation_rule:
            details["validation_rule"] = validation_rule
        
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details,
            severity="warning"
        )
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly validation error message"""
        if self.field and self.expected_type:
            return f"Invalid {self.field}: expected {self.expected_type}"
        elif self.field:
            return f"Invalid value for {self.field.replace('_', ' ').title()}"
        else:
            return "Invalid input data. Please check your values and try again."


class SchemaValidationException(DiagnoAssistException):
    """
    Exception for Pydantic schema validation errors
    Handles complex validation error aggregation
    """
    
    def __init__(
        self,
        message: str,
        validation_errors: List[Dict[str, Any]],
        schema_name: Optional[str] = None
    ):
        self.validation_errors = validation_errors
        self.schema_name = schema_name
        
        # Extract field names from validation errors
        error_fields = []
        for error in validation_errors:
            if "loc" in error:
                field_path = ".".join(str(loc) for loc in error["loc"])
                error_fields.append(field_path)
        
        details = {
            "validation_errors": validation_errors,
            "schema_name": schema_name,
            "error_fields": error_fields,
            "error_count": len(validation_errors)
        }
        
        super().__init__(
            message=message,
            error_code="SCHEMA_VALIDATION_ERROR",
            details=details,
            severity="warning"
        )
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly schema validation message"""
        error_count = len(self.validation_errors)
        
        if error_count == 1:
            error = self.validation_errors[0]
            field = ".".join(str(loc) for loc in error.get("loc", []))
            return f"Invalid {field}: {error.get('msg', 'validation failed')}"
        else:
            return f"Found {error_count} validation errors. Please check your input data."
    
    def get_field_errors(self) -> Dict[str, List[str]]:
        """Get validation errors grouped by field"""
        field_errors = {}
        
        for error in self.validation_errors:
            field_path = ".".join(str(loc) for loc in error.get("loc", ["unknown"]))
            error_msg = error.get("msg", "Validation failed")
            
            if field_path not in field_errors:
                field_errors[field_path] = []
            field_errors[field_path].append(error_msg)
        
        return field_errors


class BusinessRuleException(DiagnoAssistException):
    """
    Exception for business rule violations
    Handles domain-specific business logic violations
    """
    
    def __init__(
        self,
        message: str,
        rule_name: str,
        rule_description: Optional[str] = None,
        context_data: Optional[Dict[str, Any]] = None,
        suggested_action: Optional[str] = None
    ):
        self.rule_name = rule_name
        self.rule_description = rule_description
        self.context_data = context_data or {}
        self.suggested_action = suggested_action
        
        details = {
            "rule_name": rule_name,
            "rule_description": rule_description,
            "context_data": context_data,
            "suggested_action": suggested_action
        }
        
        super().__init__(
            message=message,
            error_code="BUSINESS_RULE_VIOLATION",
            details=details,
            severity="warning"
        )
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly business rule violation message"""
        if self.suggested_action:
            return f"Business rule violation: {self.rule_description or self.rule_name}. {self.suggested_action}"
        elif self.rule_description:
            return f"Business rule violation: {self.rule_description}"
        else:
            return f"Business rule violation: {self.rule_name}"


class DataIntegrityException(DiagnoAssistException):
    """
    Exception for data integrity violations
    Handles referential integrity, constraints, and data consistency issues
    """
    
    def __init__(
        self,
        message: str,
        integrity_type: str,  # "referential", "unique", "check", "foreign_key"
        table_name: Optional[str] = None,
        column_name: Optional[str] = None,
        constraint_name: Optional[str] = None,
        related_record: Optional[str] = None
    ):
        self.integrity_type = integrity_type
        self.table_name = table_name
        self.column_name = column_name
        self.constraint_name = constraint_name
        self.related_record = related_record
        
        details = {
            "integrity_type": integrity_type,
            "table_name": table_name,
            "column_name": column_name,
            "constraint_name": constraint_name,
            "related_record": related_record
        }
        
        super().__init__(
            message=message,
            error_code="DATA_INTEGRITY_ERROR",
            details=details,
            severity="error"
        )
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly data integrity error message"""
        if self.integrity_type == "unique":
            if self.column_name:
                return f"A record with this {self.column_name.replace('_', ' ')} already exists."
            else:
                return "This record already exists."
        
        elif self.integrity_type == "foreign_key":
            if self.related_record:
                return f"Referenced record '{self.related_record}' does not exist."
            else:
                return "Referenced record does not exist."
        
        elif self.integrity_type == "referential":
            return "Cannot delete this record because it is referenced by other data."
        
        elif self.integrity_type == "check":
            if self.column_name:
                return f"Invalid value for {self.column_name.replace('_', ' ')}."
            else:
                return "Data validation constraint violated."
        
        else:
            return "Data integrity constraint violated."


class ConcurrencyException(DiagnoAssistException):
    """
    Exception for concurrency and race condition issues
    Handles optimistic locking, version conflicts, etc.
    """
    
    def __init__(
        self,
        message: str,
        resource_type: str,
        resource_id: str,
        expected_version: Optional[int] = None,
        actual_version: Optional[int] = None,
        conflict_user: Optional[str] = None
    ):
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.expected_version = expected_version
        self.actual_version = actual_version
        self.conflict_user = conflict_user
        
        details = {
            "resource_type": resource_type,
            "resource_id": resource_id,
            "expected_version": expected_version,
            "actual_version": actual_version,
            "conflict_user": conflict_user
        }
        
        super().__init__(
            message=message,
            error_code="CONCURRENCY_ERROR",
            details=details,
            severity="warning"
        )
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly concurrency error message"""
        if self.conflict_user:
            return f"This {self.resource_type.lower()} is being edited by {self.conflict_user}. Please refresh and try again."
        elif self.expected_version and self.actual_version:
            return f"This {self.resource_type.lower()} has been modified by another user. Please refresh and try again."
        else:
            return f"Conflict detected while updating {self.resource_type.lower()}. Please refresh and try again."


class RateLimitException(DiagnoAssistException):
    """
    Exception for rate limiting violations
    """
    
    def __init__(
        self,
        message: str,
        limit_type: str,  # "requests_per_minute", "api_calls", "compute_time"
        current_usage: int,
        limit: int,
        reset_time: Optional[int] = None,
        user_id: Optional[str] = None
    ):
        self.limit_type = limit_type
        self.current_usage = current_usage
        self.limit = limit
        self.reset_time = reset_time
        self.user_id = user_id
        
        details = {
            "limit_type": limit_type,
            "current_usage": current_usage,
            "limit": limit,
            "reset_time": reset_time,
            "user_id": user_id
        }
        
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details,
            severity="warning"
        )
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly rate limit error message"""
        if self.reset_time:
            return f"Rate limit exceeded. Please wait {self.reset_time} seconds before trying again."
        else:
            return "Rate limit exceeded. Please wait before making more requests."


class ConfigurationException(DiagnoAssistException):
    """
    Exception for configuration and setup errors
    """
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        config_file: Optional[str] = None,
        expected_value: Optional[str] = None,
        current_value: Optional[str] = None
    ):
        self.config_key = config_key
        self.config_file = config_file
        self.expected_value = expected_value
        self.current_value = current_value
        
        details = {
            "config_key": config_key,
            "config_file": config_file,
            "expected_value": expected_value,
            "current_value": current_value
        }
        
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            details=details,
            severity="error"
        )
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly configuration error message"""
        if self.config_key:
            return f"Configuration error: {self.config_key} is not properly configured."
        else:
            return "System configuration error. Please contact your administrator."