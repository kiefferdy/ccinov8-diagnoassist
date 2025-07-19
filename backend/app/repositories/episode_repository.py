"""
Episode repository for DiagnoAssist Backend
"""
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.repositories.base_repository import BaseRepository
from app.models.episode import EpisodeModel, EpisodeCategoryEnum, EpisodeStatusEnum
from app.core.exceptions import DatabaseException


class EpisodeRepository(BaseRepository[EpisodeModel]):
    """Repository for Episode entities"""
    
    def __init__(self):
        super().__init__("episodes")
        self._id_counter = 1
    
    def _to_dict(self, episode: EpisodeModel) -> Dict[str, Any]:
        """Convert EpisodeModel to dictionary for MongoDB storage"""
        return {
            "id": episode.id,
            "patient_id": episode.patient_id,
            "chief_complaint": episode.chief_complaint,
            "category": episode.category.value,
            "status": episode.status.value,
            "related_episode_ids": episode.related_episode_ids,
            "tags": episode.tags,
            "last_encounter_id": episode.last_encounter_id,
            "created_at": episode.created_at,
            "updated_at": episode.updated_at,
            "resolved_at": episode.resolved_at,
            "notes": episode.notes
        }
    
    def _from_dict(self, data: Dict[str, Any]) -> EpisodeModel:
        """Convert dictionary from MongoDB to EpisodeModel"""
        return EpisodeModel(
            id=data.get("id"),
            patient_id=data.get("patient_id", ""),
            chief_complaint=data.get("chief_complaint", ""),
            category=EpisodeCategoryEnum(data.get("category", "routine")),
            status=EpisodeStatusEnum(data.get("status", "active")),
            related_episode_ids=data.get("related_episode_ids", []),
            tags=data.get("tags", []),
            last_encounter_id=data.get("last_encounter_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            resolved_at=data.get("resolved_at"),
            notes=data.get("notes")
        )
    
    def _get_entity_name(self) -> str:
        """Get entity name for error messages"""
        return "Episode"
    
    def _generate_id(self) -> str:
        """Generate unique episode ID"""
        episode_id = f"E{self._id_counter:03d}"
        self._id_counter += 1
        return episode_id
    
    async def get_by_patient_id(
        self, 
        patient_id: str,
        status: Optional[EpisodeStatusEnum] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[EpisodeModel]:
        """Get episodes for a specific patient"""
        try:
            filter_dict = {"patient_id": patient_id}
            
            if status:
                filter_dict["status"] = status.value
            
            return await self.get_all(
                filter_dict=filter_dict,
                skip=skip,
                limit=limit,
                sort_field="created_at",
                sort_direction=-1
            )
            
        except Exception as e:
            raise DatabaseException(
                f"Database error while retrieving episodes for patient {patient_id}: {str(e)}",
                "read"
            )
    
    async def get_by_status(
        self,
        status: EpisodeStatusEnum,
        skip: int = 0,
        limit: int = 50
    ) -> List[EpisodeModel]:
        """Get episodes by status"""
        filter_dict = {"status": status.value}
        return await self.get_all(
            filter_dict=filter_dict,
            skip=skip,
            limit=limit
        )
    
    async def get_by_category(
        self,
        category: EpisodeCategoryEnum,
        skip: int = 0,
        limit: int = 50
    ) -> List[EpisodeModel]:
        """Get episodes by category"""
        filter_dict = {"category": category.value}
        return await self.get_all(
            filter_dict=filter_dict,
            skip=skip,
            limit=limit
        )
    
    async def search_by_chief_complaint(self, query: str) -> List[EpisodeModel]:
        """Search episodes by chief complaint"""
        try:
            collection = await self.get_collection()
            
            search_query = {
                "chief_complaint": {
                    "$regex": query,
                    "$options": "i"
                }
            }
            
            cursor = collection.find(search_query).sort("created_at", -1)
            documents = await cursor.to_list(length=100)
            
            return [self._from_dict(doc) for doc in documents]
            
        except Exception as e:
            raise DatabaseException(
                f"Database error while searching episodes by chief complaint: {str(e)}",
                "search"
            )
    
    async def get_by_tags(self, tags: List[str]) -> List[EpisodeModel]:
        """Get episodes by tags"""
        try:
            collection = await self.get_collection()
            
            # Find episodes that contain any of the specified tags
            query = {
                "tags": {
                    "$in": tags
                }
            }
            
            cursor = collection.find(query).sort("created_at", -1)
            documents = await cursor.to_list(length=100)
            
            return [self._from_dict(doc) for doc in documents]
            
        except Exception as e:
            raise DatabaseException(
                f"Database error while retrieving episodes by tags: {str(e)}",
                "search"
            )
    
    async def get_related_episodes(self, episode_id: str) -> List[EpisodeModel]:
        """Get episodes related to a specific episode"""
        try:
            collection = await self.get_collection()
            
            # Find episodes that reference this episode or are referenced by this episode
            query = {
                "$or": [
                    {"related_episode_ids": episode_id},
                    {"id": {"$in": await self._get_related_episode_ids(episode_id)}}
                ]
            }
            
            cursor = collection.find(query).sort("created_at", -1)
            documents = await cursor.to_list(length=50)
            
            return [self._from_dict(doc) for doc in documents]
            
        except Exception as e:
            raise DatabaseException(
                f"Database error while retrieving related episodes: {str(e)}",
                "search"
            )
    
    async def _get_related_episode_ids(self, episode_id: str) -> List[str]:
        """Get related episode IDs for a specific episode"""
        episode = await self.get_by_id(episode_id)
        return episode.related_episode_ids if episode else []
    
    async def update_status(self, episode_id: str, status: EpisodeStatusEnum) -> EpisodeModel:
        """Update episode status"""
        update_fields = {"status": status.value}
        
        # Set resolved_at if status is resolved
        if status == EpisodeStatusEnum.RESOLVED:
            update_fields["resolved_at"] = datetime.utcnow()
        elif status != EpisodeStatusEnum.RESOLVED:
            update_fields["resolved_at"] = None
        
        return await self.update_fields(episode_id, update_fields)
    
    async def update_last_encounter(self, episode_id: str, encounter_id: str) -> EpisodeModel:
        """Update the last encounter ID for an episode"""
        return await self.update_fields(episode_id, {"last_encounter_id": encounter_id})
    
    async def add_related_episode(self, episode_id: str, related_episode_id: str) -> EpisodeModel:
        """Add a related episode"""
        try:
            collection = await self.get_collection()
            
            # Add to related_episode_ids array if not already present
            result = await collection.update_one(
                {"id": episode_id},
                {
                    "$addToSet": {"related_episode_ids": related_episode_id},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            if result.matched_count > 0:
                updated_data = await collection.find_one({"id": episode_id})
                return self._from_dict(updated_data)
            else:
                from app.core.exceptions import NotFoundError
                raise NotFoundError("Episode", episode_id)
                
        except Exception as e:
            if isinstance(e, DatabaseException):
                raise
            raise DatabaseException(
                f"Database error while adding related episode: {str(e)}",
                "update"
            )
    
    async def remove_related_episode(self, episode_id: str, related_episode_id: str) -> EpisodeModel:
        """Remove a related episode"""
        try:
            collection = await self.get_collection()
            
            # Remove from related_episode_ids array
            result = await collection.update_one(
                {"id": episode_id},
                {
                    "$pull": {"related_episode_ids": related_episode_id},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            if result.matched_count > 0:
                updated_data = await collection.find_one({"id": episode_id})
                return self._from_dict(updated_data)
            else:
                from app.core.exceptions import NotFoundError
                raise NotFoundError("Episode", episode_id)
                
        except Exception as e:
            if isinstance(e, DatabaseException):
                raise
            raise DatabaseException(
                f"Database error while removing related episode: {str(e)}",
                "update"
            )
    
    async def get_active_episodes_for_patient(self, patient_id: str) -> List[EpisodeModel]:
        """Get active episodes for a patient"""
        return await self.get_by_patient_id(
            patient_id,
            status=EpisodeStatusEnum.ACTIVE
        )
    
    async def get_episode_statistics(self) -> Dict[str, Any]:
        """Get episode statistics"""
        try:
            collection = await self.get_collection()
            
            # Count by status
            status_counts = {}
            for status in EpisodeStatusEnum:
                count = await collection.count_documents({"status": status.value})
                status_counts[status.value] = count
            
            # Count by category
            category_counts = {}
            for category in EpisodeCategoryEnum:
                count = await collection.count_documents({"category": category.value})
                category_counts[category.value] = count
            
            # Total count
            total_count = await collection.count_documents({})
            
            return {
                "total_episodes": total_count,
                "by_status": status_counts,
                "by_category": category_counts
            }
            
        except Exception as e:
            raise DatabaseException(
                f"Database error while retrieving episode statistics: {str(e)}",
                "read"
            )


# Create repository instance
episode_repository = EpisodeRepository()