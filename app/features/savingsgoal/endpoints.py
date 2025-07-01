import re
from uuid import UUID
from fastapi import APIRouter, Query, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

# Your own imports
from app.core.database import get_db
from app.features.savingsgoal.models import SavingsGoal
from app.features.savingsgoal.schema import SavingsGoalCreate, SavingsGoalResponse
from app.features.savingsgoal.service import SavingsGoalService





# Also your uuid_to_binary function (same as uuid_to_bin)
def uuid_to_binary(u: UUID) -> bytes:
    return u.bytes

router = APIRouter()


router = APIRouter(prefix="/api/v1/savings-goals", tags=["Savings Goals"])

def parse_any_uuid(uuid_str: str) -> UUID:
    """
    Universal UUID parser that handles:
    - Standard format (with hyphens)
    - Raw hex (no hyphens)
    - 0x-prefixed hex
    """
    try:
        # Remove 0x prefix if exists
        clean_str = re.sub(r'^0x', '', uuid_str, flags=re.IGNORECASE)
        
        # Remove all hyphens
        clean_str = clean_str.replace('-', '')
        
        # Validate length (32 chars) and hex characters only
        if len(clean_str) != 32 or not re.match(r'^[0-9a-f]+$', clean_str, re.IGNORECASE):
            raise ValueError("Invalid UUID format")
            
        # Reconstruct in standard 8-4-4-4-12 format
        formatted = f"{clean_str[:8]}-{clean_str[8:12]}-{clean_str[12:16]}-{clean_str[16:20]}-{clean_str[20:]}"
        return UUID(formatted)
    except (ValueError, AttributeError) as e:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid UUID format. Accepts: standard (with hyphens), raw hex, or 0x-prefixed. Error: {str(e)}"
        )

@router.get("/", response_model=List[SavingsGoalResponse])
async def get_savings_goals(
    user_id: str = Query(
        ..., 
        description="User ID (accepts: standard UUID, raw hex, or 0x-prefixed)",
        example="08133511-671d-4165-a2fd-a896b5c81fd3",
        regex=r"^(0x)?[0-9a-fA-F]{8}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{12}$"
    ),
    db: AsyncSession = Depends(get_db)
):
    try:
        user_uuid = parse_any_uuid(user_id)
        result = await db.execute(
            select(SavingsGoal).where(SavingsGoal.user_id == uuid_to_binary(user_uuid))
        )
        return result.scalars().all()
    except HTTPException:
        raise  # Re-raise validation errors
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch savings goals: {str(e)}"
        )
    
@router.post("/", response_model=SavingsGoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    goal: SavingsGoalCreate, db: AsyncSession = Depends(get_db)
):
    try:
        new_goal = await SavingsGoalService.create_savings_goal(goal, db)
        return new_goal
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/checkSavingGoal", response_model=dict)
async def check_saving_goal(
    user_id: str = Query(..., description="User ID in any UUID format"),
    db: AsyncSession = Depends(get_db)
        ):
    """
    Updates savings goals with monthly net income
    """
    try:
        # Clean and validate the user_id first
        clean_user_id = re.sub(r'[^0-9a-fA-F]', '', user_id).lower()
        if len(clean_user_id) != 32:
            raise HTTPException(status_code=422, detail="Invalid UUID format")
            
        # Process the request
        result = await SavingsGoalService.update_savings_from_net(clean_user_id, db)
        
        # Explicitly commit if needed
        await db.commit()
        
        return result
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Savings goal update failed: {str(e)}")