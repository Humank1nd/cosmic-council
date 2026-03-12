"""
CRONUS Pipeline — C→R→O→N→U→S Sequential Deliberation

Curiosity  (Red)    → Research the problem (WHY)
Routing    (Orange) → Plan the approach (HOW)
Origin     (Yellow) → Build the solution (WHAT)
Numbers    (Green)  → Evaluate resources (BALANCE)
User       (Blue)   → Deliver the output (OUTPUT)
Support    (Purple) → Reflect & evaluate (REFLECTION)

Each totem receives the problem + all prior totem outputs.
Support decides whether another cycle is needed.
"""

from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from cronus.app.agents.runtime import run_task
from cronus.app.agents.think_tank import (
    run_think_tank,
    should_spawn_think_tank,
    ThinkTankResult,
)


# =============================================================================
# PIPELINE CONSTANTS
# =============================================================================

# Forward pass order (C-R-O-N-U)
FORWARD_TOTEMS = ["red", "orange", "yellow", "green", "blue"]

# Feedback evaluator (S)
FEEDBACK_TOTEM = "purple"

# Full CRONUS sequence
CRONUS_SEQUENCE = FORWARD_TOTEMS + [FEEDBACK_TOTEM]

TOTEM_LETTER = {
    "red": "C",
    "orange": "R",
    "yellow": "O",
    "green": "N",
    "blue": "U",
    "purple": "S",
}

TOTEM_NAME = {
    "red": "Curiosity",
    "orange": "Routing",
    "yellow": "Origin",
    "green": "Numbers",
    "blue": "User",
    "purple": "Support",
}


# =============================================================================
# DATA MODELS
# =============================================================================

class CycleStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"
    FAILED = "failed"


class TotemStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETE = "complete"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class TotemResult:
    """Result from a single totem's execution."""
    totem: str
    letter: str
    name: str
    status: TotemStatus
    analysis: str = ""
    confidence: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0
    error: Optional[str] = None
    sequence: int = 0
    think_tank: Optional[ThinkTankResult] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent": self.totem,
            "totem": self.totem,
            "letter": self.letter,
            "name": self.name,
            "status": self.status.value,
            "analysis": self.analysis,
            "confidence": self.confidence,
            "recommendations": self.recommendations,
            "execution_time_ms": self.execution_time_ms,
            "error": self.error,
            "sequence": self.sequence,
            "think_tank": self.think_tank.to_dict() if self.think_tank else None,
        }


@dataclass
class PipelineCycle:
    """Tracks a full C→R→O→N→U→S deliberation cycle."""
    cycle_id: str
    problem: str
    context: Dict[str, Any]
    status: CycleStatus = CycleStatus.PENDING
    totem_results: List[TotemResult] = field(default_factory=list)
    totem_progress: Dict[str, TotemStatus] = field(default_factory=dict)
    synthesis: Optional[str] = None
    final_output: Optional[str] = None
    should_repeat: bool = False
    cycle_number: int = 1
    max_cycles: int = 3
    created_at: str = ""
    completed_at: Optional[str] = None
    error: Optional[str] = None

    def __post_init__(self):
        if not self.created_at:
            self.created_at = _now_iso()
        # Initialize progress for all totems
        if not self.totem_progress:
            for totem in CRONUS_SEQUENCE:
                self.totem_progress[totem] = TotemStatus.QUEUED

    def to_response(self) -> Dict[str, Any]:
        """Convert to the response shape backend-client.ts expects."""
        responses = []
        for tr in self.totem_results:
            responses.append({
                "agent": tr.totem,
                "analysis": tr.analysis,
                "confidence": tr.confidence,
                "recommendations": tr.recommendations,
            })

        totems = []
        for i, totem in enumerate(CRONUS_SEQUENCE):
            tr = next((r for r in self.totem_results if r.totem == totem), None)
            totems.append({
                "id": totem,
                "sequence": i,
                "status": self.totem_progress.get(totem, TotemStatus.QUEUED).value
                    if isinstance(self.totem_progress.get(totem), TotemStatus)
                    else self.totem_progress.get(totem, "queued"),
                "output": tr.analysis if tr else None,
                "error": {"detail": tr.error} if tr and tr.error else None,
            })

        return {
            "cycle_id": self.cycle_id,
            "status": self.status.value,
            "responses": responses,
            "totems": totems,
            "synthesis": self.synthesis,
            "final_output": self.final_output,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }


# =============================================================================
# CYCLE STORE (in-memory)
# =============================================================================

_cycle_store: Dict[str, PipelineCycle] = {}


def get_cycle(cycle_id: str) -> Optional[PipelineCycle]:
    return _cycle_store.get(cycle_id)


def list_cycles() -> List[PipelineCycle]:
    return list(_cycle_store.values())


# =============================================================================
# HELPERS
# =============================================================================

def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def _generate_cycle_id() -> str:
    return f"cycle_{uuid.uuid4().hex[:12]}"


def _build_pipeline_context(
    problem: str,
    prior_outputs: List[TotemResult],
    current_totem: str,
) -> str:
    """Build the context string for a totem, including all prior outputs."""
    parts = [f"PROBLEM: {problem}"]

    if prior_outputs:
        parts.append("\n--- PRIOR COUNCIL OUTPUTS ---")
        for pr in prior_outputs:
            parts.append(
                f"\n[{pr.letter}] {pr.name} ({pr.totem}):\n{pr.analysis}"
            )
        parts.append("\n--- END PRIOR OUTPUTS ---")

    parts.append(
        f"\nYou are the {TOTEM_NAME[current_totem]} ({TOTEM_LETTER[current_totem]}) stage. "
        f"Build on the work above."
    )

    return "\n".join(parts)


def _extract_confidence(result_text: str) -> float:
    """Heuristic: extract confidence from result text or default to 0.7."""
    lower = result_text.lower()
    if "high confidence" in lower or "very confident" in lower:
        return 0.9
    if "low confidence" in lower or "uncertain" in lower:
        return 0.4
    if "moderate" in lower or "somewhat" in lower:
        return 0.6
    return 0.7


def _extract_recommendations(result_text: str) -> List[str]:
    """Heuristic: pull bullet-pointed recommendations from text."""
    recs = []
    for line in result_text.split("\n"):
        line = line.strip()
        if line.startswith(("- ", "* ", "• ")) and len(line) > 5:
            recs.append(line.lstrip("-*• ").strip())
    return recs[:5]  # Cap at 5


def _synthesize(results: List[TotemResult]) -> str:
    """Combine all totem outputs into a synthesis."""
    parts = []
    for r in results:
        if r.status == TotemStatus.COMPLETE and r.analysis:
            parts.append(f"[{r.letter}·{r.name}] {r.analysis}")
    return "\n\n".join(parts)


# =============================================================================
# PIPELINE EXECUTION
# =============================================================================

async def run_pipeline(
    problem: str,
    context: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None,
    max_cycles: int = 3,
    requested_totems: Optional[List[str]] = None,
    enable_think_tanks: bool = False,
    problem_complexity: str = "moderate",
) -> PipelineCycle:
    """
    Run the full C→R→O→N→U→S pipeline.

    Args:
        problem: The problem statement to deliberate on.
        context: Optional context dict.
        config: CRONUS config dict (from config.toml).
        max_cycles: Max deliberation cycles (Support can trigger repeats).
        requested_totems: Subset of totems to use (None = all).
        enable_think_tanks: Whether totems can spawn fractal Think Tanks.
        problem_complexity: "simple", "moderate", "complex", or "systemic".

    Returns:
        PipelineCycle with full results.
    """
    cycle_id = _generate_cycle_id()
    cycle = PipelineCycle(
        cycle_id=cycle_id,
        problem=problem,
        context=context or {},
        max_cycles=max_cycles,
        status=CycleStatus.RUNNING,
    )
    _cycle_store[cycle_id] = cycle

    runtime_config = config or {}

    # Determine which totems to run in forward pass
    forward = FORWARD_TOTEMS
    if requested_totems:
        forward = [t for t in FORWARD_TOTEMS if t in requested_totems]

    try:
        for cycle_num in range(1, max_cycles + 1):
            cycle.cycle_number = cycle_num
            prior_outputs: List[TotemResult] = []

            # =================================================================
            # FORWARD PASS: C → R → O → N → U
            # =================================================================
            for seq, totem in enumerate(forward):
                cycle.totem_progress[totem] = TotemStatus.RUNNING

                pipeline_context = _build_pipeline_context(
                    problem, prior_outputs, totem
                )

                started = time.time()
                try:
                    raw = await run_task(
                        task=problem,
                        totem=totem,
                        context=pipeline_context,
                        config=runtime_config,
                    )
                    elapsed = (time.time() - started) * 1000

                    analysis = str(raw.get("result", ""))
                    result = TotemResult(
                        totem=totem,
                        letter=TOTEM_LETTER[totem],
                        name=TOTEM_NAME[totem],
                        status=TotemStatus.COMPLETE,
                        analysis=analysis,
                        confidence=_extract_confidence(analysis),
                        recommendations=_extract_recommendations(analysis),
                        execution_time_ms=elapsed,
                        error=raw.get("error"),
                        sequence=seq,
                    )
                except Exception as e:
                    elapsed = (time.time() - started) * 1000
                    result = TotemResult(
                        totem=totem,
                        letter=TOTEM_LETTER[totem],
                        name=TOTEM_NAME[totem],
                        status=TotemStatus.ERROR,
                        error=str(e),
                        execution_time_ms=elapsed,
                        sequence=seq,
                    )

                # ─── THINK TANK GATE ─────────────────────────────
                # Spawn fractal sub-council if conditions are met
                if (
                    result.status == TotemStatus.COMPLETE
                    and enable_think_tanks
                    and should_spawn_think_tank(
                        totem=totem,
                        analysis=result.analysis,
                        confidence=result.confidence,
                        problem_complexity=problem_complexity,
                    )
                ):
                    try:
                        tank_result = await run_think_tank(
                            parent_totem=totem,
                            problem=problem,
                            parent_analysis=result.analysis,
                            config=runtime_config,
                        )
                        result.think_tank = tank_result
                        # Enrich the totem's analysis with Think Tank output
                        result.analysis = tank_result.enriched_analysis
                        result.confidence = min(
                            1.0, result.confidence + 0.1
                        )
                        result.execution_time_ms += tank_result.total_time_ms
                    except Exception:
                        pass  # Think Tank failure is non-fatal

                cycle.totem_results.append(result)
                cycle.totem_progress[totem] = result.status
                prior_outputs.append(result)

            # =================================================================
            # FEEDBACK PASS: S (Support / Purple Elephant)
            # =================================================================
            cycle.totem_progress[FEEDBACK_TOTEM] = TotemStatus.RUNNING

            feedback_context = _build_pipeline_context(
                problem, prior_outputs, FEEDBACK_TOTEM
            )
            feedback_context += (
                "\n\nEvaluate the cycle output. Respond with your reflection. "
                "If the output is adequate, say 'ADEQUATE'. "
                "If another cycle is needed, say 'REPEAT' and explain what to improve."
            )

            started = time.time()
            try:
                raw = await run_task(
                    task=problem,
                    totem=FEEDBACK_TOTEM,
                    context=feedback_context,
                    config=runtime_config,
                )
                elapsed = (time.time() - started) * 1000
                analysis = str(raw.get("result", ""))

                feedback_result = TotemResult(
                    totem=FEEDBACK_TOTEM,
                    letter=TOTEM_LETTER[FEEDBACK_TOTEM],
                    name=TOTEM_NAME[FEEDBACK_TOTEM],
                    status=TotemStatus.COMPLETE,
                    analysis=analysis,
                    confidence=_extract_confidence(analysis),
                    recommendations=_extract_recommendations(analysis),
                    execution_time_ms=elapsed,
                    sequence=len(forward),
                )
            except Exception as e:
                elapsed = (time.time() - started) * 1000
                feedback_result = TotemResult(
                    totem=FEEDBACK_TOTEM,
                    letter=TOTEM_LETTER[FEEDBACK_TOTEM],
                    name=TOTEM_NAME[FEEDBACK_TOTEM],
                    status=TotemStatus.ERROR,
                    error=str(e),
                    execution_time_ms=elapsed,
                    sequence=len(forward),
                )

            cycle.totem_results.append(feedback_result)
            cycle.totem_progress[FEEDBACK_TOTEM] = feedback_result.status

            # Check if Support says REPEAT
            should_repeat = (
                "REPEAT" in feedback_result.analysis.upper()
                and cycle_num < max_cycles
            )

            if not should_repeat:
                break

            # Reset progress for next cycle (keep results for history)
            for totem in CRONUS_SEQUENCE:
                cycle.totem_progress[totem] = TotemStatus.QUEUED

        # =================================================================
        # SYNTHESIS
        # =================================================================
        # Blue (User) output is the primary output
        blue_result = next(
            (r for r in reversed(cycle.totem_results)
             if r.totem == "blue" and r.status == TotemStatus.COMPLETE),
            None,
        )
        cycle.final_output = blue_result.analysis if blue_result else None
        cycle.synthesis = _synthesize(
            [r for r in cycle.totem_results if r.status == TotemStatus.COMPLETE]
        )
        cycle.status = CycleStatus.COMPLETED
        cycle.completed_at = _now_iso()

    except Exception as e:
        cycle.status = CycleStatus.ERROR
        cycle.error = str(e)
        cycle.completed_at = _now_iso()

    return cycle


async def run_pipeline_async(
    problem: str,
    context: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None,
    max_cycles: int = 3,
    requested_totems: Optional[List[str]] = None,
    enable_think_tanks: bool = False,
    problem_complexity: str = "moderate",
) -> str:
    """
    Fire-and-forget pipeline execution.
    Returns cycle_id immediately; pipeline runs in background.
    """
    cycle_id = _generate_cycle_id()
    cycle = PipelineCycle(
        cycle_id=cycle_id,
        problem=problem,
        context=context or {},
        max_cycles=max_cycles,
        status=CycleStatus.RUNNING,
    )
    _cycle_store[cycle_id] = cycle

    async def _run():
        # Run the pipeline and update the stored cycle in place
        result = await run_pipeline(
            problem=problem,
            context=context,
            config=config,
            max_cycles=max_cycles,
            requested_totems=requested_totems,
            enable_think_tanks=enable_think_tanks,
            problem_complexity=problem_complexity,
        )
        # Copy results into the pre-registered cycle
        cycle.status = result.status
        cycle.totem_results = result.totem_results
        cycle.totem_progress = result.totem_progress
        cycle.synthesis = result.synthesis
        cycle.final_output = result.final_output
        cycle.completed_at = result.completed_at
        cycle.error = result.error
        cycle.cycle_number = result.cycle_number

    asyncio.create_task(_run())
    return cycle_id
