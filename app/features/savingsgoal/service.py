import datetime
from decimal import Decimal
from uuid import UUID, uuid4
from typing import Optional, Dict
import uuid

from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.expense.models import Expense
from app.features.income.models import Income
from app.features.savingsgoal.models import SavingsGoal
from app.features.savingsgoal.schema import SavingsGoalCreate,SavingsGoalUpdate

class SavingsGoalService:
    """Service layer for savings goal operations with financial calculations"""

    @staticmethod
    def _validate_uuid(uuid_str: str) -> UUID:
        """Centralized UUID validation that handles all formats"""
        try:
            clean = uuid_str.lower().replace('0x', '').replace('-', '')
            if len(clean) != 32:
                raise ValueError("Invalid length")
            return UUID(hex=clean)
        except ValueError as e:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid UUID format: {uuid_str}. Must be 32-character hex (with optional 0x/hyphens)"
            )

    @staticmethod
    async def create_savings_goal(
        goal_data: SavingsGoalCreate, 
        db: AsyncSession
    ) -> SavingsGoal:
        """Creates a new savings goal with zero initial amount"""
        try:
            goal = SavingsGoal(
                id=uuid4().bytes,
                user_id=SavingsGoalService._validate_uuid(goal_data.user_id).bytes,
                name=goal_data.name,
                description=goal_data.description,
                target_amount=goal_data.target_amount,
                saved_amount=Decimal("0.00"),
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow()
            )
            db.add(goal)
            await db.commit()
            await db.refresh(goal)
            return goal
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create savings goal: {str(e)}"
            )

    @staticmethod
    async def calculate_monthly_net(
        user_id: str, 
        db: AsyncSession
    ) -> Decimal:
        """Calculates (income - expenses) for the last 30 days"""
        try:
            user_uuid = SavingsGoalService._validate_uuid(user_id).bytes
            date_threshold = datetime.datetime.utcnow() - datetime.timedelta(days=30)

            # Get total income
            income = await db.execute(
                select(func.coalesce(func.sum(Income.amount), Decimal('0')))
                .where(Income.user_id == user_uuid)
                .where(Income.created_at >= date_threshold)
            )
            
            # Get total expenses
            expenses = await db.execute(
                select(func.coalesce(func.sum(Expense.amount), Decimal('0')))
                .where(Expense.user_id == user_uuid)
                .where(Expense.created_at >= date_threshold)
            )

            return income.scalar_one() - expenses.scalar_one()

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Monthly net calculation failed: {str(e)}"
            )

    @staticmethod
    async def update_savings_from_net(self, user_id: str, db: AsyncSession):
        try:
            # Convert user_id to binary
            user_id_bin = uuid.UUID(hex=user_id).bytes
            
            # 1. Get user's net income
            income_stmt = select(func.sum(Income.amount)).where(
                Income.user_id == user_id_bin,
                Income.frequency == "MONTHLY"
            )
            income_result = await db.execute(income_stmt)
            net_income = income_result.scalar() or 0.0

            # 2. Get current savings goals
            goals_stmt = select(SavingsGoal).where(
                SavingsGoal.user_id == user_id_bin,
                SavingsGoal.is_active == True
            )
            goals_result = await db.execute(goals_stmt)
            goals = goals_result.scalars().all()

            # 3. Update each goal
            updates = []
            for goal in goals:
                # Your update logic here
                updates.append(goal)
            
            # Refresh objects if needed
            for goal in updates:
                await db.refresh(goal)
            
            return {
                "status": "success",
                "updated_goals": len(updates),
                "net_income_applied": net_income
            }
            
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=str(e))



    @staticmethod
    async def get_goals_by_user(
        user_id: str,
        db: AsyncSession
    ) -> list[SavingsGoal]:
        """Retrieves all savings goals for a user"""
        try:
            user_uuid = SavingsGoalService._validate_uuid(user_id).bytes
            result = await db.execute(
                select(SavingsGoal)
                .where(SavingsGoal.user_id == user_uuid)
            )
            return result.scalars().all()
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch savings goals: {str(e)}"
            )