from fastapi import APIRouter
from app.features.auth.endpoints import router as auth_router
from app.features.user.endpoints import router as user_router

router = APIRouter()
router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(user_router, prefix="/users", tags=["Users"])