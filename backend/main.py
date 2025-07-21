"""
DiagnoAssist FastAPI Application Entry Point
FHIR R4 Compliant Medical Diagnosis Assistant API
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import uvicorn

# Import API routers
from api import api_router

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
    
    settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🏥 DiagnoAssist FHIR Server Starting...")
    print(f"📋 API Documentation: http://localhost:8000/docs")
    print(f"🔍 FHIR Metadata: http://localhost:8000/fhir/R4/metadata")
    print(f"👥 FHIR Patients: http://localhost:8000/fhir/R4/Patient")
    print(f"📊 Health Check: http://localhost:8000/health")
    
    # Initialize database if needed
    try:
        from config.database import init_db
        await init_db()
        print("✅ Database initialized successfully")
    except ImportError:
        print("⚠️  Database initialization skipped - config.database not found")
    except Exception as e:
        print(f"⚠️  Database initialization error: {e}")
    
    yield
    
    # Shutdown
    print("👋 DiagnoAssist FHIR Server shutting down...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="AI-powered medical diagnosis assistant with FHIR R4 compliance",
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

# Include API router
app.include_router(api_router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "DiagnoAssist FHIR Server",
        "version": settings.app_version,
        "fhir_version": "R4",
        "endpoints": {
            "docs": "/docs",
            "fhir_metadata": "/fhir/R4/metadata",
            "fhir_patients": "/fhir/R4/Patient",
            "health": "/health"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "DiagnoAssist FHIR Server",
        "version": settings.app_version,
        "fhir_version": "R4"
    }

# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "http_error",
                "message": exc.detail,
                "status_code": exc.status_code
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "type": "validation_error",
                "message": "Invalid request data",
                "details": exc.errors()
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "type": "internal_error",
                "message": "An internal server error occurred"
            }
        }
    )

# Run server when called directly
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )