"""
Base database models and mixins for the Cosmic Council system.
Provides common model functionality and database abstractions.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from enum import Enum
import uuid
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

class Status(Enum):
    """Common status enumeration for database models."""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TimestampMixin:
    """Mixin for models that need timestamp tracking."""
    
    def __init__(self):
        self.created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
        self.updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(timezone.utc)

class StatusMixin:
    """Mixin for models that need status tracking."""
    
    def __init__(self):
        self.status: Status = Status.DRAFT
    
    def set_status(self, status: Status) -> None:
        """Set the status and update timestamp."""
        self.status = status
        if hasattr(self, 'touch'):
            self.touch()

class BaseModel(ABC):
    """Base model class for all database entities."""
    
    def __init__(self):
        self.id: str = str(uuid.uuid4())
        self.created_at: datetime = datetime.now(timezone.utc)
        self.updated_at: datetime = datetime.now(timezone.utc)
        self.status: Status = Status.DRAFT
        self.metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary."""
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'status': self.status.value,
            'metadata': self.metadata
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Populate the model from a dictionary."""
        self.id = data.get('id', str(uuid.uuid4()))
        self.created_at = datetime.fromisoformat(data.get('created_at', datetime.now(timezone.utc).isoformat()))
        self.updated_at = datetime.fromisoformat(data.get('updated_at', datetime.now(timezone.utc).isoformat()))
        self.status = Status(data.get('status', Status.DRAFT.value))
        self.metadata = data.get('metadata', {})
    
    def touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(timezone.utc)
    
    def set_status(self, status: Status) -> None:
        """Set the status and update timestamp."""
        self.status = status
        self.touch()
    
    @abstractmethod
    def validate(self) -> bool:
        """Validate the model data."""
        pass
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, status={self.status.value})"
    
    def __repr__(self) -> str:
        return self.__str__()

@dataclass
class CycleModel(BaseModel):
    """Model for cycle entities."""
    
    def __init__(self):
        super().__init__()
        self.objective_ref: str = ""
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.parent_cycle_id: Optional[str] = None
        self.child_cycle_ids: list = field(default_factory=list)
    
    def validate(self) -> bool:
        """Validate the cycle model."""
        return bool(self.objective_ref.strip())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with cycle-specific fields."""
        base_dict = super().to_dict()
        base_dict.update({
            'objective_ref': self.objective_ref,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'parent_cycle_id': self.parent_cycle_id,
            'child_cycle_ids': self.child_cycle_ids
        })
        return base_dict

@dataclass
class StageExecutionModel(BaseModel):
    """Model for stage execution entities."""
    
    def __init__(self):
        super().__init__()
        self.cycle_id: str = ""
        self.stage_code: str = ""
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.input_data: Dict[str, Any] = field(default_factory=dict)
        self.output_data: Dict[str, Any] = field(default_factory=dict)
        self.error_message: Optional[str] = None
    
    def validate(self) -> bool:
        """Validate the stage execution model."""
        return bool(self.cycle_id.strip() and self.stage_code.strip())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with stage-specific fields."""
        base_dict = super().to_dict()
        base_dict.update({
            'cycle_id': self.cycle_id,
            'stage_code': self.stage_code,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'input_data': self.input_data,
            'output_data': self.output_data,
            'error_message': self.error_message
        })
        return base_dict

@dataclass
class AuditLogModel(BaseModel):
    """Model for audit log entities."""
    
    def __init__(self):
        super().__init__()
        self.entity_type: str = ""
        self.entity_id: str = ""
        self.action: str = ""
        self.actor: str = ""
        self.details: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """Validate the audit log model."""
        return bool(self.entity_type.strip() and self.entity_id.strip() and self.action.strip())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with audit-specific fields."""
        base_dict = super().to_dict()
        base_dict.update({
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'action': self.action,
            'actor': self.actor,
            'details': self.details
        })
        return base_dict
