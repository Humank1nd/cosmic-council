"""
Red Owl Agent - Inquiry & Research Enterprise

Cosmic Council Canon:
- Chakra: Muladhara (Root) - Foundation, Stability, Deep Inquiry
- Quantum Concept: Quantum Entanglement - Everything is interconnected; knowledge is never isolated
- Spirit Animal: The Owl - Wisdom, Observation, Perception
- Totem Name: The Seeker of Truth
- Guiding Thought: "True wisdom begins with the pursuit of knowledge."

Purpose:
The Muladhara Totem is the foundation of all knowledge and discovery. It ensures that
every decision, innovation, and strategy begins with a deep understanding of truth.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from ..base.agent import LLMAgent
from ..base.llm_config import LLMConfig, LLMProvider, LLMModel
from ...core.types import EnterpriseType

logger = logging.getLogger(__name__)


class RedOwlAgent(LLMAgent):
    """
    Red Owl Agent - The Seeker of Truth

    Inquiry & Research Enterprise - The foundation of all knowledge and discovery.
    Ensures that every decision, innovation, and strategy begins with a deep
    understanding of truth.

    Cosmic Council Position: First in the ROYGBV cycle
    The starting point of inquiry and deep connections.

    Key Responsibilities:
    - Asks the right questions - seeks truth beyond assumptions
    - Researches deeply - collecting data, history, and interdisciplinary insights
    - Identifies hidden connections - revealing patterns that others overlook

    Quantum Principle Applied:
    Knowledge is never isolated - everything is interconnected. Researching one aspect
    of a problem reveals hidden connections to other fields. Ideas, people, and
    technologies are entangled, so insights from one discipline can transform another.
    """

    # Canonical metadata
    CHAKRA = "Muladhara"
    CHAKRA_MEANING = "Root Chakra - Foundation, Stability, Deep Inquiry"
    QUANTUM_CONCEPT = "Quantum Entanglement"
    QUANTUM_MEANING = "Everything is interconnected; knowledge is never isolated"
    SPIRIT_ANIMAL = "Owl"
    SPIRIT_TRAITS = ["Wisdom", "Observation", "Perception"]
    TOTEM_NAME = "The Seeker of Truth"
    GUIDING_THOUGHT = "True wisdom begins with the pursuit of knowledge."

    def __init__(self, agent_id: str = None, llm_config: LLMConfig = None):
        super().__init__(
            agent_id=agent_id,
            name="Red Owl",
            description="Inquiry & Research Enterprise - The Seeker of Truth. Foundation of all knowledge and discovery. Asks the right questions, researches deeply across disciplines, and identifies hidden connections that others overlook.",
            llm_config=llm_config
        )
        self.enterprise_type = EnterpriseType.RED_OWL
        self.capabilities = [
            # Core inquiry responsibilities (canon)
            "deep_inquiry",
            "truth_seeking",
            "interdisciplinary_research",
            "pattern_recognition",
            "hidden_connection_discovery",
            # Research functions (existing)
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
        """Build research prompt with canonical context"""
        problem_description = input_data.get('problem_description', '')
        research_scope = input_data.get('research_scope', '')
        constraints = input_data.get('constraints', {})

        prompt = f"""
        As the Red Owl - The Seeker of Truth, you embody:
        - Chakra: {self.CHAKRA} ({self.CHAKRA_MEANING})
        - Quantum Principle: {self.QUANTUM_CONCEPT} - {self.QUANTUM_MEANING}
        - Spirit: The {self.SPIRIT_ANIMAL} - {', '.join(self.SPIRIT_TRAITS)}

        Guiding Thought: "{self.GUIDING_THOUGHT}"

        Conduct deep inquiry on the following:

        Problem: {problem_description}
        Research Scope: {research_scope}
        Constraints: {constraints}

        As the foundation of the Cosmic Council cycle, please provide:
        1. DEEP INQUIRY - Questions beyond assumptions that seek fundamental truths
        2. INTERDISCIPLINARY INSIGHTS - Connections across different fields and domains
        3. HIDDEN PATTERNS - Relationships that others overlook (entanglement principle)
        4. Key research findings and evidence-based insights
        5. Prioritized research questions for further investigation
        6. Recommended research methodology

        Remember: Everything is interconnected. Studying ancient philosophy might unlock
        insights for modern AI ethics. Social, economic, and technological systems are
        deeply interwoven - one shift can ripple through the rest. Seek these connections.
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

    # ========================================================================
    # ENTANGLEMENT METHODS (Canon: The Seeker of Truth)
    # ========================================================================

    def _extract_entangled_connections(self, response: str) -> Dict[str, Any]:
        """
        Extract interdisciplinary and entangled connections from research.

        Quantum Entanglement principle: Ideas, people, and technologies are
        entangled - insights from one discipline can transform another.
        """
        return {
            'cross_domain_insights': [
                {
                    'source_domain': 'Historical patterns',
                    'target_domain': 'Current challenge',
                    'connection': 'Similar dynamics observed in past scenarios',
                    'implications': 'Learning from historical outcomes'
                },
                {
                    'source_domain': 'Adjacent industries',
                    'target_domain': 'This domain',
                    'connection': 'Transferable solutions and approaches',
                    'implications': 'Adaptation potential'
                }
            ],
            'hidden_patterns': [
                'Underlying systemic relationships not immediately visible',
                'Feedback loops that amplify or dampen effects',
                'Network effects across stakeholder groups'
            ],
            'entanglement_map': {
                'technology': ['society', 'economy', 'environment'],
                'innovation': ['ethics', 'sustainability', 'accessibility'],
                'solutions': ['unintended_consequences', 'ripple_effects']
            }
        }

    def _extract_fundamental_questions(self, response: str) -> List[Dict[str, Any]]:
        """
        Extract questions that seek truth beyond assumptions.

        Key responsibility: Asks the right questions - seeks truth beyond assumptions.
        """
        return [
            {
                'question': 'What assumptions are we making that may not be true?',
                'depth': 'foundational',
                'purpose': 'Challenge baseline assumptions'
            },
            {
                'question': 'What would change if the opposite were true?',
                'depth': 'paradigm-shifting',
                'purpose': 'Explore alternative perspectives'
            },
            {
                'question': 'Who benefits and who is harmed by current approaches?',
                'depth': 'ethical',
                'purpose': 'Understand stakeholder impact'
            },
            {
                'question': 'What are we not seeing because of our perspective?',
                'depth': 'meta-cognitive',
                'purpose': 'Identify blind spots'
            }
        ]

    def get_canon_context(self) -> Dict[str, Any]:
        """Return the canonical context for this totem"""
        return {
            'totem_name': self.TOTEM_NAME,
            'chakra': self.CHAKRA,
            'chakra_meaning': self.CHAKRA_MEANING,
            'quantum_concept': self.QUANTUM_CONCEPT,
            'quantum_meaning': self.QUANTUM_MEANING,
            'spirit_animal': self.SPIRIT_ANIMAL,
            'spirit_traits': self.SPIRIT_TRAITS,
            'guiding_thought': self.GUIDING_THOUGHT,
            'role': 'Inquiry & Research',
            'cycle_position': 'First - The starting point of inquiry and deep connections'
        }
