from pydantic import BaseModel, Field, constr
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
    saved_amount: Decimal = Field(default=Decimal("0.00"), ge=0.00)

class SavingsGoalCreate(SavingsGoalBase):
    user_id: UUID

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
