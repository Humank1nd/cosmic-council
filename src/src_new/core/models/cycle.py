"""
Cycle domain models.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from .base import BaseModel
from ..types import CycleStatus, EnterpriseType


class Cycle(BaseModel):
    """Represents a problem-solving cycle"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.problem_id = kwargs.get('problem_id', '')
        self.status = kwargs.get('status', CycleStatus.PENDING)
        self.enterprises = kwargs.get('enterprises', [])
        self.current_enterprise = kwargs.get('current_enterprise')
        self.results = kwargs.get('results', {})
        self.started_at = kwargs.get('started_at')
        self.completed_at = kwargs.get('completed_at')
        self.created_by = kwargs.get('created_by')
    
    def validate(self) -> bool:
        """Validate cycle data"""
        if not self.problem_id:
            return False
        if not isinstance(self.status, CycleStatus):
            return False
        return True
    
    def start(self) -> None:
        """Start the cycle"""
        self.status = CycleStatus.RUNNING
        self.started_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def complete(self) -> None:
        """Complete the cycle"""
        self.status = CycleStatus.COMPLETED
        self.completed_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def fail(self, error_message: str) -> None:
        """Mark cycle as failed"""
        self.status = CycleStatus.FAILED
        self.completed_at = datetime.now(timezone.utc)
        self.update_metadata('error_message', error_message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        base_dict = super().to_dict()
        return {
            **base_dict,
            'problem_id': self.problem_id,
            'status': self.status.value,
            'enterprises': [e.value for e in self.enterprises],
            'current_enterprise': self.current_enterprise.value if self.current_enterprise else None,
            'results': self.results,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'created_by': self.created_by
        }


class CycleResult(BaseModel):
    """Represents the result of a cycle execution"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cycle_id = kwargs.get('cycle_id', '')
        self.enterprise_type = kwargs.get('enterprise_type')
        self.result_data = kwargs.get('result_data', {})
        self.success = kwargs.get('success', False)
        self.error_message = kwargs.get('error_message', '')
        self.execution_time = kwargs.get('execution_time', 0)
        self.metrics = kwargs.get('metrics', {})
    
    def validate(self) -> bool:
        """Validate cycle result"""
        return bool(self.cycle_id and self.enterprise_type)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        base_dict = super().to_dict()
        return {
            **base_dict,
            'cycle_id': self.cycle_id,
            'enterprise_type': self.enterprise_type.value if self.enterprise_type else None,
            'result_data': self.result_data,
            'success': self.success,
            'error_message': self.error_message,
            'execution_time': self.execution_time,
            'metrics': self.metrics
        }
