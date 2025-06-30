from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import UserCreate, UserResponse, UserLogin, TokenResponse
from .service import AuthService
from app.core.database import get_db
from app.core.exceptions import ConflictError, AuthenticationError, AccountLockedError

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
    responses={
        400: {"description": "Bad request"},
        401: {"description": "Unauthorized"},
        409: {"description": "Conflict"}
    }
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Validation error"},
        409: {"description": "Email or username already exists"}
    }
)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user account
    
    - **email**: must be unique and valid
    - **username**: 3-20 chars, alphanumeric
    - **password**: minimum 8 characters
    - **phone_number**: optional, E.164 format
    """
    service = AuthService(db)
    try:
        user = await service.register_user(user_data)
        return user.to_response()
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "Invalid credentials or inactive account"}
    }
)
async def login(
    request: Request,
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return access token
    
    - **email_or_username**: Can be either email or username
    - **password**: User's password
    """
    service = AuthService(db)
    try:
        user = await service.authenticate_user(
            identifier=login_data.email_or_username,
            password=login_data.password
        )
        return await service.generate_token_response(user)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except AccountLockedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )