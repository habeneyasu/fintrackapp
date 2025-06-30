from typing import Optional
from uuid import UUID
from app.core.exceptions import NotFoundError
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select

from app.features.category.models import BudgetCategory
from app.features.category.schemas import BudgetCategoryCreate, BudgetCategoryResponse
from app.core.logger import logger
from app.core.database import get_db


class BudgetCategoryService:
    """Service layer for budget category operations"""

    def __init__(self, db: AsyncSession = Depends(get_db)): 
        self.db = db

    async def create_category(
        self, category_data: BudgetCategoryCreate
    ) -> BudgetCategoryResponse:
        try:
            db_category = BudgetCategory(
                **category_data.dict(exclude={"user_id"}),
                user_id=self._uuid_to_binary(category_data.user_id)
            )
            self.db.add(db_category)
            await self.db.commit()
            await self.db.refresh(db_category)

            logger.info(f"Created budget category {db_category.id} for user {category_data.user_id}")
            return BudgetCategoryResponse.model_validate(db_category, from_attributes=True)

        except ValueError as ve:
            logger.error(f"Validation error: {str(ve)}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create category")

    async def get_category_by_id(self, category_id: str) -> BudgetCategoryResponse:
        """Handle both string and UUID inputs"""
        try:
            # Convert input to UUID bytes
            if isinstance(category_id, UUID):
                uuid_bytes = category_id.bytes
            elif category_id.startswith('0x'):
                uuid_bytes = bytes.fromhex(category_id[2:])
            else:
                uuid_bytes = UUID(category_id).bytes
                
            # Query with binary UUID
            category = await self.db.execute(
                select(BudgetCategory)
                .where(BudgetCategory.id == uuid_bytes)
            )
            category = category.scalar_one_or_none()
            
            if not category:
                raise NotFoundError("Category not found")
                
            return self._category_to_response(category)
            
        except (ValueError, AttributeError) as e:
            raise ValueError(f"Invalid ID format: {str(e)}")
    

    async def get_categories_by_user(self, user_id: str | UUID) -> list[BudgetCategoryResponse]:
        """Retrieve all categories for a user with flexible ID input"""
        try:
            # Convert to binary UUID for query
            user_id_bytes = BudgetCategory.uuid_to_bin(user_id)
            
            # Execute query
            result = await self.db.execute(
                select(BudgetCategory)
                .where(BudgetCategory.user_id == user_id_bytes)
                .order_by(BudgetCategory.created_at.desc())  # Newest first
            )
            categories = result.scalars().all()
            
            if not categories:
                raise NotFoundError("No categories found for this user")
                
            return [self._category_to_response(cat) for cat in categories]
            
        except ValueError as e:
            raise ValueError(f"Invalid user ID format: {str(e)}")

    def _category_to_response(self, category: BudgetCategory) -> BudgetCategoryResponse:
        """Convert DB model to Pydantic response"""
        return BudgetCategoryResponse(
            id=category.id,
            user_id=category.user_id,
            name=category.name,
            budget_limit=category.budget_limit,
            type=category.type,
            description=category.description,
            created_at=category.created_at,
            updated_at=category.updated_at
        )



    def _uuid_to_binary(self, uuid_value):
        """Converts UUID to MySQL binary format"""
        if isinstance(uuid_value, str):
            return UUID(uuid_value).bytes
        elif isinstance(uuid_value, UUID):
            return uuid_value.bytes
        raise ValueError("Input must be a UUID string or UUID object")
