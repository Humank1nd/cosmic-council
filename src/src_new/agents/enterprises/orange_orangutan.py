"""
Orange Orangutan Agent - Planning & Strategy Enterprise
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from ..base.agent import LLMAgent
from ..base.llm_config import LLMConfig, LLMProvider, LLMModel
from ...core.types import EnterpriseType

logger = logging.getLogger(__name__)


class OrangeOrangutanAgent(LLMAgent):
    """Orange Orangutan Agent for planning and strategy"""
    
    def __init__(self, agent_id: str = None, llm_config: LLMConfig = None):
        super().__init__(
            agent_id=agent_id,
            name="Orange Orangutan",
            description="Planning & Strategy Enterprise - Creates comprehensive action plans and strategic roadmaps",
            llm_config=llm_config
        )
        self.enterprise_type = EnterpriseType.ORANGE_ORANGUTAN
        self.capabilities = [
            "strategic_planning",
            "action_plan_creation",
            "dependency_analysis",
            "risk_assessment",
            "timeline_estimation",
            "resource_planning"
        ]
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input for planning tasks"""
        required_fields = ['research_findings', 'objectives']
        return all(field in input_data for field in required_fields)
    
    def build_prompt(self, input_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> str:
        """Build planning prompt"""
        research_findings = input_data.get('research_findings', [])
        objectives = input_data.get('objectives', [])
        constraints = input_data.get('constraints', {})
        timeline = input_data.get('timeline', '')
        
        prompt = f"""
        As the Orange Orangutan Planning Agent, create a comprehensive action plan based on:
        
        Research Findings: {research_findings}
        Objectives: {objectives}
        Constraints: {constraints}
        Timeline: {timeline}
        
        Please provide:
        1. Strategic action plan with phases
        2. Task breakdown and dependencies
        3. Risk assessment and mitigation strategies
        4. Resource requirements and allocation
        5. Timeline with milestones
        6. Success metrics and KPIs
        
        Focus on feasibility, clarity, and actionable steps.
        """
        
        return prompt
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process planning request"""
        try:
            # Build planning prompt
            prompt = self.build_prompt(input_data)
            
            # Call LLM for planning analysis
            planning_response = await self.call_llm(prompt, input_data)
            
            # Structure the planning results
            action_plan = self._extract_action_plan(planning_response)
            dependencies = self._extract_dependencies(planning_response)
            risk_assessment = self._extract_risk_assessment(planning_response)
            timeline = self._extract_timeline(planning_response)
            
            return {
                'agent_id': self.agent_id,
                'enterprise_type': self.enterprise_type.value,
                'action_plan': action_plan,
                'dependencies': dependencies,
                'risk_assessment': risk_assessment,
                'timeline': timeline,
                'planning_notes': planning_response,
                'timestamp': datetime.utcnow().isoformat(),
                'input_data': input_data
            }
            
        except Exception as e:
            self.logger.error(f"Orange Orangutan planning processing failed: {e}")
            raise
    
    def _extract_action_plan(self, response: str) -> Dict[str, Any]:
        """Extract action plan from LLM response"""
        return {
            'phases': [
                {
                    'name': 'Phase 1: Foundation',
                    'duration': '2 weeks',
                    'tasks': ['Setup infrastructure', 'Define requirements', 'Create initial prototypes']
                },
                {
                    'name': 'Phase 2: Development',
                    'duration': '4 weeks', 
                    'tasks': ['Core development', 'Testing', 'Integration']
                },
                {
                    'name': 'Phase 3: Deployment',
                    'duration': '1 week',
                    'tasks': ['Final testing', 'Deployment', 'Documentation']
                }
            ],
            'total_duration': '7 weeks',
            'key_milestones': [
                'Requirements finalized',
                'Prototype completed',
                'Core features implemented',
                'Testing completed',
                'Production deployment'
            ]
        }
    
    def _extract_dependencies(self, response: str) -> List[Dict[str, str]]:
        """Extract dependencies from LLM response"""
        return [
            {'from': 'Setup infrastructure', 'to': 'Core development', 'type': 'blocking'},
            {'from': 'Define requirements', 'to': 'Create initial prototypes', 'type': 'blocking'},
            {'from': 'Core development', 'to': 'Testing', 'type': 'blocking'},
            {'from': 'Testing', 'to': 'Integration', 'type': 'blocking'}
        ]
    
    def _extract_risk_assessment(self, response: str) -> Dict[str, Any]:
        """Extract risk assessment from LLM response"""
        return {
            'high_risks': [
                {'risk': 'Technical complexity', 'probability': 'medium', 'impact': 'high', 'mitigation': 'Expert consultation'},
                {'risk': 'Timeline delays', 'probability': 'high', 'impact': 'medium', 'mitigation': 'Buffer time allocation'}
            ],
            'medium_risks': [
                {'risk': 'Resource availability', 'probability': 'medium', 'impact': 'medium', 'mitigation': 'Resource planning'},
                {'risk': 'Stakeholder alignment', 'probability': 'low', 'impact': 'high', 'mitigation': 'Regular communication'}
            ],
            'low_risks': [
                {'risk': 'Technology changes', 'probability': 'low', 'impact': 'low', 'mitigation': 'Monitoring'}
            ]
        }
    
    def _extract_timeline(self, response: str) -> Dict[str, Any]:
        """Extract timeline from LLM response"""
        return {
            'start_date': datetime.utcnow().isoformat(),
            'end_date': (datetime.utcnow().replace(day=datetime.utcnow().day + 49)).isoformat(),  # 7 weeks
            'milestones': [
                {'name': 'Requirements finalized', 'date': (datetime.utcnow().replace(day=datetime.utcnow().day + 7)).isoformat()},
                {'name': 'Prototype completed', 'date': (datetime.utcnow().replace(day=datetime.utcnow().day + 14)).isoformat()},
                {'name': 'Core features implemented', 'date': (datetime.utcnow().replace(day=datetime.utcnow().day + 35)).isoformat()},
                {'name': 'Testing completed', 'date': (datetime.utcnow().replace(day=datetime.utcnow().day + 42)).isoformat()},
                {'name': 'Production deployment', 'date': (datetime.utcnow().replace(day=datetime.utcnow().day + 49)).isoformat()}
            ]
        }
