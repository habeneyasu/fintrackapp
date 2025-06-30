from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.features.income.service import IncomeService
from app.features.income.schemas import IncomeCreate, IncomeResponse, IncomeUpdate



income_router = APIRouter(
    prefix="/api/v1/incomes",
    tags=["Income"],
    responses={404: {"description": "Not found"}}
)
@income_router.post("/createIncome", response_model=IncomeResponse)
async def create_income(
    income: IncomeCreate, 
    db: AsyncSession = Depends(get_db)
):
    service = IncomeService(db)
    try:
        return await service.create_income(income)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@income_router.get("/getIncomeById/{income_id}", response_model=IncomeResponse)
async def read_income(income_id: str, db: AsyncSession = Depends(get_db)):
    service = IncomeService(db)
    income = await service.get_income(income_id)
    if not income:
        raise HTTPException(status_code=404, detail="Income not found")
    return income

@income_router.get("/getIncomeByUserId/{user_id}", response_model=List[IncomeResponse])
async def list_user_incomes(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Clean the user_id by stripping whitespace and converting to UUID
        clean_user_id = str(UUID(user_id.strip()))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid user ID format: {str(e)}"
        )
    
    service = IncomeService(db)
    return await service.list_incomes(clean_user_id, skip, limit)

@income_router.put("/updateIncome/{income_id}", response_model=IncomeResponse)
async def update_income(
    income_id: str,
    income: IncomeUpdate,
    db: AsyncSession = Depends(get_db)
):
    service = IncomeService(db)
    updated_income = await service.update_income(income_id, income)
    if not updated_income:
        raise HTTPException(status_code=404, detail="Income not found")
    return updated_income

@income_router.delete("/deleteIncome/{income_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_income(income_id: str, db: AsyncSession = Depends(get_db)):
    service = IncomeService(db)
    success = await service.delete_income(income_id)
    if not success:
        raise HTTPException(status_code=404, detail="Income not found")
    return None