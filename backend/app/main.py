"""
FastAPI application entry point for DiagnoAssist Backend
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.core.exceptions import DiagnoAssistException
from app.api.api import api_router

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level.upper()))
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("DiagnoAssist Backend starting up...")
    
    # Initialize database connection
    try:
        from app.core.database import init_database
        await init_database()
        logger.info("Database connection initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    # Initialize FHIR client
    try:
        from app.core.fhir_client import init_fhir_client
        await init_fhir_client()
        logger.info("FHIR client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize FHIR client: {e}")
        # Don't raise - allow app to start without FHIR
    
    # Initialize AI client
    try:
        from app.core.ai_client import initialize_ai_client
        initialize_ai_client(settings.gemini_api_key)
        logger.info("AI client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize AI client: {e}")
        # Don't raise - allow app to start without AI
    
    # Initialize template service
    try:
        from app.services.template_initialization import initialize_template_service_with_dependencies
        await initialize_template_service_with_dependencies()
        logger.info("Template service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize template service: {e}")
        # Don't raise - allow app to start without templates
    
    # Initialize report service
    try:
        from app.services.report_initialization import initialize_report_service_with_dependencies
        await initialize_report_service_with_dependencies()
        logger.info("Report service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize report service: {e}")
        # Don't raise - allow app to start without reports
    
    # Initialize search service
    try:
        from app.services.search_initialization import initialize_search_service_with_dependencies
        await initialize_search_service_with_dependencies()
        logger.info("Search service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize search service: {e}")
        # Don't raise - allow app to start without search
    
    # Performance optimization system removed - using simplified approach
    logger.info("Performance optimization system: simplified (removed complex enterprise features)")
    
    yield
    
    # Shutdown
    logger.info("DiagnoAssist Backend shutting down...")
    
    # Close database connections
    try:
        from app.core.database import close_database
        await close_database()
        logger.info("Database connection closed successfully")
    except Exception as e:
        logger.error(f"Error closing database connection: {e}")
    
    # Close FHIR client
    try:
        from app.core.fhir_client import close_fhir_client
        await close_fhir_client()
        logger.info("FHIR client closed successfully")
    except Exception as e:
        logger.error(f"Error closing FHIR client: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.project_name,
    version=settings.project_version,
    description="AI-powered medical diagnosis assistant backend",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(DiagnoAssistException)
async def diagnoassist_exception_handler(request: Request, exc: DiagnoAssistException):
    """Handle custom DiagnoAssist exceptions"""
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            }
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": exc.errors(),
            }
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": "HTTP_ERROR",
                "message": exc.detail,
                "details": {},
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "details": {} if not settings.debug else {"error": str(exc)},
            }
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "service": settings.project_name,
            "version": settings.project_version,
            "environment": settings.environment,
        }
    }


# Include API router
app.include_router(api_router, prefix=settings.api_v1_prefix)

# Include WebSocket router
from app.api.v1.websocket import router as websocket_router
app.include_router(websocket_router, prefix="/ws", tags=["websocket"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )