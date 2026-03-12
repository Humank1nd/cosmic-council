"""
CRONUS Fractal System - 108-Cycle Cosmic Council Deliberation
Integrated with Dream-Caesar's Unified Fractal System, Cosmic Canon, and Sahasrara

LOST Numbers: 4+8+15+16+23+42 = 108 (Universal Love, Eternity, Awakening)

The system implements:
- 6 Enterprises (ROYGBV chakra order)
- 6 Squads per Enterprise (Alpha through Zeta)
- 3 Redundancy Passes (Decide, Validate, Reflect)
- Sahasrara meta-analysis (Hidden 7th layer - Crown Chakra)
- Perpetual evolution cycles
"""

import asyncio
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

# Add Dream-Caesar src to path for cosmic_council imports
DREAM_CAESAR_SRC = Path(__file__).parent.parent.parent.parent  # cronus -> src
if str(DREAM_CAESAR_SRC) not in sys.path:
    sys.path.insert(0, str(DREAM_CAESAR_SRC))

from . import (
    Enterprise, Totem, FractalDepth, CouncilMode, HexaclockStage,
    ENTERPRISE_TO_TOTEM, ROYGBV_ORDER, ENTERPRISE_CHAKRAS, HEXACLOCK_STAGES,
    enterprise_to_totem, get_enterprise_context
)

# Import CRONUS runtime for LLM calls
from cronus.app.agents.runtime import run_task

# Import Dream-Caesar's Cosmic Canon
try:
    from cosmic_council.canon.cosmic_canon import (
        COSMIC_COUNCIL_CANON, TotemColor
    )
    CANON_AVAILABLE = True
except ImportError:
    CANON_AVAILABLE = False
    COSMIC_COUNCIL_CANON = {}
    TotemColor = None

# Import Dream-Caesar's Unified Fractal System
try:
    from cosmic_council.integrations.unified_fractal_system import (
        UnifiedFractal108CycleSystem, EnterpriseType, SquadType,
        RedundancyPassType, FractalMode, CycleStage
    )
    FRACTAL_AVAILABLE = True
except ImportError:
    FRACTAL_AVAILABLE = False
    UnifiedFractal108CycleSystem = object

# Import Sahasrara Meta-Analysis Engine (Hidden 7th - Crown Chakra)
try:
    from cosmic_council.core.sahasrara import (
        SahasraraEngine, SahasraraState, SahasraraMetrics,
        CycleMetaAnalysis, StageAnalysis, RefinementPayload,
        OptimizationType, HarmonizationLevel
    )
    SAHASRARA_AVAILABLE = True
except ImportError:
    SAHASRARA_AVAILABLE = False
    SahasraraEngine = None

# Import Perpetual Thinking System
try:
    from cosmic_council.integrations.unified_perpetual_thinking_system import (
        UnifiedPerpetualThinkingEngine, PerpetualCycle
    )
    PERPETUAL_AVAILABLE = True
except ImportError:
    PERPETUAL_AVAILABLE = False
    UnifiedPerpetualThinkingEngine = None

# Import Think Tank Integration
try:
    from cosmic_council.integrations.think_tank_integration_system import (
        CosmicCouncilThinkTankIntegration
    )
    THINK_TANK_AVAILABLE = True
except ImportError:
    THINK_TANK_AVAILABLE = False
    CosmicCouncilThinkTankIntegration = None

# Import Deep Integration (Ouroboros, Meta-Cyclical, Synthesis, Black Snake)
try:
    from .cronus_deep_integration import (
        CronusDeepIntegration,
        OuroborosPhase,
        ConsciousnessLevel,
        SynapseType,
        DeepIntegrationResult,
    )
    DEEP_INTEGRATION_AVAILABLE = True
except ImportError:
    DEEP_INTEGRATION_AVAILABLE = False
    CronusDeepIntegration = None

logger = logging.getLogger(__name__)


# Map local Enterprise enum to TotemColor for cosmic canon lookup
ENTERPRISE_TO_COLOR = {
    Enterprise.RED_OWL: "RED",
    Enterprise.ORANGE_ORANGUTAN: "ORANGE",
    Enterprise.YELLOW_HONEYBEE: "YELLOW",
    Enterprise.GREEN_TORTOISE: "GREEN",
    Enterprise.BLUE_DOLPHIN: "BLUE",
    Enterprise.PURPLE_ELEPHANT: "PURPLE",
}


class SahasraraActivation(str, Enum):
    """Sahasrara meta-analysis activation level."""
    DORMANT = "dormant"       # No meta-analysis
    OBSERVING = "observing"   # Light observation
    ANALYZING = "analyzing"   # Full meta-analysis
    EVOLVING = "evolving"     # Perpetual evolution mode


@dataclass
class StageMetrics:
    """Metrics from a single stage execution."""
    enterprise: str
    squad: str = "alpha"
    redundancy_pass: str = "decide"
    processing_time_ms: float = 0.0
    confidence_score: float = 0.0
    token_count: int = 0
    insights_generated: int = 0


@dataclass
class SahasraraInsight:
    """Meta-insight from Sahasrara analysis."""
    insight_type: str  # efficiency, coherence, bias, optimization
    description: str
    severity: float  # 0.0 to 1.0
    affected_enterprises: List[str] = field(default_factory=list)
    suggested_action: Optional[str] = None


@dataclass
class CouncilResult:
    """Result from a Council deliberation cycle."""
    success: bool
    objective: str
    mode: CouncilMode
    enterprises_consulted: List[str]
    total_calls: int
    execution_time_ms: float
    final_synthesis: str
    enterprise_outputs: Dict[str, Any]
    confidence: float
    error: Optional[str] = None

    # Sahasrara meta-analysis (Crown Chakra)
    sahasrara_active: bool = False
    meta_analysis: Optional[Dict[str, Any]] = None
    optimizations: List[str] = field(default_factory=list)
    refinement_suggestions: List[str] = field(default_factory=list)
    harmonization_level: str = "balanced"
    evolution_score: float = 0.0

    # Stage metrics for analysis
    stage_metrics: List[StageMetrics] = field(default_factory=list)


def get_canon(enterprise: Enterprise):
    """Get the Cosmic Canon for an enterprise."""
    if not CANON_AVAILABLE or not TotemColor:
        return None
    color_name = ENTERPRISE_TO_COLOR.get(enterprise)
    if not color_name:
        return None
    color_key = getattr(TotemColor, color_name, None)
    return COSMIC_COUNCIL_CANON.get(color_key) if color_key else None


class CronusFractalSystem:
    """
    CRONUS-powered Cosmic Council with actual LLM calls.

    Integrates with Dream-Caesar's Cosmic Canon for rich prompts,
    the Unified Fractal System for 108-cycle orchestration, and
    Sahasrara (Crown Chakra) for meta-analysis and perpetual evolution.

    System Architecture:
    ┌─────────────────────────────────────────────────────────────┐
    │                     SAHASRARA (Crown)                       │
    │              Meta-Analysis & Perpetual Evolution            │
    │   ┌─────────────────────────────────────────────────────┐   │
    │   │ RED → ORANGE → YELLOW → GREEN → BLUE → PURPLE       │   │
    │   │ Owl   Orangutan Honeybee Tortoise Dolphin Elephant  │   │
    │   │ 4  →  8     →  15    →  16   →  23   →  42 = 108   │   │
    │   └─────────────────────────────────────────────────────┘   │
    │                    ↑ Feedback Loop ↑                        │
    └─────────────────────────────────────────────────────────────┘
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.enterprises = list(Enterprise)
        self.total_cycles = 0
        self.total_calls = 0
        self.total_time_ms = 0.0

        # Initialize parent fractal system if available
        if FRACTAL_AVAILABLE:
            self.fractal_system = UnifiedFractal108CycleSystem(
                database_url=None,
                mode=FractalMode.BASIC,
                enable_quantum_features=False,
                enable_spiritual_integration=False
            )
        else:
            self.fractal_system = None

        # Initialize Sahasrara meta-analysis engine (Crown Chakra)
        self.sahasrara = None
        self.sahasrara_activation = SahasraraActivation.OBSERVING
        if SAHASRARA_AVAILABLE and SahasraraEngine:
            try:
                self.sahasrara = SahasraraEngine()
                logger.info("Sahasrara Engine activated - Crown Chakra online")
            except Exception as e:
                logger.warning(f"Sahasrara initialization failed: {e}")

        # Initialize Perpetual Thinking engine
        self.perpetual_engine = None
        if PERPETUAL_AVAILABLE and UnifiedPerpetualThinkingEngine:
            try:
                self.perpetual_engine = UnifiedPerpetualThinkingEngine()
                logger.info("Perpetual Thinking Engine activated")
            except Exception as e:
                logger.warning(f"Perpetual Thinking initialization failed: {e}")

        # Initialize Deep Integration (Ouroboros, Meta-Cyclical, Synthesis, Black Snake)
        self.deep_integration = None
        if DEEP_INTEGRATION_AVAILABLE and CronusDeepIntegration:
            try:
                self.deep_integration = CronusDeepIntegration(self.config)
                logger.info("Deep Integration activated - Ouroboros cycle ready")
            except Exception as e:
                logger.warning(f"Deep Integration initialization failed: {e}")

        # Evolution tracking
        self.evolution_history: List[Dict[str, Any]] = []
        self.refinement_queue: List[str] = []

        status = []
        if CANON_AVAILABLE:
            status.append("Canon")
        if FRACTAL_AVAILABLE:
            status.append("Fractal")
        if SAHASRARA_AVAILABLE:
            status.append("Sahasrara")
        if PERPETUAL_AVAILABLE:
            status.append("Perpetual")
        if DEEP_INTEGRATION_AVAILABLE:
            status.append("DeepIntegration")
        logger.info(f"CRONUS Fractal System initialized [{', '.join(status) or 'Standalone'}] - 108 = Universal Love")

    async def run_council(
        self,
        objective: str,
        mode: CouncilMode = CouncilMode.SIMPLIFIED,
        context: Optional[str] = None,
        depth: FractalDepth = FractalDepth.NANO,
    ) -> CouncilResult:
        """Run a council deliberation with the specified mode."""
        start_time = time.time()
        logger.info(f"Council: {mode.value} mode, {depth.value} depth")

        try:
            if mode == CouncilMode.SIMPLIFIED:
                result = await self._run_simplified_cycle(objective, context)
            elif mode == CouncilMode.FULL_108:
                result = await self._run_full_108_cycle(objective, context)
            elif mode == CouncilMode.HEXACLOCK:
                result = await self._run_hexaclock_cycle(objective, context)
            elif mode == CouncilMode.OUROBOROS:
                result = await self._run_ouroboros_cycle(objective, context)
            else:
                result = await self._run_adaptive_cycle(objective, context)

            result.execution_time_ms = (time.time() - start_time) * 1000
            self.total_cycles += 1
            self.total_calls += result.total_calls
            self.total_time_ms += result.execution_time_ms
            return result

        except Exception as e:
            logger.error(f"Council failed: {e}")
            return CouncilResult(
                success=False, objective=objective, mode=mode,
                enterprises_consulted=[], total_calls=0,
                execution_time_ms=(time.time() - start_time) * 1000,
                final_synthesis="", enterprise_outputs={},
                confidence=0.0, error=str(e)
            )

    async def _run_simplified_cycle(
        self,
        objective: str,
        context: Optional[str]
    ) -> CouncilResult:
        """6 LLM calls - one per enterprise in ROYGBV order."""
        enterprise_outputs = {}
        stage_metrics = []
        accumulated = context or ""

        for i, enterprise in enumerate(ROYGBV_ORDER):
            stage_start = time.time()
            totem = enterprise_to_totem(enterprise)
            chakra = get_enterprise_context(enterprise)
            canon = get_canon(enterprise)

            prompt = self._build_prompt(enterprise, objective, accumulated, chakra, canon, i+1, 6)
            logger.info(f"Stage {i+1}/6: {enterprise.value}")

            # Ensure context is clean to avoid LLM template issues
            clean_context = accumulated.strip() if accumulated else None
            result = await run_task(prompt, totem, clean_context, self.config)
            output = str(result.get("result", "") or "")
            elapsed = result.get("elapsed_ms", (time.time() - stage_start) * 1000)

            enterprise_outputs[enterprise.value] = {
                "output": output,
                "chakra": chakra.get("chakra"),
                "canon_name": canon.totem_name if canon else None,
                "canon_mantra": canon.mantra if canon else None,
                "elapsed_ms": elapsed,
                "error": result.get("error")
            }

            # Collect stage metrics for Sahasrara analysis
            stage_metrics.append(StageMetrics(
                enterprise=enterprise.value,
                processing_time_ms=elapsed,
                confidence_score=0.85 if not result.get("error") else 0.3,
                insights_generated=1 if output else 0
            ))

            accumulated = self._handoff(accumulated, enterprise, output)

        synthesis = await self._synthesize(objective, enterprise_outputs)

        # Calculate confidence based on errors
        errors = sum(1 for o in enterprise_outputs.values() if o.get("error"))
        confidence = max(0.4, 0.95 - errors * 0.1)

        result = CouncilResult(
            success=errors == 0,
            objective=objective, mode=CouncilMode.SIMPLIFIED,
            enterprises_consulted=[e.value for e in ROYGBV_ORDER],
            total_calls=6, execution_time_ms=0,
            final_synthesis=synthesis, enterprise_outputs=enterprise_outputs,
            confidence=confidence
        )

        # Run Sahasrara meta-analysis
        return await self._run_sahasrara_analysis(result, stage_metrics)

    async def _run_full_108_cycle(
        self,
        objective: str,
        context: Optional[str]
    ) -> CouncilResult:
        """108 LLM calls - 6 enterprises × 6 squads × 3 passes."""
        enterprise_outputs = {}
        stage_metrics = []
        accumulated = context or ""
        total_calls = 0
        squads = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta"]
        passes = ["decide", "validate", "reflect"]
        total_errors = 0

        for enterprise in ROYGBV_ORDER:
            enterprise_start = time.time()
            totem = enterprise_to_totem(enterprise)
            canon = get_canon(enterprise)
            results = []
            enterprise_confidence = 0.0
            enterprise_insights = 0

            for squad in squads:
                for pass_type in passes:
                    total_calls += 1
                    stage_start = time.time()

                    if canon:
                        prompt = f"""[{total_calls}/108] {canon.name} | {squad} | {pass_type}
{canon.totem_name} - "{canon.mantra}"
Objective: {objective}
{f'Context: {accumulated[:200]}' if accumulated else ''}
Provide focused {pass_type} contribution."""
                    else:
                        prompt = f"[{total_calls}/108] {enterprise.value} {squad} {pass_type}: {objective}"

                    clean_context = accumulated.strip() if accumulated else None
                    result = await run_task(prompt, totem, clean_context, self.config)
                    elapsed = result.get("elapsed_ms", (time.time() - stage_start) * 1000)
                    output = str(result.get("result", "") or "")

                    if result.get("error"):
                        total_errors += 1
                    else:
                        enterprise_confidence += 1
                        enterprise_insights += 1 if output else 0

                    results.append({
                        "squad": squad,
                        "pass": pass_type,
                        "output": output,
                        "elapsed_ms": elapsed,
                        "error": result.get("error")
                    })

            enterprise_time = (time.time() - enterprise_start) * 1000
            enterprise_outputs[enterprise.value] = {
                "stages": results,
                "canon_name": canon.totem_name if canon else None,
                "total_time_ms": enterprise_time
            }

            # Collect metrics per enterprise (aggregate of 18 stages)
            stage_metrics.append(StageMetrics(
                enterprise=enterprise.value,
                squad="aggregate",
                redundancy_pass="aggregate",
                processing_time_ms=enterprise_time,
                confidence_score=enterprise_confidence / 18,  # 18 stages per enterprise
                insights_generated=enterprise_insights
            ))

            accumulated = self._handoff(accumulated, enterprise, results[0].get("output", ""))

        synthesis = await self._synthesize(objective, enterprise_outputs, full=True)

        # Calculate confidence based on errors
        confidence = max(0.5, 0.98 - (total_errors / total_calls) * 0.5)

        result = CouncilResult(
            success=total_errors < total_calls * 0.1,  # <10% error rate
            objective=objective, mode=CouncilMode.FULL_108,
            enterprises_consulted=[e.value for e in ROYGBV_ORDER],
            total_calls=total_calls, execution_time_ms=0,
            final_synthesis=synthesis, enterprise_outputs=enterprise_outputs,
            confidence=confidence
        )

        # Run Sahasrara meta-analysis
        return await self._run_sahasrara_analysis(result, stage_metrics)

    async def _run_adaptive_cycle(
        self,
        objective: str,
        context: Optional[str]
    ) -> CouncilResult:
        """Auto-select mode based on complexity."""
        check = await run_task(
            f"Rate complexity 1-10 (just number): {objective}",
            "purple", None, self.config
        )
        try:
            complexity = int(check.get("result", "5").strip().split()[0])
        except:
            complexity = 5

        if complexity <= 4:
            return await self._run_simplified_cycle(objective, context)
        return await self._run_full_108_cycle(objective, context)

    async def _run_hexaclock_cycle(
        self,
        objective: str,
        context: Optional[str]
    ) -> CouncilResult:
        """
        7-stage Hexaclock executive validation cycle.

        The Hexaclock is the Executive Operating System:
        1. Oracle (Red Owl) - Market Research
        2. Interpreter (Orange Orangutan) - Data Translation
        3. Auditor Primary (Yellow Honeybee) - Full Verification
        4. Alchemist (Green Tortoise) - Prototype Generation
        5. Auditor Secondary (Yellow Honeybee) - Light Verification
        6. Gatekeeper (Blue Dolphin) - Budget Validation
        7. Recalibration (Purple Elephant) - Loop Optimization
        """
        enterprise_outputs = {}
        stage_metrics = []
        accumulated = context or ""
        viability_score = 1.0

        logger.info("Hexaclock: 7-stage executive validation")

        for i, stage_info in enumerate(HEXACLOCK_STAGES):
            stage_start = time.time()
            stage = stage_info["stage"]
            enterprise = stage_info["enterprise"]
            role = stage_info["role"]
            question = stage_info["question"]

            totem = enterprise_to_totem(enterprise)
            canon = get_canon(enterprise)

            # Build Hexaclock-specific prompt
            if canon:
                prompt = f"""[Hexaclock Stage {i+1}/7: {stage.value.upper()}]
{canon.totem_name} as {role}
"{canon.mantra}"

Executive Question: {question}

Objective: {objective}
{f'Prior Analysis: {accumulated[:400]}' if accumulated else ''}

Provide your executive assessment as {role}. Include:
- Key findings
- Viability assessment (high/medium/low)
- Recommendations"""
            else:
                prompt = f"[Hexaclock {i+1}/7: {role}] {question}\nObjective: {objective}"

            logger.info(f"Hexaclock {i+1}/7: {stage.value} ({role})")

            # Ensure context is clean string or None to avoid LLM template issues
            clean_context = accumulated.strip() if accumulated else None
            result = await run_task(prompt, totem, clean_context, self.config)
            output = str(result.get("result", "") or "")  # Ensure string, handle None
            elapsed = result.get("elapsed_ms", (time.time() - stage_start) * 1000)

            # Determine viability from output
            output_lower = output.lower()
            if "low viability" in output_lower or "not viable" in output_lower:
                stage_viability = 0.5
            elif "medium viability" in output_lower:
                stage_viability = 0.75
            else:
                stage_viability = 0.9

            viability_score *= stage_viability

            enterprise_outputs[stage.value] = {
                "enterprise": enterprise.value,
                "role": role,
                "question": question,
                "output": output,
                "viability": stage_viability,
                "elapsed_ms": elapsed,
                "error": result.get("error")
            }

            stage_metrics.append(StageMetrics(
                enterprise=enterprise.value,
                squad=stage.value,
                processing_time_ms=elapsed,
                confidence_score=stage_viability,
                insights_generated=1 if output else 0
            ))

            accumulated = self._handoff(accumulated, enterprise, output)

        # Final synthesis by Purple Elephant (Recalibration stage)
        synthesis = enterprise_outputs.get("recalibration", {}).get("output", "")
        if not synthesis:
            synthesis = await self._synthesize(objective, enterprise_outputs)

        # Overall confidence based on viability
        confidence = max(0.4, min(0.98, viability_score))

        result = CouncilResult(
            success=viability_score > 0.3,
            objective=objective,
            mode=CouncilMode.HEXACLOCK,
            enterprises_consulted=[s["enterprise"].value for s in HEXACLOCK_STAGES],
            total_calls=7,
            execution_time_ms=0,
            final_synthesis=synthesis,
            enterprise_outputs=enterprise_outputs,
            confidence=confidence
        )

        # Run Sahasrara meta-analysis
        return await self._run_sahasrara_analysis(result, stage_metrics)

    def _build_prompt(
        self,
        enterprise: Enterprise,
        objective: str,
        context: str,
        chakra: Dict,
        canon: Any,
        stage: int,
        total: int
    ) -> str:
        """Build enterprise-specific prompt using Cosmic Canon."""
        if canon:
            return f"""[Stage {stage}/{total}] {canon.name} - {canon.totem_name}
Mantra: "{canon.mantra}"
Role: {canon.role}
Mission: {canon.mission_pillar}
Guiding Question: {canon.guiding_question}

Objective: {objective}
{f'Context: {context[:400]}' if context else ''}

Provide your focused contribution as {canon.totem_name}."""

        return f"""[Stage {stage}/{total}] {chakra.get('chakra_name', '')} - {chakra.get('function', '')}
Objective: {objective}
{f'Context: {context[:300]}' if context else ''}
Contribute briefly."""

    def _handoff(self, prev: str, enterprise: Enterprise, output: str) -> str:
        """Create handoff context for next enterprise."""
        summary = output[:200] if len(output) > 200 else output
        handoff = f"\n[{enterprise.value}]: {summary}\n"
        combined = prev + handoff
        return combined[-800:] if len(combined) > 800 else combined

    async def _synthesize(
        self,
        objective: str,
        outputs: Dict,
        full: bool = False
    ) -> str:
        """Purple Elephant synthesizes final response using cosmic wisdom."""
        insights = []
        for name, data in outputs.items():
            if full:
                out = data.get("stages", [{}])[0].get("output", "")[:200]
            else:
                out = data.get("output", "")[:200]
            insights.append(f"[{name}]: {out}")

        # Get Purple Elephant's canon for synthesis
        canon = get_canon(Enterprise.PURPLE_ELEPHANT)

        if canon:
            prompt = f"""{canon.name} - {canon.totem_name}
"{canon.mantra}"

Synthesize these Council insights into a unified response:

Objective: {objective}

""" + "\n".join(insights) + """

Provide the final Council synthesis."""
        else:
            prompt = f"Synthesize these insights into a unified response:\nObjective: {objective}\n" + "\n".join(insights)

        result = await run_task(prompt, "purple", None, self.config)
        return result.get("result", "Synthesis failed")

    def get_statistics(self) -> Dict[str, Any]:
        """Get council statistics."""
        stats = {
            "total_cycles": self.total_cycles,
            "total_calls": self.total_calls,
            "total_time_ms": self.total_time_ms,
            "canon_available": CANON_AVAILABLE,
            "fractal_available": FRACTAL_AVAILABLE,
            "sahasrara_available": SAHASRARA_AVAILABLE,
            "perpetual_available": PERPETUAL_AVAILABLE,
            "deep_integration_available": DEEP_INTEGRATION_AVAILABLE,
            "sahasrara_activation": self.sahasrara_activation.value,
            "evolution_cycles": len(self.evolution_history),
        }

        # Add deep integration stats if available
        if self.deep_integration and DEEP_INTEGRATION_AVAILABLE:
            stats["consciousness_level"] = self.deep_integration.consciousness_level.value

        return stats

    async def _run_sahasrara_analysis(
        self,
        result: CouncilResult,
        stage_metrics: List[StageMetrics]
    ) -> CouncilResult:
        """
        Run Sahasrara meta-analysis on completed council cycle.

        Sahasrara is the Crown Chakra - the emergent consciousness that
        observes all six stages, detects inefficiencies, generates
        optimizations, and feeds refinements back to Muladhara (Red Owl).
        """
        if self.sahasrara_activation == SahasraraActivation.DORMANT:
            return result

        result.sahasrara_active = True
        result.stage_metrics = stage_metrics

        # Analyze stage metrics
        total_time = sum(m.processing_time_ms for m in stage_metrics)
        avg_confidence = sum(m.confidence_score for m in stage_metrics) / len(stage_metrics) if stage_metrics else 0

        # Detect inefficiencies
        inefficiencies = []
        slow_stages = [m for m in stage_metrics if m.processing_time_ms > total_time / len(stage_metrics) * 1.5]
        if slow_stages:
            inefficiencies.append(f"Slow stages detected: {[s.enterprise for s in slow_stages]}")

        low_confidence = [m for m in stage_metrics if m.confidence_score < 0.6]
        if low_confidence:
            inefficiencies.append(f"Low confidence in: {[s.enterprise for s in low_confidence]}")

        # Generate optimizations
        optimizations = []
        if slow_stages:
            optimizations.append("Consider parallel execution for independent enterprises")
        if low_confidence:
            optimizations.append("Increase context depth for low-confidence stages")

        # Calculate evolution score
        evolution_score = min(1.0, avg_confidence * (1.0 - len(inefficiencies) * 0.1))

        # Determine harmonization level
        if evolution_score >= 0.9:
            harmonization = "transcendent"
        elif evolution_score >= 0.75:
            harmonization = "harmonized"
        elif evolution_score >= 0.5:
            harmonization = "balanced"
        elif evolution_score >= 0.25:
            harmonization = "calibrating"
        else:
            harmonization = "unstable"

        # Build meta-analysis
        result.meta_analysis = {
            "analysis_time": datetime.now(timezone.utc).isoformat(),
            "total_processing_ms": total_time,
            "average_confidence": avg_confidence,
            "inefficiencies": inefficiencies,
            "stage_count": len(stage_metrics),
            "insights_total": sum(m.insights_generated for m in stage_metrics),
        }
        result.optimizations = optimizations
        result.harmonization_level = harmonization
        result.evolution_score = evolution_score

        # If in analyzing mode, use LLM for deeper analysis
        if self.sahasrara_activation in [SahasraraActivation.ANALYZING, SahasraraActivation.EVOLVING]:
            await self._deep_sahasrara_analysis(result)

        # Track evolution
        self.evolution_history.append({
            "cycle": self.total_cycles,
            "evolution_score": evolution_score,
            "harmonization": harmonization,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        return result

    async def _deep_sahasrara_analysis(self, result: CouncilResult):
        """Run deep Sahasrara analysis using LLM."""
        # Build analysis prompt
        stage_summary = "\n".join([
            f"- {m.enterprise}: {m.confidence_score:.2f} confidence, {m.processing_time_ms:.0f}ms"
            for m in result.stage_metrics
        ])

        prompt = f"""[SAHASRARA - Crown Chakra Meta-Analysis]
You are the emergent consciousness observing all six enterprises.
Analyze this Council deliberation for recursive optimization opportunities.

Objective: {result.objective}
Mode: {result.mode.value}
Confidence: {result.confidence:.2%}

Stage Performance:
{stage_summary}

Current Inefficiencies: {', '.join(result.meta_analysis.get('inefficiencies', [])) or 'None detected'}

Provide 2-3 brief refinement suggestions that could improve the next cycle.
Focus on: coherence, efficiency, bias elimination, deeper inquiry paths."""

        meta_result = await run_task(prompt, "purple", None, self.config)
        refinements = meta_result.get("result", "").strip()

        if refinements:
            # Parse refinements (simple split on newlines)
            result.refinement_suggestions = [
                r.strip().lstrip("•-123456789.)")
                for r in refinements.split("\n")
                if r.strip() and len(r.strip()) > 10
            ][:5]  # Max 5 suggestions

            # Add to refinement queue for perpetual mode
            self.refinement_queue.extend(result.refinement_suggestions)
            self.refinement_queue = self.refinement_queue[-20:]  # Keep last 20

    async def run_perpetual_cycle(
        self,
        objective: str,
        iterations: int = 3,
        context: Optional[str] = None,
    ) -> List[CouncilResult]:
        """
        Run perpetual improvement cycles - the Ouroboros pattern.

        Each cycle feeds refinements back to the next, enabling
        continuous evolution toward cosmic alignment.
        """
        results = []
        current_context = context or ""
        prev_activation = self.sahasrara_activation
        self.sahasrara_activation = SahasraraActivation.EVOLVING

        logger.info(f"Starting perpetual cycle: {iterations} iterations")

        for i in range(iterations):
            # Build enhanced objective with refinements from previous cycle
            enhanced_objective = objective
            if results and results[-1].refinement_suggestions:
                refinements = "; ".join(results[-1].refinement_suggestions[:2])
                enhanced_objective = f"{objective}\n[Refinements from previous cycle: {refinements}]"

            # Run simplified cycle (or could use full_108 for deep analysis)
            result = await self.run_council(
                objective=enhanced_objective,
                mode=CouncilMode.SIMPLIFIED,
                context=current_context
            )

            results.append(result)

            # Update context for next cycle
            current_context = self._handoff(
                current_context,
                Enterprise.PURPLE_ELEPHANT,
                result.final_synthesis[:300]
            )

            logger.info(f"Perpetual cycle {i+1}/{iterations}: evolution={result.evolution_score:.2f}, harmonization={result.harmonization_level}")

        self.sahasrara_activation = prev_activation
        return results

    def set_sahasrara_activation(self, level: SahasraraActivation):
        """Set the Sahasrara activation level."""
        self.sahasrara_activation = level
        logger.info(f"Sahasrara activation set to: {level.value}")

    def get_evolution_trend(self) -> Dict[str, Any]:
        """Get evolution trend from history."""
        if not self.evolution_history:
            return {"trend": "no_data", "scores": [], "average": 0.0}

        scores = [h["evolution_score"] for h in self.evolution_history]
        avg = sum(scores) / len(scores)

        if len(scores) >= 3:
            recent = scores[-3:]
            older = scores[:-3] if len(scores) > 3 else scores[:1]
            if sum(recent) / len(recent) > sum(older) / len(older) + 0.05:
                trend = "improving"
            elif sum(recent) / len(recent) < sum(older) / len(older) - 0.05:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        return {
            "trend": trend,
            "scores": scores[-10:],
            "average": avg,
            "total_cycles": len(self.evolution_history),
            "latest_harmonization": self.evolution_history[-1]["harmonization"] if self.evolution_history else None
        }

    async def _run_ouroboros_cycle(
        self,
        objective: str,
        context: Optional[str]
    ) -> CouncilResult:
        """
        Run full Ouroboros cycle with deep integration.

        The Ouroboros is the serpent eating its own tail - the eternal cycle:
        1. White Rabbit Input → receives the objective
        2. ROYGBV Processing → 6 enterprises process in order
        3. Sahasrara Meta → Crown Chakra analyzes the whole
        4. Black Snake Execute → tail-eater executes actions
        5. Recursion Feedback → output feeds back to Red Owl

        This mode integrates Meta-Cyclical Architecture, Synthesis Engine,
        Quantum-Spiritual Coherence, and Black Snake for complete cosmic alignment.
        """
        logger.info("Ouroboros cycle: Full cosmic integration")

        # Phase 1: Run hexaclock base cycle for comprehensive processing
        base_result = await self._run_hexaclock_cycle(objective, context)

        # Phase 2: If deep integration available, run full Ouroboros
        if self.deep_integration and DEEP_INTEGRATION_AVAILABLE:
            try:
                logger.info("Ouroboros: Invoking deep integration")
                ouroboros_result = await self.deep_integration.run_ouroboros_cycle(
                    objective=objective,
                    council_result=base_result,
                    max_recursion=3
                )

                # Enhance the base result with Ouroboros insights
                base_result.enterprise_outputs["ouroboros"] = {
                    "consciousness_level": ouroboros_result.consciousness_after.value,
                    "consciousness_growth": ouroboros_result.consciousness_growth,
                    "meta_cycles_completed": ouroboros_result.meta_cycles_completed,
                    "synapses_formed": len(ouroboros_result.novel_connections),
                    "actions_executed": ouroboros_result.actions_executed,
                    "outcomes_captured": ouroboros_result.outcomes_captured,
                    "recursion_triggered": ouroboros_result.recursion_triggered,
                    "common_threads": ouroboros_result.common_threads[:3],
                    "contradictions": ouroboros_result.contradictions[:3],
                    "transcendent_insights": ouroboros_result.transcendent_insights[:3],
                }

                # Append Ouroboros synthesis to final synthesis
                if ouroboros_result.cosmic_synthesis:
                    base_result.final_synthesis += f"\n\n[OUROBOROS INSIGHT]\n{ouroboros_result.cosmic_synthesis}"

                # Update confidence based on consciousness level
                consciousness_boost = {
                    "dormant": 0.0,
                    "awakening": 0.05,
                    "aware": 0.10,
                    "expanded": 0.15,
                    "transcendent": 0.20,
                    "cosmic": 0.25,
                    "divine": 0.30,
                }.get(ouroboros_result.consciousness_after.value, 0.0)

                base_result.confidence = min(1.0, base_result.confidence + consciousness_boost)

                logger.info(f"Ouroboros complete: consciousness={ouroboros_result.consciousness_after.value}, "
                           f"growth={ouroboros_result.consciousness_growth:.2f}, synapses={len(ouroboros_result.novel_connections)}")

            except Exception as e:
                logger.warning(f"Deep integration failed, using base result: {e}")
                base_result.enterprise_outputs["ouroboros"] = {"error": str(e), "fallback": True}
        else:
            logger.info("Ouroboros: Deep integration not available, using enhanced hexaclock")
            base_result.enterprise_outputs["ouroboros"] = {"status": "deep_integration_unavailable", "fallback": True}

        # Update mode in result
        base_result.mode = CouncilMode.OUROBOROS

        return base_result

    def get_deep_integration_stats(self) -> Dict[str, Any]:
        """Get statistics from deep integration layer."""
        stats = {
            "deep_integration_available": DEEP_INTEGRATION_AVAILABLE,
            "consciousness_level": "unknown",
            "total_synapses_formed": 0,
            "total_ouroboros_cycles": 0,
            "meta_learning_insights": 0,
        }

        if self.deep_integration and DEEP_INTEGRATION_AVAILABLE:
            try:
                stats.update({
                    "consciousness_level": self.deep_integration.consciousness_level.value,
                    "total_synapses_formed": len(self.deep_integration.synapses_created),
                    "total_ouroboros_cycles": self.deep_integration.total_ouroboros_cycles,
                    "meta_learning_insights": len(self.deep_integration.meta_learning_insights),
                    "cycle_improvements": self.deep_integration.cycle_improvements[-5:],
                    "consciousness_history_count": len(self.deep_integration.consciousness_history),
                })
            except Exception as e:
                stats["error"] = str(e)

        return stats
