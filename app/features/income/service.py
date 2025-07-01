from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.features.auth.models import User
from app.features.income.models import Income
from app.features.income.schemas import IncomeCreate, IncomeUpdate, IncomeResponse
import uuid

class IncomeService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_income(self, income_data: IncomeCreate):
        try:
            # Convert UUID to binary
            user_id_bin = Income.uuid_to_bin(income_data.user_id)
            
            # Check if user exists
            user_exists = await self.db.execute(
                select(1).where(User.id == user_id_bin)
            )
            if not user_exists.scalar():
                raise HTTPException(
                    status_code=404,
                    detail=f"User with ID {income_data.user_id} not found"
                )

            # Proceed with creation
            new_income = Income(
                user_id=user_id_bin,
                source=income_data.source,
                amount=income_data.amount,
                frequency=income_data.frequency,
                notes=income_data.notes
            )
            
            self.db.add(new_income)
            await self.db.commit()
            await self.db.refresh(new_income)
            return new_income
            
        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=400, detail=str(e))
    
    async def get_income(self, income_id: str) -> Optional[Income]:
        result = await self.db.execute(
            select(Income).where(Income.id == uuid.UUID(income_id).bytes)
        )
        return result.scalar_one_or_none()
    
    async def list_incomes(
        self, 
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Income]:
        result = await self.db.execute(
            select(Income)
            .where(Income.user_id == uuid.UUID(user_id).bytes)
            .offset(skip)
            .limit(limit)
            .order_by(Income.created_at.desc())
        )
        return result.scalars().all()
    
    async def update_income(
        self, 
        income_id: str,
        income_data: IncomeUpdate
    ) -> Optional[Income]:
        income = await self.get_income(income_id)
        if not income:
            return None
        
        update_data = income_data.dict(exclude_unset=True)
        if 'frequency' in update_data:
            update_data['is_recurring'] = update_data['frequency'] != "One-time"
        
        for field, value in update_data.items():
            setattr(income, field, value)
        
        await self.db.commit()
        await self.db.refresh(income)
        return income
    
    async def delete_income(self, income_id: str) -> bool:
        income = await self.get_income(income_id)
        if not income:
            return False
        
        await self.db.delete(income)
        await self.db.commit()
        return True
    
    @staticmethod
    async def get_incomes_by_user(
        user_id: str,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> list[IncomeResponse]:
        try:
            # Normalize the UUID first
            if not user_id:
                raise HTTPException(status_code=422, detail="User ID cannot be empty")
                
            # Remove 0x prefix if exists
            clean_uuid = user_id[2:] if user_id.startswith('0x') else user_id
            clean_uuid = clean_uuid.replace('-', '').lower()
            
            # Validate length
            if len(clean_uuid) != 32:
                raise HTTPException(
                    status_code=422,
                    detail=f"Invalid UUID length after cleaning: {clean_uuid}"
                )
            
            # Convert to binary
            uuid_bytes = uuid.UUID(hex=clean_uuid).bytes
            
            # Query database
            result = await db.execute(
                select(Income)
                .where(Income.user_id == uuid_bytes)
                .offset(skip)
                .limit(limit)
            )
            return [IncomeResponse.model_validate(i) for i in result.scalars()]
            
        except ValueError as e:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid UUID format: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Database error: {str(e)}"
            )