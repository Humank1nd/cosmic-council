"""
Legacy perpetual AI integration compatibility shim for tests.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from ai_llm_integration import AILLMIntegration, LLMConfig
from perpetual_thinking_engine import PerpetualCycle, CycleType, PatternType
from perpetual_database_service import PerpetualDatabaseService
from think_tank_integration_system import CosmicCouncilThinkTankIntegration


class AIEnhancementLevel(Enum):
    NONE = "none"
    ASSISTED = "assisted"
    ENHANCED = "enhanced"
    AUTONOMOUS = "autonomous"


class AIThinkingMode(Enum):
    CREATIVE = "creative"
    LOGICAL = "logical"
    CRITICAL = "critical"
    EMPATHIC = "empathic"
    STRATEGIC = "strategic"


@dataclass
class AICycleEnhancement:
    cycle_id: str
    ai_enhancement_level: AIEnhancementLevel
    ai_thinking_mode: AIThinkingMode
    ai_prompt_used: str
    ai_response_summary: str
    ai_confidence: float
    ai_reasoning: str
    ai_tokens_used: int
    ai_processing_time: float
    impact_score: float = 0.0
    learning_feedback: Optional[str] = None
    enhancement_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class PerpetualAISession:
    session_id: str
    session_name: str
    initial_input: str
    ai_enhancement_level: AIEnhancementLevel = AIEnhancementLevel.ENHANCED
    ai_learning_enabled: bool = True
    ai_adaptation_enabled: bool = True
    ai_breakthrough_detection: bool = True
    status: str = "active"
    ai_sessions_history: List[str] = field(default_factory=list)
    ai_cycle_enhancements: List[AICycleEnhancement] = field(default_factory=list)
    ai_session_insights: List[str] = field(default_factory=list)
    ai_learning_history: List[Dict[str, Any]] = field(default_factory=list)
    ai_collaborative_metrics: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class PerpetualAIThinkingEngine:
    def __init__(self, database_url: str = "sqlite:///:memory:", ai_config: Optional[LLMConfig] = None):
        self.name = "Perpetual AI Thinking Engine"
        self.database_url = database_url
        self.ai_config = ai_config or LLMConfig()
        self.ai_integration = AILLMIntegration(self.ai_config)
        self.db_service = PerpetualDatabaseService(database_url)
        self.think_tank_integration = CosmicCouncilThinkTankIntegration()
        self.ai_sessions: Dict[str, PerpetualAISession] = {}
        self.cycles: List[PerpetualCycle] = []

    async def start_ai_enhanced_perpetual_cycle(
        self,
        initial_input: str,
        ai_enhancement_level: AIEnhancementLevel = AIEnhancementLevel.ENHANCED,
        ai_learning_enabled: bool = True,
        ai_adaptation_enabled: bool = True,
        ai_breakthrough_detection: bool = True,
        max_cycles: int = 1,
    ) -> str:
        session_id = str(uuid.uuid4())
        session = PerpetualAISession(
            session_id=session_id,
            session_name=f"AI-Enhanced Session {session_id[:8]}",
            initial_input=initial_input,
            ai_enhancement_level=ai_enhancement_level,
            ai_learning_enabled=ai_learning_enabled,
            ai_adaptation_enabled=ai_adaptation_enabled,
            ai_breakthrough_detection=ai_breakthrough_detection,
        )
        self.ai_sessions[session_id] = session
        await self.db_service.save_session(
            {
                "session_id": session_id,
                "session_name": session.session_name,
                "status": session.status,
                "created_at": session.created_at.isoformat(),
                "ai_enhancement_level": session.ai_enhancement_level.value,
            }
        )

        cycle_iterations = max(1, int(max_cycles))
        for i in range(cycle_iterations):
            cycle = PerpetualCycle(
                cycle_number=i + 1,
                cycle_type=CycleType.EXPLORATION,
                input_data=initial_input,
            )
            cycle.confidence_score = 0.7
            cycle.creativity_score = 0.7
            cycle.wisdom_density = 0.7
            cycle.processing_time = 0.01

            try:
                integration_result = await self.think_tank_integration.conduct_integrated_inquiry(initial_input)
                cycle.output_data["integration_result"] = {
                    "overall_confidence": getattr(integration_result, "overall_confidence", 0.7)
                }
                cycle.output_data["think_tank_results"] = getattr(
                    integration_result, "think_tank_results", {}
                )
                cycle.output_data["integration_synthesis"] = getattr(
                    integration_result, "integration_synthesis", {}
                )
            except Exception:
                session.status = "terminated_with_error"
                break

            self.cycles.append(cycle)
            session.ai_sessions_history.append(cycle.id)
            if session.ai_enhancement_level != AIEnhancementLevel.NONE:
                session.ai_cycle_enhancements.append(
                    AICycleEnhancement(
                        cycle_id=cycle.id,
                        ai_enhancement_level=session.ai_enhancement_level,
                        ai_thinking_mode=self._determine_ai_thinking_mode(cycle.cycle_type, session.ai_enhancement_level),
                        ai_prompt_used=initial_input,
                        ai_response_summary="auto-generated",
                        ai_confidence=0.75,
                        ai_reasoning="compatibility-shim",
                        ai_tokens_used=42,
                        ai_processing_time=0.01,
                        impact_score=0.75,
                    )
                )

            await self.db_service.save_cycle(
                session_id,
                {
                    "id": cycle.id,
                    "cycle_number": cycle.cycle_number,
                    "status": cycle.status.value,
                    "cycle_type": cycle.cycle_type.value,
                },
            )

        if session.status != "terminated_with_error":
            session.status = "completed"
        session.ai_collaborative_metrics = {
            "total_cycles": len(session.ai_sessions_history),
            "total_enhancements": len(session.ai_cycle_enhancements),
        }
        await self.db_service.save_metrics(
            session_id,
            {
                "total_cycles": len(session.ai_sessions_history),
                "ai_confidence_avg": (
                    sum(e.ai_confidence for e in session.ai_cycle_enhancements)
                    / max(1, len(session.ai_cycle_enhancements))
                ),
            },
        )
        return session_id

    def _determine_ai_thinking_mode(
        self, cycle_type: CycleType, ai_enhancement_level: AIEnhancementLevel
    ) -> AIThinkingMode:
        if ai_enhancement_level == AIEnhancementLevel.NONE:
            return AIThinkingMode.LOGICAL

        mapping = {
            CycleType.EXPLORATION: AIThinkingMode.CREATIVE,
            CycleType.CONVERGENCE: AIThinkingMode.LOGICAL,
            CycleType.SYNTHESIS: AIThinkingMode.CRITICAL,
            CycleType.META_REFLECTION: AIThinkingMode.EMPATHIC,
            CycleType.BREAKTHROUGH: AIThinkingMode.CREATIVE,
            CycleType.ADAPTATION: AIThinkingMode.STRATEGIC,
        }
        return mapping.get(cycle_type, AIThinkingMode.LOGICAL)

    async def _get_ai_enhanced_input(
        self,
        ai_session: PerpetualAISession,
        current_input: str,
        ai_context: Dict[str, Any],
        ai_mode: AIThinkingMode,
    ) -> Tuple[str, Any]:
        if ai_session.ai_enhancement_level == AIEnhancementLevel.NONE:
            return current_input, None

        response = await self.ai_integration.generate_response(
            prompt=current_input,
            context=ai_context,
            mode=ai_mode.value,
        )
        return response.content, response

    def _adjust_metric_with_ai(
        self, original_score: float, ai_confidence: float, ai_enhancement_level: AIEnhancementLevel
    ) -> float:
        if ai_enhancement_level == AIEnhancementLevel.NONE:
            return original_score
        if ai_enhancement_level == AIEnhancementLevel.ASSISTED:
            return (original_score + ai_confidence) / 2
        if ai_enhancement_level == AIEnhancementLevel.ENHANCED:
            return original_score * 0.6 + ai_confidence * 0.4
        if ai_enhancement_level == AIEnhancementLevel.AUTONOMOUS:
            return original_score * 0.4 + ai_confidence * 0.6
        return original_score

    async def _should_ai_adapt(self, ai_session: PerpetualAISession, cycle: PerpetualCycle) -> bool:
        if ai_session.ai_enhancement_level == AIEnhancementLevel.NONE:
            return False

        if cycle.pattern_type == PatternType.STAGNATION and cycle.confidence_score < 0.5:
            return True
        if cycle.confidence_score >= 0.9 and cycle.creativity_score >= 0.9:
            return True
        return False

    async def get_ai_session_analytics(self, session_id: str) -> Optional[Dict[str, Any]]:
        session = self.ai_sessions.get(session_id)
        if not session:
            return None

        enhancements = session.ai_cycle_enhancements
        total_cycles = len(enhancements)
        if total_cycles == 0:
            avg_confidence = 0.0
            avg_impact = 0.0
            total_tokens = 0
            total_processing = 0.0
        else:
            avg_confidence = sum(e.ai_confidence for e in enhancements) / total_cycles
            avg_impact = sum(e.impact_score for e in enhancements) / total_cycles
            total_tokens = sum(e.ai_tokens_used for e in enhancements)
            total_processing = sum(e.ai_processing_time for e in enhancements)

        return {
            "session_id": session.session_id,
            "session_name": session.session_name,
            "ai_enhancement_level": session.ai_enhancement_level.value,
            "total_ai_enhanced_cycles": total_cycles,
            "avg_ai_confidence": round(avg_confidence, 10),
            "avg_impact_score": round(avg_impact, 10),
            "total_ai_tokens_used": total_tokens,
            "total_ai_processing_time_seconds": round(total_processing, 10),
            "ai_session_insights_count": len(session.ai_session_insights),
            "ai_learning_events_count": len(session.ai_learning_history),
        }

    async def get_ai_enhanced_cycle_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        session = self.ai_sessions.get(session_id)
        if not session or not session.ai_sessions_history:
            return None

        cycle_id = session.ai_sessions_history[-1]
        cycle = next((c for c in self.cycles if c.id == cycle_id), None)
        if not cycle:
            return None

        return {
            "session_id": session_id,
            "cycle_id": cycle.id,
            "cycle_number": cycle.cycle_number,
            "cycle_type": cycle.cycle_type.value,
            "status": cycle.status.value,
            "confidence_score": cycle.confidence_score,
            "creativity_score": cycle.creativity_score,
            "wisdom_density": cycle.wisdom_density,
            "pattern_type": cycle.pattern_type.value if cycle.pattern_type else None,
            "processing_time": cycle.processing_time,
            "ai_enhancement_level": session.ai_enhancement_level.value,
        }
