"""
DiagnoAssist FastAPI Application Entry Point
FHIR R4 Compliant Medical Diagnosis Assistant API
UPDATED: Added proper exception handling for CRUD tests
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import uvicorn

# FIXED: Load .env file first
from dotenv import load_dotenv
load_dotenv()

# Print loaded env vars for debugging
print(f"🔍 DATABASE_URL loaded: {'✅ Yes' if os.getenv('DATABASE_URL') else '❌ No'}")
print(f"🔍 SUPABASE_URL loaded: {'✅ Yes' if os.getenv('SUPABASE_URL') else '❌ No'}")

# Simple settings for reliable startup
class SimpleSettings:
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

settings = SimpleSettings()

# Test imports with error handling
EXCEPTION_HANDLING_AVAILABLE = False
DATABASE_AVAILABLE = False
API_ROUTER_AVAILABLE = False
FHIR_ROUTER_AVAILABLE = False

# Try to import exception handling
try:
    from exceptions.validation import ValidationException
    EXCEPTION_HANDLING_AVAILABLE = True
    print("✅ Exception handling loaded")
except ImportError as e:
    print(f"⚠️ Exception handling not available: {e}")

# Try to import database
try:
    from config.database import get_database, test_database_connection
    DATABASE_AVAILABLE = True
    print("✅ Database config loaded")
except ImportError as e:
    print(f"⚠️ Database config not available: {e}")

# Try to import API routers
try:
    from api import api_router
    API_ROUTER_AVAILABLE = True
    print("✅ API router loaded")
except ImportError as e:
    print(f"⚠️ API router not available: {e}")

try:
    from api.fhir import router as fhir_router
    FHIR_ROUTER_AVAILABLE = True
    print("✅ FHIR router loaded")
except ImportError as e:
    print(f"⚠️ FHIR router not available: {e}")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("diagnoassist")

# ===========================================================================
# ADDED: Exception Handlers for Proper Error Codes
# ===========================================================================

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors properly (422 instead of 500)"""
    logger.warning(f"Validation error for {request.method} {request.url}: {exc.errors()}")
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body": exc.body if hasattr(exc, 'body') else None
        }
    )

async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic ValidationError exceptions"""
    logger.warning(f"Pydantic validation error for {request.method} {request.url}: {exc.errors()}")
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors()
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error for {request.method} {request.url}: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan with safe startup"""
    logger.info("🚀 DiagnoAssist FHIR Server starting up...")
    print("🚀 DiagnoAssist FHIR Server starting up...")
    
    # Test exception system safely
    if EXCEPTION_HANDLING_AVAILABLE:
        try:
            test_exc = ValidationException(
                message="Startup validation test",
                field="test_field"
            )
            logger.info("✅ Exception system operational")
            print("✅ Exception system operational")
        except Exception as e:
            logger.error(f"❌ Exception system error: {e}")
            print(f"❌ Exception system error: {e}")
    
    # Test database safely
    if DATABASE_AVAILABLE:
        try:
            if test_database_connection():
                logger.info("✅ Database connection successful")
                print("✅ Database connection successful")
            else:
                logger.warning("⚠️ Database connection failed")
                print("⚠️ Database connection failed")
        except Exception as e:
            logger.error(f"❌ Database test error: {e}")
            print(f"❌ Database test error: {e}")
    
    print(f"🎯 Server ready at http://localhost:8000")
    print(f"📚 API Documentation: http://localhost:8000/docs")
    print(f"🏥 FHIR R4 Endpoint: http://localhost:8000/fhir/R4/metadata")
    print(f"🔧 Press Ctrl+C to stop the server")
    
    yield
    
    logger.info("👋 DiagnoAssist FHIR Server shutting down...")
    print("👋 DiagnoAssist FHIR Server shutting down...")

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="AI-powered medical diagnosis assistant with FHIR R4 compliance",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# ===========================================================================
# ADDED: Register Exception Handlers
# ===========================================================================

# Register exception handlers for proper error codes
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

print("✅ Exception handlers registered - validation errors will now return 422")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers if available
if API_ROUTER_AVAILABLE:
    app.include_router(api_router)
    logger.info("✅ API router included")

if FHIR_ROUTER_AVAILABLE:
    app.include_router(fhir_router)
    logger.info("✅ FHIR router included")
else:
    # Add basic FHIR endpoints as fallback
    @app.get("/fhir/R4/metadata", tags=["FHIR"])
    async def fhir_metadata():
        return {
            "resourceType": "CapabilityStatement",
            "status": "draft",
            "fhirVersion": "4.0.1",
            "format": ["json"],
            "rest": [{
                "mode": "server",
                "resource": [
                    {"type": "Patient"},
                    {"type": "Encounter"},
                    {"type": "Observation"}
                ]
            }]
        }
    
    @app.get("/fhir/R4/Patient", tags=["FHIR"])
    async def fhir_patients():
        return {
            "resourceType": "Bundle",
            "type": "searchset",
            "total": 0,
            "entry": []
        }

# Health check endpoints
@app.get("/health", tags=["Health"])
async def health_check():
    """Comprehensive health check"""
    components = {
        "exception_handling": "up" if EXCEPTION_HANDLING_AVAILABLE else "down",
        "database": "up" if DATABASE_AVAILABLE else "down",
        "api_router": "up" if API_ROUTER_AVAILABLE else "down",
        "fhir_router": "up" if FHIR_ROUTER_AVAILABLE else "down"
    }
    
    status = "healthy" if any(comp == "up" for comp in components.values()) else "degraded"
    
    return {
        "status": status,
        "version": settings.app_version,
        "components": components,
        "fhir_version": "R4"
    }

@app.get("/health/exception-system", tags=["Health"])
async def exception_system_health():
    """Exception system health check"""
    if not EXCEPTION_HANDLING_AVAILABLE:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unavailable",
                "message": "Exception handling system not available"
            }
        )
    
    try:
        # Test with correct parameter
        test_exc = ValidationException(
            message="Health check test exception",
            field="test_field"
        )
        
        return {
            "status": "operational",
            "features": {
                "validation_exceptions": True,
                "fhir_error_formatting": True
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error", 
                "message": str(e)
            }
        )

# ===========================================================================
# ADDED: Development Auth Test Endpoint
# ===========================================================================

@app.get("/test/auth", tags=["Development"])
async def test_auth_endpoint():
    """Test endpoint to verify authentication setup for development"""
    return {
        "message": "This endpoint tests authentication",
        "instructions": [
            "Send a request with 'Authorization: Bearer any-token' header",
            "The API will return a mock user in development mode",
            "This allows CRUD tests to work without real authentication"
        ],
        "example_headers": {
            "Authorization": "Bearer dev-token-123",
            "Content-Type": "application/json"
        }
    }

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint"""
    return {
        "message": "DiagnoAssist FHIR Server",
        "version": settings.app_version,
        "fhir_version": "R4",
        "status": "operational",
        "endpoints": {
            "documentation": "/docs",
            "health_check": "/health",
            "fhir_metadata": "/fhir/R4/metadata",
            "fhir_patients": "/fhir/R4/Patient",
            "test_auth": "/test/auth"  # Added for development
        }
    }

# FIXED: Proper server startup
def start_server():
    """Start the server with proper configuration"""
    print("🚀 Initializing DiagnoAssist Server...")
    print(f"📍 Host: 0.0.0.0")
    print(f"🔌 Port: 8000")
    print(f"🔄 Reload: True")
    print("🔧 Exception handlers enabled for proper validation errors")
    
    try:
        # Use string format to fix uvicorn warning and ensure server stays up
        uvicorn.run(
            "main:app",  # FIXED: Use string format instead of app object
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        print("💡 Trying fallback method...")
        
        # Fallback: run without reload if string method fails
        uvicorn.run(
            app,
            host="0.0.0.0", 
            port=8000,
            reload=False,  # Disable reload to avoid warning
            log_level="info"
        )

if __name__ == "__main__":
    start_server()