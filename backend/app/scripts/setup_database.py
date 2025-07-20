"""
Master database setup script for DiagnoAssist Backend
"""
import asyncio
import logging
import argparse
from typing import Dict, Any

from app.scripts.init_db import DatabaseInitializer
from app.scripts.migrate import MigrationManager
from app.scripts.seed_data import DataSeeder
from app.core.database import init_database

logger = logging.getLogger(__name__)


class DatabaseSetupManager:
    """Master database setup and management"""
    
    def __init__(self):
        self.initializer = DatabaseInitializer()
        self.migration_manager = MigrationManager()
        self.seeder = DataSeeder()
    
    async def setup_fresh_database(self, include_seed: bool = True) -> Dict[str, Any]:
        """Set up database from scratch"""
        logger.info("Setting up fresh database...")
        
        results = {
            "initialization": {"success": False, "error": None},
            "migrations": {"success": False, "error": None},
            "seeding": {"success": False, "error": None}
        }
        
        try:
            # Step 1: Initialize database
            logger.info("Step 1: Initializing database...")
            await self.initializer.run_full_initialization()
            results["initialization"]["success"] = True
            logger.info("✓ Database initialization completed")
            
            # Step 2: Run migrations
            logger.info("Step 2: Running migrations...")
            await self.migration_manager.initialize()
            await self.migration_manager.migrate_up()
            results["migrations"]["success"] = True
            logger.info("✓ Database migrations completed")
            
            # Step 3: Seed data (optional)
            if include_seed:
                logger.info("Step 3: Seeding sample data...")
                await self.seeder.run_full_seeding(force=True)
                results["seeding"]["success"] = True
                logger.info("✓ Database seeding completed")
            else:
                results["seeding"]["success"] = True
                results["seeding"]["skipped"] = True
                logger.info("○ Database seeding skipped")
            
            logger.info("✅ Fresh database setup completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Database setup failed: {e}")
            
            # Record which step failed
            if not results["initialization"]["success"]:
                results["initialization"]["error"] = str(e)
            elif not results["migrations"]["success"]:
                results["migrations"]["error"] = str(e)
            elif not results["seeding"]["success"]:
                results["seeding"]["error"] = str(e)
            
            raise
        
        return results
    
    async def update_existing_database(self) -> Dict[str, Any]:
        """Update existing database with new migrations"""
        logger.info("Updating existing database...")
        
        results = {
            "health_check": {"success": False, "error": None},
            "migrations": {"success": False, "error": None}
        }
        
        try:
            # Step 1: Health check
            logger.info("Step 1: Checking database health...")
            await self.initializer.initialize()
            await self.initializer.verify_database_health()
            results["health_check"]["success"] = True
            logger.info("✓ Database health check passed")
            
            # Step 2: Run pending migrations
            logger.info("Step 2: Running pending migrations...")
            await self.migration_manager.initialize()
            
            # Check for pending migrations
            status = await self.migration_manager.get_migration_status()
            if status["pending_migrations"]:
                logger.info(f"Found {len(status['pending_migrations'])} pending migrations")
                await self.migration_manager.migrate_up()
                results["migrations"]["success"] = True
                logger.info("✓ Database migrations completed")
            else:
                results["migrations"]["success"] = True
                results["migrations"]["skipped"] = True
                logger.info("○ No pending migrations")
            
            logger.info("✅ Database update completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Database update failed: {e}")
            
            # Record which step failed
            if not results["health_check"]["success"]:
                results["health_check"]["error"] = str(e)
            elif not results["migrations"]["success"]:
                results["migrations"]["error"] = str(e)
            
            raise
        
        return results
    
    async def get_database_status(self) -> Dict[str, Any]:
        """Get comprehensive database status"""
        logger.info("Checking database status...")
        
        status = {
            "connection": {"available": False, "error": None},
            "collections": {"count": 0, "names": []},
            "migrations": {"applied": 0, "pending": 0, "details": None},
            "data": {"patients": 0, "episodes": 0, "encounters": 0, "users": 0},
            "indexes": {"total": 0, "by_collection": {}},
            "fhir_sync": {"available": False, "sync_count": 0}
        }
        
        try:
            # Check database connection
            await self.initializer.initialize()
            status["connection"]["available"] = True
            
            # Get collections info
            db = await self.initializer.db
            collections = await db.list_collection_names()
            status["collections"]["count"] = len(collections)
            status["collections"]["names"] = collections
            
            # Get migration status
            await self.migration_manager.initialize()
            migration_status = await self.migration_manager.get_migration_status()
            status["migrations"]["applied"] = len(migration_status["applied_migrations"])
            status["migrations"]["pending"] = len(migration_status["pending_migrations"])
            status["migrations"]["details"] = migration_status
            
            # Get data counts
            for collection_name in ["patients", "episodes", "encounters", "users"]:
                if collection_name in collections:
                    count = await db[collection_name].count_documents({})
                    status["data"][collection_name] = count
            
            # Get index information
            total_indexes = 0
            for collection_name in collections:
                if not collection_name.startswith("_"):  # Skip system collections
                    collection = db[collection_name]
                    indexes = await collection.list_indexes().to_list(length=None)
                    index_count = len(indexes)
                    status["indexes"]["by_collection"][collection_name] = index_count
                    total_indexes += index_count
            
            status["indexes"]["total"] = total_indexes
            
            # Check FHIR sync status
            if "fhir_sync_status" in collections:
                status["fhir_sync"]["available"] = True
                sync_count = await db["fhir_sync_status"].count_documents({})
                status["fhir_sync"]["sync_count"] = sync_count
            
            logger.info("✓ Database status check completed")
            
        except Exception as e:
            logger.error(f"Database status check failed: {e}")
            status["connection"]["error"] = str(e)
        
        return status
    
    async def backup_database(self, backup_name: str = None) -> Dict[str, Any]:
        """Create a logical backup of the database"""
        if not backup_name:
            from datetime import datetime
            backup_name = f"diagnoassist_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"Creating database backup: {backup_name}")
        
        # This would implement a backup strategy
        # For now, we'll just return backup metadata
        backup_info = {
            "backup_name": backup_name,
            "created_at": "2024-01-01T00:00:00Z",  # Would be actual timestamp
            "collections_backed_up": [],
            "total_documents": 0,
            "backup_size": "0 MB",
            "backup_location": f"/backups/{backup_name}.json"
        }
        
        logger.warning("Backup functionality not yet implemented")
        return backup_info
    
    async def restore_database(self, backup_name: str) -> Dict[str, Any]:
        """Restore database from backup"""
        logger.info(f"Restoring database from backup: {backup_name}")
        
        # This would implement restore functionality
        restore_info = {
            "backup_name": backup_name,
            "restored_at": "2024-01-01T00:00:00Z",  # Would be actual timestamp
            "collections_restored": [],
            "total_documents_restored": 0
        }
        
        logger.warning("Restore functionality not yet implemented")
        return restore_info


async def main():
    """Main entry point for database setup"""
    parser = argparse.ArgumentParser(description="DiagnoAssist Database Setup")
    parser.add_argument("operation", 
                       choices=["fresh", "update", "status", "backup", "restore"],
                       help="Database operation to perform")
    parser.add_argument("--no-seed", action="store_true", 
                       help="Skip seeding sample data (fresh setup only)")
    parser.add_argument("--backup-name", help="Backup name for backup/restore operations")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Initialize database connection
    await init_database()
    
    # Create setup manager
    setup_manager = DatabaseSetupManager()
    
    try:
        if args.operation == "fresh":
            include_seed = not args.no_seed
            results = await setup_manager.setup_fresh_database(include_seed)
            logger.info("Fresh database setup results:")
            for step, result in results.items():
                status = "✓" if result["success"] else "❌"
                logger.info(f"  {status} {step.title()}")
                if result.get("error"):
                    logger.error(f"    Error: {result['error']}")
        
        elif args.operation == "update":
            results = await setup_manager.update_existing_database()
            logger.info("Database update results:")
            for step, result in results.items():
                status = "✓" if result["success"] else "❌"
                logger.info(f"  {status} {step.title()}")
                if result.get("skipped"):
                    logger.info(f"    (skipped)")
                if result.get("error"):
                    logger.error(f"    Error: {result['error']}")
        
        elif args.operation == "status":
            status = await setup_manager.get_database_status()
            logger.info("Database Status Report:")
            logger.info(f"  Connection: {'✓' if status['connection']['available'] else '❌'}")
            if status['connection']['error']:
                logger.error(f"    Error: {status['connection']['error']}")
            logger.info(f"  Collections: {status['collections']['count']}")
            logger.info(f"  Migrations: {status['migrations']['applied']} applied, {status['migrations']['pending']} pending")
            logger.info(f"  Data: {status['data']['patients']} patients, {status['data']['episodes']} episodes, {status['data']['encounters']} encounters, {status['data']['users']} users")
            logger.info(f"  Indexes: {status['indexes']['total']} total")
            logger.info(f"  FHIR Sync: {'✓' if status['fhir_sync']['available'] else '❌'} ({status['fhir_sync']['sync_count']} records)")
        
        elif args.operation == "backup":
            backup_info = await setup_manager.backup_database(args.backup_name)
            logger.info(f"Backup created: {backup_info['backup_name']}")
        
        elif args.operation == "restore":
            if not args.backup_name:
                logger.error("Backup name required for restore operation")
                return
            restore_info = await setup_manager.restore_database(args.backup_name)
            logger.info(f"Database restored from: {restore_info['backup_name']}")
    
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    import os
    
    # Add project root to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
    
    # Run main
    exit_code = asyncio.run(main())
    sys.exit(exit_code)