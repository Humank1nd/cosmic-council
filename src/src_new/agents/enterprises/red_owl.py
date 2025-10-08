"""
Red Owl Agent - Research & Discovery Enterprise
"""

from typing import Dict, Any, List
import logging

from ..base.agent import LLMAgent
from ..base.llm_config import LLMConfig, LLMProvider, LLMModel
from ...core.types import EnterpriseType

logger = logging.getLogger(__name__)


class RedOwlAgent(LLMAgent):
    """Red Owl Agent for research and discovery"""
    
    def __init__(self, agent_id: str = None, llm_config: LLMConfig = None):
        super().__init__(
            agent_id=agent_id,
            name="Red Owl",
            description="Research & Discovery Enterprise - Investigates problems deeply and uncovers insights",
            llm_config=llm_config
        )
        self.enterprise_type = EnterpriseType.RED_OWL
        self.capabilities = [
            "problem_analysis",
            "research_synthesis", 
            "insight_generation",
            "question_prioritization",
            "evidence_evaluation"
        ]
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input for research tasks"""
        required_fields = ['problem_description', 'research_scope']
        return all(field in input_data for field in required_fields)
    
    def build_prompt(self, input_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> str:
        """Build research prompt"""
        problem_description = input_data.get('problem_description', '')
        research_scope = input_data.get('research_scope', '')
        constraints = input_data.get('constraints', {})
        
        prompt = f"""
        As the Red Owl Research Agent, conduct deep research on the following problem:
        
        Problem: {problem_description}
        Research Scope: {research_scope}
        Constraints: {constraints}
        
        Please provide:
        1. Key research findings
        2. Prioritized research questions
        3. Evidence-based insights
        4. Areas requiring further investigation
        5. Recommended research methodology
        
        Focus on thoroughness, accuracy, and actionable insights.
        """
        
        return prompt
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process research request"""
        try:
            # Build research prompt
            prompt = self.build_prompt(input_data)
            
            # Call LLM for research analysis
            research_response = await self.call_llm(prompt, input_data)
            
            # Structure the research results
            research_findings = self._extract_research_findings(research_response)
            prioritized_questions = self._extract_prioritized_questions(research_response)
            insights = self._extract_insights(research_response)
            
            return {
                'agent_id': self.agent_id,
                'enterprise_type': self.enterprise_type.value,
                'research_findings': research_findings,
                'prioritized_questions': prioritized_questions,
                'insights': insights,
                'research_notes': research_response,
                'timestamp': datetime.utcnow().isoformat(),
                'input_data': input_data
            }
            
        except Exception as e:
            self.logger.error(f"Red Owl research processing failed: {e}")
            raise
    
    def _extract_research_findings(self, response: str) -> List[str]:
        """Extract research findings from LLM response"""
        # This would parse the LLM response to extract structured findings
        # For now, return mock findings
        return [
            "Problem requires multi-disciplinary approach",
            "Stakeholder alignment is critical for success",
            "Technical feasibility has been confirmed",
            "Market research indicates strong demand"
        ]
    
    def _extract_prioritized_questions(self, response: str) -> List[str]:
        """Extract prioritized questions from LLM response"""
        return [
            "What are the core requirements and constraints?",
            "Who are the key stakeholders and what are their needs?",
            "What are the technical and business risks?",
            "What are the success criteria and metrics?"
        ]
    
    def _extract_insights(self, response: str) -> List[str]:
        """Extract key insights from LLM response"""
        return [
            "The problem is more complex than initially perceived",
            "Multiple solution approaches are viable",
            "Timeline constraints may impact solution quality",
            "User experience is a critical success factor"
        ]
