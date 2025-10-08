"""
Cycle repository for database operations.
"""

from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, asc, func
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.exc import SQLAlchemyError
import logging

from .base_repository import BaseRepository
from ..models.cycle import Cycle, CycleResult

logger = logging.getLogger(__name__)


class CycleRepository(BaseRepository[Cycle]):
    """Repository for Cycle model"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Cycle)
    
    async def get_by_problem_id(self, problem_id: str) -> List[Cycle]:
        """Get cycles by problem ID"""
        try:
            result = await self.session.execute(
                select(Cycle)
                .where(Cycle.problem_id == problem_id)
                .order_by(desc(Cycle.created_at))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting cycles by problem ID {problem_id}: {e}")
            raise
    
    async def get_by_status(self, status: str) -> List[Cycle]:
        """Get cycles by status"""
        try:
            result = await self.session.execute(
                select(Cycle)
                .where(Cycle.status == status)
                .order_by(desc(Cycle.created_at))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting cycles by status {status}: {e}")
            raise
    
    async def get_active_cycles(self) -> List[Cycle]:
        """Get all active cycles (running or paused)"""
        try:
            result = await self.session.execute(
                select(Cycle)
                .where(Cycle.status.in_(['running', 'paused']))
                .order_by(desc(Cycle.created_at))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting active cycles: {e}")
            raise
    
    async def get_completed_cycles(self) -> List[Cycle]:
        """Get all completed cycles"""
        try:
            result = await self.session.execute(
                select(Cycle)
                .where(Cycle.status == 'completed')
                .order_by(desc(Cycle.completed_at))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting completed cycles: {e}")
            raise
    
    async def get_failed_cycles(self) -> List[Cycle]:
        """Get all failed cycles"""
        try:
            result = await self.session.execute(
                select(Cycle)
                .where(Cycle.status == 'failed')
                .order_by(desc(Cycle.completed_at))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting failed cycles: {e}")
            raise
    
    async def get_by_creator(self, user_id: str) -> List[Cycle]:
        """Get cycles created by a user"""
        try:
            result = await self.session.execute(
                select(Cycle)
                .where(Cycle.created_by == user_id)
                .order_by(desc(Cycle.created_at))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting cycles by creator {user_id}: {e}")
            raise
    
    async def get_with_relationships(self, cycle_id: str) -> Optional[Cycle]:
        """Get cycle with all relationships loaded"""
        try:
            result = await self.session.execute(
                select(Cycle)
                .options(
                    selectinload(Cycle.enterprises),
                    selectinload(Cycle.results)
                )
                .where(Cycle.id == cycle_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error getting cycle with relationships {cycle_id}: {e}")
            raise
    
    async def get_cycles_by_date_range(self, start_date: str, end_date: str) -> List[Cycle]:
        """Get cycles within a date range"""
        try:
            result = await self.session.execute(
                select(Cycle)
                .where(
                    and_(
                        Cycle.created_at >= start_date,
                        Cycle.created_at <= end_date
                    )
                )
                .order_by(desc(Cycle.created_at))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting cycles by date range {start_date}-{end_date}: {e}")
            raise
    
    async def get_cycle_statistics(self) -> Dict[str, Any]:
        """Get cycle statistics"""
        try:
            # Total cycles
            total_result = await self.session.execute(
                select(func.count(Cycle.id))
            )
            total_cycles = total_result.scalar()
            
            # Cycles by status
            status_result = await self.session.execute(
                select(Cycle.status, func.count(Cycle.id))
                .group_by(Cycle.status)
            )
            status_counts = dict(status_result.fetchall())
            
            # Average execution time (for completed cycles)
            time_result = await self.session.execute(
                select(
                    func.avg(
                        func.extract('epoch', Cycle.completed_at) - 
                        func.extract('epoch', Cycle.started_at)
                    )
                )
                .where(Cycle.status == 'completed')
            )
            avg_execution_time = time_result.scalar() or 0.0
            
            # Success rate
            success_result = await self.session.execute(
                select(func.count(Cycle.id))
                .where(Cycle.status == 'completed')
            )
            successful_cycles = success_result.scalar()
            success_rate = (successful_cycles / total_cycles * 100) if total_cycles > 0 else 0.0
            
            return {
                'total_cycles': total_cycles,
                'by_status': status_counts,
                'average_execution_time': float(avg_execution_time),
                'success_rate': float(success_rate)
            }
        except SQLAlchemyError as e:
            logger.error(f"Error getting cycle statistics: {e}")
            raise


class CycleResultRepository(BaseRepository[CycleResult]):
    """Repository for CycleResult model"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, CycleResult)
    
    async def get_by_cycle_id(self, cycle_id: str) -> List[CycleResult]:
        """Get results by cycle ID"""
        try:
            result = await self.session.execute(
                select(CycleResult)
                .where(CycleResult.cycle_id == cycle_id)
                .order_by(asc(CycleResult.created_at))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting results by cycle ID {cycle_id}: {e}")
            raise
    
    async def get_by_enterprise_type(self, enterprise_type: str) -> List[CycleResult]:
        """Get results by enterprise type"""
        try:
            result = await self.session.execute(
                select(CycleResult)
                .where(CycleResult.enterprise_type == enterprise_type)
                .order_by(desc(CycleResult.created_at))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting results by enterprise type {enterprise_type}: {e}")
            raise
    
    async def get_successful_results(self) -> List[CycleResult]:
        """Get all successful results"""
        try:
            result = await self.session.execute(
                select(CycleResult)
                .where(CycleResult.success == 'true')
                .order_by(desc(CycleResult.created_at))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting successful results: {e}")
            raise
    
    async def get_failed_results(self) -> List[CycleResult]:
        """Get all failed results"""
        try:
            result = await self.session.execute(
                select(CycleResult)
                .where(CycleResult.success == 'false')
                .order_by(desc(CycleResult.created_at))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting failed results: {e}")
            raise
    
    async def get_enterprise_performance(self, enterprise_type: str) -> Dict[str, Any]:
        """Get performance metrics for an enterprise type"""
        try:
            # Total executions
            total_result = await self.session.execute(
                select(func.count(CycleResult.id))
                .where(CycleResult.enterprise_type == enterprise_type)
            )
            total_executions = total_result.scalar()
            
            # Successful executions
            success_result = await self.session.execute(
                select(func.count(CycleResult.id))
                .where(
                    and_(
                        CycleResult.enterprise_type == enterprise_type,
                        CycleResult.success == 'true'
                    )
                )
            )
            successful_executions = success_result.scalar()
            
            # Average execution time
            time_result = await self.session.execute(
                select(func.avg(CycleResult.execution_time))
                .where(CycleResult.enterprise_type == enterprise_type)
            )
            avg_execution_time = time_result.scalar() or 0.0
            
            # Average quality score
            quality_result = await self.session.execute(
                select(func.avg(CycleResult.quality_score))
                .where(CycleResult.enterprise_type == enterprise_type)
            )
            avg_quality_score = quality_result.scalar() or 0.0
            
            # Success rate
            success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0.0
            
            return {
                'enterprise_type': enterprise_type,
                'total_executions': total_executions,
                'successful_executions': successful_executions,
                'success_rate': float(success_rate),
                'average_execution_time': float(avg_execution_time),
                'average_quality_score': float(avg_quality_score)
            }
        except SQLAlchemyError as e:
            logger.error(f"Error getting enterprise performance for {enterprise_type}: {e}")
            raise
