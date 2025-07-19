"""
User repository for DiagnoAssist Backend
"""
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.repositories.base_repository import BaseRepository
from app.models.auth import UserModel, UserProfile, UserRoleEnum, UserStatusEnum
from app.core.exceptions import DatabaseException


class UserRepository(BaseRepository[UserModel]):
    """Repository for User entities"""
    
    def __init__(self):
        super().__init__("users")
        self._id_counter = 1
    
    def _to_dict(self, user: UserModel) -> Dict[str, Any]:
        """Convert UserModel to dictionary for MongoDB storage"""
        return {
            "id": user.id,
            "email": user.email,
            "hashed_password": user.hashed_password,
            "role": user.role.value,
            "status": user.status.value,
            "profile": {
                "first_name": user.profile.first_name,
                "last_name": user.profile.last_name,
                "specialty": user.profile.specialty,
                "license_number": user.profile.license_number,
                "department": user.profile.department,
                "phone": user.profile.phone
            },
            "is_verified": user.is_verified,
            "last_login": user.last_login,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
    
    def _from_dict(self, data: Dict[str, Any]) -> UserModel:
        """Convert dictionary from MongoDB to UserModel"""
        # Parse profile
        profile_data = data.get("profile", {})
        profile = UserProfile(
            first_name=profile_data.get("first_name", ""),
            last_name=profile_data.get("last_name", ""),
            specialty=profile_data.get("specialty"),
            license_number=profile_data.get("license_number"),
            department=profile_data.get("department"),
            phone=profile_data.get("phone")
        )
        
        return UserModel(
            id=data.get("id"),
            email=data.get("email", ""),
            hashed_password=data.get("hashed_password", ""),
            role=UserRoleEnum(data.get("role", "doctor")),
            status=UserStatusEnum(data.get("status", "pending_verification")),
            profile=profile,
            is_verified=data.get("is_verified", False),
            last_login=data.get("last_login"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
    
    def _get_entity_name(self) -> str:
        """Get entity name for error messages"""
        return "User"
    
    def _generate_id(self) -> str:
        """Generate unique user ID"""
        user_id = f"U{self._id_counter:03d}"
        self._id_counter += 1
        return user_id
    
    async def get_by_email(self, email: str) -> Optional[UserModel]:
        """Get user by email address"""
        return await self.get_by_field("email", email)
    
    async def get_by_role(
        self,
        role: UserRoleEnum,
        skip: int = 0,
        limit: int = 50
    ) -> List[UserModel]:
        """Get users by role"""
        filter_dict = {"role": role.value}
        return await self.get_all(
            filter_dict=filter_dict,
            skip=skip,
            limit=limit,
            sort_field="profile.last_name",
            sort_direction=1
        )
    
    async def get_by_status(
        self,
        status: UserStatusEnum,
        skip: int = 0,
        limit: int = 50
    ) -> List[UserModel]:
        """Get users by status"""
        filter_dict = {"status": status.value}
        return await self.get_all(
            filter_dict=filter_dict,
            skip=skip,
            limit=limit
        )
    
    async def search_by_name(self, name_query: str) -> List[UserModel]:
        """Search users by first or last name"""
        try:
            collection = await self.get_collection()
            
            # Search in both first and last name
            query = {
                "$or": [
                    {
                        "profile.first_name": {
                            "$regex": name_query,
                            "$options": "i"
                        }
                    },
                    {
                        "profile.last_name": {
                            "$regex": name_query,
                            "$options": "i"
                        }
                    }
                ]
            }
            
            cursor = collection.find(query).sort("profile.last_name", 1)
            documents = await cursor.to_list(length=100)
            
            return [self._from_dict(doc) for doc in documents]
            
        except Exception as e:
            raise DatabaseException(
                f"Database error while searching users by name: {str(e)}",
                "search"
            )
    
    async def get_by_department(self, department: str) -> List[UserModel]:
        """Get users by department"""
        filter_dict = {"profile.department": department}
        return await self.get_all(
            filter_dict=filter_dict,
            sort_field="profile.last_name",
            sort_direction=1
        )
    
    async def get_by_specialty(self, specialty: str) -> List[UserModel]:
        """Get users by specialty"""
        filter_dict = {"profile.specialty": specialty}
        return await self.get_all(
            filter_dict=filter_dict,
            sort_field="profile.last_name",
            sort_direction=1
        )
    
    async def update_last_login(self, user_id: str) -> UserModel:
        """Update last login timestamp"""
        return await self.update_fields(user_id, {"last_login": datetime.utcnow()})
    
    async def update_password(self, user_id: str, hashed_password: str) -> UserModel:
        """Update user password"""
        return await self.update_fields(user_id, {"hashed_password": hashed_password})
    
    async def update_status(self, user_id: str, status: UserStatusEnum) -> UserModel:
        """Update user status"""
        update_fields = {"status": status.value}
        
        # Auto-verify if status is active
        if status == UserStatusEnum.ACTIVE:
            update_fields["is_verified"] = True
        
        return await self.update_fields(user_id, update_fields)
    
    async def verify_user(self, user_id: str) -> UserModel:
        """Verify user email"""
        update_fields = {
            "is_verified": True,
            "status": UserStatusEnum.ACTIVE.value
        }
        return await self.update_fields(user_id, update_fields)
    
    async def update_profile(self, user_id: str, profile: UserProfile) -> UserModel:
        """Update user profile"""
        profile_dict = {
            "profile.first_name": profile.first_name,
            "profile.last_name": profile.last_name,
            "profile.specialty": profile.specialty,
            "profile.license_number": profile.license_number,
            "profile.department": profile.department,
            "profile.phone": profile.phone
        }
        return await self.update_fields(user_id, profile_dict)
    
    async def get_active_users(self) -> List[UserModel]:
        """Get all active users"""
        return await self.get_by_status(UserStatusEnum.ACTIVE)
    
    async def get_verified_users(self) -> List[UserModel]:
        """Get all verified users"""
        filter_dict = {"is_verified": True}
        return await self.get_all(filter_dict=filter_dict)
    
    async def get_healthcare_providers(self) -> List[UserModel]:
        """Get doctors and nurses"""
        try:
            filter_dict = {
                "role": {
                    "$in": [UserRoleEnum.DOCTOR.value, UserRoleEnum.NURSE.value]
                }
            }
            return await self.get_all(
                filter_dict=filter_dict,
                sort_field="profile.last_name",
                sort_direction=1
            )
            
        except Exception as e:
            raise DatabaseException(
                f"Database error while retrieving healthcare providers: {str(e)}",
                "read"
            )
    
    async def get_user_statistics(self) -> Dict[str, Any]:
        """Get user statistics"""
        try:
            collection = await self.get_collection()
            
            # Count by role
            role_counts = {}
            for role in UserRoleEnum:
                count = await collection.count_documents({"role": role.value})
                role_counts[role.value] = count
            
            # Count by status
            status_counts = {}
            for status in UserStatusEnum:
                count = await collection.count_documents({"status": status.value})
                status_counts[status.value] = count
            
            # Total count
            total_count = await collection.count_documents({})
            
            # Verified users count
            verified_count = await collection.count_documents({"is_verified": True})
            
            return {
                "total_users": total_count,
                "verified_users": verified_count,
                "by_role": role_counts,
                "by_status": status_counts
            }
            
        except Exception as e:
            raise DatabaseException(
                f"Database error while retrieving user statistics: {str(e)}",
                "read"
            )
    
    async def search_users(
        self,
        name: Optional[str] = None,
        email: Optional[str] = None,
        role: Optional[UserRoleEnum] = None,
        status: Optional[UserStatusEnum] = None,
        department: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[UserModel]:
        """Search users with multiple filters"""
        try:
            filter_dict = {}
            
            if name:
                filter_dict["$or"] = [
                    {"profile.first_name": {"$regex": name, "$options": "i"}},
                    {"profile.last_name": {"$regex": name, "$options": "i"}}
                ]
            
            if email:
                filter_dict["email"] = {"$regex": email, "$options": "i"}
            
            if role:
                filter_dict["role"] = role.value
            
            if status:
                filter_dict["status"] = status.value
            
            if department:
                filter_dict["profile.department"] = department
            
            return await self.get_all(
                filter_dict=filter_dict,
                skip=skip,
                limit=limit,
                sort_field="profile.last_name",
                sort_direction=1
            )
            
        except Exception as e:
            raise DatabaseException(
                f"Database error while searching users: {str(e)}",
                "search"
            )


# Create repository instance
user_repository = UserRepository()