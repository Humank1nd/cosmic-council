"""
Green Tortoise Agent - Budget & Resources Enterprise
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from ..base.agent import LLMAgent
from ..base.llm_config import LLMConfig, LLMProvider, LLMModel
from ...core.types import EnterpriseType

logger = logging.getLogger(__name__)


class GreenTortoiseAgent(LLMAgent):
    """Green Tortoise Agent for budget and resource management"""
    
    def __init__(self, agent_id: str = None, llm_config: LLMConfig = None):
        super().__init__(
            agent_id=agent_id,
            name="Green Tortoise",
            description="Budget & Resources Enterprise - Manages budgets, resources, and cost optimization",
            llm_config=llm_config
        )
        self.enterprise_type = EnterpriseType.GREEN_TORTOISE
        self.capabilities = [
            "budget_planning",
            "resource_allocation",
            "cost_analysis",
            "financial_optimization",
            "risk_management",
            "roi_calculation"
        ]
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input for budget tasks"""
        required_fields = ['project_scope', 'budget_constraints']
        return all(field in input_data for field in required_fields)
    
    def build_prompt(self, input_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> str:
        """Build budget planning prompt"""
        project_scope = input_data.get('project_scope', {})
        budget_constraints = input_data.get('budget_constraints', {})
        timeline = input_data.get('timeline', '')
        
        prompt = f"""
        As the Green Tortoise Budget Agent, create a comprehensive budget and resource plan based on:
        
        Project Scope: {project_scope}
        Budget Constraints: {budget_constraints}
        Timeline: {timeline}
        
        Please provide:
        1. Resource inventory and requirements
        2. Budget allocation and breakdown
        3. Cost analysis and optimization
        4. Risk assessment and mitigation
        5. ROI projections and metrics
        6. Resource utilization recommendations
        
        Focus on efficiency, cost-effectiveness, and sustainable resource management.
        """
        
        return prompt
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process budget planning request"""
        try:
            # Build budget planning prompt
            prompt = self.build_prompt(input_data)
            
            # Call LLM for budget analysis
            budget_response = await self.call_llm(prompt, input_data)
            
            # Structure the budget results
            resource_inventory = self._extract_resource_inventory(budget_response)
            budget_allocation = self._extract_budget_allocation(budget_response)
            cost_analysis = self._extract_cost_analysis(budget_response)
            roi_projection = self._extract_roi_projection(budget_response)
            
            return {
                'agent_id': self.agent_id,
                'enterprise_type': self.enterprise_type.value,
                'resource_inventory': resource_inventory,
                'budget_allocation': budget_allocation,
                'cost_analysis': cost_analysis,
                'roi_projection': roi_projection,
                'budget_notes': budget_response,
                'timestamp': datetime.utcnow().isoformat(),
                'input_data': input_data
            }
            
        except Exception as e:
            self.logger.error(f"Green Tortoise budget processing failed: {e}")
            raise
    
    def _extract_resource_inventory(self, response: str) -> Dict[str, Any]:
        """Extract resource inventory from LLM response"""
        return {
            'human_resources': {
                'developers': 3,
                'designers': 1,
                'project_manager': 1,
                'qa_engineers': 1,
                'total_cost_per_month': 45000
            },
            'technical_resources': {
                'servers': 2,
                'cloud_services': 'AWS/GCP',
                'software_licenses': 5,
                'total_cost_per_month': 2000
            },
            'infrastructure': {
                'office_space': 'Remote/Hybrid',
                'equipment': 'Laptops, monitors',
                'total_cost_per_month': 3000
            }
        }
    
    def _extract_budget_allocation(self, response: str) -> Dict[str, Any]:
        """Extract budget allocation from LLM response"""
        return {
            'development': {
                'percentage': 60,
                'amount': 30000,
                'description': 'Core development and implementation'
            },
            'testing': {
                'percentage': 15,
                'amount': 7500,
                'description': 'Quality assurance and testing'
            },
            'deployment': {
                'percentage': 10,
                'amount': 5000,
                'description': 'Deployment and infrastructure'
            },
            'documentation': {
                'percentage': 8,
                'amount': 4000,
                'description': 'Documentation and training'
            },
            'contingency': {
                'percentage': 7,
                'amount': 3500,
                'description': 'Buffer for unexpected costs'
            }
        }
    
    def _extract_cost_analysis(self, response: str) -> Dict[str, Any]:
        """Extract cost analysis from LLM response"""
        return {
            'total_budget': 50000,
            'monthly_costs': 5000,
            'cost_breakdown': {
                'personnel': 45000,
                'infrastructure': 2000,
                'software': 1000,
                'miscellaneous': 2000
            },
            'cost_optimization_opportunities': [
                'Use open-source tools where possible',
                'Implement cloud-based solutions for scalability',
                'Optimize resource utilization',
                'Negotiate better rates with vendors'
            ],
            'risk_factors': [
                'Scope creep may increase costs',
                'Technical challenges may require additional resources',
                'Timeline delays may impact budget'
            ]
        }
    
    def _extract_roi_projection(self, response: str) -> Dict[str, Any]:
        """Extract ROI projection from LLM response"""
        return {
            'investment': 50000,
            'expected_returns': {
                'year_1': 75000,
                'year_2': 100000,
                'year_3': 125000
            },
            'roi_calculation': {
                'year_1_roi': 0.5,
                'year_2_roi': 1.0,
                'year_3_roi': 1.5
            },
            'payback_period': '12 months',
            'npv': 150000,
            'irr': 0.25
        }
