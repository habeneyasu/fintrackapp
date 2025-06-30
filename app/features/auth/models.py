import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.mysql import BINARY
from app.db.base import Base

class User(Base):
    __tablename__ = "users"
    
    # Primary key as binary UUID (optimized for MySQL)
    id = Column(BINARY(16), primary_key=True, default=lambda: uuid.uuid4().bytes)
    
    # Personal information
    first_name = Column(String(50), nullable=False)
    middle_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=False)
    
    # Authentication fields
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Contact information
    phone_number = Column(String(20), unique=True, nullable=True)
    
    # Metadata
    currency = Column(String(3), default="ETB")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
   # last_login_at = Column(DateTime, nullable=True)

    @property
    def uuid(self):
        """Public-facing UUID representation"""
        return str(uuid.UUID(bytes=self.id)) if self.id else None

    def to_response(self):
        """Convert model to API response format"""
        return {
            "id": self.uuid,
            "email": self.email,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone_number": self.phone_number,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }