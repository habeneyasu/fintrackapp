from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid

class CurrencyEnum(str, Enum):
    ETB = "ETB"
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"

class UserBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50, example="John")
    middle_name: Optional[str] = Field(None, max_length=50, example="Michael")
    last_name: str = Field(..., min_length=1, max_length=50, example="Doe")
    email: EmailStr = Field(..., example="user@example.com")
    phone_number: str = Field(
        ...,
        pattern=r"^\+?[1-9]\d{1,14}$",
        example="+251911234567"
    )
    currency: CurrencyEnum = Field(default=CurrencyEnum.ETB)

class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        pattern=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$",
        example="SecurePass123",
        description="Must contain uppercase, lowercase, and numbers"
    )

    @field_validator('phone_number')
    def validate_phone(cls, v):
        if not v.startswith('+'):
            return f"+{v}"  # Auto-prepend + if missing
        return v

class UserLogin(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., example="SecurePass123")

class UserResponse(UserBase):
    id: str = Field(..., example=str(uuid.uuid4()))
    is_active: bool = Field(default=True)
    created_at: datetime = Field(..., example="2023-01-01T00:00:00Z")
    updated_at: datetime = Field(..., example="2023-01-01T00:00:00Z")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v)
        }