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
    
    def update(self, obj_id: Union[UUID, str, int], update_data: Dict[str, Any]) -> Optional[ModelType]:
        """
        Update a record
        
        Args:
            obj_id: Record ID
            update_data: Dictionary of fields to update
            
        Returns:
            Updated model instance or None if failed
        """
        try:
            db_obj = self.get_by_id(obj_id)
            if not db_obj:
                logger.warning(f"{self.model.__name__} with ID {obj_id} not found")
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
            logger.error(f"Error updating {self.model.__name__} with ID {obj_id}: {str(e)}")
            return None
    
    def delete(self, obj_id: Union[UUID, str, int]) -> bool:
        """
        Delete a record
        
        Args:
            obj_id: Record ID
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            db_obj = self.get_by_id(obj_id)
            if not db_obj:
                logger.warning(f"{self.model.__name__} with ID {obj_id} not found")
                return False
                
            self.db.delete(db_obj)
            self.db.commit()
            
            logger.info(f"Deleted {self.model.__name__} with ID: {obj_id}")
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting {self.model.__name__} with ID {obj_id}: {str(e)}")
            return False
    
    def count(self) -> int:
        """
        Count total records
        
        Returns:
            Total number of records
        """
        try:
            return self.db.query(self.model).count()
        except SQLAlchemyError as e:
            logger.error(f"Error counting {self.model.__name__}: {str(e)}")
            return 0
    
    def exists(self, obj_id: Union[UUID, str, int]) -> bool:
        """
        Check if record exists
        
        Args:
            obj_id: Record ID
            
        Returns:
            True if record exists, False otherwise
        """
        try:
            return self.db.query(self.model).filter(self.model.id == obj_id).first() is not None
        except SQLAlchemyError as e:
            logger.error(f"Error checking existence of {self.model.__name__} with ID {obj_id}: {str(e)}")
            return False
    
    def filter_by(self, **filters) -> List[ModelType]:
        """
        Filter records by field values
        
        Args:
            **filters: Field-value pairs to filter by
            
        Returns:
            List of matching model instances
        """
        try:
            query = self.db.query(self.model)
            
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)
                    
            return query.all()
            
        except SQLAlchemyError as e:
            logger.error(f"Error filtering {self.model.__name__}: {str(e)}")
            return []