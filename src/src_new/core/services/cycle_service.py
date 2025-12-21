"""
Cycle service for managing problem-solving cycles in the Cosmic Council system.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import logging
import asyncio

from ..models.cycle import Cycle, CycleResult
from ..models.problem import Problem
from ..types import CycleStatus, EnterpriseType

logger = logging.getLogger(__name__)


class CycleService:
    """Service for managing problem-solving cycles"""
    
    def __init__(self, repository=None, enterprise_service=None):
        self.repository = repository
        self.enterprise_service = enterprise_service
        self.logger = logger
    
    async def create_cycle(self, cycle_data: Dict[str, Any]) -> Cycle:
        """Create a new problem-solving cycle"""
        try:
            cycle = Cycle(**cycle_data)
            if not cycle.validate():
                raise ValueError("Invalid cycle data")
            
            if self.repository:
                await self.repository.create(cycle)
            
            self.logger.info(f"Created cycle: {cycle.id}")
            return cycle
            
        except Exception as e:
            self.logger.error(f"Error creating cycle: {e}")
            raise
    
    async def get_cycle(self, cycle_id: str) -> Optional[Cycle]:
        """Get a cycle by ID"""
        try:
            if self.repository:
                return await self.repository.get_by_id(cycle_id)
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting cycle {cycle_id}: {e}")
            raise
    
    async def start_cycle(self, cycle_id: str) -> Optional[Cycle]:
        """Start a cycle execution"""
        try:
            if self.repository:
                cycle = await self.repository.get_by_id(cycle_id)
                if not cycle:
                    return None
                
                if cycle.status != CycleStatus.PENDING:
                    raise ValueError(f"Cannot start cycle in status: {cycle.status}")
                
                cycle.start()
                await self.repository.update(cycle)
                
                self.logger.info(f"Started cycle: {cycle_id}")
                return cycle
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error starting cycle {cycle_id}: {e}")
            raise
    
    async def execute_cycle(self, cycle_id: str) -> Optional[Cycle]:
        """Execute a complete cycle"""
        try:
            cycle = await self.get_cycle(cycle_id)
            if not cycle:
                return None
            
            if cycle.status != CycleStatus.PENDING:
                raise ValueError(f"Cannot execute cycle in status: {cycle.status}")
            
            cycle.start()
            await self.repository.update(cycle)
            
            # Execute each enterprise in sequence
            for enterprise_type in cycle.enterprises:
                try:
                    cycle.current_enterprise = enterprise_type
                    await self.repository.update(cycle)
                    
                    # Execute enterprise (placeholder - would integrate with actual enterprise service)
                    result = await self._execute_enterprise(cycle, enterprise_type)
                    
                    # Store result
                    cycle.results[enterprise_type.value] = result
                    
                except Exception as e:
                    self.logger.error(f"Error executing enterprise {enterprise_type}: {e}")
                    cycle.fail(f"Enterprise {enterprise_type} failed: {str(e)}")
                    await self.repository.update(cycle)
                    return cycle
            
            # Complete the cycle
            cycle.complete()
            await self.repository.update(cycle)
            
            self.logger.info(f"Completed cycle: {cycle_id}")
            return cycle
            
        except Exception as e:
            self.logger.error(f"Error executing cycle {cycle_id}: {e}")
            if cycle:
                cycle.fail(str(e))
                await self.repository.update(cycle)
            raise
    
    async def pause_cycle(self, cycle_id: str) -> Optional[Cycle]:
        """Pause a running cycle"""
        try:
            if self.repository:
                cycle = await self.repository.get_by_id(cycle_id)
                if not cycle:
                    return None
                
                if cycle.status != CycleStatus.RUNNING:
                    raise ValueError(f"Cannot pause cycle in status: {cycle.status}")
                
                cycle.status = CycleStatus.PAUSED
                cycle.updated_at = datetime.now(timezone.utc)
                await self.repository.update(cycle)
                
                self.logger.info(f"Paused cycle: {cycle_id}")
                return cycle
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error pausing cycle {cycle_id}: {e}")
            raise
    
    async def resume_cycle(self, cycle_id: str) -> Optional[Cycle]:
        """Resume a paused cycle"""
        try:
            if self.repository:
                cycle = await self.repository.get_by_id(cycle_id)
                if not cycle:
                    return None
                
                if cycle.status != CycleStatus.PAUSED:
                    raise ValueError(f"Cannot resume cycle in status: {cycle.status}")
                
                cycle.status = CycleStatus.RUNNING
                cycle.updated_at = datetime.now(timezone.utc)
                await self.repository.update(cycle)
                
                self.logger.info(f"Resumed cycle: {cycle_id}")
                return cycle
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error resuming cycle {cycle_id}: {e}")
            raise
    
    async def cancel_cycle(self, cycle_id: str) -> Optional[Cycle]:
        """Cancel a cycle"""
        try:
            if self.repository:
                cycle = await self.repository.get_by_id(cycle_id)
                if not cycle:
                    return None
                
                if cycle.status in [CycleStatus.COMPLETED, CycleStatus.FAILED]:
                    raise ValueError(f"Cannot cancel cycle in status: {cycle.status}")
                
                cycle.status = CycleStatus.FAILED
                cycle.completed_at = datetime.now(timezone.utc)
                cycle.update_metadata('cancelled', True)
                await self.repository.update(cycle)
                
                self.logger.info(f"Cancelled cycle: {cycle_id}")
                return cycle
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error cancelling cycle {cycle_id}: {e}")
            raise
    
    async def _execute_enterprise(self, cycle: Cycle, enterprise_type: EnterpriseType) -> Dict[str, Any]:
        """Execute a single enterprise (placeholder implementation)"""
        try:
            # This would integrate with the actual enterprise service
            # For now, return a placeholder result
            result = {
                'enterprise_type': enterprise_type.value,
                'execution_time': 1.0,
                'success': True,
                'output_data': {
                    'message': f"Enterprise {enterprise_type.value} executed successfully",
                    'timestamp': datetime.now(timezone.utc).isoformat()
                },
                'metrics': {
                    'processing_time': 1.0,
                    'quality_score': 0.8
                }
            }
            
            # Simulate some processing time
            await asyncio.sleep(0.1)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing enterprise {enterprise_type}: {e}")
            return {
                'enterprise_type': enterprise_type.value,
                'execution_time': 0.0,
                'success': False,
                'error_message': str(e),
                'output_data': {}
            }
    
    async def get_cycle_results(self, cycle_id: str) -> List[CycleResult]:
        """Get all results for a cycle"""
        try:
            if self.repository:
                return await self.repository.get_results_by_cycle_id(cycle_id)
            return []
            
        except Exception as e:
            self.logger.error(f"Error getting cycle results: {e}")
            raise
