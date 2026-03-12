"""
Dream Caesar CRONUS - FastAPI Bridge

Curiosity · Routing · Origin · Numbers · User · Support

The hands of Dream Caesar, connecting the Next.js frontend
to the CRONUS agent execution engine.

This API serves as the bridge between the Cosmic Council
(philosophy/structure) and the actual execution layer.
"""

import asyncio
import os
import sys
from contextlib import asynccontextmanager
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Any

import toml
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Setup paths for Dream-Caesar integration
CRONUS_ROOT = Path(__file__).resolve().parents[1]  # cronus folder
DREAM_CAESAR_SRC = CRONUS_ROOT.parent  # D:\dream-caesar\src
if str(CRONUS_ROOT) not in sys.path:
    sys.path.insert(0, str(CRONUS_ROOT))
if str(DREAM_CAESAR_SRC) not in sys.path:
    sys.path.insert(0, str(DREAM_CAESAR_SRC))

from cronus.app.agents.runtime import run_task
from cronus.app.agents.pipeline import (
    run_pipeline,
    run_pipeline_async,
    get_cycle,
    TOTEM_LETTER,
    TOTEM_NAME,
    CRONUS_SEQUENCE,
)
from cronus.app.tools import TOOL_HANDLERS
from cronus.app.council import CouncilMode, FractalDepth
from cronus.app.council.cronus_fractal_system import CronusFractalSystem, CouncilResult
ENV_FILE = os.getenv("CRONUS_ENV_FILE") or str(CRONUS_ROOT / ".env.local")
if Path(ENV_FILE).exists():
    load_dotenv(ENV_FILE)

# Load configuration
CONFIG_PATH = Path(__file__).parent.parent / "config" / "config.toml"
config = toml.load(CONFIG_PATH) if CONFIG_PATH.exists() else {}

# ===========================================================================
# LIFESPAN - Startup/shutdown
# ===========================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan."""
    print("=" * 60)
    print("CRONUS API - STARTING")
    print("=" * 60 + "\n")
    yield
    print("\nCRONUS API shutting down...")
    print("Goodbye.\n")

# ============================================================================
# MODELS
# ============================================================================

class TotemId(str, Enum):
    RED = "red"
    ORANGE = "orange"
    YELLOW = "yellow"
    GREEN = "green"
    BLUE = "blue"
    PURPLE = "purple"


class TaskRequest(BaseModel):
    """A task to be executed by the Cronus system"""
    task: str = Field(..., description="The task description")
    totem: Optional[TotemId] = Field(None, description="Target totem/agent type")
    context: Optional[str] = Field(None, description="Additional context")
    priority: Optional[int] = Field(1, ge=1, le=5, description="Priority 1-5")
    session_id: Optional[str] = Field("default", description="Session identifier")


class TaskResult(BaseModel):
    """Result of a task execution"""
    success: bool
    result: Any
    agent_used: str
    totem: str
    execution_time_ms: float
    steps_taken: List[str]
    error: Optional[str] = None


class AgentFlowRequest(BaseModel):
    """Request for a multi-agent flow"""
    flow_name: str
    tasks: List[TaskRequest]
    parallel: bool = False


class AgentFlowResult(BaseModel):
    """Result of a multi-agent flow"""
    success: bool
    results: List[TaskResult]
    total_time_ms: float
    agents_involved: List[str]


class BrowseRequest(BaseModel):
    """Request for browser automation"""
    url: str
    action: str = Field("read", description="Action: read, click, fill, screenshot")
    selector: Optional[str] = None
    value: Optional[str] = None


class BrowseResult(BaseModel):
    """Result of browser automation"""
    success: bool
    content: Optional[str] = None
    screenshot_url: Optional[str] = None
    error: Optional[str] = None


class ToolRequest(BaseModel):
    """Request to use an MCP tool"""
    tool_name: str
    parameters: Dict[str, Any]


class ToolResult(BaseModel):
    """Result of tool execution"""
    success: bool
    result: Any
    tool_used: str
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    agents_available: List[str]
    mcp_enabled: bool
    a2a_enabled: bool


class CouncilRequest(BaseModel):
    """Request for 108-cycle Cosmic Council deliberation."""
    objective: str = Field(..., description="The objective/problem for the council")
    mode: str = Field("simplified", description="simplified (6 calls), full_108 (108 calls), or adaptive")
    context: Optional[str] = Field(None, description="Additional context for deliberation")
    depth: str = Field("nano", description="Fractal depth: macro, micro, nano, pico, femto, atto, zepto, yocto, ronto, quecto")


class CouncilResponse(BaseModel):
    """Result of Cosmic Council deliberation."""
    success: bool
    objective: str
    mode: str
    enterprises_consulted: List[str]
    total_calls: int
    execution_time_ms: float
    final_synthesis: str
    enterprise_outputs: Dict[str, Any]
    confidence: float
    error: Optional[str] = None

    # Sahasrara (Crown Chakra) meta-analysis
    sahasrara_active: bool = False
    meta_analysis: Optional[Dict[str, Any]] = None
    optimizations: List[str] = []
    refinement_suggestions: List[str] = []
    harmonization_level: str = "balanced"
    evolution_score: float = 0.0


class PerpetualCycleRequest(BaseModel):
    """Request for perpetual evolution cycles."""
    objective: str
    iterations: int = 3
    context: Optional[str] = None


class PerpetualCycleResponse(BaseModel):
    """Response from perpetual evolution cycles."""
    success: bool
    iterations_completed: int
    final_evolution_score: float
    final_harmonization: str
    final_synthesis: str
    evolution_trend: str
    cycle_summaries: List[Dict[str, Any]]


# ============================================================================
# APP SETUP
# ============================================================================

app = FastAPI(
    title="Dream Caesar CRONUS",
    description="Curiosity · Routing · Origin · Numbers · User · Support — the hands of the Cosmic Council",
    version="0.2.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.get("api", {}).get("cors_origins", ["http://localhost:3000"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include telemetry router for Cosmic Console
# app.include_router(telemetry_router)  # Depends on genesis / legacy external repo


# ============================================================================  
# AGENT IMPLEMENTATIONS
# ============================================================================  

def _resolve_agent_used(totem: TotemId) -> str:
    for agent_id, agent_config in config.get("agents", {}).items():
        if agent_config.get("totem") == totem.value:
            return agent_id
    return f"{totem.value}-agent"


async def execute_task_with_runtime(task: TaskRequest, totem: TotemId) -> TaskResult:
    """Execute a task via the configured runtime."""
    runtime_result = await run_task(task.task, totem.value, task.context, config)
    error_message = runtime_result.get("error")
    if runtime_result.get("provider") == "unconfigured":
        error_message = runtime_result.get("result")
    return TaskResult(
        success=error_message is None,
        result=runtime_result.get("result"),
        agent_used=_resolve_agent_used(totem),
        totem=totem.value,
        execution_time_ms=runtime_result.get("elapsed_ms", 0.0),
        steps_taken=runtime_result.get("steps", []),
        error=error_message,
    )


async def execute_research_task(task: TaskRequest) -> TaskResult:
    """Research Agent - Red Owl"""
    return await execute_task_with_runtime(task, TotemId.RED)


async def execute_executive_task(task: TaskRequest) -> TaskResult:
    """Executive Agent - Orange Orangutan"""
    return await execute_task_with_runtime(task, TotemId.ORANGE)


async def execute_creative_task(task: TaskRequest) -> TaskResult:
    """Creative Agent - Yellow Bee"""
    return await execute_task_with_runtime(task, TotemId.YELLOW)


async def execute_temporal_task(task: TaskRequest) -> TaskResult:
    """Temporal Agent - Green Tortoise"""
    return await execute_task_with_runtime(task, TotemId.GREEN)


async def execute_comms_task(task: TaskRequest) -> TaskResult:
    """Communications Agent - Blue Dolphin"""
    return await execute_task_with_runtime(task, TotemId.BLUE)


async def execute_empathy_task(task: TaskRequest) -> TaskResult:
    """Empathy Agent - Purple Elephant"""
    return await execute_task_with_runtime(task, TotemId.PURPLE)


# Agent router
AGENT_EXECUTORS = {
    TotemId.RED: execute_research_task,
    TotemId.ORANGE: execute_executive_task,
    TotemId.YELLOW: execute_creative_task,
    TotemId.GREEN: execute_temporal_task,
    TotemId.BLUE: execute_comms_task,
    TotemId.PURPLE: execute_empathy_task,
}


# ============================================================================
# ROUTES
# ============================================================================

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check and API info"""
    return HealthResponse(
        status="operational",
        version="0.2.0",
        agents_available=list(config.get("agents", {}).keys()),
        mcp_enabled=config.get("mcp", {}).get("enabled", False),
        a2a_enabled=config.get("a2a", {}).get("enabled", False),
    )


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return await root()


@app.post("/execute", response_model=TaskResult)
async def execute_task(request: TaskRequest):
    """
    Execute a task through the appropriate Cosmic Council agent.

    If totem is not specified, the system will auto-route based on task analysis.
    """
    try:
        totem = request.totem or TotemId.PURPLE
        executor = AGENT_EXECUTORS.get(totem, execute_empathy_task)
        return await executor(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/flow", response_model=AgentFlowResult)
async def run_flow(request: AgentFlowRequest):
    """
    Run a multi-agent flow (Orange Orangutan orchestration).

    Executes multiple tasks, optionally in parallel.
    """
    import asyncio
    import time

    start_time = time.time()
    results = []
    agents_involved = set()

    try:
        if request.parallel:
            # Execute all tasks in parallel
            tasks = [execute_task(task) for task in request.tasks]
            results = await asyncio.gather(*tasks)
        else:
            # Execute sequentially
            for task in request.tasks:
                result = await execute_task(task)
                results.append(result)

        for r in results:
            agents_involved.add(r.agent_used)

        total_time = (time.time() - start_time) * 1000

        return AgentFlowResult(
            success=all(r.success for r in results),
            results=results,
            total_time_ms=total_time,
            agents_involved=list(agents_involved),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/browse", response_model=BrowseResult)
async def browse(request: BrowseRequest):
    """
    Computer vision browsing (Red Owl research capability).

    Uses mss screen capture + vision LLM analysis instead of Playwright.
    Actions:
      - screenshot: capture current screen and optionally analyze
      - read: capture screen + analyze what's visible at the URL context
    """
    from cronus.app.tools.vision import handle_screenshot, handle_vision_analyze

    try:
        if request.action == "screenshot":
            result = handle_screenshot({})
            if result.get("error"):
                return BrowseResult(success=False, error=result["error"])
            return BrowseResult(
                success=True,
                content=f"Screenshot captured ({result.get('width')}x{result.get('height')})",
                screenshot_url=result.get("save_path"),
            )
        else:
            # Default: capture screen and analyze with vision model
            prompt = request.value or f"Describe what is currently visible on screen. Context: browsing {request.url}"
            result = handle_vision_analyze({"prompt": prompt})
            if result.get("error"):
                return BrowseResult(success=False, error=result["error"])
            return BrowseResult(
                success=True,
                content=result.get("analysis", ""),
                screenshot_url=None,
            )
    except Exception as e:
        return BrowseResult(success=False, error=str(e))


@app.post("/tool", response_model=ToolResult)
async def use_tool(request: ToolRequest):
    """
    Execute an MCP tool (Yellow Bee building capability).

    Interfaces with the Model Context Protocol for tool execution.
    """
    handler = TOOL_HANDLERS.get(request.tool_name)
    if not handler:
        return ToolResult(
            success=False,
            result=None,
            tool_used=request.tool_name,
            error=f"Unknown tool: {request.tool_name}",
        )
    try:
        if asyncio.iscoroutinefunction(handler):
            result = await handler(request.parameters)
        else:
            result = await asyncio.to_thread(handler, request.parameters)
        return ToolResult(
            success=True,
            result=result,
            tool_used=request.tool_name,
            error=None,
        )
    except Exception as e:
        return ToolResult(
            success=False,
            result=None,
            tool_used=request.tool_name,
            error=str(e),
        )


@app.get("/agents")
async def list_agents():
    """List all available agents and their capabilities"""
    return {
        "agents": {
            agent_id: {
                "name": agent_config.get("name"),
                "totem": agent_config.get("totem"),
                "capabilities": agent_config.get("capabilities", []),
                "description": agent_config.get("description"),
            }
            for agent_id, agent_config in config.get("agents", {}).items()
        }
    }


@app.get("/tools")
async def list_tools():
    """List all available CRONUS tools"""
    from cronus.app.tools import TOOL_HANDLERS, TOOL_SCHEMAS
    tools = []
    for schema in TOOL_SCHEMAS:
        fn = schema.get("function", {})
        tools.append({"name": fn.get("name"), "description": fn.get("description", "")})
    # Include any handlers without schemas
    schema_names = {s.get("function", {}).get("name") for s in TOOL_SCHEMAS}
    for name in TOOL_HANDLERS:
        if name not in schema_names:
            tools.append({"name": name, "description": ""})
    return {"tools": tools, "count": len(tools)}


# ============================================================================
# COSMIC COUNCIL ENDPOINTS (Dream Caesar ↔ CRONUS fusion)
# ============================================================================

# -- Models for the council endpoints --

class CosmicSolveRequest(BaseModel):
    """Request to run the C→R→O→N→U→S pipeline."""
    problem: str = Field(..., description="The problem to deliberate on")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    max_cycles: int = Field(3, ge=1, le=10, description="Max deliberation cycles")
    agents: Optional[List[str]] = Field(None, description="Subset of totems to use")
    enable_think_tanks: bool = Field(False, description="Enable fractal Think Tanks inside each totem")
    problem_complexity: str = Field("moderate", description="simple|moderate|complex|systemic")


@app.get("/agents/cosmic-totems")
async def cosmic_totems():
    """
    Return the 6 CRONUS totems with their identity.
    This is the endpoint Dream Caesar's BackendClient expects.
    """
    agents_config = config.get("agents", {})
    totems = []
    for totem in CRONUS_SEQUENCE:
        letter = TOTEM_LETTER[totem]
        name = TOTEM_NAME[totem]
        # Find the agent config for this totem
        agent_cfg = next(
            (cfg for cfg in agents_config.values() if cfg.get("totem") == totem),
            {},
        )
        totems.append({
            "id": totem,
            "letter": letter,
            "name": f"{name} ({agent_cfg.get('spirit', totem.title())})",
            "color": totem,
            "specialty": agent_cfg.get("description", ""),
        })
    return {"agents": totems}


@app.post("/agents/solve")
async def cosmic_solve(request: CosmicSolveRequest):
    """
    Run the full C→R→O→N→U→S pipeline.

    For quick problems, runs synchronously and returns completed result.
    For complex problems (max_cycles > 1), kicks off async and returns cycle_id.
    """
    try:
        if request.max_cycles <= 1:
            # Synchronous: run and return
            cycle = await run_pipeline(
                problem=request.problem,
                context=request.context,
                config=config,
                max_cycles=1,
                requested_totems=request.agents,
                enable_think_tanks=request.enable_think_tanks,
                problem_complexity=request.problem_complexity,
            )
            return cycle.to_response()
        else:
            # Async: fire-and-forget, return cycle_id for polling
            cycle_id = await run_pipeline_async(
                problem=request.problem,
                context=request.context,
                config=config,
                max_cycles=request.max_cycles,
                requested_totems=request.agents,
                enable_think_tanks=request.enable_think_tanks,
                problem_complexity=request.problem_complexity,
            )
            return {
                "cycle_id": cycle_id,
                "status": "running",
                "responses": [],
                "totems": [
                    {"id": t, "sequence": i, "status": "queued", "output": None, "error": None}
                    for i, t in enumerate(CRONUS_SEQUENCE)
                ],
                "synthesis": None,
                "final_output": None,
                "created_at": None,
                "completed_at": None,
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents/cycles/{cycle_id}")
async def cosmic_cycle_status(cycle_id: str):
    """
    Get the status of a deliberation cycle.
    Dream Caesar's BackendClient polls this endpoint.
    """
    cycle = get_cycle(cycle_id)
    if not cycle:
        raise HTTPException(status_code=404, detail=f"Cycle {cycle_id} not found")
    return cycle.to_response()


# ============================================================================
# THINK TANK ENDPOINTS (Fractal sub-councils)
# ============================================================================

class ThinkTankRequest(BaseModel):
    """Request to run a Think Tank for a specific totem."""
    parent_totem: str = Field(..., description="Parent totem color (red/orange/yellow/green/blue/purple)")
    problem: str = Field(..., description="The problem statement")
    parent_analysis: str = Field(..., description="The parent totem's initial analysis to deepen")


@app.post("/agents/think-tank")
async def run_think_tank_endpoint(request: ThinkTankRequest):
    """
    Run a fractal Think Tank for a specific totem.

    Spawns 6 sub-agents (ROYGBV) inside the totem's mind,
    each with specialized prompts and tools for that totem's domain.
    Returns enriched analysis from the mini-council.
    """
    from cronus.app.agents.think_tank import run_think_tank as _run_think_tank

    if request.parent_totem not in CRONUS_SEQUENCE:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid totem: {request.parent_totem}. Must be one of {CRONUS_SEQUENCE}",
        )

    try:
        result = await _run_think_tank(
            parent_totem=request.parent_totem,
            problem=request.problem,
            parent_analysis=request.parent_analysis,
            config=config,
        )
        return result.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 108-CYCLE COSMIC COUNCIL (LOST Numbers: 4+8+15+16+23+42 = 108)
# ============================================================================

# Singleton fractal system instance
_council_system: Optional[CronusFractalSystem] = None


def get_council_system() -> CronusFractalSystem:
    """Get or create the council system singleton."""
    global _council_system
    if _council_system is None:
        _council_system = CronusFractalSystem(config)
    return _council_system


@app.post("/council", response_model=CouncilResponse)
async def run_council(request: CouncilRequest):
    """
    Run a 108-cycle Cosmic Council deliberation.

    The LOST Numbers (4+8+15+16+23+42 = 108) guide the fractal flow:
    - RED OWL (4): Research & Inquiry - Muladhara/Root
    - ORANGE ORANGUTAN (8): Strategy & Planning - Svadisthana/Sacral
    - YELLOW HONEYBEE (15): Creation & Innovation - Manipura/Solar Plexus
    - GREEN TORTOISE (16): Resource Management - Anahata/Heart
    - BLUE DOLPHIN (23): Communication & Influence - Vishuddha/Throat
    - PURPLE ELEPHANT (42): Reflection & Ethics - Ajna/Third Eye

    Modes:
    - simplified: 6 LLM calls (1 per enterprise)
    - full_108: 108 LLM calls (6 enterprises × 6 squads × 3 passes)
    - adaptive: Auto-select based on complexity
    - hexaclock: 7-stage executive validation (Oracle→Interpreter→Auditor→Alchemist→Auditor→Gatekeeper→Recalibration)
    - ouroboros: Full cosmic integration with Meta-Cyclical, Synthesis, Black Snake, and Reflection
    """
    try:
        # Parse mode
        mode_map = {
            "simplified": CouncilMode.SIMPLIFIED,
            "full_108": CouncilMode.FULL_108,
            "adaptive": CouncilMode.ADAPTIVE,
            "hexaclock": CouncilMode.HEXACLOCK,
            "ouroboros": CouncilMode.OUROBOROS,
        }
        mode = mode_map.get(request.mode.lower(), CouncilMode.SIMPLIFIED)

        # Parse depth
        depth_map = {
            "macro": FractalDepth.MACRO,
            "micro": FractalDepth.MICRO,
            "nano": FractalDepth.NANO,
            "pico": FractalDepth.PICO,
            "femto": FractalDepth.FEMTO,
            "atto": FractalDepth.ATTO,
            "zepto": FractalDepth.ZEPTO,
            "yocto": FractalDepth.YOCTO,
            "ronto": FractalDepth.RONTO,
            "quecto": FractalDepth.QUECTO,
        }
        depth = depth_map.get(request.depth.lower(), FractalDepth.NANO)

        # Run the council
        system = get_council_system()
        result = await system.run_council(
            objective=request.objective,
            mode=mode,
            context=request.context,
            depth=depth,
        )

        return CouncilResponse(
            success=result.success,
            objective=result.objective,
            mode=result.mode.value,
            enterprises_consulted=result.enterprises_consulted,
            total_calls=result.total_calls,
            execution_time_ms=result.execution_time_ms,
            final_synthesis=result.final_synthesis,
            enterprise_outputs=result.enterprise_outputs,
            confidence=result.confidence,
            error=result.error,
            # Sahasrara meta-analysis
            sahasrara_active=result.sahasrara_active,
            meta_analysis=result.meta_analysis,
            optimizations=result.optimizations,
            refinement_suggestions=result.refinement_suggestions,
            harmonization_level=result.harmonization_level,
            evolution_score=result.evolution_score,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/council/stats")
async def council_stats():
    """Get council statistics."""
    system = get_council_system()
    return system.get_statistics()


@app.post("/council/perpetual", response_model=PerpetualCycleResponse)
async def run_perpetual_cycle(request: PerpetualCycleRequest):
    """
    Run perpetual improvement cycles - the Ouroboros pattern.

    Each cycle feeds refinements back to the next, enabling
    continuous evolution toward cosmic alignment. Sahasrara (Crown Chakra)
    observes all cycles and accelerates evolution.

    The cycle flows:
    RED OWL → ORANGE → YELLOW → GREEN → BLUE → PURPLE
                         ↑                        |
                         +--- SAHASRARA ←---------+
                              (observes & refines)
    """
    try:
        system = get_council_system()
        results = await system.run_perpetual_cycle(
            objective=request.objective,
            iterations=min(request.iterations, 10),  # Cap at 10
            context=request.context,
        )

        if not results:
            raise HTTPException(status_code=500, detail="Perpetual cycle failed")

        # Get evolution trend
        trend = system.get_evolution_trend()

        # Build cycle summaries
        summaries = [
            {
                "iteration": i + 1,
                "confidence": r.confidence,
                "evolution_score": r.evolution_score,
                "harmonization": r.harmonization_level,
                "refinements_count": len(r.refinement_suggestions),
            }
            for i, r in enumerate(results)
        ]

        final = results[-1]
        return PerpetualCycleResponse(
            success=final.success,
            iterations_completed=len(results),
            final_evolution_score=final.evolution_score,
            final_harmonization=final.harmonization_level,
            final_synthesis=final.final_synthesis,
            evolution_trend=trend.get("trend", "unknown"),
            cycle_summaries=summaries,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/council/evolution")
async def get_evolution_status():
    """
    Get the evolution status from Sahasrara meta-analysis.

    Returns evolution trend, harmonization history, and
    optimization insights from the Crown Chakra.
    """
    system = get_council_system()
    trend = system.get_evolution_trend()

    return {
        "sahasrara_active": system.sahasrara is not None,
        "sahasrara_activation": system.sahasrara_activation.value,
        "evolution_trend": trend,
        "refinement_queue": system.refinement_queue[-5:],  # Last 5 refinements
        "total_evolution_cycles": len(system.evolution_history),
    }


@app.post("/council/sahasrara/activate")
async def activate_sahasrara(level: str = "analyzing"):
    """
    Activate Sahasrara meta-analysis layer.

    Levels:
    - dormant: No meta-analysis
    - observing: Light observation (default)
    - analyzing: Full meta-analysis with LLM
    - evolving: Perpetual evolution mode
    """
    from cronus.app.council.cronus_fractal_system import SahasraraActivation

    level_map = {
        "dormant": SahasraraActivation.DORMANT,
        "observing": SahasraraActivation.OBSERVING,
        "analyzing": SahasraraActivation.ANALYZING,
        "evolving": SahasraraActivation.EVOLVING,
    }

    activation = level_map.get(level.lower(), SahasraraActivation.OBSERVING)
    system = get_council_system()
    system.set_sahasrara_activation(activation)

    return {
        "success": True,
        "sahasrara_activation": activation.value,
        "message": f"Sahasrara activated at {activation.value} level"
    }


@app.get("/council/deep-integration")
async def get_deep_integration_stats():
    """
    Get deep integration statistics.

    Shows the state of the Ouroboros cycle, Meta-Cyclical Architecture,
    Synthesis Engine, Quantum-Spiritual Coherence, and Black Snake execution.
    """
    system = get_council_system()
    stats = system.get_deep_integration_stats()

    return {
        "success": True,
        **stats,
        "council_modes": ["simplified", "full_108", "hexaclock", "ouroboros"],
        "ouroboros_info": {
            "description": "Full cosmic integration cycle",
            "phases": [
                "white_rabbit_input",
                "roygbv_processing",
                "sahasrara_meta",
                "black_snake_execute",
                "recursion_feedback"
            ],
            "consciousness_levels": [
                "dormant", "awakening", "aware", "expanded",
                "transcendent", "cosmic", "divine"
            ]
        }
    }


# ============================================================================
# COSMIC CANON ENDPOINTS (Full spiritual/quantum/philosophical framework)
# ============================================================================

@app.get("/canon")
async def get_full_canon():
    """
    Get the complete Cosmic Council canon.

    Returns all levels of the spiritual, quantum, and philosophical
    framework including:
    - 6 Totems (ROYGBV) with full profiles
    - 6 Chakras with energy frequencies
    - 6 Quantum concepts
    - 6 Mantras and archetypes
    - LOST Numbers (4+8+15+16+23+42 = 108)
    - 10 Fractal depth levels
    """
    from cronus.app.canon import CosmicCanonBridge
    bridge = CosmicCanonBridge()
    return bridge.to_api_response()


@app.get("/canon/totems")
async def get_all_totems():
    """Get all 6 totems with their complete profiles."""
    from cronus.app.canon import get_full_totem_profile, TOTEM_COLORS
    return {
        "totems": {
            color: get_full_totem_profile(color)
            for color in TOTEM_COLORS
        },
        "order": TOTEM_COLORS,
        "sequence": "ROYGBV (Red -> Orange -> Yellow -> Green -> Blue -> Purple)",
    }


@app.get("/canon/totems/{totem}")
async def get_single_totem(totem: str):
    """Get complete profile for a single totem."""
    from cronus.app.canon import get_full_totem_profile, TOTEM_COLORS
    totem = totem.lower()
    if totem not in TOTEM_COLORS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid totem: {totem}. Must be one of {TOTEM_COLORS}"
        )
    return get_full_totem_profile(totem)


@app.get("/canon/chakras")
async def get_chakras():
    """Get all chakra alignments with energy frequencies."""
    from cronus.app.canon import CHAKRAS
    return {
        "chakras": CHAKRAS,
        "note": "Energy frequencies in Hz aligned with Solfeggio scale",
    }


@app.get("/canon/quantum")
async def get_quantum_concepts():
    """Get all quantum concepts and their applications."""
    from cronus.app.canon import QUANTUM_CONCEPTS
    return {
        "quantum_concepts": QUANTUM_CONCEPTS,
        "note": "Each quantum principle guides the totem's function",
    }


@app.get("/canon/mantras")
async def get_mantras():
    """Get all mantras for each totem."""
    from cronus.app.canon import MANTRAS, TOTEM_NAMES
    return {
        "mantras": {
            color: {
                "totem": TOTEM_NAMES[color],
                "mantra": mantra,
            }
            for color, mantra in MANTRAS.items()
        }
    }


@app.get("/canon/lost-numbers")
async def get_lost_numbers():
    """
    Get the LOST Numbers and their meaning.

    The sacred sequence: 4 + 8 + 15 + 16 + 23 + 42 = 108
    Representing Universal Love, Eternity, and Awakening.
    """
    from cronus.app.canon import LOST_NUMBERS
    return LOST_NUMBERS


@app.get("/canon/fractal-depths")
async def get_fractal_depths():
    """
    Get all 10 fractal depth levels.

    From Macro (10^0) through Quecto (10^-9), representing
    the recursive layers of analysis and insight.
    """
    from cronus.app.canon.cosmic_integration import FRACTAL_DEPTH_INFO, FractalDepth
    return {
        "depths": {
            depth.value: info
            for depth, info in FRACTAL_DEPTH_INFO.items()
        },
        "count": 10,
        "order": [d.value for d in FractalDepth],
    }


@app.get("/canon/prompt/{totem}")
async def get_canon_prompt_endpoint(totem: str, task: str, context: Optional[str] = None):
    """
    Generate a canon-enriched prompt for a totem.

    This endpoint generates prompts that embed the full spiritual,
    quantum, and philosophical framework for maximum alignment.
    """
    from cronus.app.canon import get_canon_prompt, TOTEM_COLORS
    totem = totem.lower()
    if totem not in TOTEM_COLORS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid totem: {totem}. Must be one of {TOTEM_COLORS}"
        )
    prompt = get_canon_prompt(totem, task, context or "")
    return {
        "totem": totem,
        "task": task,
        "prompt": prompt,
    }


# ============================================================================
# PIPELINE ASYNC ENDPOINTS (for OpenClaw atomic integration)
# ============================================================================

class PipelineAsyncRequest(BaseModel):
    """Request to start an async pipeline."""
    problem: str = Field(..., description="The problem to deliberate on")
    max_cycles: int = Field(3, ge=1, le=10, description="Max deliberation cycles")
    enable_think_tanks: bool = Field(False, description="Enable fractal Think Tanks")


@app.post("/agents/pipeline/async")
async def start_pipeline_async(request: PipelineAsyncRequest):
    """
    Start a pipeline asynchronously.
    Returns cycle_id immediately; use GET /agents/pipeline/{cycle_id} to poll.
    """
    try:
        cycle_id = await run_pipeline_async(
            problem=request.problem,
            config=config,
            max_cycles=request.max_cycles,
            enable_think_tanks=request.enable_think_tanks,
        )
        return {
            "cycle_id": cycle_id,
            "status": "running",
            "message": f"Pipeline started. Poll /agents/pipeline/{cycle_id} for status.",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents/pipeline/{cycle_id}")
async def get_pipeline_status(cycle_id: str):
    """Get the status of an async pipeline by cycle_id."""
    cycle = get_cycle(cycle_id)
    if not cycle:
        raise HTTPException(status_code=404, detail=f"Cycle {cycle_id} not found")
    return cycle.to_response()


@app.get("/agents/cycles")
async def list_cycles():
    """List all deliberation cycles (active and completed)."""
    from cronus.app.agents.pipeline import list_cycles as _list_cycles
    cycles = _list_cycles()
    return {
        "cycles": [c.to_response() for c in cycles],
        "count": len(cycles),
    }


# ============================================================================
# TOOLS/CALL ENDPOINT (for VM and other tools via OpenClaw)
# ============================================================================

class ToolCallRequest(BaseModel):
    """Request to call a tool by name."""
    name: str = Field(..., description="Tool name (e.g., cronus_vm_exec)")
    params: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")


@app.post("/tools/call")
async def call_tool(request: ToolCallRequest):
    """
    Call any CRONUS tool by name.
    Used by OpenClaw atomic integration for VM execution and other tools.
    """
    handler = TOOL_HANDLERS.get(request.name)
    if not handler:
        raise HTTPException(status_code=404, detail=f"Tool not found: {request.name}")

    try:
        if asyncio.iscoroutinefunction(handler):
            result = await handler(request.params)
        else:
            result = await asyncio.to_thread(handler, request.params)
        return {
            "success": True,
            "tool": request.name,
            "result": result,
        }
    except Exception as e:
        return {
            "success": False,
            "tool": request.name,
            "error": str(e),
        }


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    host = config.get("api", {}).get("host", "0.0.0.0")
    port = config.get("api", {}).get("port", 8010)

    uvicorn.run(app, host=host, port=port)

