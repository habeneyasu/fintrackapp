from sqlalchemy import Column, DateTime, Text, ForeignKey, String
from sqlalchemy.dialects.mysql import BINARY
from sqlalchemy import Enum as SqlEnum, Numeric
import uuid
from datetime import datetime
from decimal import Decimal
from app.db.base import Base
from app.core.config import Type

class BudgetCategory(Base):
    __tablename__ = "budget_categories"
    
    id = Column(BINARY(16), primary_key=True, default=lambda: uuid.uuid4().bytes)
    user_id = Column(BINARY(16), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    budget_limit = Column(Numeric(12, 2), nullable=False)
    type = Column(SqlEnum(Type), nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # UUID Conversion Methods
    @property
    def uuid(self) -> str | None:
        """Convert binary UUID to standard UUID string"""
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
    def prepare_for_db(data: dict) -> dict:
        """Prepare data for database insertion with proper type conversions"""
        prepared = data.copy()
        
        # Handle UUID fields
        for field in ['id', 'user_id']:
            if field in prepared:
                prepared[field] = BudgetCategory.uuid_to_bin(prepared[field])
        
        # Handle Decimal fields
        if 'budget_limit' in prepared:
            if isinstance(prepared['budget_limit'], Decimal):
                prepared['budget_limit'] = float(prepared['budget_limit'])
        
        return prepared