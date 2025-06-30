import datetime
from decimal import Decimal  # Added for proper monetary handling
from sqlalchemy import Column, Numeric, ForeignKey, CheckConstraint,String,DateTime
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from uuid import uuid4
from app.db.base import Base
from sqlalchemy.dialects.mysql import BINARY
from datetime import datetime



class SavingsGoal(Base):
    __tablename__ = "savings_goals"
    __table_args__ = (
        CheckConstraint('target_amount >= 0.01', name='check_target_amount_positive'),
        CheckConstraint('saved_amount >= 0', name='check_saved_amount_non_negative'),
    )

    id = Column(BINARY(16), primary_key=True, default=lambda: uuid4().bytes)
    user_id = Column(BINARY(16), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Changed from Float to Numeric for precise decimal calculations
    target_amount = Column(Numeric(12, 2), nullable=False)  # 12 digits, 2 decimal places
    saved_amount = Column(Numeric(12, 2), default=Decimal('0.00'), nullable=False)
    
    name = Column(String(100), nullable=False)  # Added missing field
    description = Column(String(255), nullable=True)  # Added missing field
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


    @hybrid_property
    def progress(self) -> float:
        """Calculate completion percentage (0.0 to 1.0)"""
        if not self.target_amount:
            return 0.0
        return float(self.saved_amount / self.target_amount)

    @progress.expression
    def progress(cls):
        """SQL expression for progress calculation"""
        return cls.saved_amount / cls.target_amount

    @hybrid_property
    def is_achieved(self) -> bool:
        """Determine if goal is fully achieved"""
        return self.progress >= 1

    @is_achieved.expression
    def is_achieved(cls):
        """SQL expression for achievement check"""
        return cls.saved_amount >= cls.target_amount