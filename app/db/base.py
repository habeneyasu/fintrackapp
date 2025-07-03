from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr

Base = declarative_base()

# Optional: Add a base mixin for common columns
class BaseMixin:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

# Import all models (critical for alembic autogenerate)
from app.features.auth.models import User  # noqa: F401
from app.features.income.models import Income  # noqa: F401
from app.features.category.models import BudgetCategory  # noqa: F401
from app.features.expense.models import Expense  # noqa: F401
from app.features.savingsgoal.models import SavingsGoal  # noqa: F401
