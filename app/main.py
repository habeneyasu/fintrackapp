import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.database import engine, AsyncSessionLocal
from app.db.base import Base
from app.features.auth.endpoints import router as auth_router
from app.features.income.endpoints import income_router
from app.features.category.endpoints import router as budget_category_router
from app.features.expense.endpoints import router as expense_router
from app.features.savingsgoal.endpoints import router as savings_goal_router

#env = os.getenv("APP_ENV", "local")  # default to local
#load_dotenv(dotenv_path=f"configs/environments/{env}.env")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code (replaces @app.on_event("startup"))
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown code would go here (optional)
    # (replaces @app.on_event("shutdown") if you had it)

app = FastAPI(
    title="Finance Tracker API",
    description="API for personal finance management",
    version="1.0.0",
    lifespan=lifespan  # Add lifespan handler here
)

# Include auth routers
app.include_router(
    auth_router,
    tags=["Authentication"]
)

# Include income routers
app.include_router(
    income_router,
    tags=["Income"]
)

app.include_router(
    budget_category_router,
    tags=["Budget Categories"]
)

app.include_router(
    expense_router,
    tags=["Expenses"]
)

app.include_router(
    savings_goal_router,
    tags=["Savings Goals"]
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database dependency (unchanged)
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()