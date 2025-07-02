from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.db.base import Base
from app.features.auth.endpoints import router as auth_router
from app.features.income.endpoints import income_router
from app.features.category.endpoints import router as budget_category_router
from app.features.expense.endpoints import router as expense_router
from app.features.savingsgoal.endpoints import router as savings_goal_router
import os
import asyncio
from contextlib import asynccontextmanager

# Database connection with retry logic
async def get_engine():
    DB_URL = f"mysql+asyncmy://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    
    for attempt in range(5):
        try:
            engine = create_async_engine(
                DB_URL,
                poolclass=NullPool,  # Important for Render's free tier
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database connection
    engine = await get_engine()
    app.state.engine = engine
    
    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Clean up
    await engine.dispose()

app = FastAPI(
    title="Finance Tracker API",
    description="API for personal finance management",
    version="1.0.0",
    lifespan=lifespan
)

# Health check endpoint (required for Render)
@app.get("/health")
async def health_check():
    try:
        async with app.state.engine.begin() as conn:
            await conn.execute("SELECT 1")
        return {"status": "healthy"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Include routers
app.include_router(auth_router, tags=["Authentication"])
app.include_router(income_router, tags=["Income"])
app.include_router(budget_category_router, tags=["Budget Categories"])
app.include_router(expense_router, tags=["Expenses"])
app.include_router(savings_goal_router, tags=["Savings Goals"])

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database dependency
async def get_db():
    async_session = async_sessionmaker(
        app.state.engine, 
        expire_on_commit=False,
        class_=AsyncSession
    )
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()