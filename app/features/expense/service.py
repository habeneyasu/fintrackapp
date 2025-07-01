from uuid import UUID
from decimal import Decimal
import uuid
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.features.expense.models import Expense
from app.features.expense.schemas import ExpenseCreate, ExpenseResponse
from app.core.exceptions import NotFoundError, ConflictError
from app.core.logger import logger
from app.features.category.models import BudgetCategory  

class ExpenseService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_expense(self, expense_data: ExpenseCreate) -> ExpenseResponse:
        """
        Register a new expense with validation
        Args:
            expense_data: Validated expense data
        Returns:
            ExpenseResponse: The created expense
        Raises:
            NotFoundError: If category/user doesn't exist
            ConflictError: If duplicate expense detected
        """
        try:
            # Validate category exists
            if not await self._validate_category(expense_data.category_id):
                raise NotFoundError("Specified category does not exist")

            # Convert UUIDs to binary format
            expense_dict = expense_data.model_dump()
            expense_dict["user_id"] = self._uuid_to_binary(expense_dict["user_id"])
            expense_dict["category_id"] = self._uuid_to_binary(expense_dict["category_id"])

            # Create and save expense
            db_expense = Expense(**expense_dict)
            self.db.add(db_expense)
            await self.db.commit()
            await self.db.refresh(db_expense)

            logger.info(
                f"Created expense {db_expense.uuid} for user {expense_data.user_id}",
                extra={
                    "amount": expense_data.amount,
                    "category": expense_data.category_id
                }
            )

            return await self._expense_to_response(db_expense)

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Expense creation failed: {str(e)}")
            raise

    async def _validate_category(self, category_id: UUID) -> bool:
        """Check if category exists"""
       
        result = await self.db.execute(
            select(BudgetCategory)
            .where(BudgetCategory.id == self._uuid_to_binary(category_id))
        )
        return result.scalar_one_or_none() is not None

    def _uuid_to_binary(self, uuid_input) -> bytes:
        """Handle multiple UUID formats (string, UUID object, bytes)"""
        if isinstance(uuid_input, bytes):
            return uuid_input
        if isinstance(uuid_input, UUID):
            return uuid_input.bytes
        if isinstance(uuid_input, str):
            if uuid_input.startswith('0x'):
                return bytes.fromhex(uuid_input[2:])
            return UUID(uuid_input).bytes
        raise ValueError("Invalid UUID format")

    async def _expense_to_response(self, expense: Expense) -> ExpenseResponse:
        """Convert DB model to Pydantic response"""
        return ExpenseResponse(
            id=expense.id,
            user_id=expense.user_id,
            category_id=expense.category_id,
            name=expense.name,
            amount=expense.amount,
            remark=expense.remark,
            is_essential=expense.is_essential,
            payment_method=expense.payment_method,
            created_at=expense.created_at,
            updated_at=expense.updated_at
        )
    
    async def get_all_expenses(self, user_id: UUID) -> list[ExpenseResponse]:
        """
        Retrieve all expenses for a specific user
        Args:
            user_id: UUID of the user
        Returns:
            list[ExpenseResponse]: List of user's expenses
        Raises:
            NotFoundError: If user has no expenses
        """
        try:
            result = await self.db.execute(
                select(Expense)
                .where(Expense.user_id == self._uuid_to_binary(user_id))
            )
            expenses = result.scalars().all()
            
            if not expenses:
                raise NotFoundError("No expenses found for this user")
                
            logger.info(f"Retrieved {len(expenses)} expenses for user {user_id}")
            return [await self._expense_to_response(exp) for exp in expenses]
            
        except Exception as e:
            logger.error(f"Failed to fetch expenses: {str(e)}")
            raise
    
     

    @staticmethod
    async def get_expenses_by_user(
        user_id: str,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> list[ExpenseResponse]:
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
                select(Expense)
                .where(Expense.user_id == uuid_bytes)
                .offset(skip)
                .limit(limit)
            )
            return [ExpenseResponse.model_validate(i) for i in result.scalars()]
            
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