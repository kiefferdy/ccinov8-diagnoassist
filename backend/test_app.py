"""
Minimal DiagnoAssist Test App - Exception System Integration Test
This is a standalone app to test just the exception handling system
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Simple settings class for testing
class TestSettings:
    app_name = "DiagnoAssist Test API"
    app_version = "1.0.0-test"
    debug = True
    cors_origins = ["*"]  # Allow all for testing
    log_level = "INFO"
    enable_error_rate_limiting = True
    max_errors_per_minute = 10
    include_request_details = True
    enable_performance_monitoring = True
    enable_security_logging = True

settings = TestSettings()

# Test if exception handling is available
EXCEPTION_HANDLING_AVAILABLE = False
try:
    from exceptions import (
        setup_exception_handlers,
        DiagnoAssistException,
        PatientSafetyException,
        EXCEPTION_STATUS_MAP
    )
    from exceptions.middleware import setup_middleware
    from exceptions.handlers import log_exception
    from exceptions.medical import ClinicalDataException
    from exceptions.validation import ValidationException
    EXCEPTION_HANDLING_AVAILABLE = True
    print("✅ Exception handling system imported successfully")
except ImportError as e:
    print(f"❌ Exception handling not available: {e}")
    EXCEPTION_HANDLING_AVAILABLE = False

# Set up logging
logging.basicConfig(
    level=getattr(logging, settings.log_level, "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Patient safety webhook for testing
async def patient_safety_webhook(alert_payload: Dict[str, Any]) -> None:
    """Test webhook for patient safety alerts"""
    logger.critical(f"🚨 TEST PATIENT SAFETY ALERT: {alert_payload}")
    print("🚨" * 10)
    print(f"PATIENT SAFETY ALERT: {alert_payload}")
    print("🚨" * 10)

# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Test application lifespan"""
    logger.info("🚀 Test server starting...")
    print("🚀 Test server starting...")
    
    if EXCEPTION_HANDLING_AVAILABLE:
        try:
            test_exc = DiagnoAssistException(
                message="Test startup validation",
                error_code="TEST_STARTUP"
            )
            logger.info("✅ Exception system validated")
            print("✅ Exception system validated")
        except Exception as e:
            logger.error(f"❌ Exception validation failed: {e}")
            print(f"❌ Exception validation failed: {e}")
    
    print("🎯 Test server ready at http://localhost:8000")
    yield
    
    logger.info("👋 Test server shutting down...")
    print("👋 Test server shutting down...")

# Create minimal FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Minimal test app for exception system validation",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Processing-Time", "X-Error-Type"]
)

# Set up exception handling if available
if EXCEPTION_HANDLING_AVAILABLE:
    try:
        exception_config = {
            "include_request_details": settings.include_request_details,
            "enable_performance_monitoring": settings.enable_performance_monitoring,
            "enable_security_logging": settings.enable_security_logging,
            "enable_error_rate_limiting": settings.enable_error_rate_limiting,
            "max_errors_per_minute": settings.max_errors_per_minute,
            "safety_alert_webhook": patient_safety_webhook,
            "custom_error_handlers": {}
        }
        
        # Set up middleware (order matters!)
        setup_middleware(app, exception_config)
        
        # Set up exception handlers
        setup_exception_handlers(app)
        
        logger.info("✅ Exception handling configured")
        print("✅ Exception handling configured")
        
    except Exception as e:
        logger.error(f"❌ Exception setup failed: {e}")
        print(f"❌ Exception setup failed: {e}")
        EXCEPTION_HANDLING_AVAILABLE = False

# Fallback handlers if exception system not available
if not EXCEPTION_HANDLING_AVAILABLE:
    @app.exception_handler(HTTPException)
    async def fallback_http_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"message": exc.detail, "type": "http_error"}}
        )
    
    @app.exception_handler(Exception)
    async def fallback_general_handler(request: Request, exc: Exception):
        logger.error(f"Fallback handler: {exc}")
        return JSONResponse(
            status_code=500,
            content={"error": {"message": "Internal server error", "type": "general_error"}}
        )

# Test endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "DiagnoAssist Exception System Test",
        "version": settings.app_version,
        "exception_handling": EXCEPTION_HANDLING_AVAILABLE,
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "test_exceptions": "/test/exception/{type}"
        }
    }

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "exception_handling": EXCEPTION_HANDLING_AVAILABLE,
        "timestamp": "2025-07-22T12:00:00Z"
    }

@app.get("/health/exception-system")
async def exception_health():
    """Exception system health"""
    if not EXCEPTION_HANDLING_AVAILABLE:
        return JSONResponse(
            status_code=503,
            content={"status": "unavailable", "message": "Exception system not loaded"}
        )
    
    return {
        "status": "operational",
        "exception_mappings": len(EXCEPTION_STATUS_MAP),
        "features": {
            "patient_safety_alerts": True,
            "performance_monitoring": settings.enable_performance_monitoring,
            "security_logging": settings.enable_security_logging,
            "error_rate_limiting": settings.enable_error_rate_limiting
        }
    }

# Exception test endpoints (only if exception system available)
if EXCEPTION_HANDLING_AVAILABLE:
    @app.get("/test/exception/validation")
    async def test_validation_exception():
        """Test validation exception"""
        raise ValidationException(
            message="Test validation error",
            field_name="test_field",
            provided_value="invalid_value"
        )
    
    @app.get("/test/exception/patient_safety")
    async def test_patient_safety_exception():
        """Test patient safety exception"""
        raise PatientSafetyException(
            message="Test patient safety alert",
            patient_id="TEST_PATIENT_123",
            safety_rule="test_safety_rule",
            risk_level="HIGH"
        )
    
    @app.get("/test/exception/clinical_data")
    async def test_clinical_data_exception():
        """Test clinical data exception"""
        raise ClinicalDataException(
            message="Test clinical data error",
            data_type="laboratory_results",
            patient_id="TEST_PATIENT_123",
            safety_critical=True
        )
    
    @app.get("/test/exception/general")
    async def test_general_exception():
        """Test general exception"""
        raise DiagnoAssistException(
            message="Test general DiagnoAssist exception",
            error_code="TEST_ERROR"
        )
    
    @app.get("/test/exception/standard")
    async def test_standard_exception():
        """Test standard Python exception"""
        raise ValueError("Test standard Python exception")

else:
    # Placeholder endpoints if exception system not available
    @app.get("/test/exception/{exception_type}")
    async def test_exception_fallback(exception_type: str):
        """Fallback test endpoint"""
        return JSONResponse(
            status_code=503,
            content={
                "error": {
                    "message": "Exception system not available - cannot test exceptions",
                    "type": "system_unavailable"
                }
            }
        )

# Simple error endpoint for basic testing
@app.get("/test/basic-error")
async def test_basic_error():
    """Basic error test that doesn't require exception system"""
    raise HTTPException(status_code=400, detail="Basic test error")

# Run the app
if __name__ == "__main__":
    print("🧪 Starting DiagnoAssist Exception System Test Server...")
    print("📝 This is a minimal test app to validate exception handling integration")
    print("🔗 Access at: http://localhost:8000")
    print("📚 Docs at: http://localhost:8000/docs")
    
    try:
        uvicorn.run(
            "test_app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"💥 Failed to start server: {e}")