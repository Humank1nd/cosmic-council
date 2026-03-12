"""
CRONUS Routes — Extractable APIRouter

All CRONUS route handlers as an APIRouter that can be included
in any FastAPI app (standalone CRONUS or unified Dream Caesar).

Usage:
    router = create_cronus_router(genesis, config)
    app.include_router(router)
"""

import asyncio
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, HTTPException

from .main import (
    # Models
    TotemId,
    TaskRequest,
    TaskResult,
    AgentFlowRequest,
    AgentFlowResult,
    BrowseRequest,
    BrowseResult,
    ToolRequest,
    ToolResult,
    HealthResponse,
    GenesisStatus,
    GenesisContextResponse,
    CosmicSolveRequest,
    ThinkTankRequest,
    # Helpers
    _resolve_agent_used,
    execute_task_with_runtime,
    AGENT_EXECUTORS,
)

from app.agents.runtime import run_task
from app.agents.pipeline import (
    run_pipeline,
    run_pipeline_async,
    get_cycle,
    TOTEM_LETTER,
    TOTEM_NAME,
    CRONUS_SEQUENCE,
)
from app.tools import TOOL_HANDLERS


def create_cronus_router(genesis_state, cronus_config: dict) -> APIRouter:
    """
    Factory that creates a CRONUS APIRouter bound to the given
    genesis state and config. This allows the same routes to work
    in both standalone CRONUS and the unified Dream Caesar app.
    """
    router = APIRouter(tags=["CRONUS Engine"])
    genesis = genesis_state
    config = cronus_config

    # ================================================================
    # HEALTH & STATUS
    # ================================================================

    @router.get("/", response_model=HealthResponse)
    async def root():
        ctx = genesis.get_context()
        return HealthResponse(
            status="operational" if genesis.operational else "boot_failed",
            version="0.2.0",
            agents_available=list(config.get("agents", {}).keys()),
            mcp_enabled=config.get("mcp", {}).get("enabled", False),
            a2a_enabled=config.get("a2a", {}).get("enabled", False),
            genesis_operational=genesis.operational,
            genesis_identity=ctx.identity_hash if ctx else None,
            genesis_continuity=ctx.continuity_id if ctx else None,
        )

    @router.get("/health", response_model=HealthResponse)
    async def health():
        return await root()

    @router.get("/genesis", response_model=GenesisStatus)
    async def genesis_status():
        if not genesis.boot_result:
            return GenesisStatus(operational=False)
        return GenesisStatus(
            operational=genesis.operational,
            identity=genesis.boot_result.get("identity"),
            continuity_id=genesis.boot_result.get("continuity_id"),
            calibration=genesis.boot_result.get("calibration"),
            boot_time_ms=genesis.boot_result.get("boot_time_ms"),
            tasks=genesis.boot_result.get("tasks"),
            provider=genesis.boot_result.get("provider"),
            model=genesis.boot_result.get("model"),
            capabilities=genesis.boot_result.get("capabilities"),
        )

    @router.get("/genesis/context", response_model=GenesisContextResponse)
    async def genesis_context():
        ctx = genesis.get_context()
        if not ctx:
            return GenesisContextResponse(operational=False)
        return GenesisContextResponse(
            operational=genesis.operational,
            substrate={
                "cpu_count": ctx.cpu_count,
                "memory_total_mb": ctx.memory_total_mb,
                "memory_available_mb": ctx.memory_available_mb,
                "platform": ctx.platform_name,
                "hostname": ctx.hostname,
                "workspace_path": ctx.workspace_path,
                "scratch_path": ctx.scratch_path,
                "storage_total_gb": ctx.storage_total_gb,
                "storage_free_gb": ctx.storage_free_gb,
            },
            invariants={
                "identity_hash": ctx.identity_hash,
                "calibration_hash": ctx.calibration_hash,
                "max_file_size": ctx.max_file_size,
                "max_tool_rounds": ctx.max_tool_rounds,
                "timeout_seconds": ctx.timeout_seconds,
                "max_concurrent": ctx.max_concurrent,
                "permissions": ctx.permissions,
                "allowed_paths": list(ctx.allowed_paths) if ctx.allowed_paths else [],
                "sealed": ctx.invariants_sealed,
            },
            capabilities={
                "tools": list(ctx.tool_handlers.keys()) if ctx.tool_handlers else [],
                "llm_provider": ctx.llm_provider,
                "llm_model": ctx.llm_model,
                "perception_ready": ctx.perception_ready,
                "planning_ready": ctx.planning_ready,
                "execution_ready": ctx.execution_ready,
            },
            boundaries={
                "safety_controller_active": ctx.safety_controller_active,
                "priority_order": ctx.priority_order,
                "sandbox_created": ctx.sandbox_created,
                "watchdog_armed": ctx.watchdog_armed,
                "failsafe_armed": ctx.failsafe_armed,
                "failsafes": ctx.failsafes,
            },
        )

    @router.post("/genesis/reboot", response_model=GenesisStatus)
    async def genesis_reboot():
        nonlocal genesis
        from .main import GenesisState
        genesis = GenesisState()
        genesis._initialized = False
        genesis.__init__()
        result = await genesis.boot()
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=f"Genesis reboot failed: {result.get('error')}")
        return GenesisStatus(
            operational=genesis.operational,
            identity=result.get("identity"),
            continuity_id=result.get("continuity_id"),
            calibration=result.get("calibration"),
            boot_time_ms=result.get("boot_time_ms"),
            tasks=result.get("tasks"),
            provider=result.get("provider"),
            model=result.get("model"),
            capabilities=result.get("capabilities"),
        )

    # ================================================================
    # TASK EXECUTION
    # ================================================================

    @router.post("/execute", response_model=TaskResult)
    async def execute_task(request: TaskRequest):
        try:
            totem = request.totem or TotemId.PURPLE
            executor = AGENT_EXECUTORS.get(totem)
            if executor:
                return await executor(request)
            return await execute_task_with_runtime(request, totem)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/flow", response_model=AgentFlowResult)
    async def run_flow(request: AgentFlowRequest):
        import time
        start_time = time.time()
        results = []
        agents_involved = set()
        try:
            if request.parallel:
                tasks = [execute_task(task) for task in request.tasks]
                results = await asyncio.gather(*tasks)
            else:
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

    # ================================================================
    # BROWSING & TOOLS
    # ================================================================

    @router.post("/browse", response_model=BrowseResult)
    async def browse(request: BrowseRequest):
        from app.tools.vision import handle_screenshot, handle_vision_analyze
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
                prompt = request.value or f"Describe what is currently visible on screen. Context: browsing {request.url}"
                result = handle_vision_analyze({"prompt": prompt})
                if result.get("error"):
                    return BrowseResult(success=False, error=result["error"])
                return BrowseResult(success=True, content=result.get("analysis", ""), screenshot_url=None)
        except Exception as e:
            return BrowseResult(success=False, error=str(e))

    @router.post("/tool", response_model=ToolResult)
    async def use_tool(request: ToolRequest):
        handler = TOOL_HANDLERS.get(request.tool_name)
        if not handler:
            return ToolResult(success=False, result=None, tool_used=request.tool_name, error=f"Unknown tool: {request.tool_name}")
        try:
            if asyncio.iscoroutinefunction(handler):
                result = await handler(request.parameters)
            else:
                result = await asyncio.to_thread(handler, request.parameters)
            return ToolResult(success=True, result=result, tool_used=request.tool_name, error=None)
        except Exception as e:
            return ToolResult(success=False, result=None, tool_used=request.tool_name, error=str(e))

    @router.get("/tools")
    async def list_tools():
        from app.tools import TOOL_HANDLERS, TOOL_SCHEMAS
        tools = []
        for schema in TOOL_SCHEMAS:
            fn = schema.get("function", {})
            tools.append({"name": fn.get("name"), "description": fn.get("description", "")})
        schema_names = {s.get("function", {}).get("name") for s in TOOL_SCHEMAS}
        for name in TOOL_HANDLERS:
            if name not in schema_names:
                tools.append({"name": name, "description": ""})
        return {"tools": tools, "count": len(tools)}

    # ================================================================
    # AGENTS
    # ================================================================

    @router.get("/agents")
    async def list_agents():
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

    @router.get("/agents/cosmic-totems")
    async def cosmic_totems():
        agents_config = config.get("agents", {})
        totems = []
        for totem in CRONUS_SEQUENCE:
            letter = TOTEM_LETTER[totem]
            name = TOTEM_NAME[totem]
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

    @router.post("/agents/solve")
    async def cosmic_solve(request: CosmicSolveRequest):
        try:
            if request.max_cycles <= 1:
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

    @router.get("/agents/cycles/{cycle_id}")
    async def cosmic_cycle_status(cycle_id: str):
        cycle = get_cycle(cycle_id)
        if not cycle:
            raise HTTPException(status_code=404, detail=f"Cycle {cycle_id} not found")
        return cycle.to_response()

    # ================================================================
    # THINK TANKS
    # ================================================================

    @router.post("/agents/think-tank")
    async def run_think_tank_endpoint(request: ThinkTankRequest):
        from app.agents.think_tank import run_think_tank as _run_think_tank
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

    return router
