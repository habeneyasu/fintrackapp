from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.features.income.models import Income
from app.features.income.schemas import IncomeCreate, IncomeUpdate, IncomeResponse
import uuid

class IncomeService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_income(self, income_data: IncomeCreate) -> Income:
         # Convert Pydantic model to dict and prepare for DB
        db_data = Income.prepare_for_db(income_data.dict())
        
        # Generate binary UUID for primary key
        db_data['id'] = uuid.uuid4().bytes
        
        # Set timestamps
        now = datetime.utcnow()
        db_data['created_at'] = now
        db_data['updated_at'] = now
        
        # Set is_recurring based on frequency
        db_data['is_recurring'] = db_data['frequency'] != 'One-time'
        
        income = Income(**db_data)
        self.db.add(income)
        await self.db.commit()
        await self.db.refresh(income)
        return income
    
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