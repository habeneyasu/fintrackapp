from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from typing import Optional
from app.core.config import PaymentMethod

class ExpenseBase(BaseModel):
    name: str = Field(..., max_length=100, example="Groceries")
    amount: Decimal = Field(..., gt=0, example=150.75)
    remark: Optional[str] = Field(None, example="Weekly supermarket shopping")
    is_essential: bool = Field(default=True, example=True)
    payment_method: PaymentMethod = Field(..., example="CREDIT_CARD")

    model_config = ConfigDict(
        json_encoders={
            Decimal: lambda v: float(v),
            PaymentMethod: lambda v: v.value
        }
    )

class ExpenseCreate(ExpenseBase):
    user_id: UUID = Field(..., example="a3c47a68-9db9-42f5-8a30-16c2d343ddf9")
    category_id: UUID = Field(..., example="b5d47a68-9db9-42f5-8a30-16c2d343ddf9")

class ExpenseUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    amount: Optional[Decimal] = Field(None, gt=0)
    remark: Optional[str] = None
    is_essential: Optional[bool] = None
    payment_method: Optional[PaymentMethod] = None
    category_id: Optional[UUID] = None

class ExpenseResponse(ExpenseBase):
    id: UUID
    user_id: UUID
    category_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            UUID: str,
            Decimal: float,
            datetime: lambda v: v.isoformat(),
            PaymentMethod: lambda v: v.value
        }
    )