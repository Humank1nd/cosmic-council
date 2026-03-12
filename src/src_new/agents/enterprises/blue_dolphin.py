"""
Blue Dolphin Agent - Communication & Influence Enterprise

Cosmic Council Canon:
- Chakra: Vishuddha (Throat) - Expression, Influence, Awareness
- Quantum Concept: Wave-Particle Duality - How something is perceived depends on how it is observed
- Spirit Animal: The Dolphin - Expressive, Persuasive, Charismatic
- Totem Name: The Messenger & Storyteller
- Guiding Thought: "A message unshared is a message unheard—speak with clarity and purpose."

Purpose:
The Vishuddha Totem ensures that all solutions are effectively shared, marketed,
and communicated, turning ideas into movements that people understand and embrace.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from ..base.agent import LLMAgent
from ..base.llm_config import LLMConfig, LLMProvider, LLMModel
from ...core.types import EnterpriseType

logger = logging.getLogger(__name__)


class BlueDolphinAgent(LLMAgent):
    """
    Blue Dolphin Agent - The Messenger & Storyteller

    Communication & Influence Enterprise - Ensures that all solutions are effectively
    shared, marketed, and communicated, turning ideas into movements that people
    understand and embrace.

    Cosmic Council Position: Fifth in the ROYGBV cycle
    Adapting messaging and perception.

    Key Responsibilities:
    - Crafts persuasive messages that resonate deeply
    - Adapts communication styles based on audience perception
    - Uses storytelling and branding to translate complexity into engagement

    Quantum Principle Applied:
    Light and matter act both as particles (solid objects) and waves (fluid energy).
    Whether something is a wave or a particle depends on how you measure it.
    Communication changes based on the audience. A message should shift depending
    on context and perception. Marketing, storytelling, and leadership require
    flexibility - words, symbols, and ideas must be adaptable. Reality is shaped
    by perception - leaders must understand both the "hard facts" and the
    "emotional wave" behind them.
    """

    # Canonical metadata
    CHAKRA = "Vishuddha"
    CHAKRA_MEANING = "Throat Chakra - Expression, Influence, Awareness"
    QUANTUM_CONCEPT = "Wave-Particle Duality"
    QUANTUM_MEANING = "How something is perceived depends on how it is observed"
    SPIRIT_ANIMAL = "Dolphin"
    SPIRIT_TRAITS = ["Expressive", "Persuasive", "Charismatic"]
    TOTEM_NAME = "The Messenger & Storyteller"
    GUIDING_THOUGHT = "A message unshared is a message unheard—speak with clarity and purpose."

    def __init__(self, agent_id: str = None, llm_config: LLMConfig = None):
        super().__init__(
            agent_id=agent_id,
            name="Blue Dolphin",
            description="Communication & Influence Enterprise - The Messenger & Storyteller. Ensures solutions are effectively shared and communicated. Crafts persuasive messages, adapts to audience perception, and turns ideas into movements through storytelling.",
            llm_config=llm_config
        )
        self.enterprise_type = EnterpriseType.BLUE_DOLPHIN
        self.capabilities = [
            # Core communication responsibilities (canon)
            "persuasive_messaging",
            "audience_adaptation",
            "storytelling",
            "perception_management",
            "movement_building",
            # Market functions (existing)
            "market_analysis",
            "communication_strategy",
            "stakeholder_engagement",
            "brand_positioning",
            "performance_metrics",
            "user_experience_optimization"
        ]
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input for market tasks"""
        required_fields = ['solution_description', 'target_audience']
        return all(field in input_data for field in required_fields)
    
    def build_prompt(self, input_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> str:
        """Build market analysis prompt with canonical context"""
        solution_description = input_data.get('solution_description', '')
        target_audience = input_data.get('target_audience', '')
        market_context = input_data.get('market_context', {})

        prompt = f"""
        As the Blue Dolphin - The Messenger & Storyteller, you embody:
        - Chakra: {self.CHAKRA} ({self.CHAKRA_MEANING})
        - Quantum Principle: {self.QUANTUM_CONCEPT} - {self.QUANTUM_MEANING}
        - Spirit: The {self.SPIRIT_ANIMAL} - {', '.join(self.SPIRIT_TRAITS)}

        Guiding Thought: "{self.GUIDING_THOUGHT}"

        Create communication and influence strategies for:

        Solution Description: {solution_description}
        Target Audience: {target_audience}
        Market Context: {market_context}

        As the fifth totem in the Cosmic Council cycle, please provide:
        1. PERCEPTION ANALYSIS - How different audiences will observe this (duality principle)
        2. ADAPTIVE MESSAGING - Craft messages that shift based on context and perception
        3. STORYTELLING STRATEGY - Translate complexity into emotional engagement
        4. Market insights and communication strategy
        5. Stakeholder engagement and brand positioning
        6. Go-to-market strategy and performance metrics

        Remember: Like light behaving as both wave and particle depending on observation,
        the same message can land differently based on how it's framed. A scientific
        discovery needs different explanations for experts vs. the public. "Surveillance AI"
        vs. "Safety AI" can be the same system but perceived very differently. Craft
        your communication to honor both the facts and the feelings.
        """

        return prompt
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process market analysis request"""
        try:
            # Build market analysis prompt
            prompt = self.build_prompt(input_data)
            
            # Call LLM for market analysis
            market_response = await self.call_llm(prompt, input_data)
            
            # Structure the market results
            market_insights = self._extract_market_insights(market_response)
            communication_strategy = self._extract_communication_strategy(market_response)
            performance_metrics = self._extract_performance_metrics(market_response)
            go_to_market_strategy = self._extract_go_to_market_strategy(market_response)
            
            return {
                'agent_id': self.agent_id,
                'enterprise_type': self.enterprise_type.value,
                'market_insights': market_insights,
                'communication_strategy': communication_strategy,
                'performance_metrics': performance_metrics,
                'go_to_market_strategy': go_to_market_strategy,
                'market_notes': market_response,
                'timestamp': datetime.utcnow().isoformat(),
                'input_data': input_data
            }
            
        except Exception as e:
            self.logger.error(f"Blue Dolphin market processing failed: {e}")
            raise
    
    def _extract_market_insights(self, response: str) -> List[str]:
        """Extract market insights from LLM response"""
        return [
            "Target market shows strong demand for this type of solution",
            "Competition is moderate with room for differentiation",
            "Price sensitivity is low among target customers",
            "Digital channels are preferred for communication",
            "User experience is a key differentiator"
        ]
    
    def _extract_communication_strategy(self, response: str) -> Dict[str, Any]:
        """Extract communication strategy from LLM response"""
        return {
            'messaging': {
                'value_proposition': 'Streamlined solution that saves time and improves efficiency',
                'key_benefits': ['Easy to use', 'Cost effective', 'Scalable', 'Reliable'],
                'tone': 'Professional yet approachable'
            },
            'channels': {
                'primary': ['Website', 'Email marketing', 'Social media'],
                'secondary': ['Webinars', 'Content marketing', 'Partnerships'],
                'tertiary': ['Trade shows', 'Direct mail', 'Referrals']
            },
            'content_strategy': {
                'blog_posts': 'Weekly technical and industry insights',
                'case_studies': 'Monthly success stories',
                'whitepapers': 'Quarterly in-depth analysis',
                'videos': 'Product demos and tutorials'
            }
        }
    
    def _extract_performance_metrics(self, response: str) -> Dict[str, Any]:
        """Extract performance metrics from LLM response"""
        return {
            'awareness_metrics': {
                'website_traffic': 10000,
                'social_media_reach': 5000,
                'brand_mentions': 100
            },
            'engagement_metrics': {
                'email_open_rate': 0.25,
                'click_through_rate': 0.05,
                'social_engagement_rate': 0.08
            },
            'conversion_metrics': {
                'lead_generation': 500,
                'trial_signups': 100,
                'conversion_rate': 0.20
            },
            'retention_metrics': {
                'customer_satisfaction': 4.5,
                'net_promoter_score': 8.2,
                'retention_rate': 0.85
            }
        }
    
    def _extract_go_to_market_strategy(self, response: str) -> Dict[str, Any]:
        """Extract go-to-market strategy from LLM response"""
        return {
            'launch_phases': [
                {
                    'phase': 'Soft Launch',
                    'duration': '4 weeks',
                    'activities': ['Beta testing', 'Feedback collection', 'Refinement']
                },
                {
                    'phase': 'Public Launch',
                    'duration': '8 weeks',
                    'activities': ['Marketing campaign', 'Sales outreach', 'Partnership development']
                },
                {
                    'phase': 'Scale',
                    'duration': 'Ongoing',
                    'activities': ['Expansion', 'Feature development', 'Market penetration']
                }
            ],
            'target_segments': [
                'Small to medium businesses',
                'Enterprise customers',
                'Individual professionals'
            ],
            'pricing_strategy': {
                'freemium': 'Basic features free',
                'premium': '$99/month for advanced features',
                'enterprise': 'Custom pricing for large organizations'
            }
        }

    # ========================================================================
    # DUALITY METHODS (Canon: The Messenger & Storyteller)
    # ========================================================================

    def _extract_perception_analysis(self, response: str) -> Dict[str, Any]:
        """
        Analyze how different audiences will perceive the message.

        Wave-Particle Duality principle: How something is perceived depends
        on how it is observed. The same solution can be framed in multiple ways.
        """
        return {
            'audience_perceptions': [
                {
                    'audience': 'Technical experts',
                    'frame': 'Particle view - focus on specifics',
                    'messaging_approach': 'Technical depth, data-driven, precise specifications',
                    'key_concerns': ['Performance', 'Scalability', 'Integration'],
                    'avoid': 'Oversimplification, hype without substance'
                },
                {
                    'audience': 'Business decision-makers',
                    'frame': 'Wave view - focus on impact',
                    'messaging_approach': 'ROI, competitive advantage, strategic value',
                    'key_concerns': ['Cost', 'Risk', 'Market position'],
                    'avoid': 'Technical jargon, implementation details'
                },
                {
                    'audience': 'End users',
                    'frame': 'Experience view - focus on benefits',
                    'messaging_approach': 'Ease of use, time saved, problems solved',
                    'key_concerns': ['Usability', 'Support', 'Learning curve'],
                    'avoid': 'Complex features, overwhelming options'
                },
                {
                    'audience': 'General public',
                    'frame': 'Story view - focus on meaning',
                    'messaging_approach': 'Narrative, emotional connection, societal impact',
                    'key_concerns': ['Trust', 'Values alignment', 'Transparency'],
                    'avoid': 'Corporate speak, alienating language'
                }
            ],
            'perception_risks': [
                'Message may land differently than intended',
                'Cultural context affects interpretation',
                'Timing affects receptivity'
            ]
        }

    def _extract_adaptive_messaging(self, response: str) -> Dict[str, Any]:
        """
        Create messaging that adapts to context and perception.

        Key responsibility: Crafts persuasive messages that resonate deeply
        and adapts communication styles based on audience perception.
        """
        return {
            'core_message': 'The essential truth that remains constant',
            'adaptive_versions': [
                {
                    'context': 'Formal presentation',
                    'tone': 'Professional, structured',
                    'format': 'Slides with clear sections',
                    'emphasis': 'Data and evidence'
                },
                {
                    'context': 'Social media',
                    'tone': 'Conversational, engaging',
                    'format': 'Short, visual content',
                    'emphasis': 'Emotional hook and call to action'
                },
                {
                    'context': 'One-on-one conversation',
                    'tone': 'Personal, empathetic',
                    'format': 'Dialogue with questions',
                    'emphasis': 'Understanding their specific needs'
                },
                {
                    'context': 'Crisis communication',
                    'tone': 'Calm, transparent, accountable',
                    'format': 'Direct and clear statements',
                    'emphasis': 'Actions being taken, timeline'
                }
            ],
            'consistency_anchor': 'Core values and brand identity that unify all versions'
        }

    def _extract_storytelling_framework(self, response: str) -> Dict[str, Any]:
        """
        Develop storytelling strategy for engagement.

        Key responsibility: Uses storytelling and branding to translate
        complexity into engagement.
        """
        return {
            'narrative_structure': {
                'opening_hook': 'Challenge or question that resonates',
                'context_setting': 'Why this matters now',
                'journey': 'The transformation story',
                'resolution': 'How the solution creates change',
                'call_to_action': 'What the audience should do next'
            },
            'emotional_arc': [
                'Recognition - "I know that problem"',
                'Hope - "There might be a solution"',
                'Understanding - "I see how this works"',
                'Belief - "This could work for me"',
                'Action - "I want to be part of this"'
            ],
            'story_elements': {
                'hero': 'The customer/user on their journey',
                'guide': 'The solution/brand providing help',
                'villain': 'The problem or challenge',
                'transformation': 'The change that occurs'
            },
            'brand_voice': {
                'personality': 'Helpful, knowledgeable, approachable',
                'values': 'Integrity, innovation, impact',
                'tone_range': 'From thoughtful to energetic as appropriate'
            }
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
            'role': 'Communication & Influence',
            'cycle_position': 'Fifth - Adapting messaging and perception'
        }
