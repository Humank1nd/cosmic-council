"""
Domain Alignment Layer
Defines industry-specific missions, objectives, and constraints for the Cosmic Council
"""

from typing import Dict, Any, List
from dataclasses import dataclass, field
from .types import ProblemDomain

@dataclass
class DomainContext:
    """Strategic context for a specific problem domain"""
    domain: ProblemDomain
    mission_focus: str
    objectives: List[str]
    auto_constraints: List[str] = field(default_factory=list)
    cross_system_triggers: List[str] = field(default_factory=list)

class DomainRegistry:
    """Registry of domain-specific strategic alignments"""
    
    DOMAINS = {
        ProblemDomain.SCIENCE_AI: DomainContext(
            domain=ProblemDomain.SCIENCE_AI,
            mission_focus="Ensure ethical AI and prevent algorithmic biases through quantum-inspired decision making.",
            objectives=[
                "Prevent algorithmic bias",
                "Implement quantum-inspired AI logic",
                "Fuse physics, neuroscience, and metaphysics"
            ],
            auto_constraints=[
                "Must comply with E8 Ethical AI Guidelines",
                "Requires multi-model cross-validation"
            ],
            cross_system_triggers=["service-physics-engine-e8"]
        ),
        
        ProblemDomain.GOVERNANCE: DomainContext(
            domain=ProblemDomain.GOVERNANCE,
            mission_focus="Implement systems-thinking models for fair policy-making and global sustainability.",
            objectives=[
                "Fair policy-making",
                "Global sustainability frameworks",
                "Urban and international collaboration"
            ],
            auto_constraints=[
                "Must align with UN Sustainability Goals",
                "Requires transparent audit logging"
            ],
            cross_system_triggers=["core-security-auth"]
        ),
        
        ProblemDomain.BUSINESS: DomainContext(
            domain=ProblemDomain.BUSINESS,
            mission_focus="Develop scalable and sustainable business models through holistic intelligence.",
            objectives=[
                "Scalable business models",
                "Holistic leadership decision-making",
                "Ethical impact marketing"
            ],
            auto_constraints=[
                "Maximize long-term stakeholder value over short-term profit",
                "Financial sustainability audit required"
            ],
            cross_system_triggers=["service-finance-ledger"]
        ),
        
        ProblemDomain.CREATIVITY: DomainContext(
            domain=ProblemDomain.CREATIVITY,
            mission_focus="Encourage the fusion of art, technology, and consciousness to uplift human potential.",
            objectives=[
                "Fusion of art and consciousness",
                "Cultural transformation storytelling",
                "Media that expands human potential"
            ],
            auto_constraints=[
                "Must be accessible and inclusive",
                "Prioritize spiritual/uplifting impact"
            ],
            cross_system_triggers=["service-creative-reasoning"]
        ),
        
        ProblemDomain.PERSONAL_GROWTH: DomainContext(
            domain=ProblemDomain.PERSONAL_GROWTH,
            mission_focus="Teach self-awareness and emotional resilience through integrated thinking.",
            objectives=[
                "Self-awareness and wisdom",
                "Emotional resilience",
                "Foster personal transformation"
            ],
            auto_constraints=[
                "Privacy-first data handling",
                "Empathetic tone enforcement"
            ],
            cross_system_triggers=["service-privacy-vault"]
        )
    }

    @classmethod
    def get_context(cls, domain: ProblemDomain) -> DomainContext:
        """Get the context for a specific domain"""
        return cls.DOMAINS.get(domain, DomainContext(
            domain=ProblemDomain.GENERAL,
            mission_focus="Holistic problem solving through the ROYGBV cycle.",
            objectives=["Balanced perspective integration"],
            auto_constraints=[]
        ))
