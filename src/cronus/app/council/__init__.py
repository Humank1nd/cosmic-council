"""
Cosmic Council Integration Module for CRONUS

The LOST Numbers (4, 8, 15, 16, 23, 42 = 108):
- 4: Red Owl - Research (Muladhara/Root)
- 8: Orange Orangutan - Logistics (Svadisthana/Sacral)
- 15: Yellow Honeybee - Development (Manipura/Solar Plexus)
- 16: Green Tortoise - Budget (Anahata/Heart)
- 23: Blue Dolphin - Market (Vishuddha/Throat)
- 42: Purple Elephant - Support (Ajna/Third Eye)
- 108: The Unified Whole (Sahasrara/Crown)
"""

from enum import Enum
from typing import Dict, Any

LOST_NUMBERS = {
    4: "RED_OWL",
    8: "ORANGE_ORANGUTAN",
    15: "YELLOW_HONEYBEE",
    16: "GREEN_TORTOISE",
    23: "BLUE_DOLPHIN",
    42: "PURPLE_ELEPHANT",
}

COSMIC_SUM = sum(LOST_NUMBERS.keys())  # 108

class Enterprise(str, Enum):
    RED_OWL = "red_owl"
    ORANGE_ORANGUTAN = "orange_orangutan"
    YELLOW_HONEYBEE = "yellow_honeybee"
    GREEN_TORTOISE = "green_tortoise"
    BLUE_DOLPHIN = "blue_dolphin"
    PURPLE_ELEPHANT = "purple_elephant"

class Totem(str, Enum):
    RED = "red"
    ORANGE = "orange"
    YELLOW = "yellow"
    GREEN = "green"
    BLUE = "blue"
    PURPLE = "purple"

ENTERPRISE_TO_TOTEM: Dict[Enterprise, Totem] = {
    Enterprise.RED_OWL: Totem.RED,
    Enterprise.ORANGE_ORANGUTAN: Totem.ORANGE,
    Enterprise.YELLOW_HONEYBEE: Totem.YELLOW,
    Enterprise.GREEN_TORTOISE: Totem.GREEN,
    Enterprise.BLUE_DOLPHIN: Totem.BLUE,
    Enterprise.PURPLE_ELEPHANT: Totem.PURPLE,
}

ROYGBV_ORDER = [
    Enterprise.RED_OWL,
    Enterprise.ORANGE_ORANGUTAN,
    Enterprise.YELLOW_HONEYBEE,
    Enterprise.GREEN_TORTOISE,
    Enterprise.BLUE_DOLPHIN,
    Enterprise.PURPLE_ELEPHANT,
]

ENTERPRISE_CHAKRAS: Dict[Enterprise, Dict[str, Any]] = {
    Enterprise.RED_OWL: {
        "chakra": "Muladhara", "chakra_name": "Root",
        "function": "Research & Inquiry", "location": "Library",
        "gemstone": "Ruby", "animal": "Owl", "lost_number": 4,
    },
    Enterprise.ORANGE_ORANGUTAN: {
        "chakra": "Svadisthana", "chakra_name": "Sacral",
        "function": "Planning & Logistics", "location": "Office",
        "gemstone": "Imperial Topaz", "animal": "Orangutan", "lost_number": 8,
    },
    Enterprise.YELLOW_HONEYBEE: {
        "chakra": "Manipura", "chakra_name": "Solar Plexus",
        "function": "Development & Creativity", "location": "Factory",
        "gemstone": "Citrine", "animal": "Honeybee", "lost_number": 15,
    },
    Enterprise.GREEN_TORTOISE: {
        "chakra": "Anahata", "chakra_name": "Heart",
        "function": "Budget & Resources", "location": "Bank",
        "gemstone": "Emerald", "animal": "Tortoise", "lost_number": 16,
    },
    Enterprise.BLUE_DOLPHIN: {
        "chakra": "Vishuddha", "chakra_name": "Throat",
        "function": "Market & Communication", "location": "Mercado",
        "gemstone": "Sapphire", "animal": "Dolphin", "lost_number": 23,
    },
    Enterprise.PURPLE_ELEPHANT: {
        "chakra": "Ajna", "chakra_name": "Third Eye",
        "function": "Support & Feedback", "location": "Hospice",
        "gemstone": "Amethyst", "animal": "Elephant", "lost_number": 42,
    },
}

class FractalDepth(str, Enum):
    MACRO = "macro"
    MICRO = "micro"
    NANO = "nano"
    PICO = "pico"
    FEMTO = "femto"
    ATTO = "atto"
    ZEPTO = "zepto"
    YOCTO = "yocto"
    RONTO = "ronto"
    QUECTO = "quecto"

class CouncilMode(str, Enum):
    """Council deliberation mode."""
    SIMPLIFIED = "simplified"  # 6 LLM calls (1 per enterprise)
    FULL_108 = "full_108"      # 108 LLM calls (6×6×3)
    ADAPTIVE = "adaptive"      # Auto-select based on complexity
    HEXACLOCK = "hexaclock"    # 7-stage executive validation
    OUROBOROS = "ouroboros"    # Full Ouroboros cycle with deep integration


class HexaclockStage(str, Enum):
    """The 7 stages of the Hexaclock executive cycle."""
    ORACLE = "oracle"                    # Red Owl - Market Research
    INTERPRETER = "interpreter"          # Orange Orangutan - Data Translation
    AUDITOR_PRIMARY = "auditor_primary"  # Yellow Honeybee - Full Verification
    ALCHEMIST = "alchemist"              # Green Tortoise - Prototype Generation
    AUDITOR_SECONDARY = "auditor_secondary"  # Yellow Honeybee - Light Verification
    GATEKEEPER = "gatekeeper"            # Blue Dolphin - Budget Validation
    RECALIBRATION = "recalibration"      # Purple Elephant - Loop Optimization


HEXACLOCK_STAGES = [
    {
        "stage": HexaclockStage.ORACLE,
        "enterprise": Enterprise.RED_OWL,
        "role": "Market Research",
        "question": "What do we need to know about this problem?",
    },
    {
        "stage": HexaclockStage.INTERPRETER,
        "enterprise": Enterprise.ORANGE_ORANGUTAN,
        "role": "Data Translation",
        "question": "How do we translate this research into actionable strategy?",
    },
    {
        "stage": HexaclockStage.AUDITOR_PRIMARY,
        "enterprise": Enterprise.YELLOW_HONEYBEE,
        "role": "Full Verification",
        "question": "Is this strategy sound and implementable?",
    },
    {
        "stage": HexaclockStage.ALCHEMIST,
        "enterprise": Enterprise.GREEN_TORTOISE,
        "role": "Prototype Generation",
        "question": "What resources and timeline are needed?",
    },
    {
        "stage": HexaclockStage.AUDITOR_SECONDARY,
        "enterprise": Enterprise.YELLOW_HONEYBEE,
        "role": "Light Verification",
        "question": "Does the prototype meet quality standards?",
    },
    {
        "stage": HexaclockStage.GATEKEEPER,
        "enterprise": Enterprise.BLUE_DOLPHIN,
        "role": "Budget Validation",
        "question": "Is this viable for stakeholders and market?",
    },
    {
        "stage": HexaclockStage.RECALIBRATION,
        "enterprise": Enterprise.PURPLE_ELEPHANT,
        "role": "Loop Optimization",
        "question": "What refinements would improve the next cycle?",
    },
]

def enterprise_to_totem(enterprise: Enterprise) -> str:
    return ENTERPRISE_TO_TOTEM[enterprise].value

def get_enterprise_context(enterprise: Enterprise) -> Dict[str, Any]:
    return ENTERPRISE_CHAKRAS.get(enterprise, {})
