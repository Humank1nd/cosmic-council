"""
Enterprise service for managing enterprises in the Cosmic Council system.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import logging

from ..models.enterprise import Enterprise, EnterpriseResult
from ..types import EnterpriseType

logger = logging.getLogger(__name__)


class EnterpriseService:
    """Service for managing enterprises"""
    
    def __init__(self, repository=None):
        self.repository = repository
        self.logger = logger
    
    async def create_enterprise(self, enterprise_data: Dict[str, Any]) -> Enterprise:
        """Create a new enterprise"""
        try:
            enterprise = Enterprise(**enterprise_data)
            if not enterprise.validate():
                raise ValueError("Invalid enterprise data")
            
            if self.repository:
                await self.repository.create(enterprise)
            
            self.logger.info(f"Created enterprise: {enterprise.id}")
            return enterprise
            
        except Exception as e:
            self.logger.error(f"Error creating enterprise: {e}")
            raise
    
    async def get_enterprise(self, enterprise_id: str) -> Optional[Enterprise]:
        """Get an enterprise by ID"""
        try:
            if self.repository:
                return await self.repository.get_by_id(enterprise_id)
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting enterprise {enterprise_id}: {e}")
            raise
    
    async def get_enterprise_by_type(self, enterprise_type: EnterpriseType) -> Optional[Enterprise]:
        """Get an enterprise by type"""
        try:
            if self.repository:
                return await self.repository.get_by_type(enterprise_type)
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting enterprise by type {enterprise_type}: {e}")
            raise
    
    async def list_enterprises(self, filters: Optional[Dict[str, Any]] = None) -> List[Enterprise]:
        """List enterprises with optional filters"""
        try:
            if self.repository:
                return await self.repository.list(filters)
            return []
            
        except Exception as e:
            self.logger.error(f"Error listing enterprises: {e}")
            raise
    
    async def update_enterprise(self, enterprise_id: str, updates: Dict[str, Any]) -> Optional[Enterprise]:
        """Update an enterprise"""
        try:
            if self.repository:
                enterprise = await self.repository.get_by_id(enterprise_id)
                if not enterprise:
                    return None
                
                # Update fields
                for key, value in updates.items():
                    if hasattr(enterprise, key):
                        setattr(enterprise, key, value)
                
                enterprise.updated_at = datetime.now(timezone.utc)
                
                if not enterprise.validate():
                    raise ValueError("Invalid updated enterprise data")
                
                await self.repository.update(enterprise)
                return enterprise
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error updating enterprise {enterprise_id}: {e}")
            raise
    
    async def execute_enterprise(self, enterprise_type: EnterpriseType, input_data: Dict[str, Any]) -> EnterpriseResult:
        """Execute an enterprise with given input data"""
        try:
            enterprise = await self.get_enterprise_by_type(enterprise_type)
            if not enterprise:
                raise ValueError(f"Enterprise {enterprise_type} not found")
            
            start_time = datetime.now(timezone.utc)
            
            # Execute enterprise logic based on type
            result_data = await self._execute_enterprise_logic(enterprise_type, input_data)
            
            end_time = datetime.now(timezone.utc)
            execution_time = (end_time - start_time).total_seconds()
            
            # Create result
            result = EnterpriseResult(
                cycle_id=input_data.get('cycle_id', ''),
                enterprise_type=enterprise_type,
                input_data=input_data,
                output_data=result_data,
                success=True,
                execution_time=execution_time,
                resources_used={'cpu_time': execution_time},
                quality_score=0.8  # Placeholder
            )
            
            if self.repository:
                await self.repository.create_result(result)
            
            self.logger.info(f"Executed enterprise {enterprise_type}: {result.id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing enterprise {enterprise_type}: {e}")
            
            # Create error result
            result = EnterpriseResult(
                cycle_id=input_data.get('cycle_id', ''),
                enterprise_type=enterprise_type,
                input_data=input_data,
                output_data={},
                success=False,
                error_message=str(e),
                execution_time=0.0,
                quality_score=0.0
            )
            
            if self.repository:
                await self.repository.create_result(result)
            
            return result
    
    async def _execute_enterprise_logic(self, enterprise_type: EnterpriseType, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the specific logic for an enterprise type"""
        try:
            if enterprise_type == EnterpriseType.RED_OWL:
                return await self._execute_research_enterprise(input_data)
            elif enterprise_type == EnterpriseType.ORANGE_ORANGUTAN:
                return await self._execute_planning_enterprise(input_data)
            elif enterprise_type == EnterpriseType.YELLOW_HONEYBEE:
                return await self._execute_development_enterprise(input_data)
            elif enterprise_type == EnterpriseType.GREEN_TORTOISE:
                return await self._execute_budget_enterprise(input_data)
            elif enterprise_type == EnterpriseType.BLUE_DOLPHIN:
                return await self._execute_market_enterprise(input_data)
            elif enterprise_type == EnterpriseType.PURPLE_ELEPHANT:
                return await self._execute_support_enterprise(input_data)
            else:
                raise ValueError(f"Unknown enterprise type: {enterprise_type}")
                
        except Exception as e:
            self.logger.error(f"Error in enterprise logic for {enterprise_type}: {e}")
            raise
    
    async def _execute_research_enterprise(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute research enterprise logic"""
        return {
            'research_findings': [
                'Key insight 1: Problem requires multi-disciplinary approach',
                'Key insight 2: Stakeholder alignment is critical',
                'Key insight 3: Technical feasibility confirmed'
            ],
            'prioritized_questions': [
                'What are the core requirements?',
                'What are the main constraints?',
                'What are the success criteria?'
            ],
            'research_notes': 'Comprehensive research completed'
        }
    
    async def _execute_planning_enterprise(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute planning enterprise logic"""
        return {
            'action_plan': {
                'phases': [
                    {'name': 'Phase 1', 'duration': '2 weeks', 'tasks': ['Task 1', 'Task 2']},
                    {'name': 'Phase 2', 'duration': '3 weeks', 'tasks': ['Task 3', 'Task 4']}
                ]
            },
            'dependencies': [
                {'from': 'Task 1', 'to': 'Task 3', 'type': 'blocking'}
            ],
            'risk_assessment': 'Low to medium risk identified'
        }
    
    async def _execute_development_enterprise(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute development enterprise logic"""
        return {
            'prototypes': [
                {'name': 'Prototype A', 'description': 'Initial concept', 'status': 'completed'},
                {'name': 'Prototype B', 'description': 'Refined version', 'status': 'in_progress'}
            ],
            'testing_results': {
                'unit_tests': '95% pass rate',
                'integration_tests': '90% pass rate'
            },
            'creative_notes': 'Innovative approach identified'
        }
    
    async def _execute_budget_enterprise(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute budget enterprise logic"""
        return {
            'resource_inventory': {
                'human_resources': 5,
                'technical_resources': 3,
                'financial_budget': 50000
            },
            'allocations': {
                'development': 60,
                'testing': 20,
                'deployment': 20
            },
            'cost_analysis': 'Budget within acceptable range'
        }
    
    async def _execute_market_enterprise(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute market enterprise logic"""
        return {
            'market_insights': [
                'Target market identified',
                'Competitive analysis completed',
                'Market opportunity validated'
            ],
            'communication_strategy': {
                'channels': ['email', 'social_media', 'direct_mail'],
                'messaging': 'Clear value proposition'
            },
            'performance_metrics': {
                'reach': 10000,
                'engagement': 0.15
            }
        }
    
    async def _execute_support_enterprise(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute support enterprise logic"""
        return {
            'user_feedback': [
                {'user': 'User A', 'rating': 5, 'comment': 'Excellent solution'},
                {'user': 'User B', 'rating': 4, 'comment': 'Good, minor improvements needed'}
            ],
            'performance_assessment': {
                'overall_score': 4.5,
                'areas_for_improvement': ['Documentation', 'Training']
            },
            'continuous_improvement': {
                'recommendations': ['Improve documentation', 'Add training materials'],
                'priority': 'high'
            }
        }
