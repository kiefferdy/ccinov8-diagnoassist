"""
Database initialization script for DiagnoAssist Backend
"""
import asyncio
import logging
from typing import Dict, List

from app.core.database import get_database

logger = logging.getLogger(__name__)


class DatabaseInitializer:
    """Database initialization and migration manager"""
    
    def __init__(self):
        self.db = None
    
    async def initialize(self):
        """Initialize database connection"""
        self.db = await get_database()
        if not self.db:
            raise Exception("Failed to connect to database")
        
        logger.info("Database connection established")
    
    async def create_collections(self):
        """Create database collections with proper settings"""
        collections = [
            "patients",
            "episodes", 
            "encounters",
            "users",
            "fhir_sync_status"
        ]
        
        existing_collections = await self.db.list_collection_names()
        
        for collection_name in collections:
            if collection_name not in existing_collections:
                await self.db.create_collection(collection_name)
                logger.info(f"Created collection: {collection_name}")
            else:
                logger.info(f"Collection already exists: {collection_name}")
    
    async def create_indexes(self):
        """Create database indexes for performance optimization"""
        
        # Patient indexes
        patient_indexes = [
            {"keys": [("id", 1)], "name": "patient_id_idx", "unique": True},
            {"keys": [("demographics.email", 1)], "name": "patient_email_idx", "unique": True, "sparse": True},
            {"keys": [("demographics.name", "text")], "name": "patient_name_text_idx"},
            {"keys": [("demographics.phone", 1)], "name": "patient_phone_idx", "sparse": True},
            {"keys": [("created_at", -1)], "name": "patient_created_desc_idx"},
            {"keys": [("demographics.date_of_birth", 1)], "name": "patient_dob_idx", "sparse": True}
        ]
        
        await self._create_collection_indexes("patients", patient_indexes)
        
        # Episode indexes
        episode_indexes = [
            {"keys": [("id", 1)], "name": "episode_id_idx", "unique": True},
            {"keys": [("patient_id", 1)], "name": "episode_patient_idx"},
            {"keys": [("status", 1)], "name": "episode_status_idx"},
            {"keys": [("category", 1)], "name": "episode_category_idx"},
            {"keys": [("created_at", -1)], "name": "episode_created_desc_idx"},
            {"keys": [("patient_id", 1), ("status", 1)], "name": "episode_patient_status_idx"},
            {"keys": [("patient_id", 1), ("created_at", -1)], "name": "episode_patient_created_idx"},
            {"keys": [("tags", 1)], "name": "episode_tags_idx", "sparse": True}
        ]
        
        await self._create_collection_indexes("episodes", episode_indexes)
        
        # Encounter indexes
        encounter_indexes = [
            {"keys": [("id", 1)], "name": "encounter_id_idx", "unique": True},
            {"keys": [("patient_id", 1)], "name": "encounter_patient_idx"},
            {"keys": [("episode_id", 1)], "name": "encounter_episode_idx", "sparse": True},
            {"keys": [("status", 1)], "name": "encounter_status_idx"},
            {"keys": [("type", 1)], "name": "encounter_type_idx"},
            {"keys": [("created_at", -1)], "name": "encounter_created_desc_idx"},
            {"keys": [("signed_at", -1)], "name": "encounter_signed_desc_idx", "sparse": True},
            {"keys": [("patient_id", 1), ("status", 1)], "name": "encounter_patient_status_idx"},
            {"keys": [("patient_id", 1), ("created_at", -1)], "name": "encounter_patient_created_idx"},
            {"keys": [("episode_id", 1), ("status", 1)], "name": "encounter_episode_status_idx", "sparse": True},
            {"keys": [("episode_id", 1), ("created_at", -1)], "name": "encounter_episode_created_idx", "sparse": True},
            {"keys": [("provider.id", 1)], "name": "encounter_provider_idx"},
            {"keys": [("signed_by", 1)], "name": "encounter_signed_by_idx", "sparse": True}
        ]
        
        await self._create_collection_indexes("encounters", encounter_indexes)
        
        # User indexes
        user_indexes = [
            {"keys": [("id", 1)], "name": "user_id_idx", "unique": True},
            {"keys": [("email", 1)], "name": "user_email_idx", "unique": True},
            {"keys": [("role", 1)], "name": "user_role_idx"},
            {"keys": [("status", 1)], "name": "user_status_idx"},
            {"keys": [("is_verified", 1)], "name": "user_verified_idx"},
            {"keys": [("profile.last_name", 1)], "name": "user_last_name_idx", "sparse": True},
            {"keys": [("profile.department", 1)], "name": "user_department_idx", "sparse": True},
            {"keys": [("profile.specialty", 1)], "name": "user_specialty_idx", "sparse": True},
            {"keys": [("created_at", -1)], "name": "user_created_desc_idx"},
            {"keys": [("last_login", -1)], "name": "user_last_login_desc_idx", "sparse": True}
        ]
        
        await self._create_collection_indexes("users", user_indexes)
        
        # FHIR sync status indexes
        fhir_sync_indexes = [
            {"keys": [("entity_id", 1), ("entity_type", 1)], "name": "fhir_sync_entity_idx", "unique": True},
            {"keys": [("entity_type", 1)], "name": "fhir_sync_type_idx"},
            {"keys": [("sync_status", 1)], "name": "fhir_sync_status_idx"},
            {"keys": [("last_sync", -1)], "name": "fhir_sync_last_sync_desc_idx", "sparse": True},
            {"keys": [("fhir_id", 1)], "name": "fhir_sync_fhir_id_idx", "sparse": True},
            {"keys": [("entity_type", 1), ("sync_status", 1)], "name": "fhir_sync_type_status_idx"}
        ]
        
        await self._create_collection_indexes("fhir_sync_status", fhir_sync_indexes)
    
    async def _create_collection_indexes(self, collection_name: str, indexes: List[Dict]):
        """Create indexes for a specific collection"""
        collection = self.db[collection_name]
        
        # Get existing indexes
        existing_indexes = await collection.list_indexes().to_list(length=None)
        existing_names = {idx.get("name") for idx in existing_indexes}
        
        for index_def in indexes:
            index_name = index_def["name"]
            if index_name not in existing_names:
                try:
                    keys = index_def["keys"]
                    options = {k: v for k, v in index_def.items() if k not in ["keys", "name"]}
                    options["name"] = index_name
                    
                    await collection.create_index(keys, **options)
                    logger.info(f"Created index {index_name} on {collection_name}")
                except Exception as e:
                    logger.error(f"Failed to create index {index_name} on {collection_name}: {e}")
            else:
                logger.info(f"Index {index_name} already exists on {collection_name}")
    
    async def setup_database_constraints(self):
        """Set up additional database constraints and validation"""
        
        # Patient collection validation
        patient_validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["id", "demographics", "created_at"],
                "properties": {
                    "id": {"bsonType": "string"},
                    "demographics": {
                        "bsonType": "object",
                        "required": ["name"],
                        "properties": {
                            "name": {"bsonType": "string", "minLength": 1},
                            "email": {"bsonType": "string"},
                            "phone": {"bsonType": "string"}
                        }
                    },
                    "created_at": {"bsonType": "date"},
                    "updated_at": {"bsonType": "date"}
                }
            }
        }
        
        # User collection validation
        user_validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["id", "email", "hashed_password", "role", "created_at"],
                "properties": {
                    "id": {"bsonType": "string"},
                    "email": {"bsonType": "string", "minLength": 5},
                    "hashed_password": {"bsonType": "string", "minLength": 10},
                    "role": {"enum": ["admin", "doctor", "nurse", "assistant"]},
                    "status": {"enum": ["active", "inactive", "suspended", "pending_verification"]},
                    "is_verified": {"bsonType": "bool"},
                    "created_at": {"bsonType": "date"},
                    "updated_at": {"bsonType": "date"}
                }
            }
        }
        
        validators = {
            "patients": patient_validator,
            "users": user_validator
        }
        
        for collection_name, validator in validators.items():
            try:
                await self.db.command("collMod", collection_name, validator=validator)
                logger.info(f"Set up validation for {collection_name}")
            except Exception as e:
                logger.warning(f"Failed to set up validation for {collection_name}: {e}")
    
    async def create_admin_user(self):
        """Create default admin user if none exists"""
        from app.models.auth import UserModel, UserProfile, UserRoleEnum, UserStatusEnum
        from app.core.security import get_password_hash
        from app.repositories.user_repository import user_repository
        
        # Check if any admin users exist
        existing_admins = await user_repository.get_by_role(UserRoleEnum.ADMIN)
        
        if not existing_admins:
            # Create default admin user
            admin_user = UserModel(
                email="admin@diagnoassist.com",
                hashed_password=get_password_hash("admin123"),  # Change in production!
                role=UserRoleEnum.ADMIN,
                status=UserStatusEnum.ACTIVE,
                profile=UserProfile(
                    first_name="System",
                    last_name="Administrator",
                    department="IT",
                    specialty="System Administration"
                ),
                is_verified=True
            )
            
            created_admin = await user_repository.create(admin_user)
            logger.info(f"Created default admin user: {created_admin.email}")
            logger.warning("IMPORTANT: Change the default admin password in production!")
        else:
            logger.info("Admin user already exists")
    
    async def verify_database_health(self):
        """Verify database health and configuration"""
        try:
            # Check connection
            server_info = await self.db.command("serverStatus")
            logger.info(f"Database server version: {server_info.get('version', 'Unknown')}")
            
            # Check collections
            collections = await self.db.list_collection_names()
            logger.info(f"Available collections: {', '.join(collections)}")
            
            # Check indexes
            for collection_name in ["patients", "episodes", "encounters", "users"]:
                if collection_name in collections:
                    collection = self.db[collection_name]
                    indexes = await collection.list_indexes().to_list(length=None)
                    logger.info(f"{collection_name} has {len(indexes)} indexes")
            
            # Test basic operations
            test_collection = self.db["_health_check"]
            test_doc = {"test": True, "timestamp": "2024-01-01T00:00:00Z"}
            
            # Insert
            result = await test_collection.insert_one(test_doc)
            assert result.inserted_id
            
            # Read
            found_doc = await test_collection.find_one({"_id": result.inserted_id})
            assert found_doc["test"] is True
            
            # Delete
            await test_collection.delete_one({"_id": result.inserted_id})
            
            logger.info("Database health check passed")
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            raise
    
    async def run_full_initialization(self):
        """Run complete database initialization"""
        logger.info("Starting database initialization...")
        
        try:
            # Initialize connection
            await self.initialize()
            
            # Create collections
            await self.create_collections()
            
            # Create indexes
            await self.create_indexes()
            
            # Set up constraints
            await self.setup_database_constraints()
            
            # Create admin user
            await self.create_admin_user()
            
            # Verify health
            await self.verify_database_health()
            
            logger.info("Database initialization completed successfully!")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise


async def init_database():
    """Initialize database with proper setup"""
    initializer = DatabaseInitializer()
    await initializer.run_full_initialization()


if __name__ == "__main__":
    import sys
    import os
    
    # Add project root to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Run initialization
    asyncio.run(init_database())