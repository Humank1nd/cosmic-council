"""
Cosmic Council Canon - The Authoritative Source of Truth

This package contains the canonical definitions from the Cosmic Council
framework documentation. All code implementations should align with these
definitions to ensure consistency with the original vision.
"""

from .cosmic_canon import (
    # Enums
    Chakra,
    QuantumConcept,
    SpiritAnimal,
    TotemColor,
    # Data classes
    TotemCanon,
    # The canonical definitions
    COSMIC_COUNCIL_CANON,
    ROYGBV_ORDER,
    ENTERPRISE_TO_COLOR,
    # Helper functions
    get_totem_by_color,
    get_totem_by_enterprise,
    get_next_totem,
    get_quantum_principle_for_totem,
    # Documentation
    CYCLE_DESCRIPTION
)

__all__ = [
    "Chakra",
    "QuantumConcept",
    "SpiritAnimal",
    "TotemColor",
    "TotemCanon",
    "COSMIC_COUNCIL_CANON",
    "ROYGBV_ORDER",
    "ENTERPRISE_TO_COLOR",
    "get_totem_by_color",
    "get_totem_by_enterprise",
    "get_next_totem",
    "get_quantum_principle_for_totem",
    "CYCLE_DESCRIPTION"
]
