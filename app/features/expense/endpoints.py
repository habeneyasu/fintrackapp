from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.expense.schemas import ExpenseCreate, ExpenseResponse
from app.features.expense.service import ExpenseService
from app.core.database import get_db
from app.core.exceptions import NotFoundError

router = APIRouter(
    prefix="/api/v1/expenses",
    tags=["Expenses"],
    responses={
        404: {"description": "Resource not found"},
        409: {"description": "Conflict - duplicate entry"}
    }
)

@router.post(
    "/",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Validation error"},
        404: {"description": "Category not found"}
    }
)
async def create_expense(
    expense_data: ExpenseCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new expense
    
    - **name**: Expense name (1-100 chars)
    - **amount**: Positive decimal value
    - **category_id**: Valid budget category UUID
    - **payment_method**: CREDIT_CARD | DEBIT_CARD | CASH | etc.
    - **is_essential**: Mark as essential/non-essential
    """
    service = ExpenseService(db)
    return await service.create_expense(expense_data)

@router.get(
    "/",
    response_model=list[ExpenseResponse],
    status_code=status.HTTP_200_OK,
    responses={
        400: {"description": "Invalid UUID format"},
        404: {"description": "No expenses found"},
        500: {"description": "Internal server error"}
    }
)
async def get_all_expenses(
    user_id: str = Query(..., description="User ID in UUID format", example="550e8400-e29b-41d4-a716-446655440000"),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all expenses for a specific user
    
    - **user_id**: UUID of the user (must be valid UUID format)
    - Returns: List of all expense records
    """
    try:
        # Validate UUID format
        uuid_obj = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format"
        )

    service = ExpenseService(db)
    return await service.get_all_expenses(uuid_obj)


@router.get("/getExpenseByUserId", response_model=list[ExpenseResponse]) 
async def read_expenses(
    user_id: str = Query(..., example="0x3D7D9ED3F6214FF59EDB5D032AC18683"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    db: AsyncSession = Depends(get_db)
      ):
    """
    Get expenses by user ID - accepts:
    - 0x-prefixed: 0x3D7D9ED3F6214FF59EDB5D032AC18683
    - Standard UUID: 3D7D9ED3-F621-4FF5-9EDB-5D032AC18683
    - Raw hex: 3D7D9ED3F6214FF59EDB5D032AC18683
    """
    return await ExpenseService.get_expenses_by_user(user_id, db, skip, limit)