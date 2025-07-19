"""
Base repository class for DiagnoAssist Backend
"""
from typing import TypeVar, Generic, List, Optional, Dict, Any
from abc import ABC, abstractmethod
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
import uuid

from app.core.database import get_database
from app.core.exceptions import NotFoundError, DatabaseException

T = TypeVar('T')


class BaseRepository(Generic[T], ABC):
    """Base repository class with common CRUD operations"""
    
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self._collection: Optional[AsyncIOMotorCollection] = None
    
    async def get_collection(self) -> AsyncIOMotorCollection:
        """Get MongoDB collection"""
        if not self._collection:
            db = await get_database()
            self._collection = db[self.collection_name]
        return self._collection
    
    @abstractmethod
    def _to_dict(self, entity: T) -> Dict[str, Any]:
        """Convert entity to dictionary for MongoDB storage"""
        pass
    
    @abstractmethod
    def _from_dict(self, data: Dict[str, Any]) -> T:
        """Convert dictionary from MongoDB to entity"""
        pass
    
    @abstractmethod
    def _get_entity_name(self) -> str:
        """Get entity name for error messages"""
        pass
    
    def _generate_id(self) -> str:
        """Generate unique ID for entity"""
        return str(uuid.uuid4())
    
    def _prepare_for_storage(self, entity: T) -> Dict[str, Any]:
        """Prepare entity for MongoDB storage"""
        data = self._to_dict(entity)
        
        # Ensure timestamps are set
        now = datetime.utcnow()
        if 'created_at' not in data or not data['created_at']:
            data['created_at'] = now
        data['updated_at'] = now
        
        # Generate ID if not present
        if not data.get('id'):
            data['id'] = self._generate_id()
        
        return data
    
    async def create(self, entity: T) -> T:
        """Create a new entity"""
        try:
            collection = await self.get_collection()
            data = self._prepare_for_storage(entity)
            
            # Insert into MongoDB
            result = await collection.insert_one(data)
            
            if result.inserted_id:
                # Retrieve the created entity
                created_data = await collection.find_one({"_id": result.inserted_id})
                return self._from_dict(created_data)
            else:
                raise DatabaseException(
                    f"Failed to create {self._get_entity_name()}",
                    "create"
                )
                
        except Exception as e:
            if isinstance(e, DatabaseException):
                raise
            raise DatabaseException(
                f"Database error while creating {self._get_entity_name()}: {str(e)}",
                "create"
            )
    
    async def get_by_id(self, entity_id: str) -> Optional[T]:
        """Get entity by ID"""
        try:
            collection = await self.get_collection()
            data = await collection.find_one({"id": entity_id})
            
            if data:
                return self._from_dict(data)
            return None
            
        except Exception as e:
            raise DatabaseException(
                f"Database error while retrieving {self._get_entity_name()}: {str(e)}",
                "read"
            )
    
    async def get_by_field(self, field: str, value: Any) -> Optional[T]:
        """Get entity by specific field"""
        try:
            collection = await self.get_collection()
            data = await collection.find_one({field: value})
            
            if data:
                return self._from_dict(data)
            return None
            
        except Exception as e:
            raise DatabaseException(
                f"Database error while retrieving {self._get_entity_name()} by {field}: {str(e)}",
                "read"
            )
    
    async def get_all(
        self, 
        filter_dict: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 50,
        sort_field: str = "created_at",
        sort_direction: int = -1
    ) -> List[T]:
        """Get all entities with filtering, pagination, and sorting"""
        try:
            collection = await self.get_collection()
            
            # Build query
            query = filter_dict or {}
            
            # Execute query with pagination and sorting
            cursor = collection.find(query).sort(sort_field, sort_direction).skip(skip).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            return [self._from_dict(doc) for doc in documents]
            
        except Exception as e:
            raise DatabaseException(
                f"Database error while retrieving {self._get_entity_name()} list: {str(e)}",
                "read"
            )
    
    async def count(self, filter_dict: Optional[Dict[str, Any]] = None) -> int:
        """Count entities with optional filtering"""
        try:
            collection = await self.get_collection()
            query = filter_dict or {}
            return await collection.count_documents(query)
            
        except Exception as e:
            raise DatabaseException(
                f"Database error while counting {self._get_entity_name()}: {str(e)}",
                "read"
            )
    
    async def update(self, entity_id: str, entity: T) -> T:
        """Update an existing entity"""
        try:
            collection = await self.get_collection()
            
            # Check if entity exists
            existing = await collection.find_one({"id": entity_id})
            if not existing:
                raise NotFoundError(self._get_entity_name(), entity_id)
            
            # Prepare update data
            data = self._prepare_for_storage(entity)
            data['id'] = entity_id  # Ensure ID doesn't change
            
            # Update in MongoDB
            result = await collection.replace_one({"id": entity_id}, data)
            
            if result.modified_count > 0 or result.matched_count > 0:
                return self._from_dict(data)
            else:
                raise DatabaseException(
                    f"Failed to update {self._get_entity_name()}",
                    "update"
                )
                
        except Exception as e:
            if isinstance(e, (NotFoundError, DatabaseException)):
                raise
            raise DatabaseException(
                f"Database error while updating {self._get_entity_name()}: {str(e)}",
                "update"
            )
    
    async def update_fields(self, entity_id: str, update_fields: Dict[str, Any]) -> T:
        """Update specific fields of an entity"""
        try:
            collection = await self.get_collection()
            
            # Check if entity exists
            existing = await collection.find_one({"id": entity_id})
            if not existing:
                raise NotFoundError(self._get_entity_name(), entity_id)
            
            # Add updated_at timestamp
            update_fields['updated_at'] = datetime.utcnow()
            
            # Update in MongoDB
            result = await collection.update_one(
                {"id": entity_id},
                {"$set": update_fields}
            )
            
            if result.modified_count > 0:
                # Retrieve updated entity
                updated_data = await collection.find_one({"id": entity_id})
                return self._from_dict(updated_data)
            else:
                # Return existing entity if no changes
                return self._from_dict(existing)
                
        except Exception as e:
            if isinstance(e, (NotFoundError, DatabaseException)):
                raise
            raise DatabaseException(
                f"Database error while updating {self._get_entity_name()} fields: {str(e)}",
                "update"
            )
    
    async def delete(self, entity_id: str) -> bool:
        """Delete an entity"""
        try:
            collection = await self.get_collection()
            
            # Check if entity exists
            existing = await collection.find_one({"id": entity_id})
            if not existing:
                raise NotFoundError(self._get_entity_name(), entity_id)
            
            # Delete from MongoDB
            result = await collection.delete_one({"id": entity_id})
            
            return result.deleted_count > 0
            
        except Exception as e:
            if isinstance(e, (NotFoundError, DatabaseException)):
                raise
            raise DatabaseException(
                f"Database error while deleting {self._get_entity_name()}: {str(e)}",
                "delete"
            )
    
    async def exists(self, entity_id: str) -> bool:
        """Check if entity exists"""
        try:
            collection = await self.get_collection()
            count = await collection.count_documents({"id": entity_id}, limit=1)
            return count > 0
            
        except Exception as e:
            raise DatabaseException(
                f"Database error while checking {self._get_entity_name()} existence: {str(e)}",
                "read"
            )
    
    async def find_by_ids(self, entity_ids: List[str]) -> List[T]:
        """Find multiple entities by their IDs"""
        try:
            collection = await self.get_collection()
            cursor = collection.find({"id": {"$in": entity_ids}})
            documents = await cursor.to_list(length=len(entity_ids))
            
            return [self._from_dict(doc) for doc in documents]
            
        except Exception as e:
            raise DatabaseException(
                f"Database error while retrieving {self._get_entity_name()} by IDs: {str(e)}",
                "read"
            )