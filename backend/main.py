"""
DiagnoAssist FastAPI Application Entry Point - MINIMAL CLEAN VERSION
FHIR R4 Compliant Medical Diagnosis Assistant API
"""

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Print loaded env vars for debugging
print(f"🔍 DATABASE_URL loaded: {'✅ Yes' if os.getenv('DATABASE_URL') else '❌ No'}")
print(f"🔍 SUPABASE_URL loaded: {'✅ Yes' if os.getenv('SUPABASE_URL') else '❌ No'}")

# Simple settings
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

settings = Settings()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="FHIR R4 Compliant Medical Diagnosis Assistant API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Track what's available
components_status = {
    "database": False,
    "api_router": False,
    "patients_router": False,
    "episodes_router": False,
    "treatments_router": False
}

# Try to include routers one by one
logger.info("🚀 DiagnoAssist API starting...")

# Test database
try:
    from config.database import SessionLocal
    db = SessionLocal()
    db.close()
    components_status["database"] = True
    logger.info("✅ Database connection successful")
except Exception as e:
    logger.warning(f"⚠️ Database connection failed: {e}")

# Try main API router first
try:
    from api import api_router
    app.include_router(api_router)
    components_status["api_router"] = True
    logger.info("✅ Main API router included")
except Exception as e:
    logger.warning(f"⚠️ Main API router failed: {e}")
    
    # Try individual routers as fallback
    try:
        from api.patients import router as patients_router
        app.include_router(patients_router, prefix="/api/v1")
        components_status["patients_router"] = True
        logger.info("✅ Patients router included")
    except Exception as e2:
        logger.warning(f"⚠️ Patients router failed: {e2}")
    
    try:
        from api.episodes import router as episodes_router
        app.include_router(episodes_router, prefix="/api/v1")
        components_status["episodes_router"] = True
        logger.info("✅ Episodes router included")
    except Exception as e3:
        logger.warning(f"⚠️ Episodes router failed: {e3}")
    
    try:
        from api.treatments import router as treatments_router
        app.include_router(treatments_router, prefix="/api/v1")
        components_status["treatments_router"] = True
        logger.info("✅ Treatments router included")
    except Exception as e4:
        logger.warning(f"⚠️ Treatments router failed: {e4}")

# Basic endpoints
@app.get("/")
async def root():
    """Root endpoint with system status"""
    return {
        "message": "DiagnoAssist API",
        "version": settings.app_version,
        "status": "running",
        "components": components_status,
        "docs": "/api/docs"
    }

@app.get("/health")
async def health_check():
    """Simple health check"""
    return {
        "status": "healthy",
        "components": components_status
    }

logger.info("✅ DiagnoAssist API startup completed")

# Development server
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )