from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr
from sqlalchemy import Column, DateTime, func

Base = declarative_base()

class BaseMixin:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

# Import all models (keep this at bottom)
from app.features.auth.models import User  # noqa: F401
from app.features.income.models import Income  # noqa: F401
from app.features.category.models import BudgetCategory  # noqa: F401
from app.features.expense.models import Expense  # noqa: F401
from app.features.savingsgoal.models import SavingsGoal  # noqa: F401