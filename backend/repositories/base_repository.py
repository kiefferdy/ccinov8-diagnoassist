"""
Base Repository for DiagnoAssist
Provides common CRUD operations for all models
"""

from typing import Generic, TypeVar, Type, List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, desc, asc, func
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

# Generic type for SQLAlchemy models
ModelType = TypeVar("ModelType")

class BaseRepository(Generic[ModelType]):
    """
    Base repository class providing common CRUD operations
    """
    
    def __init__(self, model: Type[ModelType], db: Session):
        """
        Initialize repository with model type and database session
        
        Args:
            model: SQLAlchemy model class
            db: Database session
        """
        self.model = model
        self.db = db
    
    def create(self, obj_data: Union[Dict[str, Any], ModelType]) -> Optional[ModelType]:
        """
        Create a new record
        
        Args:
            obj_data: Dictionary of data or model instance
            
        Returns:
            Created model instance or None if failed
        """
        try:
            if isinstance(obj_data, dict):
                db_obj = self.model(**obj_data)
            else:
                db_obj = obj_data
                
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            
            logger.info(f"Created {self.model.__name__} with ID: {db_obj.id}")
            return db_obj
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error creating {self.model.__name__}: {str(e)}")
            return None
    
    def get_by_id(self, obj_id: Union[UUID, str, int]) -> Optional[ModelType]:
        """
        Get record by ID
        
        Args:
            obj_id: Record ID
            
        Returns:
            Model instance or None if not found
        """
        try:
            return self.db.query(self.model).filter(self.model.id == obj_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model.__name__} by ID {obj_id}: {str(e)}")
            return None
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Get all records with pagination
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of model instances
        """
        try:
            return self.db.query(self.model).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting all {self.model.__name__}: {str(e)}")
            return []
    
    def get_by_filter(self, filters: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Get records by filter criteria
        
        Args:
            filters: Dictionary of field:value filters
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of model instances matching filters
        """
        try:
            query = self.db.query(self.model)
            
            for field, value in filters.items():
                if hasattr(self.model, field):
                    if isinstance(value, list):
                        # Handle IN queries for lists
                        query = query.filter(getattr(self.model, field).in_(value))
                    elif isinstance(value, dict):
                        # Handle special operators like gt, lt, like, etc.
                        for op, val in value.items():
                            column = getattr(self.model, field)
                            if op == 'gt':
                                query = query.filter(column > val)
                            elif op == 'gte':
                                query = query.filter(column >= val)
                            elif op == 'lt':
                                query = query.filter(column < val)
                            elif op == 'lte':
                                query = query.filter(column <= val)
                            elif op == 'like':
                                query = query.filter(column.like(f'%{val}%'))
                            elif op == 'ilike':
                                query = query.filter(column.ilike(f'%{val}%'))
                            elif op == 'ne':
                                query = query.filter(column != val)
                    else:
                        # Simple equality filter
                        query = query.filter(getattr(self.model, field) == value)
            
            return query.offset(skip).limit(limit).all()
            
        except SQLAlchemyError as e:
            logger.error(f"Error filtering {self.model.__name__}: {str(e)}")
            return []
    
    def update(self, obj_id: Union[UUID, str, int], update_data: Dict[str, Any]) -> Optional[ModelType]:
        """
        Update record by ID
        
        Args:
            obj_id: Record ID
            update_data: Dictionary of fields to update
            
        Returns:
            Updated model instance or None if failed
        """
        try:
            db_obj = self.get_by_id(obj_id)
            if not db_obj:
                logger.warning(f"{self.model.__name__} with ID {obj_id} not found for update")
                return None
            
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            
            self.db.commit()
            self.db.refresh(db_obj)
            
            logger.info(f"Updated {self.model.__name__} with ID: {obj_id}")
            return db_obj
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating {self.model.__name__} {obj_id}: {str(e)}")
            return None
    
    def delete(self, obj_id: Union[UUID, str, int]) -> bool:
        """
        Delete record by ID
        
        Args:
            obj_id: Record ID
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            db_obj = self.get_by_id(obj_id)
            if not db_obj:
                logger.warning(f"{self.model.__name__} with ID {obj_id} not found for deletion")
                return False
            
            self.db.delete(db_obj)
            self.db.commit()
            
            logger.info(f"Deleted {self.model.__name__} with ID: {obj_id}")
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting {self.model.__name__} {obj_id}: {str(e)}")
            return False
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records with optional filters
        
        Args:
            filters: Optional dictionary of field:value filters
            
        Returns:
            Number of records matching criteria
        """
        try:
            query = self.db.query(func.count(self.model.id))
            
            if filters:
                for field, value in filters.items():
                    if hasattr(self.model, field):
                        query = query.filter(getattr(self.model, field) == value)
            
            return query.scalar()
            
        except SQLAlchemyError as e:
            logger.error(f"Error counting {self.model.__name__}: {str(e)}")
            return 0
    
    def exists(self, obj_id: Union[UUID, str, int]) -> bool:
        """
        Check if record exists by ID
        
        Args:
            obj_id: Record ID
            
        Returns:
            True if record exists, False otherwise
        """
        try:
            return self.db.query(self.model.id).filter(self.model.id == obj_id).first() is not None
        except SQLAlchemyError as e:
            logger.error(f"Error checking existence of {self.model.__name__} {obj_id}: {str(e)}")
            return False
    
    def bulk_create(self, objects_data: List[Union[Dict[str, Any], ModelType]]) -> List[ModelType]:
        """
        Create multiple records in bulk
        
        Args:
            objects_data: List of dictionaries or model instances
            
        Returns:
            List of created model instances
        """
        try:
            db_objects = []
            for obj_data in objects_data:
                if isinstance(obj_data, dict):
                    db_obj = self.model(**obj_data)
                else:
                    db_obj = obj_data
                db_objects.append(db_obj)
            
            self.db.add_all(db_objects)
            self.db.commit()
            
            for db_obj in db_objects:
                self.db.refresh(db_obj)
            
            logger.info(f"Created {len(db_objects)} {self.model.__name__} records")
            return db_objects
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error bulk creating {self.model.__name__}: {str(e)}")
            return []
    
    def get_or_create(self, defaults: Optional[Dict[str, Any]] = None, **kwargs) -> tuple[ModelType, bool]:
        """
        Get existing record or create new one
        
        Args:
            defaults: Default values for creation if not found
            **kwargs: Filter criteria for finding existing record
            
        Returns:
            Tuple of (model_instance, created_flag)
        """
        try:
            # Try to find existing record
            query = self.db.query(self.model)
            for field, value in kwargs.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)
            
            instance = query.first()
            
            if instance:
                return instance, False
            
            # Create new record
            create_data = kwargs.copy()
            if defaults:
                create_data.update(defaults)
                
            instance = self.create(create_data)
            return instance, True
            
        except SQLAlchemyError as e:
            logger.error(f"Error in get_or_create for {self.model.__name__}: {str(e)}")
            return None, False