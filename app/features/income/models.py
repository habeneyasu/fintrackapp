
from ast import Index
import re
from uuid import UUID as uuid_uuid
import uuid
from datetime import datetime
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy import Column, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.mysql import BINARY
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import Numeric
from app.db.base import Base
from app.core.config import IncomeSource, IncomeFrequency

class Income(Base):
    __tablename__ = "incomes"
    id = Column(BINARY(16), primary_key=True, default=lambda: uuid.uuid4().bytes)
    user_id = Column(BINARY(16), ForeignKey("users.id"), nullable=False, index=True)
    source = Column(SqlEnum(IncomeSource), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)  # Stores up to 999,999,999.99
    frequency = Column(SqlEnum(IncomeFrequency), nullable=False, default=IncomeFrequency.MONTHLY)
    is_recurring = Column(Boolean, nullable=False, default=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @property
    def uuid(self):
        return str(uuid.UUID(bytes=self.id)) if self.id else None

    @staticmethod
    def uuid_to_bin(uuid_str: str) -> bytes:
        """Convert any valid UUID string to binary"""
        try:
            # First try standard UUID parsing
            if '-' in uuid_str:
                return uuid.UUID(uuid_str).bytes
                
            # Handle hex strings (with or without 0x prefix)
            clean = uuid_str.lower().replace('0x', '')
            if len(clean) == 32:
                return uuid.UUID(hex=clean).bytes
                
            raise ValueError("Invalid UUID format")
            
        except ValueError as e:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid UUID: {str(e)}. Must be 32-character hex."
            )

    @staticmethod
    def prepare_for_db(data: dict) -> dict:
        """Prepare income data for database insertion"""
        prepared = data.copy()
        
        # Convert enums to strings
        if 'source' in prepared:
            prepared['source'] = prepared['source'].value
            
        if 'frequency' in prepared:
            prepared['frequency'] = prepared['frequency'].value
            
        # Convert UUID strings to binary
        if 'user_id' in prepared:
            prepared['user_id'] = Income.uuid_to_bin(prepared['user_id'])
            
        # Ensure Decimal is properly handled
        if 'amount' in prepared and isinstance(prepared['amount'], Decimal):
            prepared['amount'] = float(prepared['amount'])
            
        return prepared

   