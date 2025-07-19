"""
Authentication API endpoints for DiagnoAssist Backend
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from datetime import datetime

from app.models.auth import (
    UserRegistrationRequest, UserLoginRequest, TokenResponse, LoginResponse,
    UserResponse, PasswordChangeRequest, RefreshTokenRequest, CurrentUser
)
from app.services.auth_service import auth_service
from app.middleware.auth_middleware import get_current_user, require_admin
from app.middleware.rate_limit import auth_rate_limit, login_rate_limit
from app.core.exceptions import (
    AuthenticationException, ValidationException, ConflictException, NotFoundError
)

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register_user(
    registration_data: UserRegistrationRequest,
    _: bool = Depends(auth_rate_limit),
):
    """Register a new user"""
    try:
        new_user = await auth_service.register_user(registration_data)
        return UserResponse(data=new_user)
        
    except ConflictException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )


@router.post("/login", response_model=LoginResponse)
async def login_user(
    login_data: UserLoginRequest,
    _: bool = Depends(login_rate_limit),
):
    """Authenticate user and return access token"""
    try:
        login_result = await auth_service.login_user(login_data)
        return LoginResponse(data=login_result)
        
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_data: RefreshTokenRequest):
    """Refresh access token using refresh token"""
    try:
        new_token = await auth_service.refresh_access_token(refresh_data.refresh_token)
        return new_token
        
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/logout")
async def logout_user(current_user: CurrentUser = Depends(get_current_user)):
    """Logout user (in Phase 3, will invalidate tokens using database)"""
    # For now, just return success since we're using in-memory storage
    # In Phase 3 with database, we'll add token blacklisting
    return {
        "success": True,
        "message": "Successfully logged out",
        "timestamp": datetime.utcnow()
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: CurrentUser = Depends(get_current_user)):
    """Get current user profile"""
    try:
        # Get full user data
        user = await auth_service.get_user_by_id(current_user.id)
        if not user:
            raise NotFoundError("User", current_user.id)
        
        return UserResponse(data=user)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/change-password")
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Change user password"""
    try:
        success = await auth_service.change_password(
            current_user.id,
            password_data.current_password,
            password_data.new_password
        )
        
        return {
            "success": True,
            "message": "Password changed successfully",
            "timestamp": datetime.utcnow()
        }
        
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )


@router.post("/verify-email/{user_id}")
async def verify_user_email(
    user_id: str,
    admin_user: CurrentUser = Depends(require_admin)
):
    """Verify user email (admin only, simulates email verification)"""
    try:
        verified_user = await auth_service.verify_user_email(user_id)
        return UserResponse(data=verified_user)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/activate/{user_id}")
async def activate_user(
    user_id: str,
    admin_user: CurrentUser = Depends(require_admin)
):
    """Activate user account (admin only)"""
    try:
        activated_user = await auth_service.activate_user(user_id)
        return UserResponse(data=activated_user)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/suspend/{user_id}")
async def suspend_user(
    user_id: str,
    admin_user: CurrentUser = Depends(require_admin)
):
    """Suspend user account (admin only)"""
    try:
        suspended_user = await auth_service.suspend_user(user_id)
        return UserResponse(data=suspended_user)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/validate-token")
async def validate_token(current_user: CurrentUser = Depends(get_current_user)):
    """Validate current access token"""
    return {
        "success": True,
        "data": {
            "valid": True,
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "role": current_user.role,
                "is_verified": current_user.is_verified
            }
        },
        "timestamp": datetime.utcnow()
    }


# Development/testing endpoints
@router.get("/users", response_model=Dict[str, Any])
async def list_users(admin_user: CurrentUser = Depends(require_admin)):
    """List all users (admin only, for development)"""
    users = auth_service.users_storage
    
    # Remove password hashes from response
    safe_users = []
    for user in users:
        user_dict = user.dict()
        user_dict.pop('hashed_password', None)
        safe_users.append(user_dict)
    
    return {
        "success": True,
        "data": safe_users,
        "total": len(safe_users),
        "timestamp": datetime.utcnow()
    }


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    admin_user: CurrentUser = Depends(require_admin)
):
    """Delete user (admin only, for development)"""
    # Find and remove user
    for i, user in enumerate(auth_service.users_storage):
        if user.id == user_id:
            deleted_user = auth_service.users_storage.pop(i)
            return {
                "success": True,
                "message": f"User {deleted_user.email} deleted successfully",
                "timestamp": datetime.utcnow()
            }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User {user_id} not found"
    )