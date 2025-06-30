from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from app.features.auth.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import Optional, Tuple
from app.core.database import get_db
from app.core.database import DatabaseSessionDep

# Configure Argon2 with strong parameters
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__time_cost=3,
    argon2__memory_cost=65536,  # 64MB
    argon2__parallelism=4,
    argon2__hash_len=32,
    argon2__salt_size=16
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login",
    scopes={"access": "Standard access", "refresh": "Refresh token access"}
)

class TokenService:
    @staticmethod
    def create_tokens(user_data: dict) -> dict:
        """Generate both access and refresh tokens"""
        now = datetime.utcnow()
        base_claims = {
            "sub": str(user_data["uuid"]),
            "iss": settings.TOKEN_ISSUER,
            "aud": settings.TOKEN_AUDIENCE,
            "iat": now
        }

        access_token = jwt.encode(
            {
                **base_claims,
                "type": "access",
                "email": user_data["email"],
                "username": user_data["username"],
                "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            },
            settings.SECRET_KEY.get_secret_value(),
            algorithm=settings.ALGORITHM
        )

        refresh_token = jwt.encode(
            {
                **base_claims,
                "type": "refresh",
                "exp": now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
            },
            settings.SECRET_KEY.get_secret_value(),
            algorithm=settings.ALGORITHM
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        }

    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY.get_secret_value(),
                algorithms=[settings.ALGORITHM],
                audience=settings.TOKEN_AUDIENCE,
                issuer=settings.TOKEN_ISSUER
            )
            return payload
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"}
            )

async def get_current_user(
    db: DatabaseSessionDep,  # No default comes first
    token: str = Depends(oauth2_scheme)  # Default comes after
) -> User:  # Make sure User is a Pydantic model
    """Dependency to get authenticated user from JWT"""
    payload = TokenService.verify_token(token)
    
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )

    try:
        user_uuid = UUID(payload["sub"])
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user identifier"
        )

    result = await db.execute(select(User).where(User.id == user_uuid.bytes))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency to verify user is active"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )
    return current_user