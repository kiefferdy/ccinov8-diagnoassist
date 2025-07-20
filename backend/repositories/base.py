from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from uuid import uuid4
from datetime import datetime
import logging

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")

logger = logging.getLogger(__name__)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType], ABC):
    """
    Base repository with common CRUD operations
    """
    
    def __init__(self, model: type[ModelType], db: Session):
        """
        Initialize repository with model and database session
        
        Args:
            model: SQLAlchemy model class
            db: Database session
        """
        self.model = model
        self.db = db
    
    def get(self, id: str) -> Optional[ModelType]:
        """
        Get single record by ID
        
        Args:
            id: Record identifier
            
        Returns:
            Model instance or None
        """
        try:
            return self.db.query(self.model).filter(self.model.id == id).first()
        except Exception as e:
            logger.error(f"Error getting {self.model.__name__} with id {id}: {str(e)}")
            raise
    
    def get_many(self, ids: List[str]) -> List[ModelType]:
        """
        Get multiple records by IDs
        
        Args:
            ids: List of record identifiers
            
        Returns:
            List of model instances
        """
        try:
            return self.db.query(self.model).filter(self.model.id.in_(ids)).all()
        except Exception as e:
            logger.error(f"Error getting multiple {self.model.__name__} records: {str(e)}")
            raise
    
    def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ) -> List[ModelType]:
        """
        Get all records with pagination and ordering
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field to order by
            order_desc: Whether to order in descending order
            
        Returns:
            List of model instances
        """
        try:
            query = self.db.query(self.model)
            
            # Apply ordering
            if order_by and hasattr(self.model, order_by):
                order_field = getattr(self.model, order_by)
                if order_desc:
                    query = query.order_by(desc(order_field))
                else:
                    query = query.order_by(asc(order_field))
            
            return query.offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting all {self.model.__name__} records: {str(e)}")
            raise
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records with optional filters
        
        Args:
            filters: Dictionary of field filters
            
        Returns:
            Number of records
        """
        try:
            query = self.db.query(self.model)
            
            if filters:
                conditions = []
                for field, value in filters.items():
                    if hasattr(self.model, field):
                        conditions.append(getattr(self.model, field) == value)
                if conditions:
                    query = query.filter(and_(*conditions))
            
            return query.count()
        except Exception as e:
            logger.error(f"Error counting {self.model.__name__} records: {str(e)}")
            raise
    
    def create(self, obj_in: CreateSchemaType) -> ModelType:
        """
        Create new record
        
        Args:
            obj_in: Creation schema or dictionary
            
        Returns:
            Created model instance
        """
        try:
            # Convert Pydantic model to dict if needed
            if hasattr(obj_in, 'dict'):
                obj_data = obj_in.dict(exclude_unset=True)
            else:
                obj_data = obj_in
            
            # Generate ID if not provided
            if 'id' not in obj_data or not obj_data['id']:
                obj_data['id'] = str(uuid4())
            
            # Set timestamps
            now = datetime.utcnow()
            obj_data['created_at'] = now
            obj_data['updated_at'] = now
            
            db_obj = self.model(**obj_data)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            
            logger.info(f"Created {self.model.__name__} with id: {db_obj.id}")
            return db_obj
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating {self.model.__name__}: {str(e)}")
            raise
    
    def update(self, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        """
        Update existing record
        
        Args:
            db_obj: Existing model instance
            obj_in: Update schema or dictionary
            
        Returns:
            Updated model instance
        """
        try:
            # Convert Pydantic model to dict if needed
            if hasattr(obj_in, 'dict'):
                obj_data = obj_in.dict(exclude_unset=True)
            else:
                obj_data = obj_in
            
            # Update fields
            for field, value in obj_data.items():
                if hasattr(db_obj, field) and field != 'id':
                    setattr(db_obj, field, value)
            
            # Update timestamp
            db_obj.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(db_obj)
            
            logger.info(f"Updated {self.model.__name__} with id: {db_obj.id}")
            return db_obj
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating {self.model.__name__}: {str(e)}")
            raise
    
    def delete(self, id: str) -> bool:
        """
        Delete record by ID
        
        Args:
            id: Record identifier
            
        Returns:
            True if deleted, False if not found
        """
        try:
            obj = self.get(id)
            if obj:
                self.db.delete(obj)
                self.db.commit()
                logger.info(f"Deleted {self.model.__name__} with id: {id}")
                return True
            return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting {self.model.__name__} with id {id}: {str(e)}")
            raise
    
    def exists(self, id: str) -> bool:
        """
        Check if record exists by ID
        
        Args:
            id: Record identifier
            
        Returns:
            True if exists, False otherwise
        """
        try:
            return self.db.query(self.model).filter(self.model.id == id).first() is not None
        except Exception as e:
            logger.error(f"Error checking existence of {self.model.__name__} with id {id}: {str(e)}")
            raise
    
    def search(
        self, 
        filters: Dict[str, Any], 
        skip: int = 0, 
        limit: int = 100
    ) -> List[ModelType]:
        """
        Search records with filters
        
        Args:
            filters: Dictionary of field filters
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching model instances
        """
        try:
            query = self.db.query(self.model)
            
            conditions = []
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    field_attr = getattr(self.model, field)
                    
                    # Handle different filter types
                    if isinstance(value, str) and value.startswith('%') and value.endswith('%'):
                        # LIKE search
                        conditions.append(field_attr.like(value))
                    elif isinstance(value, list):
                        # IN search
                        conditions.append(field_attr.in_(value))
                    else:
                        # Exact match
                        conditions.append(field_attr == value)
            
            if conditions:
                query = query.filter(and_(*conditions))
            
            return query.offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error searching {self.model.__name__} records: {str(e)}")
            raise