"""
Database Migration Management Script
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from config.database import test_database_connection
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

def init_alembic():
    """Initialize Alembic migrations"""
    try:
        # Test database connection first
        if not test_database_connection():
            logger.error("❌ Database connection failed")
            return False
        
        # Initialize Alembic
        subprocess.run(["alembic", "init", "migrations"], check=True)
        logger.info("✅ Alembic initialized")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to initialize Alembic: {e}")
        return False

def create_migration(message: str):
    """Create a new migration"""
    try:
        cmd = ["alembic", "revision", "--autogenerate", "-m", message]
        subprocess.run(cmd, check=True)
        logger.info(f"✅ Migration created: {message}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to create migration: {e}")
        return False

def run_migrations():
    """Run pending migrations"""
    try:
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        logger.info("✅ Migrations completed")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to run migrations: {e}")
        return False

def migration_status():
    """Check migration status"""
    try:
        subprocess.run(["alembic", "current"], check=True)
        subprocess.run(["alembic", "history"], check=True)
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to check migration status: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database Migration Management")
    parser.add_argument("command", choices=["init", "create", "migrate", "status"])
    parser.add_argument("-m", "--message", help="Migration message")
    
    args = parser.parse_args()
    
    if args.command == "init":
        init_alembic()
    elif args.command == "create":
        if not args.message:
            print("Error: Migration message required. Use -m 'your message'")
            sys.exit(1)
        create_migration(args.message)
    elif args.command == "migrate":
        run_migrations()
    elif args.command == "status":
        migration_status()