"""
Base model classes for the Cosmic Council system.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import uuid


class BaseModel(ABC):
    """Base class for all domain models"""
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', str(uuid.uuid4()))
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
        self.metadata = kwargs.get('metadata', {})
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'metadata': self.metadata
        }
    
    def update_metadata(self, key: str, value: Any) -> None:
        """Update metadata field"""
        self.metadata[key] = value
        self.updated_at = datetime.utcnow()
    
    @abstractmethod
    def validate(self) -> bool:
        """Validate model data"""
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"
