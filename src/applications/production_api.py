#!/usr/bin/env python3
"""
Production-Ready API for Agent Orchestrator Framework
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn

try:
    from production_config import get_config
except ModuleNotFoundError:
    from config.production_config import get_config
from error_handling import handle_error, ErrorContext, ErrorSeverity, ErrorCategory
from health_monitoring import get_health_monitor, run_health_checks, get_system_health, record_request
from src.core.services import CosmicCouncil, ProblemStatement, ProblemComplexity
from src.agents.supra_enterprise import EnterpriseType
from rules_engine import list_rules, evaluate_rules, follow_up_question
from structured_interaction import structured_engine, StructuredResponse
from manual import get_manual, get_examples

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
config = get_config()
health_monitor = get_health_monitor()
cosmic_council = CosmicCouncil()

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting Agent Orchestrator API...")
    
    # Initialize health monitoring
    await health_monitor.run_health_checks()
    
    # Initialize database
    try:
        from database_setup import initialize_database
        initialize_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        # Continue without database for now
    
    yield
    
    # Shutdown
    logger.info("Shutting down Agent Orchestrator API...")

# Create FastAPI app
app = FastAPI(
    title="Agent Orchestrator Framework API",
    description="Production-ready API for the Agent Orchestrator problem-solving framework",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure properly in production
)

# Request/Response middleware
@app.middleware("http")
async def request_middleware(request: Request, call_next):
    """Request/response middleware for logging and metrics"""
    start_time = datetime.now(timezone.utc)
    
    try:
        response = await call_next(request)
        record_request(success=True)
        return response
    except Exception as e:
        record_request(success=False)
        handle_error(e, ErrorContext(
            component="api",
            operation=request.method,
            metadata={"path": str(request.url), "method": request.method}
        ))
        raise
    finally:
        # Log request
        duration = (datetime.now(timezone.utc) - start_time).total_seconds()
        logger.info(f"{request.method} {request.url.path} - {duration:.3f}s")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    handle_error(exc, ErrorContext(
        component="api",
        operation=request.method,
        metadata={"path": str(request.url), "method": request.method}
    ))
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

# Authentication (simplified for now)
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify authentication token"""
    # In production, implement proper JWT verification
    if not credentials.credentials:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return credentials.credentials

# Health endpoints
@app.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check"""
    try:
        health_checks = await run_health_checks()
        system_health = get_system_health()
        
        return {
            "status": system_health["status"],
            "message": system_health["message"],
            "timestamp": system_health["timestamp"],
            "checks": system_health["checks"],
            "uptime_seconds": system_health["uptime_seconds"],
            "request_count": system_health["request_count"],
            "error_count": system_health["error_count"]
        }
    except Exception as e:
        handle_error(e, ErrorContext(component="api", operation="health_check"))
        raise HTTPException(status_code=500, detail="Health check failed")

@app.get("/metrics")
async def get_metrics():
    """Get system metrics"""
    try:
        metrics = health_monitor.collect_system_metrics()
        return {
            "timestamp": metrics.timestamp.isoformat(),
            "cpu_percent": metrics.cpu_percent,
            "memory_percent": metrics.memory_percent,
            "memory_available_mb": metrics.memory_available_mb,
            "disk_usage_percent": metrics.disk_usage_percent,
            "disk_free_gb": metrics.disk_free_gb,
            "error_rate": metrics.error_rate,
            "throughput_per_second": metrics.throughput_per_second
        }
    except Exception as e:
        handle_error(e, ErrorContext(component="api", operation="get_metrics"))
        raise HTTPException(status_code=500, detail="Failed to get metrics")

# Agent Orchestrator endpoints
@app.get("/api/v1/rules")
async def get_rules(token: str = Depends(verify_token)):
    return {
        "status": "success",
        "rules": list_rules(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.post("/api/v1/structured-interaction")
async def structured_interaction(
    payload: Dict[str, Any],
    token: str = Depends(verify_token)
):
    """Process problem using structured 9-step Agent Orchestrator interaction"""
    try:
        problem = payload.get("problem", "")
        context = payload.get("context", {})
        
        if not problem:
            raise HTTPException(status_code=400, detail="Problem is required")
        
        # Process structured interaction
        response = structured_engine.process_structured_interaction(problem, context)
        
        # Validate output quality
        validation = structured_engine.validate_output_quality(response)
        
        return {
            "status": "success",
            "structured_response": {
                "problem": response.problem,
                "totem_responses": [
                    {
                        "totem": tr.totem,
                        "emoji": tr.emoji,
                        "name": tr.name,
                        "response": tr.response,
                        "confidence": tr.confidence,
                        "next_actions": tr.next_actions
                    } for tr in response.totem_responses
                ],
                "purple_elephant_feedback": response.purple_elephant_feedback,
                "red_owl_next_questions": response.red_owl_next_questions,
                "conclusion": response.conclusion,
                "iteration_prompt": response.iteration_prompt
            },
            "quality_validation": validation,
            "timestamp": response.timestamp
        }
        
    except Exception as e:
        handle_error(e, ErrorContext(
            component="api",
            operation="structured_interaction",
            metadata={"payload": payload}
        ))
        raise HTTPException(status_code=500, detail="Failed to process structured interaction")

@app.get("/api/v1/structured-interaction/example")
async def get_structured_example(token: str = Depends(verify_token)):
    """Get example of structured interaction workflow"""
    try:
        example = structured_engine.generate_example_workflow()
        return {
            "status": "success",
            "example": example,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        handle_error(e, ErrorContext(component="api", operation="get_structured_example"))
        raise HTTPException(status_code=500, detail="Failed to get structured example")

@app.post("/api/v1/problems/solve")
async def solve_problem(
    problem_data: Dict[str, Any],
    token: str = Depends(verify_token)
):
    """Solve a problem using the Agent Orchestrator framework"""
    try:
        # Validate problem data
        required_fields = ["title", "description", "complexity", "domain", "stakeholders", "constraints", "success_criteria"]
        for field in required_fields:
            if field not in problem_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        # Create problem statement
        problem = ProblemStatement(
            title=problem_data["title"],
            description=problem_data["description"],
            complexity=ProblemComplexity(problem_data["complexity"]),
            domain=problem_data["domain"],
            stakeholders=problem_data["stakeholders"],
            constraints=problem_data["constraints"],
            success_criteria=problem_data["success_criteria"]
        )
        # Solve the problem
        result = await cosmic_council.solve_problem(problem)
        api_result = {
            "cycle_id": result.cycle_id,
            "status": result.status.value,
            "total_processing_time": result.total_processing_time,
            "overall_confidence": result.overall_confidence,
            "enterprise_results": {
                enterprise.value: {
                    "status": enterprise_result.status,
                    "confidence": enterprise_result.confidence,
                    "insights": enterprise_result.insights,
                    "recommendations": enterprise_result.recommendations,
                    "next_actions": enterprise_result.next_actions
                }
                for enterprise, enterprise_result in result.enterprise_results.items()
            },
            "final_synthesis": result.final_synthesis,
            "feedback_loop": result.feedback_loop
        }
        rules = evaluate_rules(problem_data, api_result)
        return {
            "status": "success",
            "result": api_result,
            "rules": rules,
            "follow_up": follow_up_question(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        handle_error(e, ErrorContext(
            component="api",
            operation="solve_problem",
            metadata={"problem_data": problem_data}
        ))
        raise HTTPException(status_code=500, detail="Failed to solve problem")

@app.get("/api/v1/supra_enterprise")
async def get_enterprises(token: str = Depends(verify_token)):
    """Get information about all enterprises"""
    try:
        enterprises_info = {}
        for enterprise_type in cosmic_council.enterprises:
            enterprise = cosmic_council.enterprises[enterprise_type]
            enterprises_info[enterprise_type.value] = {
                "name": enterprise.name,
                "description": enterprise.description,
                "color": enterprise.color,
                "gemstone": enterprise.gemstone,
                "personality": enterprise.personality,
                "core_principles": enterprise.core_principles,
                "processing_order": cosmic_council.processing_order.index(enterprise_type)
            }
        
        return {
            "status": "success",
            "enterprises": enterprises_info,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        handle_error(e, ErrorContext(component="api", operation="get_enterprises"))
        raise HTTPException(status_code=500, detail="Failed to get enterprises")

@app.get("/api/v1/status")
async def get_status(token: str = Depends(verify_token)):
    """Get system status"""
    try:
        return {
            "status": "success",
            "system": {
                "name": "Agent Orchestrator Framework",
                "version": "1.0.0",
                "environment": config.environment,
                "uptime_seconds": (datetime.now(timezone.utc) - health_monitor.start_time).total_seconds(),
                "enterprises_count": len(cosmic_council.enterprises),
                "processing_order": [e.value for e in cosmic_council.processing_order]
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        handle_error(e, ErrorContext(component="api", operation="get_status"))
        raise HTTPException(status_code=500, detail="Failed to get status")

# Configuration endpoint
@app.get("/api/v1/config")
async def get_config_info(token: str = Depends(verify_token)):
    """Get configuration information (non-sensitive)"""
    try:
        return {
            "status": "success",
            "config": {
                "api_host": config.api_host,
                "api_port": config.api_port,
                "environment": config.environment,
                "log_level": config.log_level,
                "max_concurrent_cycles": config.max_concurrent_cycles,
                "session_timeout": config.session_timeout,
                "cache_ttl": config.cache_ttl,
                "enable_metrics": config.enable_metrics,
                "debug": config.debug
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        handle_error(e, ErrorContext(component="api", operation="get_config"))
        raise HTTPException(status_code=500, detail="Failed to get configuration")

@app.get("/api/v1/usage")
async def get_usage(token: str = Depends(verify_token)):
    """Return a concise usage guide for the 8-step workflow"""
    guide = {
        "title": "Using the Agent Orchestrator GPT Framework",
        "steps": [
            {
                "step": 1,
                "title": "Define Your Problem or Goal Clearly",
                "details": "State your challenge clearly. The Red Owl of Inquiry gathers foundational knowledge and frames the problem."
            },
            {
                "step": 2,
                "title": "Leverage the Six Totems' Specializations",
                "details": {
                    "red_owl": "Research & Inquiry",
                    "orange_orangutan": "Planning & Logistics",
                    "yellow_honeybee": "Creativity & Development",
                    "green_tortoise": "Resources & Budgeting",
                    "blue_dolphin": "Communication & Marketing",
                    "purple_elephant": "Feedback & Reflection"
                }
            },
            {
                "step": 3,
                "title": "Iterate Using Feedback Loops",
                "details": "Use dynamic feedback to revisit and refine after testing or implementation."
            },
            {
                "step": 4,
                "title": "Apply Systems Thinking",
                "details": "Consider interconnections across totems to keep solutions holistic."
            },
            {
                "step": 5,
                "title": "Use Tools for Integration",
                "details": "Integrate Airtable, Make.com, or PM tools to track tasks, insights, and feedback."
            },
            {
                "step": 6,
                "title": "Explore Creative and Ethical Applications",
                "details": "Blend innovation, ethics, spirituality, and quantum principles for depth and clarity."
            },
            {
                "step": 7,
                "title": "Ask for Examples or Simulations",
                "details": "Request tailored examples or end-to-end simulations for your context."
            },
            {
                "step": 8,
                "title": "Collaborate as a Partner",
                "details": "Engage dialogically. Pose complex questions and iterate together."
            }
        ],
        "endpoints": {
            "solve_problem": "/api/v1/problems/solve",
            "process_totem": "/api/v1/supra_enterprise/{enterprise}/process",
            "iterate": "/api/v1/problems/iterate",
            "simulate": "/api/v1/examples/simulate",
            "airtable_upsert": "/api/v1/integrations/airtable/upsert",
            "make_trigger": "/api/v1/integrations/make/trigger"
        }
    }
    return {"status": "success", "usage": guide, "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post("/api/v1/supra_enterprise/{enterprise}/process")
async def process_with_enterprise(enterprise: str, payload: Dict[str, Any], token: str = Depends(verify_token)):
    """Run a single totem on a problem and return its partial result"""
    try:
        etype = EnterpriseType(enterprise)
        if etype not in cosmic_council.enterprises:
            raise HTTPException(status_code=404, detail="Unknown enterprise")
        required_fields = ["title", "description", "complexity", "domain"]
        for field in required_fields:
            if field not in payload:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        problem = ProblemStatement(
            title=payload["title"],
            description=payload["description"],
            complexity=ProblemComplexity(payload["complexity"]),
            domain=payload["domain"],
            stakeholders=payload.get("stakeholders", []),
            constraints=payload.get("constraints", {}),
            success_criteria=payload.get("success_criteria", [])
        )
        context = payload.get("context", {})
        agent = cosmic_council.enterprises[etype]
        result = await agent.process_problem(problem, context)
        partial = {
            "enterprise": etype.value,
            "status": result.status,
            "confidence": result.confidence,
            "insights": result.insights,
            "recommendations": result.recommendations,
            "next_actions": result.next_actions,
            "processing_time": result.processing_time,
        }
        rules = evaluate_rules({"title": payload["title"], "description": payload["description"], "domain": payload["domain"], "complexity": payload["complexity"]}, {"enterprise_results": {etype.value: partial}})
        return {
            "status": "success",
            "result": partial,
            "rules": rules,
            "follow_up": follow_up_question(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        handle_error(e, ErrorContext(component="api", operation="process_with_enterprise", metadata={"enterprise": enterprise}))
        raise HTTPException(status_code=500, detail="Failed to process with enterprise")


@app.post("/api/v1/problems/iterate")
async def iterate_problem(payload: Dict[str, Any], token: str = Depends(verify_token)):
    """Run an iteration cycle, optionally using prior feedback/context"""
    try:
        prior_context = payload.get("prior_context")
        problem_data = payload.get("problem")
        if not isinstance(problem_data, dict):
            raise HTTPException(status_code=400, detail="Missing problem payload")
        problem = ProblemStatement(
            title=problem_data["title"],
            description=problem_data["description"],
            complexity=ProblemComplexity(problem_data["complexity"]),
            domain=problem_data["domain"],
            stakeholders=problem_data.get("stakeholders", []),
            constraints=problem_data.get("constraints", {}),
            success_criteria=problem_data.get("success_criteria", [])
        )
        result = await cosmic_council.solve_problem(problem)
        api_result = {
            "cycle_id": result.cycle_id,
            "overall_confidence": result.overall_confidence,
            "final_synthesis": result.final_synthesis,
            "feedback_loop": result.feedback_loop,
            "enterprise_results": {
                k.value: {
                    "status": v.status,
                    "confidence": v.confidence,
                    "insights": v.insights,
                    "recommendations": v.recommendations,
                    "next_actions": v.next_actions,
                } for k, v in result.enterprise_results.items()
            }
        }
        if payload.get("second_pass"):
            synthesized_context = {k: {
                "insights": v["insights"],
                "recommendations": v["recommendations"],
                "confidence": v["confidence"],
            } for k, v in api_result["enterprise_results"].items()}
            if prior_context and isinstance(prior_context, dict):
                synthesized_context.update(prior_context)
        rules = evaluate_rules(problem_data, api_result)
        return {
            "status": "success",
            "iteration": api_result,
            "rules": rules,
            "follow_up": follow_up_question(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        handle_error(e, ErrorContext(component="api", operation="iterate_problem"))
        raise HTTPException(status_code=500, detail="Failed to iterate problem")


@app.post("/api/v1/examples/simulate")
async def simulate_example(payload: Dict[str, Any], token: str = Depends(verify_token)):
    """Run a tailored example/simulation for a given domain"""
    try:
        domain = payload.get("domain", "general")
        title = payload.get("title", f"Simulation for {domain.title()}")
        description = payload.get("description", f"End-to-end simulation in the {domain} domain")
        complexity = payload.get("complexity", ProblemComplexity.MODERATE.value)
        problem = ProblemStatement(
            title=title,
            description=description,
            complexity=ProblemComplexity(complexity),
            domain=domain,
            stakeholders=payload.get("stakeholders", ["Users", "Team", "Leadership"]),
            constraints=payload.get("constraints", {}),
            success_criteria=payload.get("success_criteria", ["Quality", "Time", "Cost"])
        )
        result = await cosmic_council.solve_problem(problem)
        api_result = {
            "problem": {"title": title, "domain": domain, "complexity": complexity},
            "overall_confidence": result.overall_confidence,
            "final_synthesis": result.final_synthesis,
            "feedback_loop": result.feedback_loop,
            "enterprise_results": {k.value: {
                "status": v.status,
                "confidence": v.confidence,
                "insights": v.insights,
                "recommendations": v.recommendations,
                "next_actions": v.next_actions,
            } for k, v in result.enterprise_results.items()}
        }
        rules = evaluate_rules({"title": title, "description": description, "domain": domain, "complexity": complexity}, api_result)
        return {
            "status": "success",
            "simulation": api_result,
            "rules": rules,
            "follow_up": follow_up_question(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        handle_error(e, ErrorContext(component="api", operation="simulate_example"))
        raise HTTPException(status_code=500, detail="Failed to run simulation")


# Integration stubs (Airtable / Make.com)
try:
    from integrations import get_airtable_client, get_make_client
except Exception:
    get_airtable_client = None
    get_make_client = None


@app.post("/api/v1/integrations/airtable/upsert")
async def airtable_upsert(payload: Dict[str, Any], token: str = Depends(verify_token)):
    """Upsert a record into Airtable (stub)."""
    try:
        if not get_airtable_client:
            raise HTTPException(status_code=501, detail="Airtable integration not configured")
        client = get_airtable_client()
        result = await client.upsert_record(payload.get("table", "cosmic_records"), payload.get("record", {}))
        return {"status": "success", "airtable": result, "timestamp": datetime.now(timezone.utc).isoformat()}
    except HTTPException:
        raise
    except Exception as e:
        handle_error(e, ErrorContext(component="api", operation="airtable_upsert"))
        raise HTTPException(status_code=500, detail="Airtable upsert failed")


@app.post("/api/v1/integrations/make/trigger")
async def make_trigger(payload: Dict[str, Any], token: str = Depends(verify_token)):
    """Trigger a Make.com scenario (stub)."""
    try:
        if not get_make_client:
            raise HTTPException(status_code=501, detail="Make.com integration not configured")
        client = get_make_client()
        result = await client.trigger_scenario(payload.get("scenario_id", "default_scenario"), payload.get("data", {}))
        return {"status": "success", "make": result, "timestamp": datetime.now(timezone.utc).isoformat()}
    except HTTPException:
        raise
    except Exception as e:
        handle_error(e, ErrorContext(component="api", operation="make_trigger"))
        raise HTTPException(status_code=500, detail="Make.com trigger failed")


@app.get("/api/v1/manual")
async def api_manual(token: str = Depends(verify_token)):
    return {"status": "success", "manual": get_manual(), "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/api/v1/manual/examples")
async def api_manual_examples(token: str = Depends(verify_token)):
    return {"status": "success", "examples": get_examples(), "timestamp": datetime.now(timezone.utc).isoformat()}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Agent Orchestrator Framework API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoints": {
            "health": "/health",
            "detailed_health": "/health/detailed",
            "metrics": "/metrics",
            "usage": "/api/v1/usage",
            "rules": "/api/v1/rules",
            "manual": "/api/v1/manual",
            "manual_examples": "/api/v1/manual/examples",
            "structured_interaction": "/api/v1/structured-interaction",
            "structured_example": "/api/v1/structured-interaction/example",
            "solve_problem": "/api/v1/problems/solve",
            "process_totem": "/api/v1/supra_enterprise/{enterprise}/process",
            "iterate": "/api/v1/problems/iterate",
            "simulate": "/api/v1/examples/simulate",
            "airtable_upsert": "/api/v1/integrations/airtable/upsert",
            "make_trigger": "/api/v1/integrations/make/trigger",
            "enterprises": "/api/v1/supra_enterprise",
            "status": "/api/v1/status",
            "config": "/api/v1/config"
        }
    }

def run_server():
    """Run the production server"""
    try:
        # Validate configuration
        config.validate()
        
        # Setup logging
        config.setup_logging()
        
        logger.info(f"Starting Agent Orchestrator API on {config.api_host}:{config.api_port}")
        
        # Run server
        uvicorn.run(
            "production_api:app",
            host=config.api_host,
            port=config.api_port,
            workers=config.api_workers if not config.debug else 1,
            reload=config.api_reload,
            log_level=config.log_level.lower()
        )
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise

if __name__ == "__main__":
    run_server()
