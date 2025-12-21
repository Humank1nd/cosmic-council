"""
Solution service for managing solutions in the Cosmic Council system.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import logging

from ..models.solution import Solution, SolutionComponent
from ..models.problem import Problem

logger = logging.getLogger(__name__)


class SolutionService:
    """Service for managing solutions"""
    
    def __init__(self, repository=None):
        self.repository = repository
        self.logger = logger
    
    async def create_solution(self, solution_data: Dict[str, Any]) -> Solution:
        """Create a new solution"""
        try:
            solution = Solution(**solution_data)
            if not solution.validate():
                raise ValueError("Invalid solution data")
            
            if self.repository:
                await self.repository.create(solution)
            
            self.logger.info(f"Created solution: {solution.id}")
            return solution
            
        except Exception as e:
            self.logger.error(f"Error creating solution: {e}")
            raise
    
    async def get_solution(self, solution_id: str) -> Optional[Solution]:
        """Get a solution by ID"""
        try:
            if self.repository:
                return await self.repository.get_by_id(solution_id)
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting solution {solution_id}: {e}")
            raise
    
    async def get_solutions_for_problem(self, problem_id: str) -> List[Solution]:
        """Get all solutions for a problem"""
        try:
            if self.repository:
                return await self.repository.get_by_problem_id(problem_id)
            return []
            
        except Exception as e:
            self.logger.error(f"Error getting solutions for problem {problem_id}: {e}")
            raise
    
    async def update_solution(self, solution_id: str, updates: Dict[str, Any]) -> Optional[Solution]:
        """Update a solution"""
        try:
            if self.repository:
                solution = await self.repository.get_by_id(solution_id)
                if not solution:
                    return None
                
                # Update fields
                for key, value in updates.items():
                    if hasattr(solution, key):
                        setattr(solution, key, value)
                
                solution.updated_at = datetime.now(timezone.utc)
                
                if not solution.validate():
                    raise ValueError("Invalid updated solution data")
                
                await self.repository.update(solution)
                return solution
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error updating solution {solution_id}: {e}")
            raise
    
    async def delete_solution(self, solution_id: str) -> bool:
        """Delete a solution"""
        try:
            if self.repository:
                return await self.repository.delete(solution_id)
            return False
            
        except Exception as e:
            self.logger.error(f"Error deleting solution {solution_id}: {e}")
            raise
    
    async def add_solution_component(self, solution_id: str, component_data: Dict[str, Any]) -> SolutionComponent:
        """Add a component to a solution"""
        try:
            component_data['solution_id'] = solution_id
            component = SolutionComponent(**component_data)
            
            if not component.validate():
                raise ValueError("Invalid solution component data")
            
            if self.repository:
                await self.repository.create_component(component)
            
            self.logger.info(f"Added component {component.id} to solution {solution_id}")
            return component
            
        except Exception as e:
            self.logger.error(f"Error adding solution component: {e}")
            raise
    
    async def get_solution_components(self, solution_id: str) -> List[SolutionComponent]:
        """Get all components for a solution"""
        try:
            if self.repository:
                return await self.repository.get_components_by_solution_id(solution_id)
            return []
            
        except Exception as e:
            self.logger.error(f"Error getting solution components: {e}")
            raise
    
    async def evaluate_solution(self, solution: Solution, problem: Problem) -> Dict[str, Any]:
        """Evaluate a solution against a problem"""
        try:
            evaluation = {
                'solution_id': solution.id,
                'problem_id': problem.id,
                'evaluation_date': datetime.now(timezone.utc),
                'criteria_satisfaction': {},
                'overall_score': 0.0,
                'recommendations': []
            }
            
            # Check success criteria satisfaction
            for criterion in problem.success_criteria:
                # Simple evaluation logic - can be enhanced with AI
                satisfaction_score = 0.5  # Placeholder
                evaluation['criteria_satisfaction'][criterion] = satisfaction_score
            
            # Calculate overall score
            if evaluation['criteria_satisfaction']:
                evaluation['overall_score'] = sum(evaluation['criteria_satisfaction'].values()) / len(evaluation['criteria_satisfaction'])
            
            # Generate recommendations
            if evaluation['overall_score'] < 0.7:
                evaluation['recommendations'].append("Consider refining the solution approach")
            
            if len(solution.components) < 3:
                evaluation['recommendations'].append("Add more detailed solution components")
            
            return evaluation
            
        except Exception as e:
            self.logger.error(f"Error evaluating solution: {e}")
            return {'error': str(e)}
