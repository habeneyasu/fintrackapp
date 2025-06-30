from sqlalchemy import Column, DateTime, Text, ForeignKey, String, Boolean
from sqlalchemy.dialects.mysql import BINARY
from sqlalchemy import Enum as SqlEnum, Numeric
import uuid
from datetime import datetime
from decimal import Decimal
from app.db.base import Base
from app.core.config import PaymentMethod
from typing import Optional

class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(BINARY(16), primary_key=True, default=lambda: uuid.uuid4().bytes)
    user_id = Column(BINARY(16), ForeignKey("users.id"), nullable=False, index=True)
    category_id = Column(BINARY(16), ForeignKey("budget_categories.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    remark = Column(Text, nullable=True)
    is_essential = Column(Boolean, nullable=False, default=True)
    payment_method = Column(SqlEnum(PaymentMethod), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # UUID Conversion Methods
    @property
    def uuid(self) -> Optional[str]:
        """Convert binary UUID to standard string representation"""
        return str(uuid.UUID(bytes=self.id)) if self.id else None

    @staticmethod
    def uuid_to_bin(uuid_input) -> bytes:
        """
        Convert various UUID formats to binary for MySQL
        Accepts: UUID object, UUID string, or bytes
        """
        if isinstance(uuid_input, bytes):
            return uuid_input
        elif isinstance(uuid_input, uuid.UUID):
            return uuid_input.bytes
        elif isinstance(uuid_input, str):
            if uuid_input.startswith('0x'):
                return bytes.fromhex(uuid_input[2:])
            return uuid.UUID(uuid_input).bytes
        raise ValueError(f"Cannot convert {type(uuid_input)} to UUID bytes")

    @staticmethod
    def prepare_for_export(expense: 'Expense') -> dict:
        """Convert model to export-friendly dictionary"""
        return {
            "id": expense.uuid,
            "user_id": str(uuid.UUID(bytes=expense.user_id)),
            "category_id": str(uuid.UUID(bytes=expense.category_id)),
            "name": expense.name,
            "amount": float(expense.amount),
            "remark": expense.remark,
            "is_essential": expense.is_essential,
            "payment_method": expense.payment_method.value,
            "created_at": expense.created_at.isoformat(),
            "updated_at": expense.updated_at.isoformat()
        }