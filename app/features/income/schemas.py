from datetime import datetime
from decimal import Decimal
from uuid import UUID  # Correct import from standard library
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from app.core.config import IncomeSource, IncomeFrequency

class IncomeBase(BaseModel):
    source: IncomeSource
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    frequency: IncomeFrequency = IncomeFrequency.MONTHLY
    notes: Optional[str] = Field(None, max_length=500)

class IncomeCreate(IncomeBase):
    user_id: str  # UUID string
    
    @field_validator('user_id')
    def validate_uuid(cls, v):
        try:
            return str(UUID(v))  # Validate UUID format
        except ValueError:
            raise ValueError("Invalid UUID format")
    
    class Config:
        json_encoders = {
            Decimal: lambda v: str(v)
        }

class IncomeUpdate(BaseModel):
    source: Optional[IncomeSource] = None
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    frequency: Optional[IncomeFrequency] = None
    notes: Optional[str] = Field(None, max_length=500)

class IncomeResponse(BaseModel):
    id: str
    user_id: str
    source: str
    amount: Decimal
    frequency: str
    is_recurring: bool
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    @field_validator('id', 'user_id', mode='before')
    def convert_binary_to_uuid(cls, v):
        if isinstance(v, bytes):
            try:
                return str(UUID(bytes=v))  # Now using correct UUID class
            except ValueError:
                return v.hex()
        return v
    
    class Config:
        from_attributes = True  # Updated from from_attributes in Pydantic v2
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v)
        }