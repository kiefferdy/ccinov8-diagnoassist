import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from typing import Callable

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests and responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response: {response.status_code} | "
            f"Duration: {process_time:.3f}s | "
            f"Path: {request.url.path}"
        )
        
        # Add custom headers
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Global error handling"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Unhandled error: {str(e)}", exc_info=True)
            
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": "An unexpected error occurred",
                    "type": "server_error"
                }
            )

class FHIRValidationMiddleware(BaseHTTPMiddleware):
    """FHIR-specific validation and formatting"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Only apply to FHIR endpoints
        if not request.url.path.startswith("/fhir"):
            return await call_next(request)
        
        # Add FHIR-specific headers
        response = await call_next(request)
        response.headers["X-FHIR-Version"] = "4.0.1"
        response.headers["Content-Type"] = "application/fhir+json"
        
        return response