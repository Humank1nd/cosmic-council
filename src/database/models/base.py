"""
Base database model for the Cosmic Council system.
"""

from sqlalchemy import Column, String, DateTime, Text, JSON
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid

Base = declarative_base()


class BaseModel(Base):
    """Base model with common fields"""
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    metadata = Column(JSON, default=dict)
    
    def to_dict(self) -> dict:
        """Convert model to dictionary"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def update_from_dict(self, data: dict) -> None:
        """Update model from dictionary"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now(timezone.utc)
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id})>"
