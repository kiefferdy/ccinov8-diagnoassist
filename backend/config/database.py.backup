"""
Database Configuration for DiagnoAssist
Uses existing Supabase connection with SQLAlchemy models
"""

from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging
import os
import requests

# Import settings
try:
    from .settings import get_settings
    settings = get_settings()
except ImportError:
    # Fallback for development
    class FallbackSettings:
        supabase_url = os.getenv("SUPABASE_URL", "")
        supabase_anon_key = os.getenv("SUPABASE_ANON_KEY", "")
        secret_key = os.getenv("SECRET_KEY", "fallback-secret")
        database_echo = os.getenv("DATABASE_ECHO", "false").lower() == "true"
    settings = FallbackSettings()

logger = logging.getLogger(__name__)

# For now, we'll use a simple PostgreSQL connection string
# You can get this from Supabase Dashboard > Settings > Database > Connection string
# This is a placeholder - you'll need to add your actual connection string when ready
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:password@db.project.supabase.co:5432/postgres"
)

# Database engine configuration
def create_database_engine():
    """Create SQLAlchemy engine with proper configuration"""
    
    # Use PostgreSQL connection directly for SQLAlchemy
    engine = create_engine(
        DATABASE_URL,
        echo=settings.database_echo,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,  # Validate connections before use
        pool_recycle=3600,   # Recycle connections every hour
    )
    
    return engine

# Create the engine
engine = create_database_engine()

# Session configuration
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all models
Base = declarative_base()

# FHIR-specific metadata for resource versioning
fhir_metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s", 
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }
)

def get_db() -> Generator[Session, None, None]:
    """
    Database dependency for FastAPI
    Provides a database session with proper cleanup
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

def create_database():
    """
    Create all database tables using SQLAlchemy
    This will work with the existing Supabase tables
    """
    try:
        # Import all models to ensure they're registered
        from models.patient import Patient
        from models.episode import Episode  
        from models.fhir_resource import FHIRResource
        
        # Create tables (this will not recreate existing ones)
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise

def test_database_connection() -> bool:
    """
    Test database connectivity and basic operations
    """
    try:
        db = SessionLocal()
        
        # Test basic connection
        result = db.execute(text("SELECT 1")).scalar()
        if result != 1:
            raise Exception("Basic query failed")
            
        # Test if we can access our tables
        db.execute(text("SELECT COUNT(*) FROM patients LIMIT 1")).scalar()
        
        db.close()
        logger.info("Database connection test successful")
        return True
        
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return False

def test_supabase_connection() -> bool:
    """
    Test connection to Supabase using REST API (your current method)
    """
    try:
        if not settings.supabase_url or not settings.supabase_anon_key:
            logger.error("Missing SUPABASE_URL or SUPABASE_ANON_KEY")
            return False
            
        headers = {
            'apikey': settings.supabase_anon_key,
            'Authorization': f'Bearer {settings.supabase_anon_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f"{settings.supabase_url}/rest/v1/",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info("Supabase REST API connection successful")
            return True
        else:
            logger.error(f"Supabase connection failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Supabase connection test failed: {str(e)}")
        return False

def initialize_database():
    """
    Complete database initialization
    - Test connections
    - Verify tables exist in Supabase
    - Set up SQLAlchemy models
    """
    logger.info("Initializing database...")
    
    # Test Supabase connection (your current working method)
    if not test_supabase_connection():
        logger.warning("Supabase REST API test failed, but continuing...")
    
    # For Step 2, we'll focus on getting the basic structure ready
    # The actual database connection will be refined in later steps
    logger.info("Database initialization complete (basic setup)")
    return True

# Health check function
def get_database_health() -> dict:
    """
    Get database health status for monitoring
    """
    try:
        supabase_ok = test_supabase_connection()
        
        return {
            "status": "healthy" if supabase_ok else "degraded",
            "supabase_rest": "connected" if supabase_ok else "failed",
            "supabase_url": settings.supabase_url if hasattr(settings, 'supabase_url') else "not configured"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy", 
            "error": str(e)
        }

# For backwards compatibility
def get_engine():
    """Get the SQLAlchemy engine"""
    return engine