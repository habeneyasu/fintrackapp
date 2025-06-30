from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.security import get_password_hash, verify_password
from .models import User
from .schemas import UserCreate
import uuid

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_user(self, user_data: UserCreate) -> User:
        # Check for existing email/phone
        existing_user = await self.db.execute(
            select(User).where(
                (User.email == user_data.email) | 
                (User.phone_number == user_data.phone_number)
            )
        )
        if existing_user.scalar_one_or_none():
            raise ValueError("Email or phone number already registered")

        # Create user
        db_user = User(
            **user_data.model_dump(exclude={"password"}),
            password_hash=get_password_hash(user_data.password)
        )
        self.db.add(db_user)
        await self.db.commit()
        return db_user

    async def authenticate(self, email: str, password: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user or not verify_password(password, user.password_hash):
            return None
        return user

    async def get_by_phone(self, phone: str) -> User | None:
        result = await self.db.execute(select(User).where(User.phone_number == phone))
        return result.scalar_one_or_none()