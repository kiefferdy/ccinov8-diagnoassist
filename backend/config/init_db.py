"""
Database Initialization for DiagnoAssist
Handles database setup and table creation
"""

import logging
import asyncio
from typing import Optional
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError

from .database import engine, SessionLocal, Base, test_database_connection
from .settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class DatabaseInitializer:
    """Handles all database initialization tasks"""
    
    def __init__(self):
        self.engine = engine
        self.settings = settings
    
    def check_connection(self) -> bool:
        """Test database connection"""
        logger.info("Testing database connection...")
        return test_database_connection()
    
    def check_existing_tables(self) -> dict:
        """Check which tables already exist in the database"""
        try:
            inspector = inspect(self.engine)
            existing_tables = inspector.get_table_names()
            
            # Check for our expected tables
            expected_tables = ['patients', 'episodes', 'fhir_resources']
            table_status = {}
            
            for table in expected_tables:
                exists = table in existing_tables
                table_status[table] = {
                    'exists': exists,
                    'columns': inspector.get_columns(table) if exists else []
                }
                
            logger.info(f"Existing tables: {existing_tables}")
            return table_status
            
        except Exception as e:
            logger.error(f"Error checking existing tables: {e}")
            return {}
    
    def verify_supabase_tables(self) -> bool:
        """Verify that the Supabase tables match our expected schema"""
        try:
            db = SessionLocal()
            
            # Test each table with a simple query
            test_queries = [
                ("patients", "SELECT id, first_name, last_name FROM patients LIMIT 1"),
                ("episodes", "SELECT id, patient_id, status, chief_complaint FROM episodes LIMIT 1"), 
                ("fhir_resources", "SELECT id, resource_type, resource_id, fhir_data FROM fhir_resources LIMIT 1")
            ]
            
            for table_name, query in test_queries:
                try:
                    result = db.execute(text(query)).fetchone()
                    logger.info(f"✅ Table '{table_name}': Schema verified")
                except Exception as e:
                    logger.error(f"❌ Table '{table_name}': Schema issue - {e}")
                    db.close()
                    return False
            
            db.close()
            logger.info("All Supabase tables verified successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error verifying Supabase tables: {e}")
            return False
    
    def create_sqlalchemy_models(self):
        """Create SQLAlchemy model tables (will sync with existing Supabase tables)"""
        try:
            logger.info("Creating/syncing SQLAlchemy models with database...")
            
            # Import all models to register them with Base
            from models.patient import Patient
            from models.episode import Episode
            from models.fhir_resource import FHIRResource
            
            # This will create any missing tables and columns
            # Existing tables will not be affected
            Base.metadata.create_all(bind=self.engine)
            
            logger.info("SQLAlchemy models synced successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating SQLAlchemy models: {e}")
            raise
    
    def run_initial_setup(self):
        """Run any initial setup tasks"""
        try:
            db = SessionLocal()
            
            # Create any initial data or setup tasks here
            logger.info("Running initial database setup...")
            
            # Example: Create default admin user, setup initial data, etc.
            # This is where you'd add any seed data if needed
            
            db.close()
            logger.info("Initial setup completed")
            
        except Exception as e:
            logger.error(f"Error during initial setup: {e}")
            raise
    
    def initialize(self) -> bool:
        """
        Complete database initialization process
        Returns True if successful, False otherwise
        """
        try:
            logger.info("=" * 60)
            logger.info("Starting DiagnoAssist Database Initialization")
            logger.info("=" * 60)
            
            # Step 1: Test connection
            if not self.check_connection():
                logger.error("❌ Database connection failed")
                return False
            logger.info("✅ Database connection successful")
            
            # Step 2: Check existing tables
            existing_tables = self.check_existing_tables()
            if not existing_tables:
                logger.error("❌ Could not check existing tables")
                return False
            
            # Step 3: Verify Supabase tables
            if not self.verify_supabase_tables():
                logger.error("❌ Supabase table verification failed") 
                return False
            logger.info("✅ Supabase tables verified")
            
            # Step 4: Create/sync SQLAlchemy models
            self.create_sqlalchemy_models()
            logger.info("✅ SQLAlchemy models synced")
            
            # Step 5: Run initial setup
            self.run_initial_setup()
            logger.info("✅ Initial setup completed")
            
            logger.info("=" * 60)
            logger.info("✅ Database initialization completed successfully!")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error("=" * 60)
            logger.error(f"❌ Database initialization failed: {e}")
            logger.error("=" * 60)
            return False
    
    def get_database_info(self) -> dict:
        """Get database information for diagnostics"""
        try:
            db = SessionLocal()
            inspector = inspect(self.engine)
            
            # Get table information
            tables = []
            for table_name in inspector.get_table_names():
                columns = inspector.get_columns(table_name)
                tables.append({
                    'name': table_name,
                    'columns': len(columns),
                    'column_names': [col['name'] for col in columns]
                })
            
            # Get connection info
            db_info = {
                'url': self.settings.get_database_url_safe(),
                'echo': self.settings.database_echo,
                'tables': tables,
                'table_count': len(tables),
                'pool_size': getattr(self.settings, 'connection_pool_size', 'N/A'),
                'environment': self.settings.environment
            }
            
            db.close()
            return db_info
            
        except Exception as e:
            return {'error': str(e)}


# Convenience functions
def initialize_database() -> bool:
    """Initialize database - main entry point"""
    initializer = DatabaseInitializer()
    return initializer.initialize()

def check_database_health() -> dict:
    """Check database health for monitoring"""
    initializer = DatabaseInitializer()
    health_info = {
        'connection': initializer.check_connection(),
        'tables_verified': initializer.verify_supabase_tables()
    }
    return health_info

def get_db_info() -> dict:
    """Get database information"""
    initializer = DatabaseInitializer()
    return initializer.get_database_info()


if __name__ == "__main__":
    # Run database initialization
    success = initialize_database()
    if success:
        print("Database initialized successfully!")
    else:
        print("Database initialization failed!")
        exit(1)