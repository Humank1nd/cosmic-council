"""
Problem repository for database operations.
"""

from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, asc
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.exc import SQLAlchemyError
import logging

from .base_repository import BaseRepository
from ..models.problem import Problem, ProblemStatement
from ..models.user import User, Stakeholder

logger = logging.getLogger(__name__)


class ProblemRepository(BaseRepository[Problem]):
    """Repository for Problem model"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Problem)
    
    async def get_by_domain(self, domain: str) -> List[Problem]:
        """Get problems by domain"""
        try:
            result = await self.session.execute(
                select(Problem)
                .where(Problem.domain == domain)
                .order_by(desc(Problem.created_at))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting problems by domain {domain}: {e}")
            raise
    
    async def get_by_complexity(self, complexity: str) -> List[Problem]:
        """Get problems by complexity level"""
        try:
            result = await self.session.execute(
                select(Problem)
                .where(Problem.complexity == complexity)
                .order_by(desc(Problem.created_at))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting problems by complexity {complexity}: {e}")
            raise
    
    async def get_by_status(self, status: str) -> List[Problem]:
        """Get problems by status"""
        try:
            result = await self.session.execute(
                select(Problem)
                .where(Problem.status == status)
                .order_by(desc(Problem.created_at))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting problems by status {status}: {e}")
            raise
    
    async def get_by_priority(self, priority: str) -> List[Problem]:
        """Get problems by priority"""
        try:
            result = await self.session.execute(
                select(Problem)
                .where(Problem.priority == priority)
                .order_by(desc(Problem.created_at))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting problems by priority {priority}: {e}")
            raise
    
    async def get_by_creator(self, user_id: str) -> List[Problem]:
        """Get problems created by a user"""
        try:
            result = await self.session.execute(
                select(Problem)
                .where(Problem.created_by == user_id)
                .order_by(desc(Problem.created_at))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting problems by creator {user_id}: {e}")
            raise
    
    async def get_with_relationships(self, problem_id: str) -> Optional[Problem]:
        """Get problem with all relationships loaded"""
        try:
            result = await self.session.execute(
                select(Problem)
                .options(
                    selectinload(Problem.stakeholders),
                    selectinload(Problem.constraints),
                    selectinload(Problem.success_criteria),
                    selectinload(Problem.solutions),
                    selectinload(Problem.cycles)
                )
                .where(Problem.id == problem_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error getting problem with relationships {problem_id}: {e}")
            raise
    
    async def search_problems(self, search_term: str) -> List[Problem]:
        """Search problems by title, description, or domain"""
        try:
            result = await self.session.execute(
                select(Problem)
                .where(
                    or_(
                        Problem.title.ilike(f"%{search_term}%"),
                        Problem.description.ilike(f"%{search_term}%"),
                        Problem.domain.ilike(f"%{search_term}%")
                    )
                )
                .order_by(desc(Problem.created_at))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error searching problems with term {search_term}: {e}")
            raise
    
    async def get_filtered_problems(
        self,
        domain: Optional[str] = None,
        complexity: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Problem]:
        """Get problems with multiple filters"""
        try:
            query = select(Problem)
            conditions = []
            
            if domain:
                conditions.append(Problem.domain == domain)
            if complexity:
                conditions.append(Problem.complexity == complexity)
            if status:
                conditions.append(Problem.status == status)
            if priority:
                conditions.append(Problem.priority == priority)
            
            if conditions:
                query = query.where(and_(*conditions))
            
            query = query.order_by(desc(Problem.created_at)).limit(limit).offset(offset)
            
            result = await self.session.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting filtered problems: {e}")
            raise
    
    async def get_problem_statistics(self) -> Dict[str, Any]:
        """Get problem statistics"""
        try:
            # Total problems
            total_result = await self.session.execute(
                select(func.count(Problem.id))
            )
            total_problems = total_result.scalar()
            
            # Problems by status
            status_result = await self.session.execute(
                select(Problem.status, func.count(Problem.id))
                .group_by(Problem.status)
            )
            status_counts = dict(status_result.fetchall())
            
            # Problems by complexity
            complexity_result = await self.session.execute(
                select(Problem.complexity, func.count(Problem.id))
                .group_by(Problem.complexity)
            )
            complexity_counts = dict(complexity_result.fetchall())
            
            # Problems by domain
            domain_result = await self.session.execute(
                select(Problem.domain, func.count(Problem.id))
                .group_by(Problem.domain)
            )
            domain_counts = dict(domain_result.fetchall())
            
            return {
                'total_problems': total_problems,
                'by_status': status_counts,
                'by_complexity': complexity_counts,
                'by_domain': domain_counts
            }
        except SQLAlchemyError as e:
            logger.error(f"Error getting problem statistics: {e}")
            raise


class ProblemStatementRepository(BaseRepository[ProblemStatement]):
    """Repository for ProblemStatement model"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, ProblemStatement)
    
    async def get_by_problem_id(self, problem_id: str) -> List[ProblemStatement]:
        """Get problem statements by problem ID"""
        try:
            result = await self.session.execute(
                select(ProblemStatement)
                .where(ProblemStatement.problem_id == problem_id)
                .order_by(desc(ProblemStatement.created_at))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting problem statements by problem ID {problem_id}: {e}")
            raise
    
    async def get_latest_by_problem_id(self, problem_id: str) -> Optional[ProblemStatement]:
        """Get the latest problem statement by problem ID"""
        try:
            result = await self.session.execute(
                select(ProblemStatement)
                .where(ProblemStatement.problem_id == problem_id)
                .order_by(desc(ProblemStatement.created_at))
                .limit(1)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error getting latest problem statement by problem ID {problem_id}: {e}")
            raise
