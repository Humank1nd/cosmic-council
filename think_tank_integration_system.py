"""
Legacy think tank integration compatibility shim for tests.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class ThinkTankIntegrationResult:
    overall_confidence: float = 0.75
    think_tank_results: Dict[str, Any] = field(default_factory=dict)
    integration_synthesis: Dict[str, Any] = field(default_factory=dict)


class CosmicCouncilThinkTankIntegration:
    async def conduct_integrated_inquiry(self, *_args, **_kwargs) -> ThinkTankIntegrationResult:
        return ThinkTankIntegrationResult(
            overall_confidence=0.75,
            think_tank_results={"red_owl": {"status": "completed", "confidence": 0.75}},
            integration_synthesis={"summary": "default integration synthesis", "key_insights": []},
        )
