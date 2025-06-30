from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)

class UserCreate(UserBase):
    username: str = Field(..., min_length=3, max_length=20, 
                         pattern=r'^[a-zA-Z0-9_]+$')
    password: str = Field(..., min_length=8)
    phone_number: Optional[str] = Field(
        None, 
        max_length=20,
        pattern=r'^\+?[1-9]\d{1,14}$'  # E.164 format
    )

    @field_validator('username')
    def validate_username(cls, v):
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v

class UserResponse(UserBase):
    id: str
    username: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
class UserLogin(BaseModel):
    """Schema for login requests"""
    email_or_username: str = Field(..., description="Can be either email or username")
    password: str = Field(..., min_length=8)

    @field_validator('email_or_username')
    def validate_identifier(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Identifier cannot be empty")
        return v

class TokenBase(BaseModel):
    """Base token response schema"""
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime

class TokenResponse(TokenBase):
    """Full token response with refresh token"""
    access_token: str
    user: UserResponse  # Reuses your existing UserResponse