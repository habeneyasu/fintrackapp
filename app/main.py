from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, AsyncSessionLocal
from app.db.base import Base
from app.features.auth.endpoints import router as auth_router
from app.features.income.endpoints import  income_router
from app.features.category.endpoints import router as budget_category_router
from app.features.expense.endpoints import router as expense_router
from app.features.savingsgoal.endpoints import router as savings_goal_router

app = FastAPI(
    title="Finance Tracker API",
    description="API for personal finance management",
    version="1.0.0",
)

# Include  auth routers
app.include_router(
    auth_router,
    tags=["Authentication"]
)

# Include  income routers
app.include_router(
    income_router,  # This imports the router that already has its own prefix
    tags=["Income"]  # Remove prefix here since it's already in the income_router
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

# DB Initialization
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# @app.get("/")
# async def root():
#     return {"message": "Finance Tracker API"}

# Database dependency
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