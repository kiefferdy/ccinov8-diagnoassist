#!/usr/bin/env python3
"""
DiagnoAssist Startup Script
Handles PostgreSQL setup, migrations, and server startup
"""

import os
import sys
import time
import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Load environment variables
load_dotenv()

def import_all_models():
    """Import all models to register them with SQLAlchemy"""
    try:
        # Import all models explicitly to register them
        from models.patient import Patient
        from models.episode import Episode
        from models.diagnosis import Diagnosis
        from models.treatment import Treatment
        from models.fhir_resource import FHIRResource
        
        # Add any other model imports here as needed
        print("📦 Models imported successfully")
        return True
    except ImportError as e:
        print(f"⚠️  Some models not found: {e}")
        print("📝 Will attempt to create basic tables...")
        return False

class DiagnoAssistStarter:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        self.secret_key = os.getenv("SECRET_KEY")
        self.fhir_base_url = os.getenv("FHIR_BASE_URL")
        
        if not all([self.db_url, self.secret_key, self.fhir_base_url]):
            print("❌ Missing required environment variables!")
            print("Required: DATABASE_URL, SECRET_KEY, FHIR_BASE_URL")
            sys.exit(1)
    
    def parse_db_url(self):
        """Parse PostgreSQL URL into components"""
        # postgresql://user:password@host:port/database
        if not self.db_url.startswith("postgresql://"):
            print("❌ DATABASE_URL must be a PostgreSQL URL")
            sys.exit(1)
        
        url_parts = self.db_url.replace("postgresql://", "").split("/")
        auth_host = url_parts[0]
        database = url_parts[1] if len(url_parts) > 1 else "diagnoassist"
        
        auth, host_port = auth_host.split("@")
        user, password = auth.split(":")
        host_parts = host_port.split(":")
        host = host_parts[0]
        port = int(host_parts[1]) if len(host_parts) > 1 else 5432
        
        return {
            "user": user,
            "password": password,
            "host": host,
            "port": port,
            "database": database
        }
    
    def wait_for_postgres(self, db_config, max_retries=30):
        """Wait for PostgreSQL to be available"""
        print("🔍 Waiting for PostgreSQL to be available...")
        
        for attempt in range(max_retries):
            try:
                conn = psycopg2.connect(
                    host=db_config["host"],
                    port=db_config["port"],
                    user=db_config["user"],
                    password=db_config["password"],
                    database="postgres"  # Connect to default database first
                )
                conn.close()
                print("✅ PostgreSQL is available!")
                return True
            except psycopg2.OperationalError:
                print(f"⏳ Attempt {attempt + 1}/{max_retries}: PostgreSQL not ready, waiting...")
                time.sleep(2)
        
        print("❌ PostgreSQL is not available after 60 seconds")
        return False
    
    def create_database_if_needed(self, db_config):
        """Create database if it doesn't exist"""
        try:
            # Connect to PostgreSQL server (not specific database)
            conn = psycopg2.connect(
                host=db_config["host"],
                port=db_config["port"],
                user=db_config["user"],
                password=db_config["password"],
                database="postgres"
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # Check if database exists
            cursor.execute(
                "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s",
                (db_config["database"],)
            )
            
            if not cursor.fetchone():
                print(f"📝 Creating database '{db_config['database']}'...")
                cursor.execute(f'CREATE DATABASE "{db_config["database"]}"')
                print("✅ Database created successfully!")
            else:
                print(f"✅ Database '{db_config['database']}' already exists")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Error creating database: {e}")
            return False
    
    def test_database_connection(self):
        """Test connection to the application database"""
        try:
            engine = create_engine(self.db_url)
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                print("✅ Database connection successful!")
                return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def run_migrations(self):
        """Run database migrations"""
        print("🔄 Running database migrations...")
        
        # Check if alembic is configured
        if Path("alembic.ini").exists():
            try:
                result = subprocess.run(
                    ["alembic", "upgrade", "head"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print("✅ Migrations completed successfully!")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Migration failed: {e.stderr}")
                return False
        else:
            # Fallback: Create tables directly
            print("📝 No alembic found, creating tables directly...")
            try:
                # Import models first
                import_all_models()
                
                from config.database import engine, Base
                
                # Create all tables
                Base.metadata.create_all(bind=engine)
                print("✅ Database tables created!")
                return True
            except Exception as e:
                print(f"❌ Error creating tables: {e}")
                print(f"💡 Make sure your models are in the models/ directory")
                return False
    
    def create_basic_tables(self):
        """Create basic tables if models are not available"""
        print("📝 Creating basic FHIR tables...")
        try:
            engine = create_engine(self.db_url)
            with engine.connect() as conn:
                # Create basic FHIR resources table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS fhir_resources (
                        id VARCHAR PRIMARY KEY,
                        resource_type VARCHAR NOT NULL,
                        resource_id VARCHAR NOT NULL,
                        version_id VARCHAR,
                        fhir_data JSONB NOT NULL,
                        internal_id VARCHAR,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Create indexes
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_fhir_resources_type 
                    ON fhir_resources(resource_type)
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_fhir_resources_resource_id 
                    ON fhir_resources(resource_id)
                """))
                
                conn.commit()
                print("✅ Basic FHIR tables created!")
                return True
        except Exception as e:
            print(f"❌ Error creating basic tables: {e}")
            return False
    
    def start_docker_postgres(self):
        """Start PostgreSQL using Docker Compose"""
        if Path("docker-compose.yml").exists():
            print("🐳 Starting PostgreSQL with Docker Compose...")
            try:
                subprocess.run(
                    ["docker-compose", "up", "-d", "postgres"],
                    check=True,
                    capture_output=True
                )
                print("✅ PostgreSQL container started!")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to start Docker container: {e}")
                return False
        return False
    
    def start_server(self):
        """Start the FastAPI server"""
        print("🚀 Starting DiagnoAssist FHIR Server...")
        
        port = os.getenv("PORT", "8000")
        host = os.getenv("HOST", "0.0.0.0")
        
        try:
            subprocess.run([
                "uvicorn", "main:app",
                "--reload",
                "--host", host,
                "--port", port,
                "--log-level", "info"
            ])
        except KeyboardInterrupt:
            print("\n👋 Server stopped by user")
        except Exception as e:
            print(f"❌ Server failed to start: {e}")
            return False
    
    def run(self):
        """Main startup sequence"""
        print("🏥 DiagnoAssist FHIR Server Startup")
        print("=" * 50)
        
        # Parse database configuration
        db_config = self.parse_db_url()
        print(f"🎯 Target database: {db_config['database']} on {db_config['host']}:{db_config['port']}")
        
        # Start Docker PostgreSQL if using localhost and docker-compose exists
        if db_config["host"] == "localhost" and Path("docker-compose.yml").exists():
            if not self.start_docker_postgres():
                print("⚠️  Failed to start Docker PostgreSQL, assuming it's already running")
        
        # Wait for PostgreSQL to be available
        if not self.wait_for_postgres(db_config):
            print("💡 If using Docker: docker-compose up -d postgres")
            print("💡 If using local PostgreSQL: sudo systemctl start postgresql")
            sys.exit(1)
        
        # Create database if needed
        if not self.create_database_if_needed(db_config):
            sys.exit(1)
        
        # Test connection to application database
        if not self.test_database_connection():
            sys.exit(1)
        
        # Run migrations
        if not self.run_migrations():
            print("⚠️  Migration failed, creating basic tables instead...")
            if not self.create_basic_tables():
                print("❌ Failed to create any tables. Please check your setup.")
                sys.exit(1)
        
        # Start the server
        print("\n🌐 FHIR Server will be available at:")
        print(f"   📋 Metadata: {self.fhir_base_url}/R4/metadata")
        print(f"   👥 Patients: {self.fhir_base_url}/R4/Patient")
        print(f"   📊 Observations: {self.fhir_base_url}/R4/Observation")
        print("\n🔄 Starting server...\n")
        
        self.start_server()

def main():
    """Entry point"""
    starter = DiagnoAssistStarter()
    starter.run()

if __name__ == "__main__":
    main()