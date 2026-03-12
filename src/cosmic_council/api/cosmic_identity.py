"""
Agent Orchestrator Visual Identity
Defines colors, animals, shapes, and visual properties for the hexagonal structure
"""

from typing import Dict, Any, List
from enum import Enum
from dataclasses import dataclass

from ..core.core import EnterpriseType


@dataclass
class EnterpriseVisualIdentity:
    """Visual identity for each enterprise"""
    enterprise: EnterpriseType
    name: str
    semantic_name: str  # New semantic naming for AI sorting
    animal: str
    animal_emoji: str
    gemstone: str      # New metadata from Notion
    quantum_principle: str # New metadata from Notion
    chakra: str        # New metadata from Notion
    color_name: str
    color_hex: str
    color_rgb: tuple
    core_principle: str
    role: str
    shape: str  # Position in hexagon
    position: int  # Clockwise position (0-5)
    symbol: str  # Unicode/emoji symbol


class CosmicCouncilIdentity:
    """Agent Orchestrator visual identity system"""
    
    # Complete visual identity for all enterprises
    ENTERPRISES = {
        EnterpriseType.RED_OWL: EnterpriseVisualIdentity(
            enterprise=EnterpriseType.RED_OWL,
            name="Red Owl",
            semantic_name="WHY-Research-RedOwl",
            animal="Owl",
            animal_emoji="🦉",
            gemstone="Ruby",
            quantum_principle="Entanglement",
            chakra="Muladhara",
            color_name="Red",
            color_hex="#FF0000",
            color_rgb=(255, 0, 0),
            core_principle="Curiosity",
            role="Research & Knowledge Gathering",
            shape="Top",
            position=0,
            symbol="🔴🦉"
        ),
        EnterpriseType.ORANGE_ORANGUTAN: EnterpriseVisualIdentity(
            enterprise=EnterpriseType.ORANGE_ORANGUTAN,
            name="Orange Orangutan",
            semantic_name="HOW-Planning-OrangeOrangutan",
            animal="Orangutan",
            animal_emoji="🦧",
            gemstone="Topaz",
            quantum_principle="Tunneling",
            chakra="Svadisthana",
            color_name="Orange",
            color_hex="#FFA500",
            color_rgb=(255, 165, 0),
            core_principle="Planning",
            role="Logistics & Strategic Planning",
            shape="Top-Right",
            position=1,
            symbol="🟠🦧"
        ),
        EnterpriseType.YELLOW_HONEYBEE: EnterpriseVisualIdentity(
            enterprise=EnterpriseType.YELLOW_HONEYBEE,
            name="Yellow Honeybee",
            semantic_name="WHAT-Development-YellowHoneybee",
            animal="Honeybee",
            animal_emoji="🐝",
            gemstone="Citrine",
            quantum_principle="Superposition",
            chakra="Manipura",
            color_name="Yellow",
            color_hex="#FFFF00",
            color_rgb=(255, 255, 0),
            core_principle="Creativity",
            role="Development & Innovation",
            shape="Bottom-Right",
            position=2,
            symbol="🟡🐝"
        ),
        EnterpriseType.GREEN_TORTOISE: EnterpriseVisualIdentity(
            enterprise=EnterpriseType.GREEN_TORTOISE,
            name="Green Tortoise",
            semantic_name="WHEN-Resources-GreenTortoise",
            animal="Tortoise",
            animal_emoji="🐢",
            gemstone="Emerald",
            quantum_principle="Teleportation",
            chakra="Anahata",
            color_name="Green",
            color_hex="#008000",
            color_rgb=(0, 128, 0),
            core_principle="Sustainability",
            role="Budget & Resource Management",
            shape="Bottom",
            position=3,
            symbol="🟢🐢"
        ),
        EnterpriseType.BLUE_DOLPHIN: EnterpriseVisualIdentity(
            enterprise=EnterpriseType.BLUE_DOLPHIN,
            name="Blue Dolphin",
            semantic_name="WHERE-Marketing-BlueDolphin",
            animal="Dolphin",
            animal_emoji="🐬",
            gemstone="Sapphire",
            quantum_principle="Wave-Particle Duality",
            chakra="Vishuddha",
            color_name="Blue",
            color_hex="#0000FF",
            color_rgb=(0, 0, 255),
            core_principle="Clarity",
            role="Communication & Marketing",
            shape="Bottom-Left",
            position=4,
            symbol="🔵🐬"
        ),
        EnterpriseType.PURPLE_ELEPHANT: EnterpriseVisualIdentity(
            enterprise=EnterpriseType.PURPLE_ELEPHANT,
            name="Purple Elephant",
            semantic_name="WHO-Empathy-PurpleElephant",
            animal="Elephant",
            animal_emoji="🐘",
            gemstone="Amethyst",
            quantum_principle="Quantum Field Theory",
            chakra="Ajna",
            color_name="Purple",
            color_hex="#4B0082",
            color_rgb=(75, 0, 130),
            core_principle="Empathy",
            role="Support & Continuous Improvement",
            shape="Top-Left",
            position=5,
            symbol="🟣🐘"
        )
    }
    
    @classmethod
    def get_enterprise_identity(cls, enterprise: EnterpriseType) -> EnterpriseVisualIdentity:
        """Get visual identity for an enterprise"""
        return cls.ENTERPRISES.get(enterprise)
    
    @classmethod
    def get_all_identities(cls) -> Dict[EnterpriseType, EnterpriseVisualIdentity]:
        """Get all enterprise identities"""
        return cls.ENTERPRISES
    
    @classmethod
    def get_hexagon_structure(cls) -> Dict[str, Any]:
        """Get the hexagonal structure representation"""
        return {
            "shape": "Hexagon",
            "sides": 6,
            "structure": "ROYGBV (Red, Orange, Yellow, Green, Blue, Purple/Violet)",
            "processing_order": "Clockwise",
            "visualization": {
                "center": "Problem/Goal",
                "sectors": [
                    {
                        "position": 0,
                        "enterprise": "red_owl",
                        "location": "Top",
                        "angle": 0
                    },
                    {
                        "position": 1,
                        "enterprise": "orange_orangutan",
                        "location": "Top-Right",
                        "angle": 60
                    },
                    {
                        "position": 2,
                        "enterprise": "yellow_honeybee",
                        "location": "Bottom-Right",
                        "angle": 120
                    },
                    {
                        "position": 3,
                        "enterprise": "green_tortoise",
                        "location": "Bottom",
                        "angle": 180
                    },
                    {
                        "position": 4,
                        "enterprise": "blue_dolphin",
                        "location": "Bottom-Left",
                        "angle": 240
                    },
                    {
                        "position": 5,
                        "enterprise": "purple_elephant",
                        "location": "Top-Left",
                        "angle": 300
                    }
                ]
            },
            "symbolism": {
                "hexagon": "Balance, harmony, and interconnectedness",
                "six_sides": "Six perspectives on every problem",
                "clockwise_flow": "Progressive problem-solving cycle",
                "center": "The problem or goal being addressed"
            }
        }
    
    @classmethod
    def get_color_palette(cls) -> Dict[str, Any]:
        """Get the complete color palette"""
        return {
            "primary_colors": {
                "red": {"hex": "#FF0000", "rgb": [255, 0, 0], "enterprise": "Red Owl"},
                "orange": {"hex": "#FFA500", "rgb": [255, 165, 0], "enterprise": "Orange Orangutan"},
                "yellow": {"hex": "#FFFF00", "rgb": [255, 255, 0], "enterprise": "Yellow Honeybee"},
                "green": {"hex": "#008000", "rgb": [0, 128, 0], "enterprise": "Green Tortoise"},
                "blue": {"hex": "#0000FF", "rgb": [0, 0, 255], "enterprise": "Blue Dolphin"},
                "purple": {"hex": "#4B0082", "rgb": [75, 0, 130], "enterprise": "Purple Elephant"}
            },
            "accent_colors": {
                "center": {"hex": "#FFFFFF", "rgb": [255, 255, 255], "description": "Problem/Goal center"},
                "connections": {"hex": "#808080", "rgb": [128, 128, 128], "description": "Inter-enterprise connections"}
            },
            "gradient": "ROYGBV spectrum representing the full problem-solving spectrum"
        }
    
    @classmethod
    def get_animal_symbols(cls) -> Dict[str, Any]:
        """Get all animal symbols"""
        return {
            enterprise.value: {
                "animal": identity.animal,
                "emoji": identity.animal_emoji,
                "symbol": identity.symbol,
                "meaning": f"{identity.animal} represents {identity.core_principle.lower()}"
            }
            for enterprise, identity in cls.ENTERPRISES.items()
        }
    
    @classmethod
    def get_complete_identity(cls) -> Dict[str, Any]:
        """Get complete visual identity system"""
        return {
            "cosmic_council": {
                "name": "Cosmic Council",
                "structure": "Hexagonal",
                "mission": "To integrate wisdom, innovation, and interconnected systems thinking in order to create sustainable, ethical, and holistic solutions for humanity’s greatest challenges.",
                "philosophy": "Six perspectives, one solution",
                "motto": "Through many eyes, we see the whole",
                "ultimate_goals": [
                    "Sustainable, ethical technological progress",
                    "Holistic decision-making that balances logic, creativity, and wisdom",
                    "A new paradigm of leadership, innovation, and social evolution"
                ],
                "ultimate_purpose": [
                    "Solve global challenges with a multidimensional approach.",
                    "Bridge science, philosophy, AI, and creativity into a single framework.",
                    "Ensure ethical, sustainable, and emotionally intelligent decision-making.",
                    "Enable humanity to evolve beyond outdated paradigms and into a new era of interconnected wisdom."
                ],
                "purpose_qualities": {
                    "holistic": "Integrates multiple disciplines (science, philosophy, AI, spirituality, business).",
                    "cyclical": "Continuously refines itself through reflection and iteration.",
                    "sustainable": "Focuses on long-term impact, avoiding short-term thinking.",
                    "ethical": "Ensures that all innovation and decision-making benefit the greater good."
                },
                "vision": "To guide humanity toward a future where wisdom, technology, creativity, and ethical consciousness are fully integrated—ensuring sustainable innovation, interconnected thinking, and collective evolution.",
                "ultimate_vision_integrations": {
                    "logic_intuition": "AI and humanity thinking in harmony, not opposition.",
                    "efficiency_ethics": "Sustainable progress that benefits all, not just the privileged.",
                    "innovation_wisdom": "Rapid technological advances balanced with deep moral reflection.",
                    "growth": "Personal transformation that uplifts global consciousness."
                },
                "future_envisioned": [
                    "A society where knowledge is decentralized, wisdom is shared, and technology serves the highest good.",
                    "A civilization where every decision is made with an awareness of its long-term, global impact.",
                    "A world where creativity, logic, ethics, and innovation evolve together—never in isolation."
                ],
                "manifesto": "The Cosmic Council is more than a framework—it is a movement toward a higher intelligence, where knowledge is integrated, solutions are sustainable, and wisdom is shared for the benefit of all.",
                "final_thought": "The true purpose of intelligence is not just to solve problems—it is to understand, refine, and elevate the human experience. The Cosmic Council is the bridge between knowledge and wisdom, between vision and reality, between technology and ethics."
            },
            "hexagon": cls.get_hexagon_structure(),
            "enterprises": {
                enterprise.value: {
                    "name": identity.name,
                    "semantic_name": identity.semantic_name,
                    "animal": identity.animal,
                    "animal_emoji": identity.animal_emoji,
                    "gemstone": identity.gemstone,
                    "quantum_principle": identity.quantum_principle,
                    "chakra": identity.chakra,
                    "symbol": identity.symbol,
                    "color": {
                        "name": identity.color_name,
                        "hex": identity.color_hex,
                        "rgb": list(identity.color_rgb)
                    },
                    "core_principle": identity.core_principle,
                    "role": identity.role,
                    "position": {
                        "number": identity.position,
                        "location": identity.shape,
                        "angle": identity.position * 60
                    }
                }
                for enterprise, identity in cls.ENTERPRISES.items()
            },
            "color_palette": cls.get_color_palette(),
            "animal_symbols": cls.get_animal_symbols(),
            "processing_flow": {
                "order": "ROYGBV",
                "sequence": [
                    {"step": 1, "enterprise": "red_owl", "symbol": "🔴🦉"},
                    {"step": 2, "enterprise": "orange_orangutan", "symbol": "🟠🦧"},
                    {"step": 3, "enterprise": "yellow_honeybee", "symbol": "🟡🐝"},
                    {"step": 4, "enterprise": "green_tortoise", "symbol": "🟢🐢"},
                    {"step": 5, "enterprise": "blue_dolphin", "symbol": "🔵🐬"},
                    {"step": 6, "enterprise": "purple_elephant", "symbol": "🟣🐘"}
                ],
                "description": "Clockwise processing through all six enterprises"
            }
        }