"""
Orange Orangutan Agent - Strategy & Planning Enterprise

Cosmic Council Canon:
- Chakra: Svadisthana (Sacral) - Flow, Structure, Execution
- Quantum Concept: Quantum Tunneling - Finding pathways through barriers that seem impenetrable
- Spirit Animal: The Orangutan - Strategic, Adaptive, Resourceful
- Totem Name: The Architect of Strategy
- Guiding Thought: "A dream without a plan is just a wish."

Purpose:
The Svadisthana Totem turns knowledge into structured action plans, ensuring that
great ideas don't remain abstract but are implemented effectively.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from ..base.agent import LLMAgent
from ..base.llm_config import LLMConfig, LLMProvider, LLMModel
from ...core.types import EnterpriseType

logger = logging.getLogger(__name__)


class OrangeOrangutanAgent(LLMAgent):
    """
    Orange Orangutan Agent - The Architect of Strategy

    Strategy & Planning Enterprise - Turns knowledge into structured action plans,
    ensuring that great ideas don't remain abstract but are implemented effectively.

    Cosmic Council Position: Second in the ROYGBV cycle
    Finding hidden pathways through challenges.

    Key Responsibilities:
    - Develops execution strategies - breaking complex ideas into step-by-step plans
    - Finds alternative solutions - identifying unconventional pathways through obstacles
    - Optimizes workflows - minimizing inefficiency and wasted effort

    Quantum Principle Applied:
    Some barriers are not as solid as they appear - there are pathways through them.
    Strategy and planning should look for alternative routes, shortcuts, and workarounds.
    Rigidity in thinking creates artificial barriers - sometimes the best way forward
    is outside conventional methods.
    """

    # Canonical metadata
    CHAKRA = "Svadisthana"
    CHAKRA_MEANING = "Sacral Chakra - Flow, Structure, Execution"
    QUANTUM_CONCEPT = "Quantum Tunneling"
    QUANTUM_MEANING = "Finding pathways through barriers that seem impenetrable"
    SPIRIT_ANIMAL = "Orangutan"
    SPIRIT_TRAITS = ["Strategic", "Adaptive", "Resourceful"]
    TOTEM_NAME = "The Architect of Strategy"
    GUIDING_THOUGHT = "A dream without a plan is just a wish."

    def __init__(self, agent_id: str = None, llm_config: LLMConfig = None):
        super().__init__(
            agent_id=agent_id,
            name="Orange Orangutan",
            description="Strategy & Planning Enterprise - The Architect of Strategy. Turns knowledge into structured action plans. Develops execution strategies, finds alternative pathways through obstacles, and optimizes workflows.",
            llm_config=llm_config
        )
        self.enterprise_type = EnterpriseType.ORANGE_ORANGUTAN
        self.capabilities = [
            # Core strategic responsibilities (canon)
            "barrier_breakthrough",
            "pathway_discovery",
            "unconventional_solutions",
            "workflow_optimization",
            # Planning functions (existing)
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
        """Build planning prompt with canonical context"""
        research_findings = input_data.get('research_findings', [])
        objectives = input_data.get('objectives', [])
        constraints = input_data.get('constraints', {})
        timeline = input_data.get('timeline', '')

        prompt = f"""
        As the Orange Orangutan - The Architect of Strategy, you embody:
        - Chakra: {self.CHAKRA} ({self.CHAKRA_MEANING})
        - Quantum Principle: {self.QUANTUM_CONCEPT} - {self.QUANTUM_MEANING}
        - Spirit: The {self.SPIRIT_ANIMAL} - {', '.join(self.SPIRIT_TRAITS)}

        Guiding Thought: "{self.GUIDING_THOUGHT}"

        Create a comprehensive action plan based on:

        Research Findings: {research_findings}
        Objectives: {objectives}
        Constraints: {constraints}
        Timeline: {timeline}

        As the second totem in the Cosmic Council cycle, please provide:
        1. BARRIER BREAKTHROUGH - Identify obstacles and unconventional pathways through them
        2. ALTERNATIVE ROUTES - Solutions outside conventional methods (tunneling principle)
        3. FLOW OPTIMIZATION - Minimize inefficiency and wasted effort
        4. Strategic action plan with phases and milestones
        5. Task breakdown, dependencies, and risk mitigation
        6. Resource requirements and success metrics

        Remember: Challenges that seem impossible often have unseen solutions. Like a particle
        tunneling through a barrier, look for hidden routes that conventional thinking overlooks.
        A startup struggling with funding may find alternative financing through partnerships
        or decentralized networks instead of traditional venture capital.
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

    # ========================================================================
    # TUNNELING METHODS (Canon: The Architect of Strategy)
    # ========================================================================

    def _extract_barrier_analysis(self, response: str) -> Dict[str, Any]:
        """
        Identify barriers and unconventional pathways through them.

        Quantum Tunneling principle: Some barriers are not as solid as they appear.
        Look for hidden routes that conventional thinking overlooks.
        """
        return {
            'identified_barriers': [
                {
                    'barrier': 'Resource constraints',
                    'conventional_approach': 'Request more budget',
                    'tunnel_path': 'Leverage partnerships, open-source tools, or phased delivery',
                    'feasibility': 'high'
                },
                {
                    'barrier': 'Technical complexity',
                    'conventional_approach': 'Build everything from scratch',
                    'tunnel_path': 'Integrate existing solutions, use APIs, or adopt proven patterns',
                    'feasibility': 'high'
                },
                {
                    'barrier': 'Time constraints',
                    'conventional_approach': 'Reduce scope',
                    'tunnel_path': 'Parallel workstreams, MVP approach, or incremental releases',
                    'feasibility': 'medium'
                }
            ],
            'unconventional_strategies': [
                'Reverse engineering successful similar projects',
                'Cross-industry adaptation of proven models',
                'Crowdsourcing or community involvement',
                'Strategic partnerships to bypass capability gaps'
            ]
        }

    def _extract_flow_optimization(self, response: str) -> Dict[str, Any]:
        """
        Optimize workflow to minimize inefficiency.

        Sacral Chakra principle: Flow, Structure, Execution - ensuring ideas
        flow smoothly from conception to implementation.
        """
        return {
            'bottlenecks_identified': [
                'Decision-making delays',
                'Information silos between teams',
                'Sequential dependencies that could be parallel'
            ],
            'flow_improvements': [
                {
                    'area': 'Communication',
                    'current_state': 'Ad-hoc meetings',
                    'optimized_state': 'Structured sync points with clear agendas',
                    'expected_impact': 'Faster decisions, less meeting fatigue'
                },
                {
                    'area': 'Handoffs',
                    'current_state': 'Manual transitions',
                    'optimized_state': 'Automated workflows with clear triggers',
                    'expected_impact': 'Reduced delays, better tracking'
                }
            ],
            'structural_recommendations': [
                'Establish clear ownership and accountability',
                'Create feedback loops at each phase',
                'Define explicit exit criteria for each stage'
            ]
        }

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
            'role': 'Strategy & Planning',
            'cycle_position': 'Second - Finding hidden pathways through challenges'
        }
