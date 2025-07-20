from sqlalchemy import create_engine, MetaData, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from .settings import get_settings
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

# Database engine configuration
if settings.database_url.startswith("sqlite"):
    # SQLite specific configuration
    engine = create_engine(
        settings.database_url,
        echo=settings.database_echo,
        connect_args={
            "check_same_thread": False,
            "timeout": 20
        },
        poolclass=StaticPool
    )
    
    # Enable foreign key constraints for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")  # Better concurrency
        cursor.execute("PRAGMA synchronous=NORMAL")  # Better performance
        cursor.close()
        
else:
    # PostgreSQL/MySQL configuration
    engine = create_engine(
        settings.database_url,
        echo=settings.database_echo,
        pool_size=settings.connection_pool_size,
        max_overflow=settings.connection_pool_overflow,
        pool_pre_ping=True,  # Validate connections
        pool_recycle=3600    # Recycle connections every hour
    )

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

def get_db() -> Session:
    """
    Database dependency for FastAPI
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
    Create all database tables
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise

def test_database_connection():
    """
    Test database connectivity
    """
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False