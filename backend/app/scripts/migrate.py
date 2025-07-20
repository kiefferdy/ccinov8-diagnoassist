"""
Database migration script for DiagnoAssist Backend
"""
import asyncio
import logging
from typing import List, Dict, Any, Callable
from datetime import datetime

from app.core.database import get_database

logger = logging.getLogger(__name__)


class Migration:
    """Base migration class"""
    
    def __init__(self, version: str, description: str):
        self.version = version
        self.description = description
        self.timestamp = datetime.utcnow()
    
    async def up(self, db):
        """Apply migration"""
        raise NotImplementedError("Migration must implement up() method")
    
    async def down(self, db):
        """Rollback migration"""
        raise NotImplementedError("Migration must implement down() method")


class Migration001AddTimestamps(Migration):
    """Add created_at and updated_at timestamps to all documents"""
    
    def __init__(self):
        super().__init__("001", "Add timestamps to all collections")
    
    async def up(self, db):
        collections = ["patients", "episodes", "encounters", "users"]
        now = datetime.utcnow()
        
        for collection_name in collections:
            collection = db[collection_name]
            
            # Update documents without created_at
            result = await collection.update_many(
                {"created_at": {"$exists": False}},
                {"$set": {"created_at": now}}
            )
            logger.info(f"Added created_at to {result.modified_count} documents in {collection_name}")
            
            # Update documents without updated_at
            result = await collection.update_many(
                {"updated_at": {"$exists": False}},
                {"$set": {"updated_at": now}}
            )
            logger.info(f"Added updated_at to {result.modified_count} documents in {collection_name}")
    
    async def down(self, db):
        collections = ["patients", "episodes", "encounters", "users"]
        
        for collection_name in collections:
            collection = db[collection_name]
            
            # Remove timestamps (be careful with this in production!)
            result = await collection.update_many(
                {},
                {"$unset": {"created_at": "", "updated_at": ""}}
            )
            logger.info(f"Removed timestamps from {result.modified_count} documents in {collection_name}")


class Migration002AddFHIRSyncCollection(Migration):
    """Add FHIR synchronization status collection"""
    
    def __init__(self):
        super().__init__("002", "Add FHIR synchronization collection")
    
    async def up(self, db):
        # Create FHIR sync status collection
        collection_name = "fhir_sync_status"
        
        if collection_name not in await db.list_collection_names():
            await db.create_collection(collection_name)
            logger.info(f"Created collection: {collection_name}")
        
        # Create indexes
        collection = db[collection_name]
        
        indexes = [
            {"keys": [("entity_id", 1), ("entity_type", 1)], "name": "entity_unique_idx", "unique": True},
            {"keys": [("sync_status", 1)], "name": "sync_status_idx"},
            {"keys": [("last_sync", -1)], "name": "last_sync_desc_idx", "sparse": True}
        ]
        
        for index_def in indexes:
            try:
                keys = index_def["keys"]
                options = {k: v for k, v in index_def.items() if k not in ["keys"]}
                await collection.create_index(keys, **options)
                logger.info(f"Created index {index_def['name']} on {collection_name}")
            except Exception as e:
                logger.warning(f"Failed to create index {index_def['name']}: {e}")
    
    async def down(self, db):
        collection_name = "fhir_sync_status"
        
        if collection_name in await db.list_collection_names():
            await db.drop_collection(collection_name)
            logger.info(f"Dropped collection: {collection_name}")


class Migration003AddWorkflowFields(Migration):
    """Add workflow fields to encounters"""
    
    def __init__(self):
        super().__init__("003", "Add workflow fields to encounters")
    
    async def up(self, db):
        collection = db["encounters"]
        
        # Add workflow field to encounters without it
        default_workflow = {
            "version": 1,
            "last_saved": datetime.utcnow(),
            "signed_version": None
        }
        
        result = await collection.update_many(
            {"workflow": {"$exists": False}},
            {"$set": {"workflow": default_workflow}}
        )
        logger.info(f"Added workflow field to {result.modified_count} encounters")
        
        # Update encounters with signed status to have signed_version
        result = await collection.update_many(
            {
                "status": "signed",
                "workflow.signed_version": {"$exists": False}
            },
            {"$set": {"workflow.signed_version": 1}}
        )
        logger.info(f"Updated signed_version for {result.modified_count} signed encounters")
    
    async def down(self, db):
        collection = db["encounters"]
        
        # Remove workflow field
        result = await collection.update_many(
            {},
            {"$unset": {"workflow": ""}}
        )
        logger.info(f"Removed workflow field from {result.modified_count} encounters")


class Migration004AddProviderInfo(Migration):
    """Add provider information to encounters"""
    
    def __init__(self):
        super().__init__("004", "Add provider information to encounters")
    
    async def up(self, db):
        encounters_collection = db["encounters"]
        users_collection = db["users"]
        
        # Get all encounters without proper provider info
        encounters = await encounters_collection.find({
            "$or": [
                {"provider.department": {"$exists": False}},
                {"provider.specialty": {"$exists": False}}
            ]
        }).to_list(length=None)
        
        for encounter in encounters:
            if "provider" in encounter and "id" in encounter["provider"]:
                provider_id = encounter["provider"]["id"]
                
                # Get user info
                user = await users_collection.find_one({"id": provider_id})
                if user and "profile" in user:
                    profile = user["profile"]
                    
                    # Update provider info
                    updated_provider = encounter["provider"].copy()
                    updated_provider["department"] = profile.get("department", "Unknown")
                    updated_provider["specialty"] = profile.get("specialty", "Unknown")
                    
                    await encounters_collection.update_one(
                        {"_id": encounter["_id"]},
                        {"$set": {"provider": updated_provider}}
                    )
                    logger.debug(f"Updated provider info for encounter {encounter.get('id', encounter['_id'])}")
        
        logger.info(f"Updated provider information for {len(encounters)} encounters")
    
    async def down(self, db):
        collection = db["encounters"]
        
        # Remove department and specialty from provider
        result = await collection.update_many(
            {},
            {"$unset": {"provider.department": "", "provider.specialty": ""}}
        )
        logger.info(f"Removed provider department/specialty from {result.modified_count} encounters")


class MigrationManager:
    """Database migration manager"""
    
    def __init__(self):
        self.db = None
        self.migrations = [
            Migration001AddTimestamps(),
            Migration002AddFHIRSyncCollection(),
            Migration003AddWorkflowFields(),
            Migration004AddProviderInfo()
        ]
    
    async def initialize(self):
        """Initialize database connection"""
        self.db = await get_database()
        if not self.db:
            raise Exception("Failed to connect to database")
        
        # Ensure migrations collection exists
        if "migrations" not in await self.db.list_collection_names():
            await self.db.create_collection("migrations")
            await self.db["migrations"].create_index("version", unique=True)
            logger.info("Created migrations collection")
    
    async def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions"""
        migrations_collection = self.db["migrations"]
        applied = await migrations_collection.find({}, {"version": 1}).to_list(length=None)
        return [m["version"] for m in applied]
    
    async def record_migration(self, migration: Migration, operation: str):
        """Record migration application or rollback"""
        migrations_collection = self.db["migrations"]
        
        if operation == "up":
            await migrations_collection.insert_one({
                "version": migration.version,
                "description": migration.description,
                "applied_at": datetime.utcnow()
            })
        elif operation == "down":
            await migrations_collection.delete_one({"version": migration.version})
    
    async def migrate_up(self, target_version: str = None):
        """Apply migrations up to target version"""
        applied_versions = await self.get_applied_migrations()
        
        for migration in self.migrations:
            # Skip if already applied
            if migration.version in applied_versions:
                continue
            
            # Stop if we've reached target version
            if target_version and migration.version > target_version:
                break
            
            logger.info(f"Applying migration {migration.version}: {migration.description}")
            
            try:
                await migration.up(self.db)
                await self.record_migration(migration, "up")
                logger.info(f"Successfully applied migration {migration.version}")
            except Exception as e:
                logger.error(f"Failed to apply migration {migration.version}: {e}")
                raise
    
    async def migrate_down(self, target_version: str):
        """Rollback migrations down to target version"""
        applied_versions = await self.get_applied_migrations()
        
        # Sort migrations in reverse order for rollback
        migrations_to_rollback = [
            m for m in reversed(self.migrations)
            if m.version in applied_versions and m.version > target_version
        ]
        
        for migration in migrations_to_rollback:
            logger.info(f"Rolling back migration {migration.version}: {migration.description}")
            
            try:
                await migration.down(self.db)
                await self.record_migration(migration, "down")
                logger.info(f"Successfully rolled back migration {migration.version}")
            except Exception as e:
                logger.error(f"Failed to rollback migration {migration.version}: {e}")
                raise
    
    async def get_migration_status(self):
        """Get current migration status"""
        applied_versions = await self.get_applied_migrations()
        
        status = {
            "applied_migrations": [],
            "pending_migrations": [],
            "total_migrations": len(self.migrations)
        }
        
        for migration in self.migrations:
            migration_info = {
                "version": migration.version,
                "description": migration.description
            }
            
            if migration.version in applied_versions:
                status["applied_migrations"].append(migration_info)
            else:
                status["pending_migrations"].append(migration_info)
        
        return status
    
    async def reset_database(self):
        """Reset database by dropping all collections (DANGEROUS!)"""
        logger.warning("RESETTING DATABASE - This will delete all data!")
        
        collections = await self.db.list_collection_names()
        for collection_name in collections:
            if collection_name not in ["admin", "config"]:  # Preserve system collections
                await self.db.drop_collection(collection_name)
                logger.info(f"Dropped collection: {collection_name}")


async def run_migrations(operation: str = "up", target_version: str = None):
    """Run database migrations"""
    manager = MigrationManager()
    await manager.initialize()
    
    if operation == "up":
        await manager.migrate_up(target_version)
    elif operation == "down":
        if not target_version:
            raise ValueError("Target version required for down migration")
        await manager.migrate_down(target_version)
    elif operation == "status":
        status = await manager.get_migration_status()
        logger.info(f"Migration Status:")
        logger.info(f"Applied: {len(status['applied_migrations'])}")
        logger.info(f"Pending: {len(status['pending_migrations'])}")
        for migration in status["applied_migrations"]:
            logger.info(f"  ✓ {migration['version']}: {migration['description']}")
        for migration in status["pending_migrations"]:
            logger.info(f"  ○ {migration['version']}: {migration['description']}")
        return status
    elif operation == "reset":
        await manager.reset_database()
    else:
        raise ValueError(f"Unknown operation: {operation}")


if __name__ == "__main__":
    import sys
    import os
    import argparse
    
    # Add project root to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="Run DiagnoAssist database migrations")
    parser.add_argument("operation", choices=["up", "down", "status", "reset"], 
                       help="Migration operation to perform")
    parser.add_argument("--target", help="Target migration version")
    args = parser.parse_args()
    
    # Run migrations
    asyncio.run(run_migrations(args.operation, args.target))