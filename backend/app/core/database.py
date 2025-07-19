"""
Database connection and management for DiagnoAssist Backend
"""
import asyncio
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """MongoDB database manager using Motor (async MongoDB driver)"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self._connection_attempts = 0
        self._max_connection_attempts = 3
    
    async def connect(self) -> bool:
        """Connect to MongoDB database"""
        try:
            self._connection_attempts += 1
            
            # Create MongoDB client
            self.client = AsyncIOMotorClient(
                settings.mongodb_uri,
                maxPoolSize=10,
                minPoolSize=1,
                maxIdleTimeMS=30000,
                retryWrites=True,
                w="majority"
            )
            
            # Get database
            self.database = self.client[settings.mongodb_database]
            
            # Test connection
            await self.client.admin.command('ping')
            
            logger.info(f"Successfully connected to MongoDB database: {settings.mongodb_database}")
            
            # Create indexes after connection
            await self._create_indexes()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB (attempt {self._connection_attempts}): {e}")
            
            if self._connection_attempts < self._max_connection_attempts:
                logger.info("Retrying connection in 5 seconds...")
                await asyncio.sleep(5)
                return await self.connect()
            else:
                logger.error("Max connection attempts reached. Database connection failed.")
                return False
    
    async def disconnect(self):
        """Disconnect from MongoDB database"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB database")
    
    async def _create_indexes(self):
        """Create database indexes for performance optimization"""
        try:
            # Patients collection indexes
            patients_collection = self.database.patients
            await patients_collection.create_index("id", unique=True)
            await patients_collection.create_index("demographics.email")
            await patients_collection.create_index("fhir_patient_id")
            await patients_collection.create_index("created_at")
            
            # Episodes collection indexes
            episodes_collection = self.database.episodes
            await episodes_collection.create_index("id", unique=True)
            await episodes_collection.create_index([("patient_id", 1), ("status", 1)])
            await episodes_collection.create_index("created_at")
            await episodes_collection.create_index("tags")
            
            # Encounters collection indexes
            encounters_collection = self.database.encounters
            await encounters_collection.create_index("id", unique=True)
            await encounters_collection.create_index("episode_id")
            await encounters_collection.create_index([("patient_id", 1), ("status", 1)])
            await encounters_collection.create_index("created_at")
            await encounters_collection.create_index("signed_at")
            await encounters_collection.create_index("fhir_encounter_id")
            
            # Users collection indexes (for auth)
            users_collection = self.database.users
            await users_collection.create_index("id", unique=True)
            await users_collection.create_index("email", unique=True)
            await users_collection.create_index("role")
            await users_collection.create_index("status")
            await users_collection.create_index("created_at")
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating database indexes: {e}")
    
    async def get_collection(self, collection_name: str):
        """Get a collection from the database"""
        if not self.database:
            raise Exception("Database not connected")
        return self.database[collection_name]
    
    async def health_check(self) -> dict:
        """Check database health"""
        try:
            if not self.client:
                return {"status": "disconnected", "error": "No database connection"}
            
            # Test connection
            result = await self.client.admin.command('ping')
            
            # Get database stats
            stats = await self.database.command("dbStats")
            
            return {
                "status": "connected",
                "database": settings.mongodb_database,
                "collections": stats.get("collections", 0),
                "data_size": stats.get("dataSize", 0),
                "index_size": stats.get("indexSize", 0),
                "ping_result": result
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}


# Create global database manager instance
db_manager = DatabaseManager()


async def get_database() -> AsyncIOMotorDatabase:
    """Dependency to get database instance"""
    if not db_manager.database:
        raise Exception("Database not connected")
    return db_manager.database


async def init_database():
    """Initialize database connection"""
    success = await db_manager.connect()
    if not success:
        raise Exception("Failed to initialize database connection")
    return db_manager.database


async def close_database():
    """Close database connection"""
    await db_manager.disconnect()