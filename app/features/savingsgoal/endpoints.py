from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from app.core.database import get_db
from app.features.savingsgoal.schema import SavingsGoalResponse
from app.features.savingsgoal.models import SavingsGoal
from sqlalchemy import select

router = APIRouter(prefix="/savings-goals", tags=["Savings Goals"])

@router.get("/", response_model=List[SavingsGoalResponse])
async def get_savings_goals(
    user_id: UUID = Query(..., description="User ID to filter savings goals"),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(
            select(SavingsGoal).where(SavingsGoal.user_id == uuid_to_binary(user_id))
        )
        goals = result.scalars().all()
        return goals
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch savings goals")
