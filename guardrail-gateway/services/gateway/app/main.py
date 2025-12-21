from fastapi import FastAPI, HTTPException, Query
from .schemas import EvalInput, EvalDecision, SimulationInput, SimulationResult, DecisionExplanation, CycleRunRequest, CycleRunResponse, CycleCompleteRequest
from .policy_engine import engine as policy
from .storage import log_decision, engine
from .autonomous_flow import autonomous_flow
from .explain import explainer
from .caps_cache import budget_caps_cache
from sqlalchemy import text
import uuid
import json
from datetime import datetime, timezone
from typing import Optional

app = FastAPI(title="Guardrail Gateway", version="0.1.0")

@app.post("/v1/evaluate", response_model=EvalDecision)
async def evaluate(payload: EvalInput):
    decision_id = str(uuid.uuid4())
    input_obj = {
        "agent": payload.agent.model_dump(),
        "resource": payload.resource.model_dump(),
        "context": payload.context,
    }
    
    # Determine which policy package to use based on resource service
    policy_package = "guard/access"  # default
    if payload.resource.service == "comms_publish":
        policy_package = "guard/brand"
    elif payload.resource.service == "compute_job":
        policy_package = "guard/budget"
    
    allow, meta = await policy.evaluate(policy_package, input_obj)
    decision = EvalDecision(
        allow=allow, 
        policies=[policy_package], 
        explanation=meta, 
        obligations=meta.get("obligations", []),
        decision_id=decision_id,
        timestamp=datetime.now(timezone.utc)
    )
    
    try:
        log_decision({
            "agent": input_obj["agent"],
            "request_json": input_obj,
            "allow": allow,
            "policy_refs": [policy_package],
            "explanation": decision.explanation,
            "latency_ms": meta.get("latency_ms", 0)
        })
        
        # Handle provenance obligations
        if "log_source_provenance" in meta.get("obligations", []):
            await _handle_provenance_obligation(decision_id, input_obj.get("context", {}))
        
        # Handle budget telemetry obligations
        if "emit_budget_usage" in meta.get("obligations", []):
            await _emit_budget_telemetry(decision_id, input_obj)
            
    except Exception as e:
        print(f"Failed to log decision or handle obligations: {e}")
    return decision

@app.post("/v1/simulate", response_model=SimulationResult)
async def simulate(payload: SimulationInput):
    """
    Enhanced simulation with policy diff capabilities
    """
    input_obj = {
        "agent": payload.agent.model_dump(),
        "resource": payload.resource.model_dump(),
        "context": payload.context,
    }
    
    # Determine policy package
    policy_package = "guard/access"
    if payload.resource.service == "comms_publish":
        policy_package = "guard/brand"
    elif payload.resource.service == "compute_job":
        policy_package = "guard/budget"
    
    result = await policy.simulate_with_diff(
        package=policy_package,
        input_obj=input_obj,
        pretend_policy_version=payload.pretend_policy_version,
        pretend_context_overrides=payload.pretend_context_overrides,
        perturbation=payload.perturbation
    )
    
    return result

@app.get("/v1/policies")
async def list_policies():
    return [{"name": "guard/access"}, {"name": "guard/brand"}, {"name": "guard/budget"}]

@app.get("/v1/explain/{decision_id}", response_model=DecisionExplanation)
async def explain_decision(decision_id: str):
    """
    Get human and agent-readable explanation for a specific decision
    """
    explanation = await explainer.explain_decision(decision_id)
    if not explanation:
        raise HTTPException(status_code=404, detail="Decision not found")
    return explanation

@app.post("/v1/autonomous-cycle")
async def execute_autonomous_cycle(problem_input: dict):
    """
    Execute a complete autonomous decision cycle through all six enterprises
    """
    try:
        result = await autonomous_flow.process_autonomous_cycle(problem_input)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Autonomous cycle failed: {str(e)}")

@app.get("/v1/supra_enterprise")
async def list_enterprises():
    """
    List all six enterprises and their roles
    """
    return {
        "enterprises": [
            {"id": "red", "name": "Red Owl", "role": "knowledge_gathering", "animal": "Owl", "principle": "Curiosity"},
            {"id": "orange", "name": "Orange Orangutan", "role": "logistics_planning", "animal": "Orangutan", "principle": "Planning"},
            {"id": "yellow", "name": "Yellow Honeybee", "role": "prototype_development", "animal": "Honeybee", "principle": "Creativity"},
            {"id": "green", "name": "Green Turtle", "role": "resource_allocation", "animal": "Turtle", "principle": "Sustainability"},
            {"id": "blue", "name": "Blue Dolphin", "role": "communication", "animal": "Dolphin", "principle": "Clarity"},
            {"id": "purple", "name": "Purple Elephant", "role": "empathy_analysis", "animal": "Elephant", "principle": "Empathy"}
        ],
        "flow": "Red → Orange → Yellow → Green → Blue → Purple → Feedback Loop"
    }

@app.get("/v1/caps")
async def get_budget_caps(
    enterprise: Optional[str] = Query(None, description="Filter by enterprise"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type")
):
    """
    Get budget caps for policy evaluation (cached for performance)
    """
    return await budget_caps_cache.get_budget_caps(enterprise, resource_type)

@app.post("/v1/cycle/start", response_model=CycleRunResponse)
async def start_cycle_run(request: CycleRunRequest):
    """
    Start a new 108-stage cycle run
    """
    try:
        # Validate that the cycle exists and is active
        e = engine()
        with e.begin() as conn:
            result = conn.execute(text("""
                SELECT cycle_id, title FROM cycles 
                WHERE cycle_id = :cycle_id AND active = true
            """), {'cycle_id': request.cycle_id})
            cycle = result.fetchone()
            
            if not cycle:
                raise HTTPException(status_code=404, detail="Cycle not found or inactive")
            
            # Create the cycle run
            run_result = conn.execute(text("""
                INSERT INTO cycle_runs (cycle_id, objective_ref, status, priority, policy_bundle, context, metadata, created_by)
                VALUES (:cycle_id, :objective_ref, 'pending', :priority, :policy_bundle, :context, :metadata, :created_by)
                RETURNING run_id, created_at
            """), {
                'cycle_id': request.cycle_id,
                'objective_ref': request.objective_ref,
                'priority': request.priority or 5,
                'policy_bundle': request.policy_bundle,
                'context': json.dumps(request.context or {}),
                'metadata': json.dumps(request.metadata or {}),
                'created_by': request.created_by or 'gateway'
            })
            run_data = run_result.fetchone()
            
            # Create all 108 stage runs
            conn.execute(text("""
                INSERT INTO cycle_stage_runs (run_id, stage_id, status)
                SELECT :run_id, stage_id, 'pending' 
                FROM cycle_stages 
                ORDER BY ordinal
            """), {'run_id': run_data.run_id})
            
            return CycleRunResponse(
                run_id=run_data.run_id,
                cycle_id=request.cycle_id,
                objective_ref=request.objective_ref,
                status='pending',
                created_at=run_data.created_at,
                message="Cycle run created successfully with 108 stages"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start cycle run: {str(e)}")

@app.post("/v1/cycle/complete")
async def complete_cycle_run(request: CycleCompleteRequest):
    """
    Mark a cycle run as completed and calculate final metrics
    """
    try:
        e = engine()
        with e.begin() as conn:
            # Update cycle run status
            conn.execute(text("""
                UPDATE cycle_runs 
                SET status = 'completed', completed_at = now()
                WHERE run_id = :run_id
            """), {'run_id': request.run_id})
            
            # Calculate final metrics
            conn.execute(text("""
                SELECT calculate_cycle_metrics(:run_id)
            """), {'run_id': request.run_id})
            
            # Get final metrics
            result = conn.execute(text("""
                SELECT * FROM cycle_run_metrics WHERE run_id = :run_id
            """), {'run_id': request.run_id})
            metrics = result.fetchone()
            
            return {
                "run_id": request.run_id,
                "status": "completed",
                "completed_at": datetime.now(timezone.utc),
                "metrics": dict(metrics._mapping) if metrics else {}
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete cycle run: {str(e)}")

@app.get("/v1/cycle/{run_id}/status")
async def get_cycle_status(run_id: str):
    """
    Get the current status and progress of a cycle run
    """
    try:
        e = engine()
        with e.begin() as conn:
            # Get cycle run details
            result = conn.execute(text("""
                SELECT cr.*, c.title as cycle_title
                FROM cycle_runs cr
                JOIN cycles c ON cr.cycle_id = c.cycle_id
                WHERE cr.run_id = :run_id
            """), {'run_id': run_id})
            cycle_run = result.fetchone()
            
            if not cycle_run:
                raise HTTPException(status_code=404, detail="Cycle run not found")
            
            # Get stage progress
            result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_stages,
                    COUNT(*) FILTER (WHERE status = 'completed') as completed_stages,
                    COUNT(*) FILTER (WHERE status = 'failed') as failed_stages,
                    COUNT(*) FILTER (WHERE status = 'running') as running_stages,
                    COUNT(*) FILTER (WHERE status = 'pending') as pending_stages
                FROM cycle_stage_runs 
                WHERE run_id = :run_id
            """), {'run_id': run_id})
            progress = result.fetchone()
            
            # Get current stage
            result = conn.execute(text("""
                SELECT cs.code, cs.name, csr.status, csr.attempted_at
                FROM cycle_stage_runs csr
                JOIN cycle_stages cs ON csr.stage_id = cs.stage_id
                WHERE csr.run_id = :run_id AND csr.status = 'running'
                ORDER BY cs.ordinal
                LIMIT 1
            """), {'run_id': run_id})
            current_stage = result.fetchone()
            
            return {
                "run_id": run_id,
                "cycle_title": cycle_run.cycle_title,
                "objective_ref": cycle_run.objective_ref,
                "status": cycle_run.status,
                "created_at": cycle_run.created_at,
                "started_at": cycle_run.started_at,
                "progress": dict(progress._mapping) if progress else {},
                "current_stage": dict(current_stage._mapping) if current_stage else None
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cycle status: {str(e)}")

@app.get("/v1/cycles")
async def list_cycles():
    """
    List all available cycle templates
    """
    try:
        e = engine()
        with e.begin() as conn:
            result = conn.execute(text("""
                SELECT cycle_id, title, description, version, active, created_at
                FROM cycles 
                WHERE active = true
                ORDER BY created_at DESC
            """))
            cycles = [dict(row._mapping) for row in result.fetchall()]
            
            return {"cycles": cycles}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list cycles: {str(e)}")

@app.get("/v1/openapi.json")
async def get_openapi():
    """
    Serve OpenAPI specification
    """
    return app.openapi()

# Helper functions for obligation handling
async def _handle_provenance_obligation(decision_id: str, context: dict):
    """Handle provenance logging obligation"""
    try:
        provenance_data = context.get("provenance", {})
        if provenance_data:
            e = engine()
            with e.begin() as conn:
                conn.execute(text("""
                    SELECT handle_provenance_obligation(:decision_id, :provenance_data)
                """), {
                    'decision_id': decision_id,
                    'provenance_data': json.dumps(provenance_data)
                })
    except Exception as e:
        print(f"Failed to handle provenance obligation: {e}")

async def _emit_budget_telemetry(decision_id: str, input_obj: dict):
    """Handle budget telemetry emission obligation"""
    try:
        agent = input_obj.get("agent", {})
        context = input_obj.get("context", {})
        
        enterprise = agent.get("enterprise", "")
        resource_type = "compute"  # Default, could be derived from resource.service
        estimated_cost = context.get("estimated_cost", 0)
        budget_cap = context.get("budget_cap", 0)
        
        if estimated_cost > 0 and budget_cap > 0:
            e = engine()
            with e.begin() as conn:
                conn.execute(text("""
                    SELECT emit_budget_telemetry(:decision_id, :agent_id, :enterprise, 
                                               :resource_type, :estimated_cost, :budget_cap)
                """), {
                    'decision_id': decision_id,
                    'agent_id': agent.get("id", ""),
                    'enterprise': enterprise,
                    'resource_type': resource_type,
                    'estimated_cost': estimated_cost,
                    'budget_cap': budget_cap
                })
    except Exception as e:
        print(f"Failed to emit budget telemetry: {e}")
