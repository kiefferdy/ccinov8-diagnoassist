"""
DiagnoAssist FastAPI Application Entry Point
FHIR R4 Compliant Medical Diagnosis Assistant API
Enhanced with Comprehensive Exception Handling
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Import configuration
try:
    from config.settings import Settings
    settings = Settings()
except ImportError:
    # Fallback settings if config module doesn't exist
    class Settings:
        app_name = "DiagnoAssist API"
        app_version = "1.0.0"
        debug = True
        cors_origins = [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000", 
            "http://127.0.0.1:5173"
        ]
        fhir_base_url = "http://localhost:8000/fhir"
        log_level = "INFO"
        enable_error_rate_limiting = True
        max_errors_per_minute = 10
        include_request_details = True
        enable_performance_monitoring = True
        enable_security_logging = True
    
    settings = Settings()

# Import exception handling
try:
    from exceptions import setup_exception_handlers
    from exceptions.middleware import setup_middleware
    from exceptions.handlers import log_exception
    from exceptions.medical import PatientSafetyException
    EXCEPTION_HANDLING_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Exception handling not available: {e}")
    EXCEPTION_HANDLING_AVAILABLE = False

# Import API routers
try:
    from api import api_router
    API_ROUTER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  API router not available: {e}")
    API_ROUTER_AVAILABLE = False

# Set up logging
logging.basicConfig(
    level=getattr(logging, settings.log_level, "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def patient_safety_webhook(alert_payload: Dict[str, Any]) -> None:
    """
    Webhook handler for patient safety alerts
    In production, this would send alerts to medical staff, paging systems, etc.
    """
    logger.critical(f"🚨 PATIENT SAFETY WEBHOOK: {alert_payload}")
    
    # In production, implement:
    # - Email alerts to medical staff
    # - Integration with paging systems
    # - Slack/Teams notifications
    # - Update patient safety dashboard
    # - Log to external monitoring system
    
    print(f"🚨 PATIENT SAFETY ALERT: Patient {alert_payload.get('patient_id')} - {alert_payload.get('safety_rule')}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events with enhanced error handling"""
    # Startup
    logger.info("🏥 DiagnoAssist FHIR Server Starting...")
    print("🏥 DiagnoAssist FHIR Server Starting...")
    print(f"📋 API Documentation: http://localhost:8000/docs")
    print(f"🔍 FHIR Metadata: http://localhost:8000/fhir/R4/metadata")
    print(f"👥 FHIR Patients: http://localhost:8000/fhir/R4/Patient")
    print(f"📊 Health Check: http://localhost:8000/health")
    
    if EXCEPTION_HANDLING_AVAILABLE:
        print("✅ Enhanced exception handling enabled")
        print("   • Medical domain-specific error handling")
        print("   • Patient safety alerting system")
        print("   • FHIR R4 compliant error responses")
        print("   • Comprehensive error logging and monitoring")
    else:
        print("⚠️  Basic exception handling only")
    
    # Initialize database if needed
    try:
        from config.database import init_db
        await init_db()
        logger.info("✅ Database initialized successfully")
        print("✅ Database initialized successfully")
    except ImportError:
        logger.warning("⚠️  Database initialization skipped - config.database not found")
        print("⚠️  Database initialization skipped - config.database not found")
    except Exception as e:
        logger.error(f"⚠️  Database initialization error: {e}")
        print(f"⚠️  Database initialization error: {e}")
        
        # Log the exception using our exception handling if available
        if EXCEPTION_HANDLING_AVAILABLE:
            log_exception(e, additional_context={"phase": "startup", "component": "database"})
    
    # Test exception handling system
    if EXCEPTION_HANDLING_AVAILABLE:
        try:
            # Test that our exception system is working
            from exceptions.base import DiagnoAssistException
            test_exc = DiagnoAssistException("Startup test - system working")
            logger.info("✅ Exception handling system validated")
        except Exception as e:
            logger.error(f"❌ Exception handling system validation failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("👋 DiagnoAssist FHIR Server shutting down...")
    print("👋 DiagnoAssist FHIR Server shutting down...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="AI-powered medical diagnosis assistant with FHIR R4 compliance and comprehensive exception handling",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Set up exception handling if available
if EXCEPTION_HANDLING_AVAILABLE:
    # Configure exception middleware
    exception_config = {
        "include_request_details": getattr(settings, "include_request_details", True),
        "enable_performance_monitoring": getattr(settings, "enable_performance_monitoring", True),
        "enable_security_logging": getattr(settings, "enable_security_logging", True),
        "enable_error_rate_limiting": getattr(settings, "enable_error_rate_limiting", True),
        "max_errors_per_minute": getattr(settings, "max_errors_per_minute", 10),
        "safety_alert_webhook": patient_safety_webhook,
        "custom_error_handlers": {
            # Add custom handlers for specific exception types if needed
            # "CustomException": custom_handler_function
        }
    }
    
    # Set up middleware first (order matters)
    setup_middleware(app, exception_config)
    
    # Set up exception handlers
    setup_exception_handlers(app)
    
    logger.info("✅ Exception handling system configured")
else:
    # Fallback basic exception handlers
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Basic fallback exception handler"""
        logger.error(f"Unhandled exception: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "message": "An internal server error occurred",
                    "type": "internal_error"
                }
            }
        )

# Include API router if available
if API_ROUTER_AVAILABLE:
    app.include_router(api_router)
    logger.info("✅ API router included")
else:
    logger.warning("⚠️  API router not available - limited functionality")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "DiagnoAssist FHIR Server",
        "version": settings.app_version,
        "fhir_version": "R4",
        "exception_handling": EXCEPTION_HANDLING_AVAILABLE,
        "api_router": API_ROUTER_AVAILABLE,
        "endpoints": {
            "docs": "/docs",
            "fhir_metadata": "/fhir/R4/metadata",
            "fhir_patients": "/fhir/R4/Patient",
            "health": "/health"
        },
        "features": {
            "enhanced_exception_handling": EXCEPTION_HANDLING_AVAILABLE,
            "patient_safety_alerts": EXCEPTION_HANDLING_AVAILABLE,
            "fhir_compliant_errors": EXCEPTION_HANDLING_AVAILABLE,
            "performance_monitoring": EXCEPTION_HANDLING_AVAILABLE and getattr(settings, "enable_performance_monitoring", True),
            "security_logging": EXCEPTION_HANDLING_AVAILABLE and getattr(settings, "enable_security_logging", True),
            "error_rate_limiting": EXCEPTION_HANDLING_AVAILABLE and getattr(settings, "enable_error_rate_limiting", True)
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Enhanced health check endpoint with exception handling status"""
    health_status = {
        "status": "healthy",
        "service": "DiagnoAssist FHIR Server",
        "version": settings.app_version,
        "fhir_version": "R4",
        "timestamp": "2025-01-20T00:00:00Z",
        "components": {
            "application": "healthy",
            "exception_handling": "healthy" if EXCEPTION_HANDLING_AVAILABLE else "limited",
            "api_router": "healthy" if API_ROUTER_AVAILABLE else "unavailable"
        }
    }
    
    # Test exception handling system
    if EXCEPTION_HANDLING_AVAILABLE:
        try:
            from exceptions.base import DiagnoAssistException
            # Quick validation that our exception system is working
            health_status["components"]["exception_validation"] = "healthy"
        except Exception:
            health_status["components"]["exception_validation"] = "degraded"
            health_status["status"] = "degraded"
    
    return health_status

# Test endpoints for exception handling (only in debug mode)
if getattr(settings, "debug", False) and EXCEPTION_HANDLING_AVAILABLE:
    
    @app.get("/test/exceptions/validation")
    async def test_validation_exception():
        """Test endpoint for validation exceptions"""
        from exceptions.validation import ValidationException
        raise ValidationException(
            message="Test validation error",
            field="test_field",
            value="invalid_value",
            validation_rule="test_rule"
        )
    
    @app.get("/test/exceptions/patient-safety")
    async def test_patient_safety_exception():
        """Test endpoint for patient safety exceptions"""
        from exceptions.medical import PatientSafetyException
        raise PatientSafetyException(
            message="Test patient safety alert",
            patient_id="TEST_PATIENT_123",
            safety_rule="Test Safety Rule",
            risk_level="HIGH",
            immediate_action_required=True
        )
    
    @app.get("/test/exceptions/not-found")
    async def test_not_found_exception():
        """Test endpoint for resource not found exceptions"""
        from exceptions.resource import ResourceNotFoundException
        raise ResourceNotFoundException(
            resource_type="Patient",
            identifier="TEST_PATIENT_999",
            identifier_type="id"
        )
    
    @app.get("/test/exceptions/fhir")
    async def test_fhir_exception():
        """Test endpoint for FHIR validation exceptions"""
        from exceptions.medical import FHIRValidationException
        raise FHIRValidationException(
            message="Test FHIR validation error",
            resource_type="Patient",
            resource_id="TEST_PATIENT_123",
            validation_errors=["Missing required field: name", "Invalid birthDate format"]
        )
    
    logger.info("🧪 Test exception endpoints enabled (debug mode)")

# Run server when called directly
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    # Log startup configuration
    logger.info(f"Starting DiagnoAssist server on {host}:{port}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Exception handling: {EXCEPTION_HANDLING_AVAILABLE}")
    logger.info(f"API router: {API_ROUTER_AVAILABLE}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=settings.log_level.lower(),
        access_log=True
    )