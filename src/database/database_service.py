"""
Database service layer that uses repositories for data access.
"""

from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from .connection import get_database_connection
from .repositories import (
    ProblemRepository, ProblemStatementRepository,
    SolutionRepository, SolutionComponentRepository,
    CycleRepository, CycleResultRepository,
    EnterpriseRepository, EnterpriseResultRepository,
    UserRepository, StakeholderRepository,
    ConstraintRepository, SuccessCriterionRepository
)

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service layer for database operations using repositories"""
    
    def __init__(self):
        self.connection = get_database_connection()
        self._repositories = {}
    
    async def get_session(self) -> AsyncSession:
        """Get database session"""
        return self.connection.get_async_session()
    
    def get_repository(self, repository_class, session: AsyncSession):
        """Get repository instance"""
        if repository_class not in self._repositories:
            self._repositories[repository_class] = repository_class(session)
        return self._repositories[repository_class]
    
    # Problem operations
    async def create_problem(self, problem_data: Dict[str, Any]) -> str:
        """Create a new problem"""
        async with self.connection.get_async_session() as session:
            repository = ProblemRepository(session)
            problem = await repository.create(problem_data)
            return str(problem.id)
    
    async def get_problem(self, problem_id: str) -> Optional[Dict[str, Any]]:
        """Get a problem by ID"""
        async with self.connection.get_async_session() as session:
            repository = ProblemRepository(session)
            problem = await repository.get_by_id(problem_id)
            return problem.to_dict() if problem else None
    
    async def get_problems_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Get problems by domain"""
        async with self.connection.get_async_session() as session:
            repository = ProblemRepository(session)
            problems = await repository.get_by_domain(domain)
            return [problem.to_dict() for problem in problems]
    
    async def update_problem(self, problem_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a problem"""
        async with self.connection.get_async_session() as session:
            repository = ProblemRepository(session)
            problem = await repository.update(problem_id, updates)
            return problem.to_dict() if problem else None
    
    async def delete_problem(self, problem_id: str) -> bool:
        """Delete a problem"""
        async with self.connection.get_async_session() as session:
            repository = ProblemRepository(session)
            return await repository.delete(problem_id)
    
    async def search_problems(self, search_term: str) -> List[Dict[str, Any]]:
        """Search problems"""
        async with self.connection.get_async_session() as session:
            repository = ProblemRepository(session)
            problems = await repository.search_problems(search_term)
            return [problem.to_dict() for problem in problems]
    
    async def get_problem_statistics(self) -> Dict[str, Any]:
        """Get problem statistics"""
        async with self.connection.get_async_session() as session:
            repository = ProblemRepository(session)
            return await repository.get_problem_statistics()
    
    # Solution operations
    async def create_solution(self, solution_data: Dict[str, Any]) -> str:
        """Create a new solution"""
        async with self.connection.get_async_session() as session:
            repository = SolutionRepository(session)
            solution = await repository.create(solution_data)
            return str(solution.id)
    
    async def get_solution(self, solution_id: str) -> Optional[Dict[str, Any]]:
        """Get a solution by ID"""
        async with self.connection.get_async_session() as session:
            repository = SolutionRepository(session)
            solution = await repository.get_by_id(solution_id)
            return solution.to_dict() if solution else None
    
    async def get_solutions_by_problem_id(self, problem_id: str) -> List[Dict[str, Any]]:
        """Get solutions by problem ID"""
        async with self.connection.get_async_session() as session:
            repository = SolutionRepository(session)
            solutions = await repository.get_by_problem_id(problem_id)
            return [solution.to_dict() for solution in solutions]
    
    async def update_solution(self, solution_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a solution"""
        async with self.connection.get_async_session() as session:
            repository = SolutionRepository(session)
            solution = await repository.update(solution_id, updates)
            return solution.to_dict() if solution else None
    
    async def delete_solution(self, solution_id: str) -> bool:
        """Delete a solution"""
        async with self.connection.get_async_session() as session:
            repository = SolutionRepository(session)
            return await repository.delete(solution_id)
    
    async def get_solution_statistics(self) -> Dict[str, Any]:
        """Get solution statistics"""
        async with self.connection.get_async_session() as session:
            repository = SolutionRepository(session)
            return await repository.get_solution_statistics()
    
    # Cycle operations
    async def create_cycle(self, cycle_data: Dict[str, Any]) -> str:
        """Create a new cycle"""
        async with self.connection.get_async_session() as session:
            repository = CycleRepository(session)
            cycle = await repository.create(cycle_data)
            return str(cycle.id)
    
    async def get_cycle(self, cycle_id: str) -> Optional[Dict[str, Any]]:
        """Get a cycle by ID"""
        async with self.connection.get_async_session() as session:
            repository = CycleRepository(session)
            cycle = await repository.get_by_id(cycle_id)
            return cycle.to_dict() if cycle else None
    
    async def get_cycles_by_problem_id(self, problem_id: str) -> List[Dict[str, Any]]:
        """Get cycles by problem ID"""
        async with self.connection.get_async_session() as session:
            repository = CycleRepository(session)
            cycles = await repository.get_by_problem_id(problem_id)
            return [cycle.to_dict() for cycle in cycles]
    
    async def update_cycle(self, cycle_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a cycle"""
        async with self.connection.get_async_session() as session:
            repository = CycleRepository(session)
            cycle = await repository.update(cycle_id, updates)
            return cycle.to_dict() if cycle else None
    
    async def get_active_cycles(self) -> List[Dict[str, Any]]:
        """Get active cycles"""
        async with self.connection.get_async_session() as session:
            repository = CycleRepository(session)
            cycles = await repository.get_active_cycles()
            return [cycle.to_dict() for cycle in cycles]
    
    async def get_cycle_statistics(self) -> Dict[str, Any]:
        """Get cycle statistics"""
        async with self.connection.get_async_session() as session:
            repository = CycleRepository(session)
            return await repository.get_cycle_statistics()
    
    # Enterprise operations
    async def get_enterprise_by_type(self, enterprise_type: str) -> Optional[Dict[str, Any]]:
        """Get enterprise by type"""
        async with self.connection.get_async_session() as session:
            repository = EnterpriseRepository(session)
            enterprise = await repository.get_by_type(enterprise_type)
            return enterprise.to_dict() if enterprise else None
    
    async def get_active_enterprises(self) -> List[Dict[str, Any]]:
        """Get active enterprises"""
        async with self.connection.get_async_session() as session:
            repository = EnterpriseRepository(session)
            enterprises = await repository.get_active_enterprises()
            return [enterprise.to_dict() for enterprise in enterprises]
    
    async def update_enterprise_configuration(self, enterprise_id: str, configuration: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update enterprise configuration"""
        async with self.connection.get_async_session() as session:
            repository = EnterpriseRepository(session)
            enterprise = await repository.update_configuration(enterprise_id, configuration)
            return enterprise.to_dict() if enterprise else None
    
    # User operations
    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        async with self.connection.get_async_session() as session:
            repository = UserRepository(session)
            user = await repository.get_by_username(username)
            return user.to_dict() if user else None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        async with self.connection.get_async_session() as session:
            repository = UserRepository(session)
            user = await repository.get_by_email(email)
            return user.to_dict() if user else None
    
    async def create_user(self, user_data: Dict[str, Any]) -> str:
        """Create a new user"""
        async with self.connection.get_async_session() as session:
            repository = UserRepository(session)
            user = await repository.create(user_data)
            return str(user.id)
    
    async def update_user(self, user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a user"""
        async with self.connection.get_async_session() as session:
            repository = UserRepository(session)
            user = await repository.update(user_id, updates)
            return user.to_dict() if user else None
    
    # Analytics operations
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        async with self.connection.get_async_session() as session:
            problem_repo = ProblemRepository(session)
            solution_repo = SolutionRepository(session)
            cycle_repo = CycleRepository(session)
            
            problem_stats = await problem_repo.get_problem_statistics()
            solution_stats = await solution_repo.get_solution_statistics()
            cycle_stats = await cycle_repo.get_cycle_statistics()
            
            return {
                'problems': problem_stats,
                'solutions': solution_stats,
                'cycles': cycle_stats,
                'timestamp': '2024-01-01T00:00:00Z'  # Placeholder
            }
    
    async def health_check(self) -> bool:
        """Check database health"""
        return await self.connection.health_check()


# Global database service instance
_database_service: Optional[DatabaseService] = None


def get_database_service() -> DatabaseService:
    """Get the global database service instance"""
    global _database_service
    if _database_service is None:
        _database_service = DatabaseService()
    return _database_service
