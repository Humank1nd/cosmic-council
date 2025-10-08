"""
Enterprise domain models.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from .base import BaseModel
from ..types import EnterpriseType


class Enterprise(BaseModel):
    """Represents an enterprise in the Cosmic Council"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.enterprise_type = kwargs.get('enterprise_type')
        self.name = kwargs.get('name', '')
        self.description = kwargs.get('description', '')
        self.capabilities = kwargs.get('capabilities', [])
        self.status = kwargs.get('status', 'active')
        self.configuration = kwargs.get('configuration', {})
        self.performance_metrics = kwargs.get('performance_metrics', {})
    
    def validate(self) -> bool:
        """Validate enterprise data"""
        if not isinstance(self.enterprise_type, EnterpriseType):
            return False
        if not self.name or not self.description:
            return False
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        base_dict = super().to_dict()
        return {
            **base_dict,
            'enterprise_type': self.enterprise_type.value if self.enterprise_type else None,
            'name': self.name,
            'description': self.description,
            'capabilities': self.capabilities,
            'status': self.status,
            'configuration': self.configuration,
            'performance_metrics': self.performance_metrics
        }


class EnterpriseResult(BaseModel):
    """Represents the result of an enterprise execution"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cycle_id = kwargs.get('cycle_id', '')
        self.enterprise_type = kwargs.get('enterprise_type')
        self.input_data = kwargs.get('input_data', {})
        self.output_data = kwargs.get('output_data', {})
        self.success = kwargs.get('success', False)
        self.error_message = kwargs.get('error_message', '')
        self.execution_time = kwargs.get('execution_time', 0)
        self.resources_used = kwargs.get('resources_used', {})
        self.quality_score = kwargs.get('quality_score', 0.0)
    
    def validate(self) -> bool:
        """Validate enterprise result"""
        return bool(self.cycle_id and self.enterprise_type)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        base_dict = super().to_dict()
        return {
            **base_dict,
            'cycle_id': self.cycle_id,
            'enterprise_type': self.enterprise_type.value if self.enterprise_type else None,
            'input_data': self.input_data,
            'output_data': self.output_data,
            'success': self.success,
            'error_message': self.error_message,
            'execution_time': self.execution_time,
            'resources_used': self.resources_used,
            'quality_score': self.quality_score
        }
