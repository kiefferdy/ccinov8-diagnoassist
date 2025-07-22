"""
Enhanced Exception Middleware for DiagnoAssist
Advanced error handling, monitoring, and response customization
"""

import time
import json
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from uuid import uuid4
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from .base import DiagnoAssistException
from .medical import PatientSafetyException, ClinicalDataException
from .handlers import log_exception, create_error_response, get_status_code_for_exception

logger = logging.getLogger(__name__)


class DiagnoAssistExceptionMiddleware(BaseHTTPMiddleware):
    """
    Enhanced exception middleware with medical-specific features
    """
    
    def __init__(
        self,
        app,
        include_request_details: bool = True,
        enable_performance_monitoring: bool = True,
        enable_security_logging: bool = True,
        safety_alert_webhook: Optional[Callable] = None,
        custom_error_handlers: Optional[Dict[str, Callable]] = None
    ):
        super().__init__(app)
        self.include_request_details = include_request_details
        self.enable_performance_monitoring = enable_performance_monitoring
        self.enable_security_logging = enable_security_logging
        self.safety_alert_webhook = safety_alert_webhook
        self.custom_error_handlers = custom_error_handlers or {}
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request with enhanced exception handling"""
        # Initialize request tracking
        request_id = str(uuid4())
        start_time = time.time()
        
        # Add request context
        request.state.request_id = request_id
        request.state.start_time = start_time
        
        # Extract user information if available
        user_id = await self._extract_user_id(request)
        if user_id:
            request.state.user_id = user_id
        
        try:
            # Process request
            response = await call_next(request)
            
            # Log performance metrics if enabled
            if self.enable_performance_monitoring:
                await self._log_performance_metrics(request, response, start_time)
            
            return response
            
        except Exception as exc:
            # Handle the exception
            return await self._handle_exception(request, exc, start_time)
    
    async def _extract_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from request (JWT token, session, etc.)"""
        try:
            # Try to get from Authorization header
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                # In a real implementation, you'd decode the JWT token
                # For now, we'll just return a placeholder
                return "extracted_user_id"
            
            # Try to get from session cookie
            session_cookie = request.cookies.get("session_id")
            if session_cookie:
                # Look up user from session
                return "session_user_id"
            
            return None
            
        except Exception:
            return None
    
    async def _handle_exception(
        self, 
        request: Request, 
        exc: Exception, 
        start_time: float
    ) -> JSONResponse:
        """Handle exception with enhanced logging and response"""
        
        # Extract request context
        user_id = getattr(request.state, "user_id", None)
        request_id = getattr(request.state, "request_id", "unknown")
        
        # Create additional context
        additional_context = {
            "request_id": request_id,
            "processing_time": time.time() - start_time,
            "endpoint": request.url.path,
            "method": request.method
        }
        
        if self.include_request_details:
            additional_context.update({
                "query_params": dict(request.query_params),
                "path_params": getattr(request, "path_params", {}),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
                "referer": request.headers.get("referer")
            })
        
        # Handle patient safety exceptions specially
        if isinstance(exc, PatientSafetyException):
            await self._handle_patient_safety_alert(exc, request, additional_context)
        
        # Handle clinical data exceptions
        elif isinstance(exc, ClinicalDataException) and exc.safety_critical:
            await self._handle_critical_clinical_error(exc, request, additional_context)
        
        # Security logging for auth failures
        if self.enable_security_logging:
            await self._log_security_event(exc, request, additional_context)
        
        # Check for custom handlers
        exc_type_name = type(exc).__name__
        if exc_type_name in self.custom_error_handlers:
            try:
                custom_response = await self.custom_error_handlers[exc_type_name](
                    request, exc, additional_context
                )
                if custom_response:
                    return custom_response
            except Exception as handler_exc:
                logger.error(f"Custom error handler failed: {handler_exc}")
        
        # Log the exception
        log_exception(exc, request, user_id, additional_context)
        
        # Determine response format
        fhir_format = self._should_use_fhir_format(request)
        include_debug = self._should_include_debug(request)
        
        # Get status code
        status_code = get_status_code_for_exception(exc)
        
        # Create response
        response_data = create_error_response(exc, status_code, include_debug, fhir_format)
        
        # Add request tracking headers
        headers = {
            "X-Request-ID": request_id,
            "X-Error-Type": type(exc).__name__
        }
        
        # Add CORS headers if needed
        if self._needs_cors_headers(request):
            headers.update({
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*"
            })
        
        return JSONResponse(
            status_code=status_code,
            content=response_data,
            headers=headers
        )
    
    async def _handle_patient_safety_alert(
        self, 
        exc: PatientSafetyException, 
        request: Request, 
        context: Dict[str, Any]
    ) -> None:
        """Handle patient safety exceptions with special alerting"""
        
        # Create safety alert payload
        alert_payload = {
            "alert_type": "PATIENT_SAFETY",
            "severity": "CRITICAL",
            "patient_id": exc.patient_id,
            "safety_rule": exc.safety_rule,
            "risk_level": exc.risk_level,
            "immediate_action_required": exc.immediate_action_required,
            "error_id": exc.error_id,
            "timestamp": exc.timestamp.isoformat(),
            "context": context,
            "clinical_context": exc.clinical_context
        }
        
        # Log critical alert
        logger.critical(
            f"🚨 PATIENT SAFETY ALERT: {exc.safety_rule} (Patient: {exc.patient_id})",
            extra=alert_payload
        )
        
        # Send webhook if configured
        if self.safety_alert_webhook:
            try:
                await self.safety_alert_webhook(alert_payload)
            except Exception as webhook_exc:
                logger.error(f"Failed to send safety alert webhook: {webhook_exc}")
        
        # Additional safety measures could include:
        # - Send email alerts
        # - Update patient record with safety flag
        # - Notify on-call medical staff
        # - Trigger automated safety protocols
    
    async def _handle_critical_clinical_error(
        self, 
        exc: ClinicalDataException, 
        request: Request, 
        context: Dict[str, Any]
    ) -> None:
        """Handle critical clinical data errors"""
        
        alert_payload = {
            "alert_type": "CLINICAL_DATA_ERROR",
            "severity": "HIGH",
            "data_type": exc.data_type,
            "patient_id": exc.patient_id,
            "episode_id": exc.episode_id,
            "error_id": exc.error_id,
            "timestamp": exc.timestamp.isoformat(),
            "context": context
        }
        
        logger.critical(
            f"🔴 CRITICAL CLINICAL DATA ERROR: {exc.data_type}",
            extra=alert_payload
        )
    
    async def _log_security_event(
        self, 
        exc: Exception, 
        request: Request, 
        context: Dict[str, Any]
    ) -> None:
        """Log security-related events"""
        
        from .authentication import (
            AuthenticationException, 
            AuthorizationException, 
            TokenException
        )
        
        if isinstance(exc, (AuthenticationException, AuthorizationException, TokenException)):
            security_event = {
                "event_type": "SECURITY_VIOLATION",
                "violation_type": type(exc).__name__,
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
                "endpoint": request.url.path,
                "method": request.method,
                "timestamp": datetime.utcnow().isoformat(),
                "context": context
            }
            
            logger.warning(
                f"🛡️ Security Event: {type(exc).__name__}",
                extra=security_event
            )
    
    async def _log_performance_metrics(
        self, 
        request: Request, 
        response: Response, 
        start_time: float
    ) -> None:
        """Log performance metrics"""
        
        processing_time = time.time() - start_time
        
        # Log slow requests (over 2 seconds)
        if processing_time > 2.0:
            logger.warning(
                f"⏱️ Slow Request: {request.method} {request.url.path} took {processing_time:.2f}s",
                extra={
                    "request_id": getattr(request.state, "request_id", "unknown"),
                    "processing_time": processing_time,
                    "status_code": response.status_code,
                    "endpoint": request.url.path,
                    "method": request.method
                }
            )
    
    def _should_use_fhir_format(self, request: Request) -> bool:
        """Determine if response should use FHIR format"""
        return (
            request.url.path.startswith("/fhir/") or
            request.headers.get("accept", "").startswith("application/fhir+json") or
            request.headers.get("content-type", "").startswith("application/fhir+json")
        )
    
    def _should_include_debug(self, request: Request) -> bool:
        """Determine if debug information should be included"""
        return (
            request.query_params.get("debug") == "true" or
            request.headers.get("x-debug") == "true" or
            request.headers.get("x-environment") == "development"
        )
    
    def _needs_cors_headers(self, request: Request) -> bool:
        """Determine if CORS headers are needed"""
        return (
            request.url.path.startswith("/api/") or
            request.headers.get("origin") is not None
        )


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add context information to all requests
    """
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Add context to request"""
        
        # Add request metadata
        request.state.request_start = datetime.utcnow()
        request.state.request_id = str(uuid4())
        
        # Add client information
        if request.client:
            request.state.client_ip = request.client.host
            request.state.client_port = request.client.port
        
        # Add user agent parsing
        user_agent = request.headers.get("user-agent", "")
        request.state.user_agent = user_agent
        request.state.is_mobile = "mobile" in user_agent.lower()
        request.state.is_api_client = "api" in user_agent.lower() or "curl" in user_agent.lower()
        
        # Process request
        response = await call_next(request)
        
        # Add response headers
        response.headers["X-Request-ID"] = request.state.request_id
        response.headers["X-Processing-Time"] = str(
            (datetime.utcnow() - request.state.request_start).total_seconds()
        )
        
        return response


class ErrorRateLimitingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to implement rate limiting based on error patterns
    """
    
    def __init__(self, app, max_errors_per_minute: int = 10):
        super().__init__(app)
        self.max_errors_per_minute = max_errors_per_minute
        self.error_counts: Dict[str, List[datetime]] = {}
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Track error rates and implement limiting"""
        
        client_ip = request.client.host if request.client else "unknown"
        
        try:
            response = await call_next(request)
            return response
            
        except Exception as exc:
            # Track error for this client
            now = datetime.utcnow()
            
            if client_ip not in self.error_counts:
                self.error_counts[client_ip] = []
            
            # Remove old entries (older than 1 minute)
            self.error_counts[client_ip] = [
                timestamp for timestamp in self.error_counts[client_ip]
                if (now - timestamp).total_seconds() < 60
            ]
            
            # Add current error
            self.error_counts[client_ip].append(now)
            
            # Check if rate limit exceeded
            if len(self.error_counts[client_ip]) > self.max_errors_per_minute:
                from .external import RateLimitException
                
                logger.warning(
                    f"Error rate limit exceeded for {client_ip}: "
                    f"{len(self.error_counts[client_ip])} errors in last minute"
                )
                
                raise RateLimitException(
                    message=f"Error rate limit exceeded: {len(self.error_counts[client_ip])} errors per minute",
                    limit_type="errors_per_minute",
                    service_name="DiagnoAssist API",
                    current_usage=len(self.error_counts[client_ip]),
                    limit=self.max_errors_per_minute,
                    reset_seconds=60
                )
            
            # Re-raise original exception
            raise exc


def setup_middleware(app, config: Optional[Dict[str, Any]] = None) -> None:
    """
    Set up all exception-related middleware
    
    Args:
        app: FastAPI application
        config: Configuration dictionary
    """
    config = config or {}
    
    # Add request context middleware first
    app.add_middleware(RequestContextMiddleware)
    
    # Add error rate limiting if enabled
    if config.get("enable_error_rate_limiting", True):
        app.add_middleware(
            ErrorRateLimitingMiddleware,
            max_errors_per_minute=config.get("max_errors_per_minute", 10)
        )
    
    # Add main exception middleware
    app.add_middleware(
        DiagnoAssistExceptionMiddleware,
        include_request_details=config.get("include_request_details", True),
        enable_performance_monitoring=config.get("enable_performance_monitoring", True),
        enable_security_logging=config.get("enable_security_logging", True),
        safety_alert_webhook=config.get("safety_alert_webhook"),
        custom_error_handlers=config.get("custom_error_handlers", {})
    )
    
    logger.info("Exception middleware configured successfully")