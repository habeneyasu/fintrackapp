from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from . import schemas, service
from app.core.database import get_db
from app.core.security import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", response_model=schemas.UserResponse, status_code=201)
async def register(
    user_data: schemas.UserCreate, 
    db: AsyncSession = Depends(get_db)
):
    try:
        return await service.UserService(db).register_user(user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me", response_model=schemas.UserResponse)
async def get_me(
    current_user: schemas.UserResponse = Depends(get_current_user)
):
    return current_user

@router.get("/by-phone/{phone}", response_model=schemas.UserResponse)
async def get_by_phone(
    phone: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user)  # Auth required
):
    user = await service.UserService(db).get_by_phone(phone)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user