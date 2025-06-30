from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from decimal import Decimal
from uuid import UUID
from datetime import datetime
from app.core.config import Type

class BudgetCategoryBase(BaseModel):
    name: str = Field(..., max_length=100, example="Groceries")
    budget_limit: Decimal = Field(..., gt=0, example=500.00)
    type: Type = Field(..., example="INCOME")
    description: Optional[str] = Field(None, example="Monthly grocery budget")
    
    # Add model configuration
    model_config = ConfigDict(
        json_encoders={
            UUID: lambda v: str(v),  # Ensure UUID serialization
            datetime: lambda v: v.isoformat(),  # Proper datetime format
            Decimal: lambda v: float(v)  # Convert Decimal to float for JSON
        }
    )

class BudgetCategoryCreate(BudgetCategoryBase):
    user_id: UUID = Field(..., example="a3c47a68-9db9-42f5-8a30-16c2d343ddf9")

class BudgetCategoryResponse(BudgetCategoryBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    
    # Pydantic v2 config (replaces old Config class)
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            UUID: lambda v: str(v),
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }
    )