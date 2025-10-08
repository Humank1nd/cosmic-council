"""
Solution repository for database operations.
"""

from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, asc, func
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.exc import SQLAlchemyError
import logging

from .base_repository import BaseRepository
from ..models.solution import Solution, SolutionComponent

logger = logging.getLogger(__name__)


class SolutionRepository(BaseRepository[Solution]):
    """Repository for Solution model"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Solution)
    
    async def get_by_problem_id(self, problem_id: str) -> List[Solution]:
        """Get solutions by problem ID"""
        try:
            result = await self.session.execute(
                select(Solution)
                .where(Solution.problem_id == problem_id)
                .order_by(desc(Solution.created_at))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting solutions by problem ID {problem_id}: {e}")
            raise
    
    async def get_by_status(self, status: str) -> List[Solution]:
        """Get solutions by status"""
        try:
            result = await self.session.execute(
                select(Solution)
                .where(Solution.status == status)
                .order_by(desc(Solution.created_at))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting solutions by status {status}: {e}")
            raise
    
    async def get_by_creator(self, user_id: str) -> List[Solution]:
        """Get solutions created by a user"""
        try:
            result = await self.session.execute(
                select(Solution)
                .where(Solution.created_by == user_id)
                .order_by(desc(Solution.created_at))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting solutions by creator {user_id}: {e}")
            raise
    
    async def get_with_components(self, solution_id: str) -> Optional[Solution]:
        """Get solution with components loaded"""
        try:
            result = await self.session.execute(
                select(Solution)
                .options(selectinload(Solution.components))
                .where(Solution.id == solution_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error getting solution with components {solution_id}: {e}")
            raise
    
    async def get_by_confidence_score(self, min_score: float, max_score: float = 1.0) -> List[Solution]:
        """Get solutions by confidence score range"""
        try:
            result = await self.session.execute(
                select(Solution)
                .where(
                    and_(
                        Solution.confidence_score >= min_score,
                        Solution.confidence_score <= max_score
                    )
                )
                .order_by(desc(Solution.confidence_score))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting solutions by confidence score {min_score}-{max_score}: {e}")
            raise
    
    async def search_solutions(self, search_term: str) -> List[Solution]:
        """Search solutions by title, description, or approach"""
        try:
            result = await self.session.execute(
                select(Solution)
                .where(
                    or_(
                        Solution.title.ilike(f"%{search_term}%"),
                        Solution.description.ilike(f"%{search_term}%"),
                        Solution.approach.ilike(f"%{search_term}%")
                    )
                )
                .order_by(desc(Solution.created_at))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error searching solutions with term {search_term}: {e}")
            raise
    
    async def get_filtered_solutions(
        self,
        problem_id: Optional[str] = None,
        status: Optional[str] = None,
        min_confidence: Optional[float] = None,
        max_confidence: Optional[float] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Solution]:
        """Get solutions with multiple filters"""
        try:
            query = select(Solution)
            conditions = []
            
            if problem_id:
                conditions.append(Solution.problem_id == problem_id)
            if status:
                conditions.append(Solution.status == status)
            if min_confidence is not None:
                conditions.append(Solution.confidence_score >= min_confidence)
            if max_confidence is not None:
                conditions.append(Solution.confidence_score <= max_confidence)
            
            if conditions:
                query = query.where(and_(*conditions))
            
            query = query.order_by(desc(Solution.created_at)).limit(limit).offset(offset)
            
            result = await self.session.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting filtered solutions: {e}")
            raise
    
    async def get_solution_statistics(self) -> Dict[str, Any]:
        """Get solution statistics"""
        try:
            # Total solutions
            total_result = await self.session.execute(
                select(func.count(Solution.id))
            )
            total_solutions = total_result.scalar()
            
            # Solutions by status
            status_result = await self.session.execute(
                select(Solution.status, func.count(Solution.id))
                .group_by(Solution.status)
            )
            status_counts = dict(status_result.fetchall())
            
            # Average confidence score
            confidence_result = await self.session.execute(
                select(func.avg(Solution.confidence_score))
            )
            avg_confidence = confidence_result.scalar() or 0.0
            
            # Solutions by problem
            problem_result = await self.session.execute(
                select(Solution.problem_id, func.count(Solution.id))
                .group_by(Solution.problem_id)
            )
            problem_counts = dict(problem_result.fetchall())
            
            return {
                'total_solutions': total_solutions,
                'by_status': status_counts,
                'average_confidence': float(avg_confidence),
                'by_problem': problem_counts
            }
        except SQLAlchemyError as e:
            logger.error(f"Error getting solution statistics: {e}")
            raise


class SolutionComponentRepository(BaseRepository[SolutionComponent]):
    """Repository for SolutionComponent model"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, SolutionComponent)
    
    async def get_by_solution_id(self, solution_id: str) -> List[SolutionComponent]:
        """Get components by solution ID"""
        try:
            result = await self.session.execute(
                select(SolutionComponent)
                .where(SolutionComponent.solution_id == solution_id)
                .order_by(asc(SolutionComponent.priority))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting components by solution ID {solution_id}: {e}")
            raise
    
    async def get_by_type(self, component_type: str) -> List[SolutionComponent]:
        """Get components by type"""
        try:
            result = await self.session.execute(
                select(SolutionComponent)
                .where(SolutionComponent.component_type == component_type)
                .order_by(desc(SolutionComponent.created_at))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting components by type {component_type}: {e}")
            raise
    
    async def get_by_priority(self, priority: str) -> List[SolutionComponent]:
        """Get components by priority"""
        try:
            result = await self.session.execute(
                select(SolutionComponent)
                .where(SolutionComponent.priority == priority)
                .order_by(desc(SolutionComponent.created_at))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting components by priority {priority}: {e}")
            raise
    
    async def get_high_effort_components(self, min_effort: float) -> List[SolutionComponent]:
        """Get components with high estimated effort"""
        try:
            result = await self.session.execute(
                select(SolutionComponent)
                .where(SolutionComponent.estimated_effort >= min_effort)
                .order_by(desc(SolutionComponent.estimated_effort))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting high effort components {min_effort}: {e}")
            raise
    
    async def get_component_statistics(self) -> Dict[str, Any]:
        """Get component statistics"""
        try:
            # Total components
            total_result = await self.session.execute(
                select(func.count(SolutionComponent.id))
            )
            total_components = total_result.scalar()
            
            # Components by type
            type_result = await self.session.execute(
                select(SolutionComponent.component_type, func.count(SolutionComponent.id))
                .group_by(SolutionComponent.component_type)
            )
            type_counts = dict(type_result.fetchall())
            
            # Components by priority
            priority_result = await self.session.execute(
                select(SolutionComponent.priority, func.count(SolutionComponent.id))
                .group_by(SolutionComponent.priority)
            )
            priority_counts = dict(priority_result.fetchall())
            
            # Average effort
            effort_result = await self.session.execute(
                select(func.avg(SolutionComponent.estimated_effort))
            )
            avg_effort = effort_result.scalar() or 0.0
            
            return {
                'total_components': total_components,
                'by_type': type_counts,
                'by_priority': priority_counts,
                'average_effort': float(avg_effort)
            }
        except SQLAlchemyError as e:
            logger.error(f"Error getting component statistics: {e}")
            raise
