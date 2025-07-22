"""
Exception Handlers and Middleware for DiagnoAssist
Centralized error handling, logging, and response formatting
"""

import logging
import traceback
from typing import Any, Dict, Optional, Union
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from .base import DiagnoAssistException
from .medical import PatientSafetyException, ClinicalDataException
from .authentication import AuthenticationException, AuthorizationException
from .resource import ResourceNotFoundException, ResourceConflictException
from .validation import ValidationException, SchemaValidationException
from .external import RateLimitException

# Get logger
logger = logging.getLogger(__name__)

# Import the exception status mapping
try:
    from . import EXCEPTION_STATUS_MAP
except ImportError:
    # Fallback status mapping if import fails
    EXCEPTION_STATUS_MAP = {
        ValidationException: 400,
        SchemaValidationException: 400,
        AuthenticationException: 401,
        AuthorizationException: 403,
        ResourceNotFoundException: 404,
        ResourceConflictException: 409,
        RateLimitException: 429,
        PatientSafetyException: 500,
        ClinicalDataException: 500,
        DiagnoAssistException: 500,
    }


def log_exception(
    exception: Exception,
    request: Optional[Request] = None,
    user_id: Optional[str] = None,
    additional_context: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log exception with context information
    
    Args:
        exception: The exception to log
        request: FastAPI request object (if available)
        user_id: User ID associated with the request
        additional_context: Additional context information
    """
    context = additional_context or {}
    
    # Add request context if available
    if request:
        context.update({
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "request_id": getattr(request.state, "request_id", None)
        })
    
    if user_id:
        context["user_id"] = user_id
    
    # Different logging levels based on exception type
    if isinstance(exception, PatientSafetyException):
        logger.critical(
            f"PATIENT SAFETY ALERT: {exception.message}",
            extra={
                "exception_type": type(exception).__name__,
                "error_id": getattr(exception, "error_id", None),
                "context": context,
                "traceback": traceback.format_exc()
            }
        )
    elif isinstance(exception, ClinicalDataException) and exception.safety_critical:
        logger.critical(
            f"CRITICAL CLINICAL DATA ERROR: {exception.message}",
            extra={
                "exception_type": type(exception).__name__,
                "error_id": getattr(exception, "error_id", None),
                "context": context,
                "traceback": traceback.format_exc()
            }
        )
    elif isinstance(exception, DiagnoAssistException):
        if exception.severity == "critical":
            logger.critical(exception.message, extra={
                "exception_type": type(exception).__name__,
                "error_id": exception.error_id,
                "error_code": exception.error_code,
                "context": context,
                "details": exception.details
            })
        elif exception.severity == "error":
            logger.error(exception.message, extra={
                "exception_type": type(exception).__name__,
                "error_id": exception.error_id,
                "error_code": exception.error_code,
                "context": context,
                "details": exception.details
            })
        else:
            logger.warning(exception.message, extra={
                "exception_type": type(exception).__name__,
                "error_id": exception.error_id,
                "error_code": exception.error_code,
                "context": context,
                "details": exception.details
            })
    else:
        logger.error(
            f"Unhandled exception: {str(exception)}",
            extra={
                "exception_type": type(exception).__name__,
                "context": context,
                "traceback": traceback.format_exc()
            }
        )


def create_error_response(
    exception: Exception,
    status_code: Optional[int] = None,
    include_traceback: bool = False,
    fhir_format: bool = False
) -> Dict[str, Any]:
    """
    Create standardized error response
    
    Args:
        exception: The exception to format
        status_code: HTTP status code (auto-determined if None)
        include_traceback: Whether to include traceback (for debugging)
        fhir_format: Whether to format as FHIR OperationOutcome
        
    Returns:
        Error response dictionary
    """
    if isinstance(exception, DiagnoAssistException):
        if fhir_format:
            return exception.to_fhir_operation_outcome()
        
        error_response = exception.to_dict()
        
        # Add traceback for debugging if requested
        if include_traceback:
            error_response["traceback"] = exception.traceback
        
        return {
            "error": error_response,
            "success": False,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    else:
        # Handle non-DiagnoAssist exceptions
        error_id = str(datetime.utcnow().timestamp())
        
        if fhir_format:
            return {
                "resourceType": "OperationOutcome",
                "id": error_id,
                "issue": [
                    {
                        "severity": "error",
                        "code": "exception",
                        "details": {
                            "text": "An unexpected error occurred"
                        },
                        "diagnostics": str(exception) if include_traceback else None
                    }
                ],
                "meta": {
                    "lastUpdated": datetime.utcnow().isoformat(),
                    "source": "DiagnoAssist/1.0.0"
                }
            }
        
        return {
            "error": {
                "error_id": error_id,
                "error_code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {"original_error": str(exception)} if include_traceback else {},
                "severity": "error",
                "timestamp": datetime.utcnow().isoformat()
            },
            "success": False,
            "timestamp": datetime.utcnow().isoformat()
        }


def get_status_code_for_exception(exception: Exception) -> int:
    """Get appropriate HTTP status code for exception"""
    if isinstance(exception, HTTPException):
        return exception.status_code
    elif isinstance(exception, StarletteHTTPException):
        return exception.status_code
    elif type(exception) in EXCEPTION_STATUS_MAP:
        return EXCEPTION_STATUS_MAP[type(exception)]
    elif isinstance(exception, DiagnoAssistException):
        # Check parent classes
        for exc_type, status_code in EXCEPTION_STATUS_MAP.items():
            if isinstance(exception, exc_type):
                return status_code
        return 500  # Default for DiagnoAssist exceptions
    else:
        return 500  # Default for other exceptions


class ExceptionLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging exceptions and adding request context
    """
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and handle exceptions"""
        # Add request ID for tracking
        import uuid
        request.state.request_id = str(uuid.uuid4())
        
        try:
            response = await call_next(request)
            return response
            
        except Exception as exc:
            # Log the exception with request context
            user_id = getattr(request.state, "user_id", None)
            log_exception(exc, request, user_id)
            
            # Re-raise to let FastAPI exception handlers handle it
            raise exc


async def diagnoassist_exception_handler(request: Request, exc: DiagnoAssistException) -> JSONResponse:
    """
    Handler for DiagnoAssist-specific exceptions
    """
    # Log the exception
    user_id = getattr(request.state, "user_id", None)
    log_exception(exc, request, user_id)
    
    # Determine if we should use FHIR format
    fhir_format = (
        request.url.path.startswith("/fhir/") or
        request.headers.get("accept", "").startswith("application/fhir+json")
    )
    
    # Determine if we should include debug info
    include_debug = (
        request.query_params.get("debug") == "true" or
        request.headers.get("x-debug") == "true"
    )
    
    status_code = get_status_code_for_exception(exc)
    response_data = create_error_response(exc, status_code, include_debug, fhir_format)
    
    # Add CORS headers if needed
    headers = {}
    if request.url.path.startswith("/api/"):
        headers["Access-Control-Allow-Origin"] = "*"
    
    return JSONResponse(
        status_code=status_code,
        content=response_data,
        headers=headers
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handler for Pydantic validation errors
    """
    # Convert to our validation exception format
    validation_exc = SchemaValidationException(
        message="Request validation failed",
        validation_errors=exc.errors(),
        schema_name="request"
    )
    
    # Log the exception
    user_id = getattr(request.state, "user_id", None)
    log_exception(validation_exc, request, user_id)
    
    # Create response
    fhir_format = request.url.path.startswith("/fhir/")
    response_data = create_error_response(validation_exc, 422, False, fhir_format)
    
    return JSONResponse(
        status_code=422,
        content=response_data
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handler for FastAPI HTTP exceptions
    """
    # Log non-client errors
    if exc.status_code >= 500:
        user_id = getattr(request.state, "user_id", None)
        log_exception(exc, request, user_id)
    
    # Create standardized response
    fhir_format = request.url.path.startswith("/fhir/")
    
    if fhir_format:
        response_data = {
            "resourceType": "OperationOutcome",
            "issue": [
                {
                    "severity": "error" if exc.status_code >= 400 else "information",
                    "code": "processing",
                    "details": {
                        "text": exc.detail
                    }
                }
            ]
        }
    else:
        response_data = {
            "error": {
                "error_code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "status_code": exc.status_code,
                "timestamp": datetime.utcnow().isoformat()
            },
            "success": False
        }
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response_data
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for unexpected exceptions
    """
    # Always log unexpected exceptions
    user_id = getattr(request.state, "user_id", None)
    log_exception(exc, request, user_id)
    
    # Create safe error response (don't expose internal details)
    fhir_format = request.url.path.startswith("/fhir/")
    response_data = create_error_response(exc, 500, False, fhir_format)
    
    return JSONResponse(
        status_code=500,
        content=response_data
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Set up all exception handlers for the FastAPI app
    
    Args:
        app: FastAPI application instance
    """
    # Add exception logging middleware
    app.add_middleware(ExceptionLoggingMiddleware)
    
    # Register exception handlers (order matters - most specific first)
    app.add_exception_handler(DiagnoAssistException, diagnoassist_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Exception handlers configured successfully")


# Utility functions for manual exception handling

def handle_service_exception(func):
    """
    Decorator for service methods to handle exceptions consistently
    
    Usage:
        @handle_service_exception
        def my_service_method(self, ...):
            # method implementation
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DiagnoAssistException:
            # Re-raise our own exceptions
            raise
        except Exception as e:
            # Convert unknown exceptions to service exceptions
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            raise DiagnoAssistException(
                message=f"Service error in {func.__name__}",
                error_code="SERVICE_ERROR",
                details={"original_error": str(e)},
                severity="error"
            ) from e
    
    return wrapper


def raise_for_patient_safety(condition: bool, message: str, patient_id: str, safety_rule: str) -> None:
    """
    Utility function to raise patient safety exceptions
    
    Args:
        condition: If True, raise the exception
        message: Error message
        patient_id: Patient identifier
        safety_rule: Safety rule that was violated
    """
    if condition:
        raise PatientSafetyException(
            message=message,
            patient_id=patient_id,
            safety_rule=safety_rule,
            immediate_action_required=True
        )