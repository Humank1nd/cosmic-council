"""Cosmic Council data models."""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid


class Enterprise(str, Enum):
    """The six enterprises of the Cosmic Council."""
    RED_OWL = "red"           # WHY - Knowledge Gathering
    ORANGE_ORANGUTAN = "orange"  # HOW - Logistics Planning
    YELLOW_HONEYBEE = "yellow"   # WHAT - Prototype Development
    GREEN_TORTOISE = "green"     # WHEN - Resource Allocation
    BLUE_DOLPHIN = "blue"        # WHERE - Communication
    PURPLE_ELEPHANT = "purple"   # WHO - Empathy Analysis


ENTERPRISE_INFO = {
    Enterprise.RED_OWL: {
        "name": "Red Owl",
        "animal": "Owl",
        "question": "WHY",
        "role": "Knowledge Gathering & Research",
        "chakra": "Root",
        "principle": "Curiosity",
        "color": "#FF0000"
    },
    Enterprise.ORANGE_ORANGUTAN: {
        "name": "Orange Orangutan",
        "animal": "Orangutan",
        "question": "HOW",
        "role": "Logistics & Planning",
        "chakra": "Sacral",
        "principle": "Planning",
        "color": "#FF8000"
    },
    Enterprise.YELLOW_HONEYBEE: {
        "name": "Yellow Honeybee",
        "animal": "Honeybee",
        "question": "WHAT",
        "role": "Prototype & Development",
        "chakra": "Solar Plexus",
        "principle": "Creativity",
        "color": "#FFFF00"
    },
    Enterprise.GREEN_TORTOISE: {
        "name": "Green Tortoise",
        "animal": "Tortoise",
        "question": "WHEN",
        "role": "Resource Allocation & Timing",
        "chakra": "Heart",
        "principle": "Sustainability",
        "color": "#00FF00"
    },
    Enterprise.BLUE_DOLPHIN: {
        "name": "Blue Dolphin",
        "animal": "Dolphin",
        "question": "WHERE",
        "role": "Communication & Distribution",
        "chakra": "Throat",
        "principle": "Clarity",
        "color": "#0080FF"
    },
    Enterprise.PURPLE_ELEPHANT: {
        "name": "Purple Elephant",
        "animal": "Elephant",
        "question": "WHO",
        "role": "Empathy & Stakeholder Analysis",
        "chakra": "Third Eye",
        "principle": "Empathy",
        "color": "#8000FF"
    }
}


@dataclass
class Problem:
    """A problem submitted to the council."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    description: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "pending"  # pending, in_cycle, resolved


@dataclass
class EnterpriseResponse:
    """Response from a single enterprise."""
    enterprise: Enterprise
    question: str
    analysis: str
    recommendations: List[str]
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CycleResult:
    """Result of a full ROYGBV cycle."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    problem_id: str = ""
    responses: List[EnterpriseResponse] = field(default_factory=list)
    synthesis: str = ""
    action_items: List[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    status: str = "running"


@dataclass
class Solution:
    """A synthesized solution from the council."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    problem_id: str = ""
    cycle_id: str = ""
    title: str = ""
    description: str = ""
    action_items: List[str] = field(default_factory=list)
    confidence: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
