"""
External Service Exception Classes for DiagnoAssist
Handles integration with AI services, FHIR servers, and third-party APIs
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from .base import DiagnoAssistException, ExternalServiceException


class AIServiceException(ExternalServiceException):
    """
    Exception for AI/ML service integration errors
    Specialized for AI model failures, bias detection, confidence issues
    """
    
    def __init__(
        self,
        message: str,
        model_name: Optional[str] = None,
        model_version: Optional[str] = None,
        confidence_score: Optional[float] = None,
        bias_detected: bool = False,
        input_validation_error: bool = False,
        prediction_error: bool = False,
        training_required: bool = False
    ):
        self.model_name = model_name
        self.model_version = model_version
        self.confidence_score = confidence_score
        self.bias_detected = bias_detected
        self.input_validation_error = input_validation_error
        self.prediction_error = prediction_error
        self.training_required = training_required
        
        # Determine severity based on error type
        if bias_detected:
            severity = "critical"
        elif confidence_score is not None and confidence_score < 0.3:
            severity = "error"
        else:
            severity = "warning"
        
        super().__init__(
            message=message,
            service_name=f"AI Service ({model_name})" if model_name else "AI Service"
        )
        
        # Update severity after parent initialization
        self.severity = severity
        self.error_code = "AI_SERVICE_ERROR"
        
        # Add AI-specific details
        self.details.update({
            "model_name": model_name,
            "model_version": model_version,
            "confidence_score": confidence_score,
            "bias_detected": bias_detected,
            "input_validation_error": input_validation_error,
            "prediction_error": prediction_error,
            "training_required": training_required
        })
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly AI service error message"""
        if self.bias_detected:
            return "Potential bias detected in AI analysis. Manual review strongly recommended."
        elif self.confidence_score is not None and self.confidence_score < 0.5:
            return f"AI confidence is low ({self.confidence_score:.2f}). Please verify results manually."
        elif self.input_validation_error:
            return "Invalid input data for AI analysis. Please check the format and completeness."
        elif self.prediction_error:
            return "AI prediction failed. Please try again or proceed with manual analysis."
        elif self.training_required:
            return "AI model requires retraining. Results may be less accurate."
        elif self.model_name:
            return f"AI model '{self.model_name}' encountered an error. Please try again."
        else:
            return "AI analysis failed. Please try again or proceed with manual analysis."


class FHIRServerException(ExternalServiceException):
    """
    Exception for FHIR server integration errors
    """
    
    def __init__(
        self,
        message: str,
        fhir_server_url: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        operation: Optional[str] = None,  # "create", "read", "update", "delete", "search"
        fhir_error_code: Optional[str] = None,
        operation_outcome: Optional[Dict[str, Any]] = None
    ):
        self.fhir_server_url = fhir_server_url
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.operation = operation
        self.fhir_error_code = fhir_error_code
        self.operation_outcome = operation_outcome
        
        super().__init__(
            message=message,
            service_name="FHIR Server",
            endpoint=f"{fhir_server_url}/{resource_type}" if resource_type else fhir_server_url
        )
        
        self.error_code = "FHIR_SERVER_ERROR"
        
        # Add FHIR-specific details
        self.details.update({
            "fhir_server_url": fhir_server_url,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "operation": operation,
            "fhir_error_code": fhir_error_code,
            "operation_outcome": operation_outcome
        })
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly FHIR server error message"""
        if self.operation and self.resource_type:
            operations = {
                "create": f"create {self.resource_type}",
                "read": f"retrieve {self.resource_type}",
                "update": f"update {self.resource_type}",
                "delete": f"delete {self.resource_type}",
                "search": f"search {self.resource_type}"
            }
            operation_text = operations.get(self.operation, f"{self.operation} {self.resource_type}")
            return f"Failed to {operation_text} on FHIR server."
        else:
            return "FHIR server communication error. Please try again."
    
    def to_fhir_operation_outcome(self) -> Dict[str, Any]:
        """Convert to FHIR OperationOutcome, preserving original if available"""
        if self.operation_outcome:
            return self.operation_outcome
        else:
            return super().to_fhir_operation_outcome()


class ThirdPartyAPIException(ExternalServiceException):
    """
    Exception for third-party API integration errors
    """
    
    def __init__(
        self,
        message: str,
        api_name: str,
        api_endpoint: Optional[str] = None,
        api_method: str = "GET",
        rate_limited: bool = False,
        quota_exceeded: bool = False,
        api_key_invalid: bool = False,
        service_unavailable: bool = False,
        response_format_error: bool = False
    ):
        self.api_name = api_name
        self.api_endpoint = api_endpoint
        self.api_method = api_method
        self.rate_limited = rate_limited
        self.quota_exceeded = quota_exceeded
        self.api_key_invalid = api_key_invalid
        self.service_unavailable = service_unavailable
        self.response_format_error = response_format_error
        
        super().__init__(
            message=message,
            service_name=api_name,
            endpoint=api_endpoint
        )
        
        self.error_code = "THIRD_PARTY_API_ERROR"
        
        # Add API-specific details
        self.details.update({
            "api_name": api_name,
            "api_endpoint": api_endpoint,
            "api_method": api_method,
            "rate_limited": rate_limited,
            "quota_exceeded": quota_exceeded,
            "api_key_invalid": api_key_invalid,
            "service_unavailable": service_unavailable,
            "response_format_error": response_format_error
        })
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly third-party API error message"""
        if self.api_key_invalid:
            return f"Invalid API credentials for {self.api_name}. Please check configuration."
        elif self.rate_limited:
            return f"{self.api_name} rate limit exceeded. Please wait and try again."
        elif self.quota_exceeded:
            return f"{self.api_name} usage quota exceeded. Please try again later."
        elif self.service_unavailable:
            return f"{self.api_name} service is currently unavailable."
        elif self.response_format_error:
            return f"Unexpected response format from {self.api_name}."
        else:
            return f"Error communicating with {self.api_name}. Please try again."


class RateLimitException(DiagnoAssistException):
    """
    Exception for rate limiting violations
    Can be used for both internal and external rate limits
    """
    
    def __init__(
        self,
        message: str,
        limit_type: str,  # "requests_per_minute", "api_calls", "compute_time", "bandwidth"
        service_name: str,
        current_usage: int,
        limit: int,
        reset_time: Optional[datetime] = None,
        reset_seconds: Optional[int] = None,
        user_id: Optional[str] = None
    ):
        self.limit_type = limit_type
        self.service_name = service_name
        self.current_usage = current_usage
        self.limit = limit
        self.reset_time = reset_time
        self.reset_seconds = reset_seconds
        self.user_id = user_id
        
        details = {
            "limit_type": limit_type,
            "service_name": service_name,
            "current_usage": current_usage,
            "limit": limit,
            "reset_time": reset_time.isoformat() if reset_time else None,
            "reset_seconds": reset_seconds,
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
        if self.reset_seconds:
            return f"Rate limit exceeded for {self.service_name}. Please wait {self.reset_seconds} seconds."
        elif self.reset_time:
            return f"Rate limit exceeded for {self.service_name}. Please try again after {self.reset_time.strftime('%H:%M:%S')}."
        else:
            return f"Rate limit exceeded for {self.service_name}. Please wait and try again."


class DataSyncException(DiagnoAssistException):
    """
    Exception for data synchronization errors between systems
    """
    
    def __init__(
        self,
        message: str,
        source_system: str,
        target_system: str,
        sync_operation: str,  # "import", "export", "bidirectional", "validate"
        records_affected: Optional[int] = None,
        conflict_count: Optional[int] = None,
        data_integrity_issues: Optional[List[str]] = None
    ):
        self.source_system = source_system
        self.target_system = target_system
        self.sync_operation = sync_operation
        self.records_affected = records_affected
        self.conflict_count = conflict_count
        self.data_integrity_issues = data_integrity_issues or []
        
        details = {
            "source_system": source_system,
            "target_system": target_system,
            "sync_operation": sync_operation,
            "records_affected": records_affected,
            "conflict_count": conflict_count,
            "data_integrity_issues": data_integrity_issues
        }
        
        super().__init__(
            message=message,
            error_code="DATA_SYNC_ERROR",
            details=details,
            severity="error"
        )
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly data sync error message"""
        if self.conflict_count and self.conflict_count > 0:
            return f"Data synchronization failed: {self.conflict_count} conflicts detected between {self.source_system} and {self.target_system}."
        elif self.data_integrity_issues:
            return f"Data synchronization failed due to integrity issues between {self.source_system} and {self.target_system}."
        else:
            return f"Failed to synchronize data between {self.source_system} and {self.target_system}."


class WebhookException(DiagnoAssistException):
    """
    Exception for webhook delivery and processing errors
    """
    
    def __init__(
        self,
        message: str,
        webhook_url: str,
        event_type: str,
        webhook_id: Optional[str] = None,
        delivery_attempt: int = 1,
        max_attempts: int = 3,
        response_status: Optional[int] = None,
        response_body: Optional[str] = None
    ):
        self.webhook_url = webhook_url
        self.event_type = event_type
        self.webhook_id = webhook_id
        self.delivery_attempt = delivery_attempt
        self.max_attempts = max_attempts
        self.response_status = response_status
        self.response_body = response_body
        
        details = {
            "webhook_url": webhook_url,
            "event_type": event_type,
            "webhook_id": webhook_id,
            "delivery_attempt": delivery_attempt,
            "max_attempts": max_attempts,
            "response_status": response_status,
            "response_body": response_body[:200] if response_body else None
        }
        
        super().__init__(
            message=message,
            error_code="WEBHOOK_ERROR",
            details=details,
            severity="warning"
        )
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly webhook error message"""
        if self.delivery_attempt >= self.max_attempts:
            return f"Webhook delivery failed after {self.max_attempts} attempts for event '{self.event_type}'."
        else:
            return f"Webhook delivery failed for event '{self.event_type}' (attempt {self.delivery_attempt}/{self.max_attempts})."