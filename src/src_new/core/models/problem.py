"""
Problem domain models.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from .base import BaseModel
from ..types import ProblemComplexity


class Problem(BaseModel):
    """Represents a problem to be solved by the Cosmic Council"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = kwargs.get('title', '')
        self.description = kwargs.get('description', '')
        self.domain = kwargs.get('domain', '')
        self.complexity = kwargs.get('complexity', ProblemComplexity.MODERATE)
        self.status = kwargs.get('status', 'active')
        self.priority = kwargs.get('priority', 'medium')
        self.stakeholders = kwargs.get('stakeholders', [])
        self.constraints = kwargs.get('constraints', {})
        self.success_criteria = kwargs.get('success_criteria', [])
        self.due_date = kwargs.get('due_date')
        self.created_by = kwargs.get('created_by')
    
    def validate(self) -> bool:
        """Validate problem data"""
        if not self.title or not self.description:
            return False
        if not isinstance(self.complexity, ProblemComplexity):
            return False
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        base_dict = super().to_dict()
        return {
            **base_dict,
            'title': self.title,
            'description': self.description,
            'domain': self.domain,
            'complexity': self.complexity.value,
            'status': self.status,
            'priority': self.priority,
            'stakeholders': self.stakeholders,
            'constraints': self.constraints,
            'success_criteria': self.success_criteria,
            'due_date': self.due_date,
            'created_by': self.created_by
        }


class ProblemStatement(BaseModel):
    """Represents a problem statement for analysis"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.problem_id = kwargs.get('problem_id', '')
        self.statement = kwargs.get('statement', '')
        self.context = kwargs.get('context', {})
        self.assumptions = kwargs.get('assumptions', [])
        self.questions = kwargs.get('questions', [])
        self.analysis_notes = kwargs.get('analysis_notes', '')
    
    def validate(self) -> bool:
        """Validate problem statement"""
        return bool(self.problem_id and self.statement)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        base_dict = super().to_dict()
        return {
            **base_dict,
            'problem_id': self.problem_id,
            'statement': self.statement,
            'context': self.context,
            'assumptions': self.assumptions,
            'questions': self.questions,
            'analysis_notes': self.analysis_notes
        }
