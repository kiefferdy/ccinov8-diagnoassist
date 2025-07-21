"""
Template Repository for DiagnoAssist Backend

Handles data access operations for templates including:
- CRUD operations for templates
- Template searching and filtering
- Template usage tracking
- Template sharing and permissions
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection

from app.repositories.base_repository import BaseRepository
from app.models.template import (
    TemplateModel, TemplateCreateRequest, TemplateUpdateRequest, 
    TemplateSearchRequest, TemplateUsageStats, TemplateScope,
    TemplateType, TemplateCategory
)
from app.models.auth import UserModel, UserRole
from app.core.exceptions import NotFoundError, ValidationException, PermissionDeniedError

logger = logging.getLogger(__name__)


class TemplateRepository(BaseRepository[TemplateModel]):
    """Repository for template data operations"""
    
    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection, TemplateModel)
        self.collection = collection
    
    async def create_template(
        self,
        template_data: TemplateCreateRequest,
        user: UserModel
    ) -> TemplateModel:
        """
        Create a new template
        
        Args:
            template_data: Template creation data
            user: User creating the template
            
        Returns:
            Created template
        """
        try:
            # Generate template ID
            template_id = str(ObjectId())
            
            # Create template metadata
            from app.models.template import TemplateMetadata
            metadata = TemplateMetadata(
                created_by=user.id,
                created_at=datetime.utcnow(),
                version=1
            )
            
            # Create template model
            template = TemplateModel(
                id=template_id,
                **template_data.model_dump(),
                owner_id=user.id,
                metadata=metadata
            )
            
            # Insert into database
            document = self._model_to_document(template)
            result = await self.collection.insert_one(document)
            
            # Get created template
            created_template = await self.get_by_id(str(result.inserted_id))
            
            logger.info(f"Created template {template_id} by user {user.id}")
            return created_template
            
        except Exception as e:
            logger.error(f"Failed to create template: {e}")
            raise
    
    async def get_template_by_id(
        self,
        template_id: str,
        user: UserModel
    ) -> Optional[TemplateModel]:
        """
        Get template by ID with permission check
        
        Args:
            template_id: Template ID
            user: User requesting the template
            
        Returns:
            Template if found and accessible
        """
        try:
            template = await self.get_by_id(template_id)
            if not template:
                return None
            
            # Check permissions
            if not await self._has_template_access(template, user):
                raise PermissionDeniedError("Access denied to template")
            
            return template
            
        except Exception as e:
            logger.error(f"Failed to get template {template_id}: {e}")
            raise
    
    async def update_template(
        self,
        template_id: str,
        update_data: TemplateUpdateRequest,
        user: UserModel
    ) -> TemplateModel:
        """
        Update template
        
        Args:
            template_id: Template ID
            update_data: Update data
            user: User updating the template
            
        Returns:
            Updated template
        """
        try:
            # Get existing template
            template = await self.get_template_by_id(template_id, user)
            if not template:
                raise NotFoundError("Template not found")
            
            # Check edit permissions
            if not await self._has_template_edit_access(template, user):
                raise PermissionDeniedError("No permission to edit template")
            
            # Prepare update data
            update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
            
            if update_dict:
                # Update metadata
                update_dict["metadata.updated_by"] = user.id
                update_dict["metadata.updated_at"] = datetime.utcnow()
                update_dict["metadata.version"] = template.metadata.version + 1
                
                # Update in database
                await self.collection.update_one(
                    {"_id": ObjectId(template_id)},
                    {"$set": self._flatten_dict(update_dict)}
                )
            
            # Get updated template
            updated_template = await self.get_by_id(template_id)
            
            logger.info(f"Updated template {template_id} by user {user.id}")
            return updated_template
            
        except Exception as e:
            logger.error(f"Failed to update template {template_id}: {e}")
            raise
    
    async def delete_template(
        self,
        template_id: str,
        user: UserModel
    ) -> bool:
        """
        Delete template (soft delete by setting is_active=False)
        
        Args:
            template_id: Template ID
            user: User deleting the template
            
        Returns:
            Success status
        """
        try:
            # Get existing template
            template = await self.get_template_by_id(template_id, user)
            if not template:
                raise NotFoundError("Template not found")
            
            # Check delete permissions (only owner or admin)
            if template.owner_id != user.id and user.role != UserRole.ADMIN:
                raise PermissionDeniedError("No permission to delete template")
            
            # Soft delete
            await self.collection.update_one(
                {"_id": ObjectId(template_id)},
                {"$set": {
                    "is_active": False,
                    "metadata.updated_by": user.id,
                    "metadata.updated_at": datetime.utcnow()
                }}
            )
            
            logger.info(f"Deleted template {template_id} by user {user.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete template {template_id}: {e}")
            raise
    
    async def search_templates(
        self,
        search_request: TemplateSearchRequest,
        user: UserModel
    ) -> Dict[str, Any]:
        """
        Search templates with filtering and pagination
        
        Args:
            search_request: Search parameters
            user: User performing the search
            
        Returns:
            Search results with pagination
        """
        try:
            # Build query
            query = await self._build_search_query(search_request, user)
            
            # Count total results
            total_count = await self.collection.count_documents(query)
            
            # Calculate pagination
            skip = (search_request.page - 1) * search_request.limit
            
            # Build sort criteria
            sort_criteria = self._build_sort_criteria(search_request.sort_by, search_request.sort_order)
            
            # Execute search
            cursor = self.collection.find(query).sort(sort_criteria).skip(skip).limit(search_request.limit)
            documents = await cursor.to_list(length=search_request.limit)
            
            # Convert to models
            templates = [self._document_to_model(doc) for doc in documents]
            
            # Calculate pagination info
            total_pages = (total_count + search_request.limit - 1) // search_request.limit
            has_next = search_request.page < total_pages
            has_prev = search_request.page > 1
            
            return {
                "templates": templates,
                "pagination": {
                    "page": search_request.page,
                    "limit": search_request.limit,
                    "total": total_count,
                    "total_pages": total_pages,
                    "has_next": has_next,
                    "has_prev": has_prev
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to search templates: {e}")
            raise
    
    async def get_user_templates(
        self,
        user: UserModel,
        template_type: Optional[TemplateType] = None,
        category: Optional[TemplateCategory] = None,
        limit: int = 50
    ) -> List[TemplateModel]:
        """
        Get templates accessible to user
        
        Args:
            user: User requesting templates
            template_type: Filter by template type
            category: Filter by category
            limit: Maximum number of templates
            
        Returns:
            List of accessible templates
        """
        try:
            # Build query for user-accessible templates
            query = {
                "is_active": True,
                "$or": [
                    {"owner_id": user.id},
                    {"scope": TemplateScope.PUBLIC.value},
                    {"scope": TemplateScope.ORGANIZATION.value},
                    {"shared_with_users": user.id},
                    {"shared_with_roles": user.role.value}
                ]
            }
            
            # Add filters
            if template_type:
                query["template_type"] = template_type.value
            if category:
                query["category"] = category.value
            
            # Execute query
            cursor = self.collection.find(query).sort([("metadata.usage_count", -1), ("metadata.created_at", -1)]).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            # Convert to models
            templates = [self._document_to_model(doc) for doc in documents]
            
            return templates
            
        except Exception as e:
            logger.error(f"Failed to get user templates: {e}")
            raise
    
    async def get_popular_templates(
        self,
        user: UserModel,
        category: Optional[TemplateCategory] = None,
        limit: int = 10
    ) -> List[TemplateModel]:
        """
        Get popular templates based on usage statistics
        
        Args:
            user: User requesting templates
            category: Filter by category
            limit: Maximum number of templates
            
        Returns:
            List of popular templates
        """
        try:
            # Build query
            query = {
                "is_active": True,
                "is_published": True,
                "scope": {"$in": [TemplateScope.PUBLIC.value, TemplateScope.ORGANIZATION.value]},
                "metadata.usage_count": {"$gt": 0}
            }
            
            if category:
                query["category"] = category.value
            
            # Get popular templates
            cursor = self.collection.find(query).sort([
                ("metadata.rating", -1),
                ("metadata.usage_count", -1)
            ]).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            # Convert to models
            templates = [self._document_to_model(doc) for doc in documents]
            
            return templates
            
        except Exception as e:
            logger.error(f"Failed to get popular templates: {e}")
            raise
    
    async def record_template_usage(
        self,
        template_id: str,
        user: UserModel,
        encounter_id: str
    ) -> bool:
        """
        Record template usage for statistics
        
        Args:
            template_id: Template ID
            user: User using the template
            encounter_id: Encounter where template was used
            
        Returns:
            Success status
        """
        try:
            # Update usage statistics
            await self.collection.update_one(
                {"_id": ObjectId(template_id)},
                {
                    "$inc": {"metadata.usage_count": 1},
                    "$set": {"metadata.last_used": datetime.utcnow()},
                    "$addToSet": {"usage_history": {
                        "user_id": user.id,
                        "encounter_id": encounter_id,
                        "used_at": datetime.utcnow()
                    }}
                }
            )
            
            logger.info(f"Recorded template usage: {template_id} by user {user.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record template usage: {e}")
            return False
    
    async def rate_template(
        self,
        template_id: str,
        user: UserModel,
        rating: float
    ) -> bool:
        """
        Rate a template
        
        Args:
            template_id: Template ID
            user: User rating the template
            rating: Rating value (1-5)
            
        Returns:
            Success status
        """
        try:
            if not 1 <= rating <= 5:
                raise ValidationException("Rating must be between 1 and 5")
            
            # Check if user has used this template
            template = await self.get_by_id(template_id)
            if not template:
                raise NotFoundError("Template not found")
            
            # Record rating
            await self.collection.update_one(
                {"_id": ObjectId(template_id)},
                {
                    "$push": {"ratings": {
                        "user_id": user.id,
                        "rating": rating,
                        "rated_at": datetime.utcnow()
                    }}
                }
            )
            
            # Update average rating
            await self._update_average_rating(template_id)
            
            logger.info(f"User {user.id} rated template {template_id}: {rating}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rate template: {e}")
            raise
    
    async def get_template_usage_stats(
        self,
        template_id: str,
        user: UserModel
    ) -> TemplateUsageStats:
        """
        Get template usage statistics
        
        Args:
            template_id: Template ID
            user: User requesting stats
            
        Returns:
            Usage statistics
        """
        try:
            template = await self.get_template_by_id(template_id, user)
            if not template:
                raise NotFoundError("Template not found")
            
            # Get usage history
            usage_history = await self.collection.aggregate([
                {"$match": {"_id": ObjectId(template_id)}},
                {"$unwind": {"path": "$usage_history", "preserveNullAndEmptyArrays": True}},
                {"$group": {
                    "_id": "$_id",
                    "unique_users": {"$addToSet": "$usage_history.user_id"},
                    "usage_count": {"$sum": 1},
                    "last_used": {"$max": "$usage_history.used_at"}
                }}
            ]).to_list(length=1)
            
            stats_data = usage_history[0] if usage_history else {}
            
            return TemplateUsageStats(
                template_id=template_id,
                usage_count=template.metadata.usage_count,
                unique_users=len(stats_data.get("unique_users", [])),
                last_used=template.metadata.last_used,
                avg_rating=template.metadata.rating,
                rating_count=template.metadata.rating_count,
                success_rate=85.0,  # Placeholder - would be calculated from encounter completions
                avg_completion_time=None  # Placeholder - would be calculated from encounter data
            )
            
        except Exception as e:
            logger.error(f"Failed to get template usage stats: {e}")
            raise
    
    # Private helper methods
    
    async def _has_template_access(self, template: TemplateModel, user: UserModel) -> bool:
        """Check if user has access to template"""
        if template.owner_id == user.id:
            return True
        
        if template.scope == TemplateScope.PUBLIC:
            return True
        
        if template.scope == TemplateScope.ORGANIZATION:
            return True  # Assuming same organization
        
        if user.id in template.shared_with_users:
            return True
        
        if user.role.value in template.shared_with_roles:
            return True
        
        return False
    
    async def _has_template_edit_access(self, template: TemplateModel, user: UserModel) -> bool:
        """Check if user can edit template"""
        if template.owner_id == user.id:
            return True
        
        if user.role == UserRole.ADMIN:
            return True
        
        # Add additional edit permission logic as needed
        return False
    
    async def _build_search_query(self, search_request: TemplateSearchRequest, user: UserModel) -> Dict[str, Any]:
        """Build MongoDB query for template search"""
        query = {"is_active": True}
        
        # Access control
        query["$or"] = [
            {"owner_id": user.id},
            {"scope": TemplateScope.PUBLIC.value},
            {"scope": TemplateScope.ORGANIZATION.value},
            {"shared_with_users": user.id},
            {"shared_with_roles": user.role.value}
        ]
        
        # Text search
        if search_request.query:
            query["$text"] = {"$search": search_request.query}
        
        # Filters
        if search_request.template_type:
            query["template_type"] = search_request.template_type.value
        
        if search_request.category:
            query["category"] = search_request.category.value
        
        if search_request.scope:
            query["scope"] = search_request.scope.value
        
        if search_request.tags:
            query["tags"] = {"$in": search_request.tags}
        
        if search_request.owner_id:
            query["owner_id"] = search_request.owner_id
        
        if search_request.is_published is not None:
            query["is_published"] = search_request.is_published
        
        if search_request.encounter_type:
            query["encounter_types"] = search_request.encounter_type
        
        return query
    
    def _build_sort_criteria(self, sort_by: str, sort_order: str) -> List[tuple]:
        """Build sort criteria for MongoDB"""
        direction = 1 if sort_order.lower() == "asc" else -1
        
        sort_mapping = {
            "created_at": "metadata.created_at",
            "updated_at": "metadata.updated_at",
            "name": "name",
            "usage_count": "metadata.usage_count",
            "rating": "metadata.rating"
        }
        
        sort_field = sort_mapping.get(sort_by, "metadata.created_at")
        return [(sort_field, direction)]
    
    async def _update_average_rating(self, template_id: str):
        """Update average rating for template"""
        try:
            # Calculate new average rating
            pipeline = [
                {"$match": {"_id": ObjectId(template_id)}},
                {"$unwind": "$ratings"},
                {"$group": {
                    "_id": "$_id",
                    "avg_rating": {"$avg": "$ratings.rating"},
                    "rating_count": {"$sum": 1}
                }}
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(length=1)
            
            if result:
                stats = result[0]
                await self.collection.update_one(
                    {"_id": ObjectId(template_id)},
                    {"$set": {
                        "metadata.rating": round(stats["avg_rating"], 2),
                        "metadata.rating_count": stats["rating_count"]
                    }}
                )
            
        except Exception as e:
            logger.error(f"Failed to update average rating: {e}")
    
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """Flatten nested dictionary for MongoDB updates"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)