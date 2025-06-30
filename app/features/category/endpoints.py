from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.category.schemas import BudgetCategoryCreate, BudgetCategoryResponse
from app.features.category.service import BudgetCategoryService
from app.core.database import get_db
from app.core.exceptions import CredentialValidationError, NotFoundError

router = APIRouter(
    prefix="/api/v1/budget-categories",
    tags=["Budget Categories"],
    responses={
        400: {"description": "Bad request"},
        404: {"description": "Not found"},
        403: {"description": "Forbidden"}
    }
)

class ConflictError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )

@router.post(
    "/",
    response_model=BudgetCategoryResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Validation error"},
        403: {"description": "Insufficient permissions"},
        409: {"description": "Conflict (duplicate category)"},
        422: {"description": "Unprocessable entity"}
    }
)
async def create_category(
    request: Request,
    category_data: BudgetCategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new budget category
    
    - **name**: 1-100 characters
    - **budget_limit**: Positive decimal value
    - **type**: INCOME or EXPENSE
    - **description**: Optional description
    - **user_id**: Owner's UUID
    """
    service = BudgetCategoryService(db)
    try:
        return await service.create_category(category_data)
    except CredentialValidationError as e:
        raise CredentialValidationError(detail=str(e))
    except ConflictError as e:
        raise ConflictError(detail=f"Budget category already exists: {str(e)}")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(e)}"
        )
    
@router.get(
    "/{category_id}",
    response_model=BudgetCategoryResponse,
    responses={
        400: {"description": "Invalid category ID format"},
        404: {"description": "Category not found"},
        403: {"description": "Unauthorized access"}
    }
)
async def get_category_by_id(
    category_id: str,  # Accept raw string input
    db: AsyncSession = Depends(get_db)
):
    """
    Get a budget category by ID
    
    Parameters:
    - **category_id**: Raw UUID bytes string (e.g., 0xBE92213C8CAE46238B3F826D43A9A23A)
                      or standard UUID format (a3c47a68-9db9-42f5-8a30-16c2d343ddf9)
    
    Returns:
    - Full category details
    """
    service = BudgetCategoryService(db)
    try:
        return await service.get_category_by_id(category_id)  # Pass raw string
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except NotFoundError as e:
        raise NotFoundError(detail=str(e))
    
@router.get(
    "/user/{user_id}",
    response_model=list[BudgetCategoryResponse],
    responses={
        400: {"description": "Invalid UUID format"},
        404: {"description": "No categories found for user"},
        403: {"description": "Unauthorized access"}
    }
)
async def get_categories_by_user(
    user_id: str,  # Accepts both UUID strings and byte strings
    db: AsyncSession = Depends(get_db)
):
    """
    Get all budget categories for a specific user
    
    Parameters:
    - **user_id**: Can be either:
      - Standard UUID format (a3c47a68-9db9-42f5-8a30-16c2d343ddf9)
      - Raw byte string format (0xBE92213C8CAE46238B3F826D43A9A23A)
    
    Returns:
    - List of all categories belonging to the user
    """
    service = BudgetCategoryService(db)
    try:
        return await service.get_categories_by_user(user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except NotFoundError as e:
        raise NotFoundError(detail=str(e))
