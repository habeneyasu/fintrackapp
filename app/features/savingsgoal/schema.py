from pydantic import BaseModel, Field, constr, validator
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from typing import Optional

ConstrainedStr100 = constr(strip_whitespace=True, min_length=1, max_length=100)
ConstrainedStr255 = constr(strip_whitespace=True, max_length=255)

class SavingsGoalBase(BaseModel):
    name: ConstrainedStr100
    description: Optional[ConstrainedStr255] = None
    target_amount: Decimal = Field(..., ge=0.01)
    saved_amount: Decimal = Field(..., ge=0.00)

class SavingsGoalCreate(SavingsGoalBase):
     user_id: str  # accept any string

@validator('user_id')
def validate_user_id(cls, v):
        try:
            clean = v.strip()

            # Remove 0x if present
            if clean.startswith('0x') or clean.startswith('0X'):
                clean = clean[2:]

            # Remove dashes
            clean = clean.replace('-', '')

            if len(clean) != 32 or not re.fullmatch(r'[0-9a-fA-F]{32}', clean):
                raise ValueError()

            # Try to convert to UUID to confirm validity
            _ = UUID(clean)
            return v
        except Exception:
            raise ValueError(
                f"user_id must be a valid UUID string, raw hex (32 chars), or a 0x-prefixed hex"
            )

class SavingsGoalUpdate(BaseModel):
    name: Optional[ConstrainedStr100] = None
    description: Optional[ConstrainedStr255] = None
    target_amount: Optional[Decimal] = Field(None, ge=0.01)
    saved_amount: Optional[Decimal] = Field(None, ge=0.00)

class SavingsGoalResponse(SavingsGoalBase):
    id: UUID
    user_id: UUID
    progress: float
    is_achieved: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
