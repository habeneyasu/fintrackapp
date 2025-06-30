from typing import Optional
import uuid
from datetime import datetime
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import User
from .schemas import UserCreate, TokenResponse
from app.core.exceptions import (
    ConflictError,
    AuthenticationError,
    AccountLockedError
)
from app.core.security import TokenService  # From the security.py we created earlier

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.pwd_context = CryptContext(
            schemes=["bcrypt"], 
            deprecated="auto",
            bcrypt__rounds=12
        )

    async def register_user(self, user_data: UserCreate) -> User:
        """
        Register a new user with normalized data and password hashing
        """
        existing = await self._check_existing_user(
            user_data.email, 
            user_data.username
        )
        if existing:
            raise ConflictError("Email or username already registered")

        user = User(
            email=user_data.email.lower().strip(),
            username=user_data.username.lower().strip(),
            first_name=user_data.first_name.strip(),
            last_name=user_data.last_name.strip(),
            password_hash=self.get_password_hash(user_data.password),
            phone_number=self._normalize_phone(user_data.phone_number),
            is_active=True  # Default to active on registration
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def authenticate_user(self, identifier: str, password: str) -> User:
        """
        Authenticate user and return user object if valid
        """
        user = await self._get_user_by_identifier(identifier.lower().strip())
        
        if not user or not self.verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid credentials")
        
        if not user.is_active:
            raise AccountLockedError("Account is inactive")
        
        # Update last login timestamp
        user.last_login_at = datetime.utcnow()
        await self.db.commit()
        
        return user

    async def generate_token_response(self, user: User) -> TokenResponse:
        """Generate JWT tokens and prepare the response"""
        user_data = {
            "uuid": user.uuid,
            "email": user.email,
            "username": user.username
        }
        tokens = TokenService.create_tokens(user_data)
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type="bearer",
            expires_at=tokens["expires_at"],
            user=user.to_response()
        )

    # Helper Methods
    async def _check_existing_user(self, email: str, username: str) -> bool:
        result = await self.db.execute(
            select(User).where(
                (User.email == email.lower()) | 
                (User.username == username.lower())
            )
        )
        return result.scalar_one_or_none() is not None

    async def _get_user_by_identifier(self, identifier: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(
                (User.email == identifier) | 
                (User.username == identifier)
            )
        )
        return result.scalar_one_or_none()

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def _normalize_phone(self, phone: Optional[str]) -> Optional[str]:
        if not phone:
            return None
        return ''.join(filter(str.isdigit, phone.strip()))