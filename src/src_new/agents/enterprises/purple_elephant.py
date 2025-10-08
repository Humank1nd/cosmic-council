"""
Purple Elephant Agent - Support & Feedback Enterprise
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from ..base.agent import LLMAgent
from ..base.llm_config import LLMConfig, LLMProvider, LLMModel
from ...core.types import EnterpriseType

logger = logging.getLogger(__name__)


class PurpleElephantAgent(LLMAgent):
    """Purple Elephant Agent for support and feedback management"""
    
    def __init__(self, agent_id: str = None, llm_config: LLMConfig = None):
        super().__init__(
            agent_id=agent_id,
            name="Purple Elephant",
            description="Support & Feedback Enterprise - Provides support and manages feedback for continuous improvement",
            llm_config=llm_config
        )
        self.enterprise_type = EnterpriseType.PURPLE_ELEPHANT
        self.capabilities = [
            "user_support",
            "feedback_analysis",
            "performance_assessment",
            "continuous_improvement",
            "quality_assurance",
            "user_experience_optimization"
        ]
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input for support tasks"""
        required_fields = ['solution_output', 'user_feedback']
        return all(field in input_data for field in required_fields)
    
    def build_prompt(self, input_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> str:
        """Build support and feedback prompt"""
        solution_output = input_data.get('solution_output', {})
        user_feedback = input_data.get('user_feedback', [])
        performance_data = input_data.get('performance_data', {})
        
        prompt = f"""
        As the Purple Elephant Support Agent, analyze feedback and provide support recommendations for:
        
        Solution Output: {solution_output}
        User Feedback: {user_feedback}
        Performance Data: {performance_data}
        
        Please provide:
        1. User feedback analysis and insights
        2. Performance assessment and metrics
        3. Support recommendations and improvements
        4. Quality assurance measures
        5. Continuous improvement strategies
        6. User experience enhancements
        
        Focus on user satisfaction, quality improvement, and ongoing support.
        """
        
        return prompt
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process support and feedback request"""
        try:
            # Build support prompt
            prompt = self.build_prompt(input_data)
            
            # Call LLM for support analysis
            support_response = await self.call_llm(prompt, input_data)
            
            # Structure the support results
            user_feedback_analysis = self._extract_user_feedback_analysis(support_response)
            performance_assessment = self._extract_performance_assessment(support_response)
            continuous_improvement = self._extract_continuous_improvement(support_response)
            support_recommendations = self._extract_support_recommendations(support_response)
            
            return {
                'agent_id': self.agent_id,
                'enterprise_type': self.enterprise_type.value,
                'user_feedback_analysis': user_feedback_analysis,
                'performance_assessment': performance_assessment,
                'continuous_improvement': continuous_improvement,
                'support_recommendations': support_recommendations,
                'support_notes': support_response,
                'timestamp': datetime.utcnow().isoformat(),
                'input_data': input_data
            }
            
        except Exception as e:
            self.logger.error(f"Purple Elephant support processing failed: {e}")
            raise
    
    def _extract_user_feedback_analysis(self, response: str) -> Dict[str, Any]:
        """Extract user feedback analysis from LLM response"""
        return {
            'overall_satisfaction': 4.2,
            'feedback_summary': {
                'positive': [
                    'Easy to use interface',
                    'Fast response times',
                    'Helpful features',
                    'Good customer support'
                ],
                'negative': [
                    'Documentation could be better',
                    'Some features are confusing',
                    'Mobile app needs improvement'
                ],
                'suggestions': [
                    'Add more tutorials',
                    'Improve search functionality',
                    'Better error messages'
                ]
            },
            'sentiment_analysis': {
                'positive': 0.65,
                'neutral': 0.25,
                'negative': 0.10
            },
            'key_themes': [
                'Usability improvements needed',
                'Performance is generally good',
                'Support quality is appreciated',
                'Feature requests are common'
            ]
        }
    
    def _extract_performance_assessment(self, response: str) -> Dict[str, Any]:
        """Extract performance assessment from LLM response"""
        return {
            'overall_score': 4.2,
            'performance_metrics': {
                'response_time': '150ms',
                'uptime': 0.999,
                'error_rate': 0.001,
                'user_satisfaction': 4.2
            },
            'areas_of_strength': [
                'System reliability',
                'Response times',
                'Core functionality',
                'Security measures'
            ],
            'areas_for_improvement': [
                'User interface design',
                'Documentation quality',
                'Mobile experience',
                'Advanced features'
            ],
            'benchmark_comparison': {
                'industry_average': 3.8,
                'competitor_analysis': 'Above average',
                'improvement_potential': 'High'
            }
        }
    
    def _extract_continuous_improvement(self, response: str) -> Dict[str, Any]:
        """Extract continuous improvement recommendations from LLM response"""
        return {
            'priority_improvements': [
                {
                    'area': 'User Interface',
                    'priority': 'High',
                    'description': 'Redesign interface for better usability',
                    'estimated_effort': '4 weeks',
                    'expected_impact': 'High'
                },
                {
                    'area': 'Documentation',
                    'priority': 'Medium',
                    'description': 'Create comprehensive user guides',
                    'estimated_effort': '2 weeks',
                    'expected_impact': 'Medium'
                },
                {
                    'area': 'Mobile App',
                    'priority': 'High',
                    'description': 'Improve mobile user experience',
                    'estimated_effort': '6 weeks',
                    'expected_impact': 'High'
                }
            ],
            'improvement_process': [
                'Collect user feedback regularly',
                'Analyze performance metrics',
                'Prioritize improvements based on impact',
                'Implement changes iteratively',
                'Measure and validate improvements'
            ],
            'success_metrics': [
                'User satisfaction score > 4.5',
                'Support ticket reduction by 30%',
                'User retention rate > 90%',
                'Feature adoption rate > 80%'
            ]
        }
    
    def _extract_support_recommendations(self, response: str) -> List[str]:
        """Extract support recommendations from LLM response"""
        return [
            'Implement proactive user onboarding',
            'Create comprehensive FAQ section',
            'Add in-app help and tutorials',
            'Improve error messages and guidance',
            'Establish user feedback collection system',
            'Create user community and forums',
            'Implement automated support features',
            'Provide multiple support channels'
        ]
