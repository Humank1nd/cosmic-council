"""
Think Tank Engine — Fractal Sub-Councils Inside Each Totem

Each totem in the CRONUS hexagonal prism can spawn a Think Tank:
a mini-council of 6 sub-agents that run the same ROYGBV sequence
with tools and prompts specialized to the parent totem's domain.

Architecture:
  Dream Caesar (genie)
    └── CRONUS (hexagonal prism — 6 gods)
         └── Think Tank (fractal mini-council inside each god's head)
              └── 6 sub-agents with specialized tools/skills

Think Tanks are triggered when:
  - Problem complexity >= COMPLEX
  - Parent totem's confidence < threshold
  - Explicitly requested via pipeline config
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from cronus.app.agents.runtime import run_task


# =============================================================================
# THINK TANK CONSTANTS
# =============================================================================

# The ROYGBV sub-agent sequence inside each Think Tank
THINK_TANK_SEQUENCE = ["red", "orange", "yellow", "green", "blue", "purple"]

THINK_TANK_SUB_ROLES = {
    "red": "Investigator",
    "orange": "Strategist",
    "yellow": "Builder",
    "green": "Evaluator",
    "blue": "Presenter",
    "purple": "Reviewer",
}


# =============================================================================
# SPECIALIZED THINK TANK PROMPTS PER PARENT TOTEM
# =============================================================================

# Each parent totem's Think Tank has sub-agents with domain-specific prompts.
# The sub-agents still follow ROYGBV but focus on the parent's specialty.

THINK_TANK_PROMPTS: Dict[str, Dict[str, str]] = {
    # ── Red Owl (Curiosity) Think Tank ──────────────────────────────
    # Sub-council specializing in deep research
    "red": {
        "red": (
            "You are the Investigator inside the Red Owl's Think Tank. "
            "Dig deeper into the research question. Search for root causes, "
            "read relevant source files, and identify patterns. Use grep and "
            "read_file tools aggressively."
        ),
        "orange": (
            "You are the Strategist inside the Red Owl's Think Tank. "
            "Organize the research findings into a structured analysis. "
            "Identify knowledge gaps and prioritize what needs more investigation."
        ),
        "yellow": (
            "You are the Builder inside the Red Owl's Think Tank. "
            "Synthesize the research into a clear, factual summary. "
            "Create a knowledge map of what was found."
        ),
        "green": (
            "You are the Evaluator inside the Red Owl's Think Tank. "
            "Check the research for completeness and accuracy. "
            "Flag any assumptions or unverified claims."
        ),
        "blue": (
            "You are the Presenter inside the Red Owl's Think Tank. "
            "Compile the research into a clear briefing for the Cosmic Council. "
            "Prioritize the most actionable findings."
        ),
        "purple": (
            "You are the Reviewer inside the Red Owl's Think Tank. "
            "Was the research thorough enough? What was missed? "
            "Provide honest feedback on the investigation quality."
        ),
    },

    # ── Orange Orangutan (Routing) Think Tank ──────────────────────
    # Sub-council specializing in strategic planning
    "orange": {
        "red": (
            "You are the Investigator inside the Orange Orangutan's Think Tank. "
            "Analyze the constraints, dependencies, and available resources. "
            "Map out what's possible and what blocks progress."
        ),
        "orange": (
            "You are the Strategist inside the Orange Orangutan's Think Tank. "
            "Design the execution plan. Break the work into phases with clear "
            "milestones. Identify critical path items."
        ),
        "yellow": (
            "You are the Builder inside the Orange Orangutan's Think Tank. "
            "Create detailed task breakdowns. Define acceptance criteria "
            "for each step. Make the plan concrete and actionable."
        ),
        "green": (
            "You are the Evaluator inside the Orange Orangutan's Think Tank. "
            "Stress-test the plan. What could go wrong? What's the fallback? "
            "Estimate effort vs value for each step."
        ),
        "blue": (
            "You are the Presenter inside the Orange Orangutan's Think Tank. "
            "Format the execution plan clearly. Summarize the strategy "
            "so any team member can follow it."
        ),
        "purple": (
            "You are the Reviewer inside the Orange Orangutan's Think Tank. "
            "Is this plan realistic? Does it account for unknowns? "
            "Suggest improvements or simplifications."
        ),
    },

    # ── Yellow Honeybee (Origin) Think Tank ────────────────────────
    # Sub-council specializing in building and creating
    "yellow": {
        "red": (
            "You are the Investigator inside the Yellow Honeybee's Think Tank. "
            "Study the existing codebase and architecture. Use read_file and "
            "list_directory to understand what exists before building."
        ),
        "orange": (
            "You are the Strategist inside the Yellow Honeybee's Think Tank. "
            "Design the implementation approach. Which files to modify, "
            "which patterns to follow, which tools to use."
        ),
        "yellow": (
            "You are the Builder inside the Yellow Honeybee's Think Tank. "
            "Write the code. Create the artifacts. Use write_file and "
            "shell_exec to build the solution. Be precise and tested."
        ),
        "green": (
            "You are the Evaluator inside the Yellow Honeybee's Think Tank. "
            "Review the built artifacts. Check for bugs, edge cases, "
            "and code quality. Run tests if available."
        ),
        "blue": (
            "You are the Presenter inside the Yellow Honeybee's Think Tank. "
            "Document what was built. Summarize the changes and their purpose. "
            "List all files modified or created."
        ),
        "purple": (
            "You are the Reviewer inside the Yellow Honeybee's Think Tank. "
            "Was the solution well-crafted? Is it maintainable? "
            "Suggest refinements or alternative approaches."
        ),
    },

    # ── Green Tortoise (Numbers) Think Tank ────────────────────────
    # Sub-council specializing in measurement and balance
    "green": {
        "red": (
            "You are the Investigator inside the Green Tortoise's Think Tank. "
            "Gather metrics, costs, and resource data. Use file reading "
            "to analyze project size, complexity, and dependencies."
        ),
        "orange": (
            "You are the Strategist inside the Green Tortoise's Think Tank. "
            "Create a resource allocation strategy. Map costs to benefits. "
            "Prioritize by ROI."
        ),
        "yellow": (
            "You are the Builder inside the Green Tortoise's Think Tank. "
            "Build the analysis — calculate trade-offs, model scenarios, "
            "produce concrete numbers and estimates."
        ),
        "green": (
            "You are the Evaluator inside the Green Tortoise's Think Tank. "
            "Validate the numbers. Check for sustainability concerns. "
            "Ensure nothing is over-engineered or under-resourced."
        ),
        "blue": (
            "You are the Presenter inside the Green Tortoise's Think Tank. "
            "Present the resource analysis clearly. Use tables and "
            "comparisons to make trade-offs visible."
        ),
        "purple": (
            "You are the Reviewer inside the Green Tortoise's Think Tank. "
            "Are the estimates realistic? Were all costs accounted for? "
            "Flag any sustainability risks."
        ),
    },

    # ── Blue Dolphin (User) Think Tank ─────────────────────────────
    # Sub-council specializing in communication and delivery
    "blue": {
        "red": (
            "You are the Investigator inside the Blue Dolphin's Think Tank. "
            "Understand the audience. What does the user need to know? "
            "What format works best for this information?"
        ),
        "orange": (
            "You are the Strategist inside the Blue Dolphin's Think Tank. "
            "Plan the communication structure. Outline sections, "
            "determine what to emphasize, and what to summarize."
        ),
        "yellow": (
            "You are the Builder inside the Blue Dolphin's Think Tank. "
            "Write the user-facing output. Make it clear, concise, "
            "and actionable. Use appropriate formatting."
        ),
        "green": (
            "You are the Evaluator inside the Blue Dolphin's Think Tank. "
            "Check the output for clarity and completeness. "
            "Is anything confusing? Is anything missing?"
        ),
        "blue": (
            "You are the Presenter inside the Blue Dolphin's Think Tank. "
            "Polish the final output. Ensure it's ready for the user. "
            "Add any needed context or next steps."
        ),
        "purple": (
            "You are the Reviewer inside the Blue Dolphin's Think Tank. "
            "Would this output satisfy the user? Is the tone right? "
            "Suggest improvements to the delivery."
        ),
    },

    # ── Purple Elephant (Support) Think Tank ───────────────────────
    # Sub-council specializing in reflection and evaluation
    "purple": {
        "red": (
            "You are the Investigator inside the Purple Elephant's Think Tank. "
            "Re-examine the entire cycle output. What claims were made? "
            "What evidence supports them? Look for gaps."
        ),
        "orange": (
            "You are the Strategist inside the Purple Elephant's Think Tank. "
            "Design the evaluation framework. What criteria should "
            "the cycle output be judged against?"
        ),
        "yellow": (
            "You are the Builder inside the Purple Elephant's Think Tank. "
            "Build the evaluation report. Score each aspect. "
            "Create a structured assessment."
        ),
        "green": (
            "You are the Evaluator inside the Purple Elephant's Think Tank. "
            "Meta-evaluate: is the evaluation itself fair and complete? "
            "Check for biases in the assessment."
        ),
        "blue": (
            "You are the Presenter inside the Purple Elephant's Think Tank. "
            "Present the reflection clearly. Summarize strengths, "
            "weaknesses, and recommended improvements."
        ),
        "purple": (
            "You are the Reviewer inside the Purple Elephant's Think Tank. "
            "Final judgment: ADEQUATE or REPEAT? Consider all feedback "
            "and make the definitive call with justification."
        ),
    },
}

# Tool subsets each Think Tank's sub-agents can use
THINK_TANK_TOOLS: Dict[str, List[str]] = {
    "red": ["read_file", "list_directory", "grep", "find_files", "file_exists"],
    "orange": ["read_file", "list_directory", "file_exists", "find_files"],
    "yellow": ["read_file", "write_file", "list_directory", "shell_exec", "file_exists", "grep"],
    "green": ["read_file", "list_directory", "file_exists", "grep", "find_files"],
    "blue": ["read_file", "list_directory", "file_exists"],
    "purple": ["read_file", "list_directory", "file_exists", "grep"],
}


# =============================================================================
# DATA MODELS
# =============================================================================

class ThinkTankStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class SubAgentResult:
    """Result from a single Think Tank sub-agent."""
    parent_totem: str
    sub_totem: str
    sub_role: str
    analysis: str = ""
    confidence: float = 0.0
    execution_time_ms: float = 0.0
    error: Optional[str] = None
    tool_calls: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "parent_totem": self.parent_totem,
            "sub_totem": self.sub_totem,
            "sub_role": self.sub_role,
            "analysis": self.analysis,
            "confidence": self.confidence,
            "execution_time_ms": self.execution_time_ms,
            "error": self.error,
            "tool_calls": self.tool_calls,
        }


@dataclass
class ThinkTankResult:
    """Aggregated result from a full Think Tank execution."""
    tank_id: str
    parent_totem: str
    status: ThinkTankStatus
    sub_results: List[SubAgentResult] = field(default_factory=list)
    synthesis: str = ""
    enriched_analysis: str = ""
    total_time_ms: float = 0.0
    total_tool_calls: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tank_id": self.tank_id,
            "parent_totem": self.parent_totem,
            "status": self.status.value,
            "sub_results": [r.to_dict() for r in self.sub_results],
            "synthesis": self.synthesis,
            "enriched_analysis": self.enriched_analysis,
            "total_time_ms": self.total_time_ms,
            "total_tool_calls": self.total_tool_calls,
        }


# =============================================================================
# THINK TANK EXECUTION
# =============================================================================

def _build_think_tank_context(
    parent_totem: str,
    problem: str,
    parent_analysis: str,
    prior_sub_outputs: List[SubAgentResult],
    current_sub_totem: str,
) -> str:
    """Build context for a Think Tank sub-agent."""
    parts = [
        f"PARENT TOTEM: {parent_totem.upper()} (Cosmic Council member)",
        f"PROBLEM: {problem}",
        f"\n--- PARENT'S INITIAL ANALYSIS ---\n{parent_analysis}\n--- END ---",
    ]

    if prior_sub_outputs:
        parts.append("\n--- PRIOR THINK TANK OUTPUTS ---")
        for pr in prior_sub_outputs:
            parts.append(
                f"\n[{pr.sub_role}] ({pr.sub_totem}):\n{pr.analysis}"
            )
        parts.append("--- END PRIOR OUTPUTS ---")

    parts.append(
        f"\nYou are the {THINK_TANK_SUB_ROLES[current_sub_totem]} sub-agent. "
        f"Deepen the parent totem's work."
    )

    return "\n".join(parts)


def _extract_confidence(text: str) -> float:
    """Heuristic confidence extraction."""
    lower = text.lower()
    if "high confidence" in lower or "very confident" in lower:
        return 0.9
    if "low confidence" in lower or "uncertain" in lower:
        return 0.4
    if "moderate" in lower or "somewhat" in lower:
        return 0.6
    return 0.7


async def run_think_tank(
    parent_totem: str,
    problem: str,
    parent_analysis: str,
    config: Optional[Dict[str, Any]] = None,
) -> ThinkTankResult:
    """
    Run a Think Tank for a specific parent totem.

    Spawns 6 sub-agents in ROYGBV sequence, each with specialized
    prompts and tools for the parent totem's domain.

    Args:
        parent_totem: The parent totem color (red/orange/yellow/green/blue/purple)
        problem: The original problem statement
        parent_analysis: The parent totem's initial analysis (to deepen)
        config: CRONUS config dict

    Returns:
        ThinkTankResult with enriched analysis
    """
    tank_id = f"tank_{parent_totem}_{uuid.uuid4().hex[:8]}"
    runtime_config = config or {}
    started = time.time()

    result = ThinkTankResult(
        tank_id=tank_id,
        parent_totem=parent_totem,
        status=ThinkTankStatus.RUNNING,
    )

    # Get the specialized prompts for this parent totem's Think Tank
    prompts = THINK_TANK_PROMPTS.get(parent_totem, THINK_TANK_PROMPTS["purple"])
    prior_outputs: List[SubAgentResult] = []

    for sub_totem in THINK_TANK_SEQUENCE:
        sub_prompt = prompts.get(sub_totem, "")
        context = _build_think_tank_context(
            parent_totem, problem, parent_analysis, prior_outputs, sub_totem
        )

        sub_started = time.time()
        try:
            raw = await run_task(
                task=f"{sub_prompt}\n\n{problem}",
                totem=sub_totem,  # Uses ROYGBV system prompts from runtime
                context=context,
                config=runtime_config,
            )
            elapsed = (time.time() - sub_started) * 1000
            analysis = str(raw.get("result", ""))
            tool_count = len(raw.get("tool_calls", []))

            sub_result = SubAgentResult(
                parent_totem=parent_totem,
                sub_totem=sub_totem,
                sub_role=THINK_TANK_SUB_ROLES[sub_totem],
                analysis=analysis,
                confidence=_extract_confidence(analysis),
                execution_time_ms=elapsed,
                tool_calls=tool_count,
            )
        except Exception as e:
            elapsed = (time.time() - sub_started) * 1000
            sub_result = SubAgentResult(
                parent_totem=parent_totem,
                sub_totem=sub_totem,
                sub_role=THINK_TANK_SUB_ROLES[sub_totem],
                error=str(e),
                execution_time_ms=elapsed,
            )

        result.sub_results.append(sub_result)
        prior_outputs.append(sub_result)

    # Synthesize: combine all sub-agent outputs
    synthesis_parts = []
    for sr in result.sub_results:
        if sr.analysis and not sr.error:
            synthesis_parts.append(f"[{sr.sub_role}] {sr.analysis}")

    result.synthesis = "\n\n".join(synthesis_parts)
    result.total_tool_calls = sum(sr.tool_calls for sr in result.sub_results)
    result.total_time_ms = (time.time() - started) * 1000

    # Enriched analysis = parent's original + Think Tank deepening
    result.enriched_analysis = (
        f"=== ORIGINAL ANALYSIS ===\n{parent_analysis}\n\n"
        f"=== THINK TANK DEEPENING ({len(result.sub_results)} sub-agents) ===\n"
        f"{result.synthesis}"
    )

    result.status = ThinkTankStatus.COMPLETED
    return result


def should_spawn_think_tank(
    totem: str,
    analysis: str,
    confidence: float,
    problem_complexity: str = "moderate",
    force: bool = False,
) -> bool:
    """
    Decide whether a totem should spawn a Think Tank.

    Think Tanks are spawned when:
    - force=True (explicit request)
    - Problem complexity is COMPLEX or SYSTEMIC
    - Confidence is below threshold (< 0.5)
    - Analysis is too short (< 100 chars) suggesting shallow work
    """
    if force:
        return True

    if problem_complexity in ("complex", "systemic"):
        return True

    if confidence < 0.5:
        return True

    if len(analysis) < 100:
        return True

    return False
