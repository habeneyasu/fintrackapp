from datetime import datetime
from decimal import Decimal
import re
from uuid import UUID as uuid_uuid
import uuid  # Correct import from standard library
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
            # Remove all non-hex characters (including '0x' prefix and hyphens)
            clean = re.sub(r'[^0-9a-fA-F]', '', v)
            
            # Check length after cleaning
            if len(clean) != 32:
                raise ValueError(f"Expected 32 hex chars, got {len(clean)} after cleaning")
                
            # Convert to UUID object to validate
            # This is the most reliable validation
            uuid_obj = uuid.UUID(hex=clean)
            
            # Return the original input to preserve formatting
            return v
            
        except ValueError as e:
            raise ValueError(
                "Invalid UUID format. Valid examples:\n"
                "- 3d7d9ed3-f621-4ff5-9edb-5d032ac18683\n"
                "- 0x3D7D9ED3F6214FF59EDB5D032AC18683\n"
                "- 3D7D9ED3F6214FF59EDB5D032AC18683\n"
                f"Validation error: {str(e)}"
            )
    
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
                return str(uuid_uuid(bytes=v))  # Now using correct UUID class
            except ValueError:
                return v.hex()
        return v
    
    class Config:
        from_attributes = True  # Updated from from_attributes in Pydantic v2
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v)
        }