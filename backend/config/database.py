"""
Database Configuration for DiagnoAssist
Windows Compatible Version with Proper Error Handling
"""

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging
import os

logger = logging.getLogger(__name__)

# Get DATABASE_URL with proper validation
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    logger.warning("⚠️ DATABASE_URL not found in environment")
    logger.warning("⚠️ Using fallback database URL for development")
    DATABASE_URL = "postgresql://postgres:password@localhost:5432/diagnoassist"

logger.info(f"Database configured: {DATABASE_URL.split('@')[0] if '@' in DATABASE_URL else 'fallback'}@[HIDDEN]")

# Database engine with safe configuration
try:
    engine = create_engine(
        DATABASE_URL,
        echo=False,  # Disable echo to reduce noise
        pool_pre_ping=True,
        connect_args={
            "connect_timeout": 10,
        } if "postgresql://" in DATABASE_URL else {}
    )
    ENGINE_AVAILABLE = True
except Exception as e:
    logger.error(f"❌ Engine creation failed: {e}")
    engine = None
    ENGINE_AVAILABLE = False

# Session maker
if ENGINE_AVAILABLE:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    SessionLocal = None

# Declarative base
Base = declarative_base()

def get_database() -> Generator[Session, None, None]:
    """Get database session"""
    if not ENGINE_AVAILABLE or not SessionLocal:
        raise Exception("Database engine not available")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_database_connection() -> bool:
    """Test database connectivity"""
    if not ENGINE_AVAILABLE:
        logger.error("❌ Database engine not available")
        return False
    
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT 1")).scalar()
        db.close()
        
        if result == 1:
            logger.info("✅ Database connection successful")
            return True
        else:
            logger.error("❌ Database query failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def get_database_health() -> dict:
    """Get database health status"""
    return {
        "status": "healthy" if ENGINE_AVAILABLE and test_database_connection() else "unhealthy",
        "engine_available": ENGINE_AVAILABLE,
        "database_url_configured": bool(DATABASE_URL and DATABASE_URL != "postgresql://postgres:password@localhost:5432/diagnoassist")
    }

def get_engine():
    """Get SQLAlchemy engine"""
    return engine if ENGINE_AVAILABLE else None

def get_db():
    """Get database session for FastAPI dependency"""
    if not ENGINE_AVAILABLE:
        raise Exception("Database not available")
    return get_database()
