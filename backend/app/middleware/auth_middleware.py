"""
Authentication middleware for DiagnoAssist Backend
"""
from typing import Optional, List
from fastapi import Request, HTTPException, status, WebSocketException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security.utils import get_authorization_scheme_param

from app.models.auth import CurrentUser, UserRoleEnum
from app.services.auth_service import auth_service
from app.core.exceptions import AuthenticationException, AuthorizationException
from app.core.security import PermissionChecker


class JWTBearer(HTTPBearer):
    """Custom JWT Bearer authentication"""
    
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)
    
    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        """Extract and validate JWT token from request"""
        authorization: str = request.headers.get("Authorization")
        scheme, credentials = get_authorization_scheme_param(authorization)
        
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        
        return HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)


class AuthMiddleware:
    """Authentication middleware class"""
    
    def __init__(self):
        self.jwt_bearer = JWTBearer()
    
    async def get_current_user(self, request: Request) -> CurrentUser:
        """Get current authenticated user from request"""
        try:
            # Extract token
            credentials = await self.jwt_bearer(request)
            if not credentials:
                raise AuthenticationException("Authentication credentials not provided")
            
            # Get user from token
            current_user = await auth_service.get_current_user(credentials.credentials)
            return current_user
            
        except AuthenticationException as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    async def get_optional_user(self, request: Request) -> Optional[CurrentUser]:
        """Get current user if authenticated, None otherwise"""
        try:
            # Use non-auto-error JWT bearer
            jwt_bearer = JWTBearer(auto_error=False)
            credentials = await jwt_bearer(request)
            
            if not credentials:
                return None
            
            # Get user from token
            current_user = await auth_service.get_current_user(credentials.credentials)
            return current_user
            
        except Exception:
            return None


class RoleBasedAuth:
    """Role-based authentication dependency"""
    
    def __init__(self, allowed_roles: List[UserRoleEnum]):
        self.allowed_roles = allowed_roles
        self.auth_middleware = AuthMiddleware()
    
    async def __call__(self, request: Request) -> CurrentUser:
        """Check if user has required role"""
        current_user = await self.auth_middleware.get_current_user(request)
        
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[role.value for role in self.allowed_roles]}"
            )
        
        return current_user


class PermissionBasedAuth:
    """Permission-based authentication dependency"""
    
    def __init__(self, required_permission: str):
        self.required_permission = required_permission
        self.auth_middleware = AuthMiddleware()
    
    async def __call__(self, request: Request) -> CurrentUser:
        """Check if user has required permission"""
        current_user = await self.auth_middleware.get_current_user(request)
        
        if not PermissionChecker.has_permission(current_user.role, self.required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required permission: {self.required_permission}"
            )
        
        return current_user


# Create middleware instances for easy import
auth_middleware = AuthMiddleware()

# Common role-based dependencies
require_admin = RoleBasedAuth([UserRoleEnum.ADMIN])
require_doctor_or_admin = RoleBasedAuth([UserRoleEnum.DOCTOR, UserRoleEnum.ADMIN])
require_healthcare_provider = RoleBasedAuth([UserRoleEnum.DOCTOR, UserRoleEnum.NURSE, UserRoleEnum.ADMIN])
require_any_role = RoleBasedAuth([UserRoleEnum.DOCTOR, UserRoleEnum.NURSE, UserRoleEnum.ADMIN, UserRoleEnum.STUDENT])

# Common permission-based dependencies
require_patient_read = PermissionBasedAuth("patient:read")
require_patient_write = PermissionBasedAuth("patient:create")
require_patient_update = PermissionBasedAuth("patient:update")
require_patient_delete = PermissionBasedAuth("patient:delete")

require_encounter_read = PermissionBasedAuth("encounter:read")
require_encounter_write = PermissionBasedAuth("encounter:create")
require_encounter_update = PermissionBasedAuth("encounter:update")
require_encounter_delete = PermissionBasedAuth("encounter:delete")
require_encounter_sign = PermissionBasedAuth("encounter:sign")

require_episode_read = PermissionBasedAuth("episode:read")
require_episode_write = PermissionBasedAuth("episode:create")
require_episode_update = PermissionBasedAuth("episode:update")
require_episode_delete = PermissionBasedAuth("episode:delete")


# Helper functions for dependency injection
async def get_current_user(request: Request) -> CurrentUser:
    """Dependency to get current authenticated user"""
    return await auth_middleware.get_current_user(request)


async def get_optional_user(request: Request) -> Optional[CurrentUser]:
    """Dependency to get current user if authenticated"""
    return await auth_middleware.get_optional_user(request)


# Resource ownership checker
class ResourceOwnershipAuth:
    """Check if user can access specific resource (for future use with ownership)"""
    
    def __init__(self, resource_type: str):
        self.resource_type = resource_type
        self.auth_middleware = AuthMiddleware()
    
    async def __call__(self, request: Request, resource_id: str) -> CurrentUser:
        """Check if user can access the specific resource"""
        current_user = await self.auth_middleware.get_current_user(request)
        
        # For now, allow all authenticated users
        # In Phase 4, this will be enhanced with actual ownership checks
        return current_user


# WebSocket Authentication
async def get_current_user_websocket(token: str) -> CurrentUser:
    """
    Get current authenticated user from WebSocket token
    
    Args:
        token: JWT token from WebSocket query parameter
        
    Returns:
        Current user object
        
    Raises:
        WebSocketException: If authentication fails
    """
    try:
        if not token:
            raise AuthenticationException("Authentication token not provided")
        
        # Get user from token
        current_user = await auth_service.get_current_user(token)
        return current_user
        
    except AuthenticationException as e:
        raise WebSocketException(code=4001, reason=f"Authentication failed: {str(e)}")
    except Exception as e:
        raise WebSocketException(code=4001, reason="Could not validate credentials")