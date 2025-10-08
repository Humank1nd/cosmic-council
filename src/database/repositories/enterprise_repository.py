"""
Enterprise repository for database operations.
"""

from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, asc, func
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.exc import SQLAlchemyError
import logging

from .base_repository import BaseRepository
from ..models.enterprise import Enterprise, EnterpriseResult

logger = logging.getLogger(__name__)


class EnterpriseRepository(BaseRepository[Enterprise]):
    """Repository for Enterprise model"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Enterprise)
    
    async def get_by_type(self, enterprise_type: str) -> Optional[Enterprise]:
        """Get enterprise by type"""
        try:
            result = await self.session.execute(
                select(Enterprise)
                .where(Enterprise.enterprise_type == enterprise_type)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error getting enterprise by type {enterprise_type}: {e}")
            raise
    
    async def get_by_status(self, status: str) -> List[Enterprise]:
        """Get enterprises by status"""
        try:
            result = await self.session.execute(
                select(Enterprise)
                .where(Enterprise.status == status)
                .order_by(asc(Enterprise.enterprise_type))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting enterprises by status {status}: {e}")
            raise
    
    async def get_active_enterprises(self) -> List[Enterprise]:
        """Get all active enterprises"""
        try:
            result = await self.session.execute(
                select(Enterprise)
                .where(Enterprise.status == 'active')
                .order_by(asc(Enterprise.enterprise_type))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting active enterprises: {e}")
            raise
    
    async def get_with_relationships(self, enterprise_id: str) -> Optional[Enterprise]:
        """Get enterprise with all relationships loaded"""
        try:
            result = await self.session.execute(
                select(Enterprise)
                .options(
                    selectinload(Enterprise.cycles),
                    selectinload(Enterprise.results)
                )
                .where(Enterprise.id == enterprise_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error getting enterprise with relationships {enterprise_id}: {e}")
            raise
    
    async def update_configuration(self, enterprise_id: str, configuration: Dict[str, Any]) -> Optional[Enterprise]:
        """Update enterprise configuration"""
        try:
            enterprise = await self.get_by_id(enterprise_id)
            if not enterprise:
                return None
            
            enterprise.configuration = str(configuration)  # Store as JSON string
            await self.session.commit()
            await self.session.refresh(enterprise)
            return enterprise
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Error updating enterprise configuration {enterprise_id}: {e}")
            raise
    
    async def update_performance_metrics(self, enterprise_id: str, metrics: Dict[str, Any]) -> Optional[Enterprise]:
        """Update enterprise performance metrics"""
        try:
            enterprise = await self.get_by_id(enterprise_id)
            if not enterprise:
                return None
            
            enterprise.performance_metrics = str(metrics)  # Store as JSON string
            await self.session.commit()
            await self.session.refresh(enterprise)
            return enterprise
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Error updating enterprise performance metrics {enterprise_id}: {e}")
            raise
    
    async def get_enterprise_statistics(self) -> Dict[str, Any]:
        """Get enterprise statistics"""
        try:
            # Total enterprises
            total_result = await self.session.execute(
                select(func.count(Enterprise.id))
            )
            total_enterprises = total_result.scalar()
            
            # Enterprises by status
            status_result = await self.session.execute(
                select(Enterprise.status, func.count(Enterprise.id))
                .group_by(Enterprise.status)
            )
            status_counts = dict(status_result.fetchall())
            
            # Enterprises by type
            type_result = await self.session.execute(
                select(Enterprise.enterprise_type, func.count(Enterprise.id))
                .group_by(Enterprise.enterprise_type)
            )
            type_counts = dict(type_result.fetchall())
            
            return {
                'total_enterprises': total_enterprises,
                'by_status': status_counts,
                'by_type': type_counts
            }
        except SQLAlchemyError as e:
            logger.error(f"Error getting enterprise statistics: {e}")
            raise


class EnterpriseResultRepository(BaseRepository[EnterpriseResult]):
    """Repository for EnterpriseResult model"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, EnterpriseResult)
    
    async def get_by_cycle_id(self, cycle_id: str) -> List[EnterpriseResult]:
        """Get results by cycle ID"""
        try:
            result = await self.session.execute(
                select(EnterpriseResult)
                .where(EnterpriseResult.cycle_id == cycle_id)
                .order_by(asc(EnterpriseResult.created_at))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting enterprise results by cycle ID {cycle_id}: {e}")
            raise
    
    async def get_by_enterprise_id(self, enterprise_id: str) -> List[EnterpriseResult]:
        """Get results by enterprise ID"""
        try:
            result = await self.session.execute(
                select(EnterpriseResult)
                .where(EnterpriseResult.enterprise_id == enterprise_id)
                .order_by(desc(EnterpriseResult.created_at))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting enterprise results by enterprise ID {enterprise_id}: {e}")
            raise
    
    async def get_by_enterprise_type(self, enterprise_type: str) -> List[EnterpriseResult]:
        """Get results by enterprise type"""
        try:
            result = await self.session.execute(
                select(EnterpriseResult)
                .where(EnterpriseResult.enterprise_type == enterprise_type)
                .order_by(desc(EnterpriseResult.created_at))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting enterprise results by enterprise type {enterprise_type}: {e}")
            raise
    
    async def get_successful_results(self) -> List[EnterpriseResult]:
        """Get all successful results"""
        try:
            result = await self.session.execute(
                select(EnterpriseResult)
                .where(EnterpriseResult.success == 'true')
                .order_by(desc(EnterpriseResult.created_at))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting successful enterprise results: {e}")
            raise
    
    async def get_failed_results(self) -> List[EnterpriseResult]:
        """Get all failed results"""
        try:
            result = await self.session.execute(
                select(EnterpriseResult)
                .where(EnterpriseResult.success == 'false')
                .order_by(desc(EnterpriseResult.created_at))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting failed enterprise results: {e}")
            raise
    
    async def get_results_by_date_range(self, start_date: str, end_date: str) -> List[EnterpriseResult]:
        """Get results within a date range"""
        try:
            result = await self.session.execute(
                select(EnterpriseResult)
                .where(
                    and_(
                        EnterpriseResult.created_at >= start_date,
                        EnterpriseResult.created_at <= end_date
                    )
                )
                .order_by(desc(EnterpriseResult.created_at))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting enterprise results by date range {start_date}-{end_date}: {e}")
            raise
    
    async def get_high_quality_results(self, min_quality_score: float) -> List[EnterpriseResult]:
        """Get results with high quality scores"""
        try:
            result = await self.session.execute(
                select(EnterpriseResult)
                .where(EnterpriseResult.quality_score >= min_quality_score)
                .order_by(desc(EnterpriseResult.quality_score))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting high quality enterprise results {min_quality_score}: {e}")
            raise
    
    async def get_enterprise_result_statistics(self) -> Dict[str, Any]:
        """Get enterprise result statistics"""
        try:
            # Total results
            total_result = await self.session.execute(
                select(func.count(EnterpriseResult.id))
            )
            total_results = total_result.scalar()
            
            # Results by enterprise type
            type_result = await self.session.execute(
                select(EnterpriseResult.enterprise_type, func.count(EnterpriseResult.id))
                .group_by(EnterpriseResult.enterprise_type)
            )
            type_counts = dict(type_result.fetchall())
            
            # Results by success status
            success_result = await self.session.execute(
                select(EnterpriseResult.success, func.count(EnterpriseResult.id))
                .group_by(EnterpriseResult.success)
            )
            success_counts = dict(success_result.fetchall())
            
            # Average execution time
            time_result = await self.session.execute(
                select(func.avg(EnterpriseResult.execution_time))
            )
            avg_execution_time = time_result.scalar() or 0.0
            
            # Average quality score
            quality_result = await self.session.execute(
                select(func.avg(EnterpriseResult.quality_score))
            )
            avg_quality_score = quality_result.scalar() or 0.0
            
            return {
                'total_results': total_results,
                'by_enterprise_type': type_counts,
                'by_success': success_counts,
                'average_execution_time': float(avg_execution_time),
                'average_quality_score': float(avg_quality_score)
            }
        except SQLAlchemyError as e:
            logger.error(f"Error getting enterprise result statistics: {e}")
            raise
