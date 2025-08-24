from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator
import re

# Token Schemas
class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    """Schema for JWT token payload."""
    username: Optional[str] = None
    user_id: Optional[int] = None
    exp: Optional[datetime] = None

# User Base Schemas
class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$')

# Request Schemas
class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(..., min_length=8)

    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v

class UserLogin(BaseModel):
    """Schema for user login."""
    email: str  # Can be either email or username
    password: str

class UserUpdate(BaseModel):
    """Schema for updating user information."""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(
        None, 
        min_length=3, 
        max_length=50, 
        pattern=r'^[a-zA-Z0-9_]+$'
    )
    current_password: Optional[str] = None
    new_password: Optional[str] = Field(None, min_length=8)
    preferences: Optional[Dict[str, Any]] = None

    @validator('new_password')
    def password_strength(cls, v, values):
        if v is None:
            return v
            
        if not values.get('current_password'):
            raise ValueError('Current password is required to set a new password')
            
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v

# Response Schemas
class UserPublic(BaseModel):
    """Public user profile information."""
    id: int
    username: str
    created_at: datetime

    class Config:
        orm_mode = True

class UserResponse(UserPublic):
    """Extended user information (for the user themselves)."""
    email: EmailStr
    is_active: bool
    preferences: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True

# Token Refresh Schema
class TokenRefresh(BaseModel):
    """Schema for token refresh request."""
    refresh_token: str
