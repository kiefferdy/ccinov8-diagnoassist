"""
Authentication service for DiagnoAssist Backend
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from app.models.auth import (
    UserModel, UserRegistrationRequest, UserLoginRequest, 
    TokenResponse, CurrentUser, UserStatusEnum
)
from app.core.security import (
    security, get_password_hash, verify_password, 
    create_access_token, create_refresh_token, verify_token
)
from app.core.exceptions import (
    AuthenticationException, ValidationException, NotFoundError, ConflictException
)


class AuthService:
    """Authentication service class"""
    
    def __init__(self):
        # Import repository here to avoid circular imports
        from app.repositories.user_repository import user_repository
        self.user_repo = user_repository
    
    async def register_user(self, registration_data: UserRegistrationRequest) -> UserModel:
        """Register a new user"""
        
        # Check if user already exists
        existing_user = await self.user_repo.get_by_email(registration_data.email)
        if existing_user:
            raise ConflictException(
                "User with this email already exists", 
                "user",
                {"email": registration_data.email}
            )
        
        # Create password hash
        hashed_password = get_password_hash(registration_data.password)
        
        # Create new user
        new_user = UserModel(
            email=registration_data.email,
            hashed_password=hashed_password,
            role=registration_data.role,
            status=UserStatusEnum.PENDING_VERIFICATION,
            profile=registration_data.profile,
            is_verified=False,  # In real app, would send verification email
        )
        
        # Store user in database
        return await self.user_repo.create(new_user)
    
    async def authenticate_user(self, login_data: UserLoginRequest) -> Optional[UserModel]:
        """Authenticate user with email and password"""
        
        # Get user by email
        user = await self.user_repo.get_by_email(login_data.email)
        if not user:
            return None
        
        # Verify password
        if not verify_password(login_data.password, user.hashed_password):
            return None
        
        # Check user status
        if user.status == UserStatusEnum.SUSPENDED:
            raise AuthenticationException("Account is suspended")
        
        if user.status == UserStatusEnum.INACTIVE:
            raise AuthenticationException("Account is inactive")
        
        # Update last login
        await self.user_repo.update_last_login(user.id)
        
        # Refresh user data after update
        updated_user = await self.user_repo.get_by_id(user.id)
        return updated_user
    
    async def login_user(self, login_data: UserLoginRequest) -> Dict[str, Any]:
        """Login user and return tokens"""
        
        # Authenticate user
        user = await self.authenticate_user(login_data)
        if not user:
            raise AuthenticationException("Invalid email or password")
        
        # Create token data
        token_data = {
            "sub": user.id,
            "email": user.email,
            "role": user.role.value
        }
        
        # Create tokens
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        # Prepare response
        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "profile": user.profile,
                "is_verified": user.is_verified,
                "last_login": user.last_login
            },
            "tokens": {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": security.access_token_expire_minutes * 60,
                "refresh_token": refresh_token
            }
        }
    
    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token"""
        
        # Verify refresh token
        try:
            token_data = verify_token(refresh_token, "refresh")
        except Exception as e:
            raise AuthenticationException("Invalid refresh token")
        
        # Get user
        user = await self.user_repo.get_by_id(token_data.sub)
        if not user:
            raise AuthenticationException("User not found")
        
        # Check user status
        if user.status not in [UserStatusEnum.ACTIVE, UserStatusEnum.PENDING_VERIFICATION]:
            raise AuthenticationException("Account is not active")
        
        # Create new access token
        new_token_data = {
            "sub": user.id,
            "email": user.email,
            "role": user.role.value
        }
        
        access_token = create_access_token(new_token_data)
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=security.access_token_expire_minutes * 60
        )
    
    async def get_current_user(self, token: str) -> CurrentUser:
        """Get current user from access token"""
        
        # Verify token
        try:
            token_data = verify_token(token, "access")
        except Exception as e:
            raise AuthenticationException("Invalid access token")
        
        # Get user
        user = await self.user_repo.get_by_id(token_data.sub)
        if not user:
            raise AuthenticationException("User not found")
        
        # Check user status
        if user.status not in [UserStatusEnum.ACTIVE, UserStatusEnum.PENDING_VERIFICATION]:
            raise AuthenticationException("Account is not active")
        
        return CurrentUser(
            id=user.id,
            email=user.email,
            role=user.role,
            profile=user.profile,
            is_verified=user.is_verified
        )
    
    async def get_user_by_email(self, email: str) -> Optional[UserModel]:
        """Get user by email"""
        return await self.user_repo.get_by_email(email)
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserModel]:
        """Get user by ID"""
        return await self.user_repo.get_by_id(user_id)
    
    async def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """Change user password"""
        
        # Get user
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User", user_id)
        
        # Verify current password
        if not verify_password(current_password, user.hashed_password):
            raise AuthenticationException("Current password is incorrect")
        
        # Update password
        hashed_password = get_password_hash(new_password)
        await self.user_repo.update_password(user_id, hashed_password)
        
        return True
    
    async def activate_user(self, user_id: str) -> UserModel:
        """Activate user account (for admin use)"""
        return await self.user_repo.update_status(user_id, UserStatusEnum.ACTIVE)
    
    async def suspend_user(self, user_id: str) -> UserModel:
        """Suspend user account (for admin use)"""
        return await self.user_repo.update_status(user_id, UserStatusEnum.SUSPENDED)
    
    async def verify_user_email(self, user_id: str) -> UserModel:
        """Verify user email (simulate email verification)"""
        return await self.user_repo.verify_user(user_id)


# Create service instance
auth_service = AuthService()