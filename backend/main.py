"""
DiagnoAssist FastAPI Application Entry Point
FHIR R4 Compliant Medical Diagnosis Assistant API
Enhanced with Comprehensive Exception Handling (Step 7.5 Complete)
"""

import os
import logging
import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import uvicorn

# Import configuration
try:
    from config.settings import Settings
    settings = Settings()
    SETTINGS_AVAILABLE = True
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
        trusted_hosts = ["*"]
        
    settings = Settings()
    SETTINGS_AVAILABLE = False

# Import database connection
try:
    from config.database import get_database
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

# Import exception handling
try:
    from exceptions import (
        setup_exception_handlers,
        DiagnoAssistException,
        PatientSafetyException,
        EXCEPTION_STATUS_MAP
    )
    from exceptions.middleware import setup_middleware
    from exceptions.handlers import log_exception
    EXCEPTION_HANDLING_AVAILABLE = True
    
    # Import specific exceptions for testing
    from exceptions.medical import ClinicalDataException
    from exceptions.validation import ValidationException
    
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

# Set up enhanced logging
def setup_logging():
    """Configure comprehensive logging"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.log_level, "INFO"),
        format=log_format,
        handlers=[
            logging.StreamHandler(),
        ]
    )
    
    # Configure specific loggers
    logger = logging.getLogger("diagnoassist")
    logger.setLevel(getattr(logging, settings.log_level, "INFO"))
    
    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    return logger

logger = setup_logging()

# Exception handling webhook for patient safety alerts
async def patient_safety_webhook(alert_payload: Dict[str, Any]) -> None:
    """
    Enhanced webhook handler for patient safety alerts
    In production, this would integrate with:
    - Hospital paging systems
    - Electronic health records
    - Clinical decision support systems
    - Medical staff notification systems
    """
    try:
        logger.critical(
            f"🚨 PATIENT SAFETY ALERT: {alert_payload.get('alert_type', 'UNKNOWN')}",
            extra=alert_payload
        )
        
        # In production, add integrations here:
        # - Send SMS/email to on-call staff
        # - Create high-priority tickets
        # - Update patient safety monitoring systems
        # - Trigger automated safety protocols
        
        # For now, we'll just log the alert
        print("🚨" * 20)
        print(f"PATIENT SAFETY ALERT: {alert_payload}")
        print("🚨" * 20)
        
    except Exception as e:
        logger.error(f"Failed to process safety alert webhook: {e}")

# Application lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Enhanced application lifespan management with comprehensive exception handling
    """
    startup_errors = []
    
    # Startup
    logger.info("🚀 DiagnoAssist FHIR Server starting up...")
    print("🚀 DiagnoAssist FHIR Server starting up...")
    
    # Test exception handling system
    if EXCEPTION_HANDLING_AVAILABLE:
        try:
            # Validate exception system is working
            test_exc = DiagnoAssistException(
                message="Startup validation test - system working",
                error_code="STARTUP_TEST"
            )
            logger.info("✅ Exception handling system validated")
            
            # Test critical systems
            logger.info(f"✅ Exception status mapping loaded ({len(EXCEPTION_STATUS_MAP)} mappings)")
            
        except Exception as e:
            error_msg = f"❌ Exception handling system validation failed: {e}"
            logger.error(error_msg)
            startup_errors.append(error_msg)
    else:
        error_msg = "❌ Exception handling system not available"
        logger.warning(error_msg)
        startup_errors.append(error_msg)
    
    # Test database connection
    if DATABASE_AVAILABLE:
        try:
            # Test database connectivity
            db = next(get_database())
            logger.info("✅ Database connection validated")
            db.close()
        except Exception as e:
            error_msg = f"❌ Database connection failed: {e}"
            logger.error(error_msg)
            startup_errors.append(error_msg)
            if EXCEPTION_HANDLING_AVAILABLE:
                log_exception(e, additional_context={
                    "phase": "startup", 
                    "component": "database"
                })
    else:
        error_msg = "⚠️  Database not available"
        logger.warning(error_msg)
    
    # Validate configuration
    try:
        required_settings = ['app_name', 'app_version', 'cors_origins']
        for setting in required_settings:
            if not hasattr(settings, setting):
                raise ValueError(f"Missing required setting: {setting}")
        logger.info("✅ Configuration validated")
    except Exception as e:
        error_msg = f"❌ Configuration validation failed: {e}"
        logger.error(error_msg)
        startup_errors.append(error_msg)
    
    # Report startup status
    if startup_errors:
        logger.warning(f"⚠️  Startup completed with {len(startup_errors)} warnings/errors")
        for error in startup_errors:
            logger.warning(f"  - {error}")
    else:
        logger.info("✅ All systems validated successfully")
    
    print(f"🎯 Server ready at http://localhost:8000")
    print(f"📚 API Documentation: http://localhost:8000/docs")
    print(f"🔧 Exception handling: {'✅ Enabled' if EXCEPTION_HANDLING_AVAILABLE else '❌ Disabled'}")
    
    yield
    
    # Shutdown
    logger.info("👋 DiagnoAssist FHIR Server shutting down...")
    print("👋 DiagnoAssist FHIR Server shutting down...")

# Create FastAPI application with enhanced configuration
app = FastAPI(
    title=settings.app_name,
    description=(
        "AI-powered medical diagnosis assistant with FHIR R4 compliance "
        "and comprehensive exception handling"
    ),
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    # Enhanced OpenAPI configuration
    openapi_tags=[
        {"name": "Health", "description": "Health check and monitoring endpoints"},
        {"name": "FHIR", "description": "FHIR R4 compliant medical data endpoints"},
        {"name": "Diagnosis", "description": "AI-powered diagnosis endpoints"},
        {"name": "Exception Testing", "description": "Exception handling test endpoints"},
    ]
)

# Security middleware (add first)
if hasattr(settings, 'trusted_hosts') and settings.trusted_hosts != ["*"]:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts)

# Compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS middleware (before exception middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Processing-Time", "X-Error-Type"]
)

# Exception handling system integration
if EXCEPTION_HANDLING_AVAILABLE:
    try:
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
        
        # Set up middleware first (order matters!)
        setup_middleware(app, exception_config)
        
        # Set up exception handlers
        setup_exception_handlers(app)
        
        logger.info("✅ Exception handling system fully integrated")
        
    except Exception as e:
        logger.error(f"❌ Failed to configure exception handling: {e}")
        EXCEPTION_HANDLING_AVAILABLE = False

# Fallback exception handling if main system unavailable
if not EXCEPTION_HANDLING_AVAILABLE:
    @app.exception_handler(HTTPException)
    async def fallback_http_exception_handler(request: Request, exc: HTTPException):
        """Fallback HTTP exception handler"""
        logger.error(f"HTTP exception: {exc.status_code} - {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "message": exc.detail,
                    "type": "http_error",
                    "status_code": exc.status_code
                },
                "success": False
            }
        )
    
    @app.exception_handler(Exception)
    async def fallback_general_exception_handler(request: Request, exc: Exception):
        """Fallback general exception handler"""
        logger.error(f"Unhandled exception: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "message": "An internal server error occurred",
                    "type": "internal_error",
                    "status_code": 500
                },
                "success": False
            }
        )

# Include API router if available
if API_ROUTER_AVAILABLE:
    app.include_router(api_router)
    logger.info("✅ API router included")
else:
    logger.warning("⚠️  API router not available - adding placeholder endpoints")

# Health check endpoints
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Comprehensive health check endpoint
    """
    health_status = {
        "status": "healthy",
        "timestamp": "2025-07-22T12:00:00Z",
        "version": settings.app_version,
        "components": {
            "exception_handling": {
                "status": "up" if EXCEPTION_HANDLING_AVAILABLE else "down",
                "details": {
                    "available": EXCEPTION_HANDLING_AVAILABLE,
                    "exception_mappings": len(EXCEPTION_STATUS_MAP) if EXCEPTION_HANDLING_AVAILABLE else 0
                }
            },
            "database": {
                "status": "up" if DATABASE_AVAILABLE else "down",
                "details": {"available": DATABASE_AVAILABLE}
            },
            "api_router": {
                "status": "up" if API_ROUTER_AVAILABLE else "down", 
                "details": {"available": API_ROUTER_AVAILABLE}
            },
            "configuration": {
                "status": "up" if SETTINGS_AVAILABLE else "partial",
                "details": {"settings_module": SETTINGS_AVAILABLE}
            }
        }
    }
    
    # Determine overall health
    component_statuses = [comp["status"] for comp in health_status["components"].values()]
    if "down" in component_statuses:
        health_status["status"] = "degraded"
    
    status_code = 200 if health_status["status"] in ["healthy", "degraded"] else 503
    
    return JSONResponse(
        status_code=status_code,
        content=health_status
    )

@app.get("/health/exception-system", tags=["Health"])
async def exception_system_health():
    """
    Dedicated exception system health check
    """
    if not EXCEPTION_HANDLING_AVAILABLE:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unavailable",
                "message": "Exception handling system not available"
            }
        )
    
    try:
        # Test exception system functionality
        test_exc = ValidationException(
            message="Health check test exception",
            field_name="test_field"
        )
        
        return {
            "status": "operational",
            "exception_mappings": len(EXCEPTION_STATUS_MAP),
            "features": {
                "patient_safety_alerts": True,
                "fhir_error_formatting": True,
                "performance_monitoring": getattr(settings, "enable_performance_monitoring", False),
                "security_logging": getattr(settings, "enable_security_logging", False),
                "error_rate_limiting": getattr(settings, "enable_error_rate_limiting", False)
            }
        }
    except Exception as e:
        logger.error(f"Exception system health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Exception system health check failed",
                "error": str(e)
            }
        )

# Root endpoint with enhanced information
@app.get("/", tags=["Health"])
async def root():
    """
    Enhanced root endpoint with comprehensive API information
    """
    return {
        "message": "DiagnoAssist FHIR Server",
        "version": settings.app_version,
        "fhir_version": "R4",
        "status": "operational",
        "features": {
            "enhanced_exception_handling": EXCEPTION_HANDLING_AVAILABLE,
            "patient_safety_alerts": EXCEPTION_HANDLING_AVAILABLE,
            "fhir_compliant_errors": EXCEPTION_HANDLING_AVAILABLE,
            "performance_monitoring": EXCEPTION_HANDLING_AVAILABLE and getattr(settings, "enable_performance_monitoring", False),
            "security_logging": EXCEPTION_HANDLING_AVAILABLE and getattr(settings, "enable_security_logging", False),
            "error_rate_limiting": EXCEPTION_HANDLING_AVAILABLE and getattr(settings, "enable_error_rate_limiting", False),
            "database_integration": DATABASE_AVAILABLE,
            "api_endpoints": API_ROUTER_AVAILABLE
        },
        "endpoints": {
            "documentation": "/docs",
            "redoc": "/redoc",
            "health_check": "/health",
            "exception_health": "/health/exception-system",
            "fhir_metadata": "/fhir/R4/metadata" if API_ROUTER_AVAILABLE else "Not available",
            "fhir_patients": "/fhir/R4/Patient" if API_ROUTER_AVAILABLE else "Not available"
        },
        "exception_statistics": {
            "total_exception_types": len(EXCEPTION_STATUS_MAP) if EXCEPTION_HANDLING_AVAILABLE else 0,
            "safety_critical_types": 4 if EXCEPTION_HANDLING_AVAILABLE else 0,  # PatientSafetyException, ClinicalDataException, etc.
            "middleware_layers": 3 if EXCEPTION_HANDLING_AVAILABLE else 0  # Context, Rate Limiting, Main Exception
        }
    }

# Exception testing endpoints (only available in debug mode)
if settings.debug and EXCEPTION_HANDLING_AVAILABLE:
    @app.get("/test/exception/{exception_type}", tags=["Exception Testing"])
    async def test_exception(exception_type: str):
        """
        Test endpoint for various exception types (debug mode only)
        """
        if exception_type == "validation":
            raise ValidationException(
                message="Test validation error",
                field_name="test_field",
                provided_value="invalid_value"
            )
        elif exception_type == "patient_safety":
            raise PatientSafetyException(
                message="Test patient safety alert",
                patient_id="TEST_PATIENT_123",
                safety_rule="test_safety_rule",
                risk_level="HIGH"
            )
        elif exception_type == "clinical_data":
            raise ClinicalDataException(
                message="Test clinical data error",
                data_type="laboratory_results",
                patient_id="TEST_PATIENT_123",
                safety_critical=True
            )
        elif exception_type == "general":
            raise DiagnoAssistException(
                message="Test general DiagnoAssist exception",
                error_code="TEST_ERROR"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown exception type: {exception_type}. Available: validation, patient_safety, clinical_data, general"
            )

# Run the application
if __name__ == "__main__":
    try:
        uvicorn.run(
            "main:app",
            host=getattr(settings, "host", "0.0.0.0"),
            port=getattr(settings, "port", 8000),
            reload=settings.debug,
            log_level=settings.log_level.lower()
        )
    except Exception as e:
        logger.critical(f"Failed to start server: {e}")
        if EXCEPTION_HANDLING_AVAILABLE:
            log_exception(e, additional_context={"phase": "server_startup"})