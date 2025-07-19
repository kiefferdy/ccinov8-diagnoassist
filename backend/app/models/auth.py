"""
Authentication and User models for DiagnoAssist Backend
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, validator
from enum import Enum


class UserRoleEnum(str, Enum):
    """User role enumeration"""
    DOCTOR = "doctor"
    NURSE = "nurse"
    ADMIN = "admin"
    STUDENT = "student"


class UserStatusEnum(str, Enum):
    """User status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class UserProfile(BaseModel):
    """User profile information"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    specialty: Optional[str] = None
    license_number: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    
    @property
    def full_name(self) -> str:
        """Get full name"""
        return f"{self.first_name} {self.last_name}"


class UserModel(BaseModel):
    """User model for database storage"""
    id: Optional[str] = None  # Auto-generated
    email: EmailStr = Field(..., description="User email address")
    hashed_password: str = Field(..., description="Hashed password")
    role: UserRoleEnum = UserRoleEnum.DOCTOR
    status: UserStatusEnum = UserStatusEnum.PENDING_VERIFICATION
    profile: UserProfile
    is_verified: bool = False
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


# Authentication Request/Response Models
class UserRegistrationRequest(BaseModel):
    """Request model for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)
    profile: UserProfile
    role: UserRoleEnum = UserRoleEnum.DOCTOR
    
    @validator("confirm_password")
    def passwords_match(cls, v, values):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v
    
    @validator("password")
    def validate_password_strength(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        # Simplified password validation for Phase 2
        
        if not (has_upper and has_lower and has_digit):
            raise ValueError(
                "Password must contain at least one uppercase letter, "
                "one lowercase letter, and one digit"
            )
        
        return v


class UserLoginRequest(BaseModel):
    """Request model for user login"""
    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """Response model for authentication tokens"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None


class UserResponse(BaseModel):
    """Response model for user data"""
    success: bool = True
    data: UserModel
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class UserListResponse(BaseModel):
    """Response model for user list"""
    success: bool = True
    data: List[UserModel]
    total: int
    page: int = 1
    per_page: int = 50
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class LoginResponse(BaseModel):
    """Response model for successful login"""
    success: bool = True
    data: dict = Field(..., description="Contains user info and tokens")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class UserUpdateRequest(BaseModel):
    """Request model for updating user profile"""
    profile: Optional[UserProfile] = None
    role: Optional[UserRoleEnum] = None
    status: Optional[UserStatusEnum] = None


class PasswordChangeRequest(BaseModel):
    """Request model for password change"""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_new_password: str = Field(..., min_length=8, max_length=128)
    
    @validator("confirm_new_password")
    def passwords_match(cls, v, values):
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("New passwords do not match")
        return v
    
    @validator("new_password")
    def validate_password_strength(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        # Simplified password validation for Phase 2
        
        if not (has_upper and has_lower and has_digit):
            raise ValueError(
                "Password must contain at least one uppercase letter, "
                "one lowercase letter, and one digit"
            )
        
        return v


class PasswordResetRequest(BaseModel):
    """Request model for password reset"""
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    """Request model for password reset confirmation"""
    token: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_new_password: str = Field(..., min_length=8, max_length=128)
    
    @validator("confirm_new_password")
    def passwords_match(cls, v, values):
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("Passwords do not match")
        return v


class RefreshTokenRequest(BaseModel):
    """Request model for token refresh"""
    refresh_token: str = Field(..., min_length=1)


# JWT Token Models
class TokenData(BaseModel):
    """Token data for JWT payload"""
    sub: str  # Subject (user ID)
    email: str
    role: str
    exp: int  # Expiration timestamp
    iat: int  # Issued at timestamp
    type: str = "access"  # Token type (access or refresh)


class CurrentUser(BaseModel):
    """Current authenticated user model"""
    id: str
    email: EmailStr
    role: UserRoleEnum
    profile: UserProfile
    is_verified: bool
    
    class Config:
        from_attributes = True