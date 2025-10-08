"""
Problem service for managing problems in the Cosmic Council system.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from ..models.problem import Problem, ProblemStatement
from ..types import ProblemComplexity

logger = logging.getLogger(__name__)


class ProblemService:
    """Service for managing problems"""
    
    def __init__(self, repository=None):
        self.repository = repository
        self.logger = logger
    
    async def create_problem(self, problem_data: Dict[str, Any]) -> Problem:
        """Create a new problem"""
        try:
            problem = Problem(**problem_data)
            if not problem.validate():
                raise ValueError("Invalid problem data")
            
            if self.repository:
                await self.repository.create(problem)
            
            self.logger.info(f"Created problem: {problem.id}")
            return problem
            
        except Exception as e:
            self.logger.error(f"Error creating problem: {e}")
            raise
    
    async def get_problem(self, problem_id: str) -> Optional[Problem]:
        """Get a problem by ID"""
        try:
            if self.repository:
                return await self.repository.get_by_id(problem_id)
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting problem {problem_id}: {e}")
            raise
    
    async def update_problem(self, problem_id: str, updates: Dict[str, Any]) -> Optional[Problem]:
        """Update a problem"""
        try:
            if self.repository:
                problem = await self.repository.get_by_id(problem_id)
                if not problem:
                    return None
                
                # Update fields
                for key, value in updates.items():
                    if hasattr(problem, key):
                        setattr(problem, key, value)
                
                problem.updated_at = datetime.utcnow()
                
                if not problem.validate():
                    raise ValueError("Invalid updated problem data")
                
                await self.repository.update(problem)
                return problem
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error updating problem {problem_id}: {e}")
            raise
    
    async def delete_problem(self, problem_id: str) -> bool:
        """Delete a problem"""
        try:
            if self.repository:
                return await self.repository.delete(problem_id)
            return False
            
        except Exception as e:
            self.logger.error(f"Error deleting problem {problem_id}: {e}")
            raise
    
    async def list_problems(self, filters: Optional[Dict[str, Any]] = None) -> List[Problem]:
        """List problems with optional filters"""
        try:
            if self.repository:
                return await self.repository.list(filters)
            return []
            
        except Exception as e:
            self.logger.error(f"Error listing problems: {e}")
            raise
    
    async def create_problem_statement(self, statement_data: Dict[str, Any]) -> ProblemStatement:
        """Create a problem statement"""
        try:
            statement = ProblemStatement(**statement_data)
            if not statement.validate():
                raise ValueError("Invalid problem statement data")
            
            if self.repository:
                await self.repository.create_statement(statement)
            
            self.logger.info(f"Created problem statement: {statement.id}")
            return statement
            
        except Exception as e:
            self.logger.error(f"Error creating problem statement: {e}")
            raise
    
    async def analyze_problem_complexity(self, problem: Problem) -> ProblemComplexity:
        """Analyze problem complexity based on various factors"""
        try:
            complexity_score = 0
            
            # Factor in description length
            if len(problem.description) > 1000:
                complexity_score += 1
            
            # Factor in number of stakeholders
            if len(problem.stakeholders) > 5:
                complexity_score += 1
            
            # Factor in number of constraints
            if len(problem.constraints) > 3:
                complexity_score += 1
            
            # Factor in number of success criteria
            if len(problem.success_criteria) > 5:
                complexity_score += 1
            
            # Determine complexity level
            if complexity_score == 0:
                return ProblemComplexity.SIMPLE
            elif complexity_score <= 2:
                return ProblemComplexity.MODERATE
            elif complexity_score <= 3:
                return ProblemComplexity.COMPLEX
            else:
                return ProblemComplexity.SYSTEMIC
                
        except Exception as e:
            self.logger.error(f"Error analyzing problem complexity: {e}")
            return ProblemComplexity.MODERATE
