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
    # Keep column name "metadata" for schema compatibility while avoiding
    # collision with SQLAlchemy's declarative metadata attribute.
    extra_data = Column("metadata", JSON, key="extra_data", default=dict)
    
    def to_dict(self) -> dict:
        """Convert model to dictionary"""
        data = {}
        for column in self.__table__.columns:
            key = "metadata" if column.key == "extra_data" and column.name == "metadata" else column.name
            data[key] = getattr(self, column.key)
        return data
    
    def update_from_dict(self, data: dict) -> None:
        """Update model from dictionary"""
        for key, value in data.items():
            attr = "extra_data" if key == "metadata" else key
            if hasattr(self, attr):
                setattr(self, attr, value)
        self.updated_at = datetime.now(timezone.utc)
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id})>"
