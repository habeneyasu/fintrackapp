from typing import Annotated, AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.core.config import settings
from fastapi import Depends
import os
import asyncio

# Database URL construction with environment variables
DATABASE_URL = f"mysql+asyncmy://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

# Create async engine with retry logic
async def create_engine_with_retry():
    for attempt in range(5):
        try:
            engine = create_async_engine(
                DATABASE_URL,
                poolclass=NullPool,  # Important for Render's free tier
                pool_pre_ping=True,
                connect_args={
                    "connect_timeout": 10
                }
            )
            async with engine.begin() as conn:
                await conn.execute("SELECT 1")
            return engine
        except Exception as e:
            if attempt == 4:
                raise
            await asyncio.sleep(2 * attempt)

# Initialize engine on startup
engine = create_async_engine(DATABASE_URL, poolclass=NullPool)

# Session factory with explicit cleanup
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# Dependency with proper cleanup
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Type annotation for DI
DatabaseSessionDep = Annotated[AsyncSession, Depends(get_db)]