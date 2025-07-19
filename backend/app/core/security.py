"""
Security utilities for DiagnoAssist Backend
"""
import secrets
from datetime import datetime, timedelta
from typing import Optional, Union, Any, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt

from app.config import settings
from app.core.exceptions import AuthenticationException, AuthorizationException
from app.models.auth import TokenData, UserRoleEnum


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityManager:
    """Central security management class"""
    
    def __init__(self):
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
    
    def create_password_hash(self, password: str) -> str:
        """Create password hash"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=7)  # Refresh tokens last 7 days
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str, token_type: str = "access") -> TokenData:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Verify token type
            if payload.get("type") != token_type:
                raise AuthenticationException("Invalid token type")
            
            # Extract token data
            user_id: str = payload.get("sub")
            email: str = payload.get("email")
            role: str = payload.get("role")
            exp: int = payload.get("exp")
            iat: int = payload.get("iat")
            
            if not user_id or not email:
                raise AuthenticationException("Invalid token payload")
            
            return TokenData(
                sub=user_id,
                email=email,
                role=role,
                exp=exp,
                iat=iat,
                type=token_type
            )
            
        except JWTError as e:
            raise AuthenticationException(f"Token validation failed: {str(e)}")
    
    def generate_password_reset_token(self, email: str) -> str:
        """Generate password reset token"""
        data = {
            "sub": email,
            "type": "password_reset"
        }
        return self.create_access_token(data, expires_delta=timedelta(hours=1))
    
    def verify_password_reset_token(self, token: str) -> str:
        """Verify password reset token and return email"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            if payload.get("type") != "password_reset":
                raise AuthenticationException("Invalid token type")
            
            email: str = payload.get("sub")
            if not email:
                raise AuthenticationException("Invalid token payload")
            
            return email
            
        except JWTError as e:
            raise AuthenticationException(f"Password reset token validation failed: {str(e)}")
    
    def generate_api_key(self) -> str:
        """Generate secure API key"""
        return secrets.token_urlsafe(32)


class RoleChecker:
    """Role-based access control checker"""
    
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles
    
    def __call__(self, user_role: str) -> bool:
        """Check if user role is allowed"""
        if user_role not in self.allowed_roles:
            return False
        return True


class PermissionChecker:
    """Permission-based access control"""
    
    # Define role permissions
    ROLE_PERMISSIONS = {
        UserRoleEnum.ADMIN: [
            "user:create", "user:read", "user:update", "user:delete",
            "patient:create", "patient:read", "patient:update", "patient:delete",
            "episode:create", "episode:read", "episode:update", "episode:delete",
            "encounter:create", "encounter:read", "encounter:update", "encounter:delete",
            "encounter:sign", "system:admin"
        ],
        UserRoleEnum.DOCTOR: [
            "patient:create", "patient:read", "patient:update",
            "episode:create", "episode:read", "episode:update",
            "encounter:create", "encounter:read", "encounter:update", "encounter:delete",
            "encounter:sign", "user:read"
        ],
        UserRoleEnum.NURSE: [
            "patient:read", "patient:update",
            "episode:read", "episode:update",
            "encounter:create", "encounter:read", "encounter:update",
            "user:read"
        ],
        UserRoleEnum.STUDENT: [
            "patient:read", "episode:read", "encounter:read", "user:read"
        ]
    }
    
    @classmethod
    def has_permission(cls, user_role: UserRoleEnum, permission: str) -> bool:
        """Check if user role has specific permission"""
        role_permissions = cls.ROLE_PERMISSIONS.get(user_role, [])
        return permission in role_permissions
    
    @classmethod
    def can_access_patient(cls, user_role: UserRoleEnum, action: str) -> bool:
        """Check if user can perform action on patient"""
        return cls.has_permission(user_role, f"patient:{action}")
    
    @classmethod
    def can_access_encounter(cls, user_role: UserRoleEnum, action: str) -> bool:
        """Check if user can perform action on encounter"""
        return cls.has_permission(user_role, f"encounter:{action}")
    
    @classmethod
    def can_sign_encounter(cls, user_role: UserRoleEnum) -> bool:
        """Check if user can sign encounters"""
        return cls.has_permission(user_role, "encounter:sign")


# Create security manager instance
security = SecurityManager()


def get_password_hash(password: str) -> str:
    """Get password hash"""
    return security.create_password_hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return security.verify_password(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create access token"""
    return security.create_access_token(data, expires_delta)


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create refresh token"""
    return security.create_refresh_token(data, expires_delta)


def verify_token(token: str, token_type: str = "access") -> TokenData:
    """Verify token"""
    return security.verify_token(token, token_type)