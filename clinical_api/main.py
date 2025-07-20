"""
FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from clinical_api.config import (
    API_TITLE, API_DESCRIPTION, API_VERSION, 
    ALLOWED_ORIGINS, HOST, PORT, RELOAD
)

from clinical_api.database.models import create_tables
from clinical_api.database.seed_data import seed_database
from clinical_api.api.routes import health, icd10

# Create FastAPI application
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api")
app.include_router(icd10.router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Initialize database and seed data on application startup"""
    create_tables()
    seed_database()
    print(f"Clinical Documentation API started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    print("Clinical Documentation API shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=HOST, port=PORT, reload=RELOAD)