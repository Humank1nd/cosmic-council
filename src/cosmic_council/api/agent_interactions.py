"""
Enhanced Agent Interaction API
Provides comprehensive endpoints for interacting with individual enterprise agents
and orchestrating multi-agent problem-solving workflows.
"""

import asyncio
import hashlib
import ipaddress
import json
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from time import perf_counter
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum
from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel, Field, field_validator
from prometheus_client import Counter, Histogram, REGISTRY

from ..core.core import (
    ProblemStatement, ProblemComplexity, EnterpriseType, 
    CosmicCouncilRule, EnhancedEnterpriseResult, EnhancedCycleResult, TotemPersonality
)
from .cosmic_identity import CosmicCouncilIdentity, EnterpriseVisualIdentity
from ..core.hexagon import CosmicCouncilHexagon
from ..agents.working_enhanced_agents import (
    WorkingEnhancedRedOwlAgent, WorkingEnhancedOrangeOrangutanAgent,
    AnalysisDepth
)
from ..agents.hierarchical_enterprise import TaskContext

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)

# Create router for agent interactions
router = APIRouter(prefix="/api/v1/agents", tags=["Agent Interactions"])

# Global agent instances (initialized in lifespan)
agents: Dict[EnterpriseType, Any] = {}
council: Optional[CosmicCouncilHexagon] = None

# Cache for agent list (static data, can be cached)
_agent_list_cache: Optional[Dict[str, Any]] = None
_agent_response_cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}
_rate_limit_state: Dict[str, List[float]] = {}

def _get_metric(metric_type, name: str, description: str, labelnames: List[str]):
    try:
        return metric_type(name, description, labelnames)
    except ValueError:
        existing = REGISTRY._names_to_collectors.get(name)
        if existing:
            return existing
        raise


# Metrics
AGENT_API_REQUESTS = _get_metric(
    Counter,
    "cosmic_council_agent_requests_total",
    "Total agent API requests",
    ["endpoint", "enterprise", "status"],
)
AGENT_API_LATENCY = _get_metric(
    Histogram,
    "cosmic_council_agent_request_seconds",
    "Agent API request latency in seconds",
    ["endpoint", "enterprise"],
)
AGENT_API_CACHE_HITS = _get_metric(
    Counter,
    "cosmic_council_agent_cache_hits_total",
    "Agent API cache hits",
    ["endpoint", "enterprise"],
)
AGENT_API_WEBHOOKS = _get_metric(
    Counter,
    "cosmic_council_agent_webhooks_total",
    "Agent API webhook dispatches",
    ["status"],
)


def _allow_anonymous() -> bool:
    return os.getenv("ALLOW_ANONYMOUS", "false").lower() == "true"


def _allow_internal_webhooks() -> bool:
    return os.getenv("AGENT_API_ALLOW_INTERNAL_WEBHOOKS", "false").lower() == "true"


def _rate_limit_config() -> Tuple[int, int]:
    limit = int(os.getenv("AGENT_API_RATE_LIMIT", "60"))
    window = int(os.getenv("AGENT_API_RATE_LIMIT_WINDOW", "60"))
    return limit, window


def _cache_ttl_seconds() -> int:
    return int(os.getenv("AGENT_API_CACHE_TTL", "60"))


def _rate_limit_key(request: Request, credentials: Optional[HTTPAuthorizationCredentials]) -> str:
    if credentials and credentials.credentials:
        return credentials.credentials
    if request.client:
        return request.client.host
    return "anonymous"


def _prune_rate_limit(bucket: List[float], window: int, now: float) -> List[float]:
    return [ts for ts in bucket if (now - ts) < window]


def _cache_key(enterprise: str, request: "AgentProcessRequest") -> str:
    payload = {
        "enterprise": enterprise,
        "title": request.title,
        "description": request.description,
        "domain": request.domain,
        "complexity": request.complexity,
        "stakeholders": request.stakeholders,
        "constraints": request.constraints,
        "success_criteria": request.success_criteria,
        "analysis_depth": request.analysis_depth,
        "context": request.context,
    }
    raw = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _get_cached_response(cache_key: str) -> Optional[Dict[str, Any]]:
    ttl = _cache_ttl_seconds()
    if ttl <= 0:
        return None
    cached = _agent_response_cache.get(cache_key)
    if not cached:
        return None
    expires_at, payload = cached
    if time.time() > expires_at:
        _agent_response_cache.pop(cache_key, None)
        return None
    return payload


def _set_cached_response(cache_key: str, payload: Dict[str, Any]) -> None:
    ttl = _cache_ttl_seconds()
    if ttl <= 0:
        return
    _agent_response_cache[cache_key] = (time.time() + ttl, payload)


def _is_private_host(hostname: str) -> bool:
    if hostname in {"localhost"}:
        return True
    try:
        ip_addr = ipaddress.ip_address(hostname)
    except ValueError:
        return False
    return ip_addr.is_private or ip_addr.is_loopback or ip_addr.is_link_local


def _validate_webhook_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise HTTPException(status_code=400, detail="Webhook URL must use http or https")
    if not parsed.hostname:
        raise HTTPException(status_code=400, detail="Webhook URL must include a hostname")
    if not _allow_internal_webhooks() and _is_private_host(parsed.hostname):
        raise HTTPException(status_code=400, detail="Webhook URL hostname is not allowed")
    return url


async def dispatch_webhook(url: str, payload: Dict[str, Any]) -> None:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(url, json=payload)
        status_label = "success" if 200 <= response.status_code < 300 else "error"
        AGENT_API_WEBHOOKS.labels(status=status_label).inc()
    except Exception as exc:
        AGENT_API_WEBHOOKS.labels(status="error").inc()
        logger.warning(f"Webhook dispatch failed: {exc}")


async def enforce_rate_limit(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> None:
    limit, window = _rate_limit_config()
    if limit <= 0:
        return
    now = time.time()
    key = _rate_limit_key(request, credentials)
    bucket = _prune_rate_limit(_rate_limit_state.get(key, []), window, now)
    if len(bucket) >= limit:
        reset = int(bucket[0] + window) if bucket else int(now + window)
        headers = {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(reset),
        }
        raise HTTPException(status_code=429, detail="Rate limit exceeded", headers=headers)
    bucket.append(now)
    _rate_limit_state[key] = bucket


# ============================================================================
# Pydantic Models
# ============================================================================

class AgentInfoResponse(BaseModel):
    """Information about an agent"""
    enterprise: str
    name: str
    animal: str
    color: str
    core_principle: str
    communication_style: str
    thinking_pattern: str
    strengths: List[str]
    expertise_areas: List[str]
    processing_order: int
    applicable_rules: List[str]
    greeting: str
    closing: str


class AgentProcessRequest(BaseModel):
    """Request to process a problem with an agent"""
    title: str = Field(..., min_length=1, max_length=500, description="Problem title")
    description: str = Field(..., min_length=1, description="Problem description")
    domain: str = Field(..., min_length=1, max_length=200, description="Problem domain")
    complexity: str = Field(..., description="Problem complexity level")
    stakeholders: List[str] = Field(default=[], description="List of stakeholders")
    constraints: Dict[str, Any] = Field(default={}, description="Problem constraints")
    success_criteria: List[str] = Field(default=[], description="Success criteria")
    context: Dict[str, Any] = Field(default={}, description="Additional context")
    analysis_depth: str = Field(default="comprehensive", description="Analysis depth level")
    webhook_url: Optional[str] = Field(default=None, description="Optional webhook callback URL")
    
    @field_validator('complexity')
    def validate_complexity(cls, v):
        valid_complexities = ['simple', 'moderate', 'complex', 'systemic']
        if v not in valid_complexities:
            raise ValueError(f'Complexity must be one of: {valid_complexities}')
        return v

    @field_validator('analysis_depth')
    def validate_analysis_depth(cls, v):
        valid_depths = ['surface', 'quick', 'moderate', 'standard', 'comprehensive', 'deep']
        if v not in valid_depths:
            raise ValueError(f'Analysis depth must be one of: {valid_depths}')
        return v


class AgentProcessResponse(BaseModel):
    """Response from agent processing"""
    enterprise: str
    status: str
    confidence_score: float
    processing_time: float
    insights: Dict[str, Any]
    recommendations: List[str]
    next_actions: List[str]
    dependencies: List[str]
    personality_response: str
    applied_rules: List[str]
    wisdom_insights: List[str]
    questions_for_next_cycle: List[str]
    timestamp: datetime


class AgentSequenceRequest(BaseModel):
    """Request to process problem through a sequence of agents"""
    problem: AgentProcessRequest
    agent_sequence: List[str] = Field(..., description="Ordered list of agents to process")
    parallel: bool = Field(default=False, description="Process agents in parallel if possible")
    synthesize: bool = Field(default=True, description="Synthesize results from all agents")
    webhook_url: Optional[str] = Field(default=None, description="Optional webhook callback URL")
    
    @field_validator('agent_sequence')
    def validate_agent_sequence(cls, v):
        valid_agents = ['red_owl', 'orange_orangutan', 'yellow_honeybee',
                       'green_tortoise', 'blue_dolphin', 'purple_elephant']
        for agent in v:
            if agent not in valid_agents:
                raise ValueError(f'Invalid agent: {agent}. Must be one of: {valid_agents}')
        return v


class AgentSequenceResponse(BaseModel):
    """Response from agent sequence processing"""
    sequence_id: str
    status: str
    total_processing_time: float
    agent_results: Dict[str, AgentProcessResponse]
    synthesis: Optional[Dict[str, Any]] = None
    overall_confidence: float
    next_recommended_agent: Optional[str] = None
    timestamp: datetime


class AgentCollaborationRequest(BaseModel):
    """Request for multiple agents to collaborate on a problem"""
    problem: AgentProcessRequest
    collaborating_agents: List[str] = Field(..., min_length=2, description="Agents to collaborate")
    collaboration_mode: str = Field(default="sequential", description="Collaboration mode")
    webhook_url: Optional[str] = Field(default=None, description="Optional webhook callback URL")
    
    @field_validator('collaboration_mode')
    def validate_collaboration_mode(cls, v):
        valid_modes = ['sequential', 'parallel', 'iterative', 'consensus']
        if v not in valid_modes:
            raise ValueError(f'Collaboration mode must be one of: {valid_modes}')
        return v


class AgentStatusResponse(BaseModel):
    """Status information about an agent"""
    enterprise: str
    status: str
    is_available: bool
    current_processing_count: int
    total_processed: int
    average_confidence: float
    average_processing_time: float
    last_activity: Optional[datetime] = None


# ============================================================================
# Dependency Functions
# ============================================================================

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> str:
    """Get current user from authorization token"""
    try:
        # Allow anonymous access when configured
        if not credentials:
            if _allow_anonymous():
                return "anonymous"
            logger.debug("No credentials provided")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header required",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = credentials.credentials
        if not token or not token.strip():
            logger.debug("Empty token provided")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Allow test tokens only when anonymous access is enabled
        if token == "test" and _allow_anonymous():
            logger.debug("Valid test token accepted")
            return "demo_user"

        secret = os.getenv("AGENT_API_JWT_SECRET")
        algorithm = os.getenv("AGENT_API_JWT_ALGORITHM", "HS256")
        if not secret:
            if _allow_anonymous():
                return "anonymous"
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="JWT secret not configured",
            )

        payload = jwt.decode(token, secret, algorithms=[algorithm], options={"verify_aud": False})
        subject = payload.get("sub") or payload.get("user_id") or payload.get("email")
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return str(subject)
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except JWTError as e:
        logger.debug(f"JWT validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        # Log unexpected errors but still raise HTTPException
        logger.error(f"Unexpected error in get_current_user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication error",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_agent(enterprise: str) -> Any:
    """Get agent instance by enterprise type"""
    try:
        enterprise_type = EnterpriseType(enterprise.lower())
        if enterprise_type not in agents:
            raise HTTPException(
                status_code=404, 
                detail=f"Agent {enterprise} not found or not initialized"
            )
        return agents[enterprise_type]
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid enterprise type: {enterprise}")


def get_analysis_depth(depth_str: str) -> AnalysisDepth:
    """Convert string to AnalysisDepth enum"""
    depth_map = {
        'surface': AnalysisDepth.SURFACE,
        'quick': AnalysisDepth.SURFACE,  # Alias for surface
        'moderate': AnalysisDepth.MODERATE,
        'standard': AnalysisDepth.MODERATE,  # Alias for moderate
        'comprehensive': AnalysisDepth.COMPREHENSIVE,
        'deep': AnalysisDepth.DEEP
    }
    return depth_map.get(depth_str.lower() if depth_str else '', AnalysisDepth.COMPREHENSIVE)


def _build_totem_personality(enterprise_type: EnterpriseType) -> TotemPersonality:
    """Build a totem personality from visual identity for adapted agents."""
    visual_identity = CosmicCouncilIdentity.get_enterprise_identity(enterprise_type)
    if not visual_identity:
        return TotemPersonality(
            name=enterprise_type.value.replace("_", " ").title(),
            animal="Unknown",
            color="#000000",
            core_principle="Clarity",
            communication_style="Direct",
            thinking_pattern="Systematic",
            strengths=["Analysis"],
            wisdom_approach="Structured",
            metaphor=f"{enterprise_type.value} perspective",
            greeting="Greetings.",
            closing="Proceed with clarity.",
        )
    return TotemPersonality(
        name=visual_identity.name,
        animal=visual_identity.animal,
        color=visual_identity.color_hex,
        core_principle=visual_identity.core_principle,
        communication_style="Direct",
        thinking_pattern="Systematic",
        strengths=[visual_identity.role, visual_identity.core_principle],
        wisdom_approach="Structured synthesis",
        metaphor=visual_identity.symbol,
        greeting=f"Greetings from {visual_identity.name}.",
        closing="May your path be clear.",
    )


def _build_task_agent_input_data(
    enterprise_type: EnterpriseType,
    problem: ProblemStatement,
    context: Dict[str, Any],
) -> Dict[str, Any]:
    """Map API problem/context payload into task-agent specific input_data."""
    data: Dict[str, Any] = {"context": context or {}}
    if enterprise_type == EnterpriseType.YELLOW_HONEYBEE:
        data.setdefault("action_plan_id", problem.id)
        data.setdefault("root_cause", problem.description or problem.title)
        data.setdefault(
            "actions",
            context.get("actions")
            or [
                {
                    "id": f"{problem.id}-action-1",
                    "title": problem.title,
                    "category": problem.domain or "general",
                }
            ],
        )
    elif enterprise_type == EnterpriseType.GREEN_TORTOISE:
        data.setdefault("implementation_plan_id", problem.id)
        data.setdefault(
            "specifications",
            context.get("specifications")
            or [
                {
                    "id": f"{problem.id}-spec-1",
                    "action_id": f"{problem.id}-action-1",
                    "action_title": problem.title,
                    "estimated_duration_seconds": 300,
                }
            ],
        )
        data.setdefault("dependencies", context.get("dependencies", []))
    elif enterprise_type == EnterpriseType.BLUE_DOLPHIN:
        data.setdefault("schedule_id", problem.id)
        data.setdefault(
            "slots",
            context.get("slots")
            or [
                {
                    "id": f"{problem.id}-slot-1",
                    "action_id": f"{problem.id}-action-1",
                    "action_title": problem.title,
                }
            ],
        )
    elif enterprise_type == EnterpriseType.PURPLE_ELEPHANT:
        data.setdefault("location_plan_id", problem.id)
        data.setdefault(
            "targets",
            context.get("targets")
            or [
                {
                    "id": f"{problem.id}-target-1",
                    "action_id": f"{problem.id}-action-1",
                    "action_title": problem.title,
                }
            ],
        )
    return data


async def _run_task_agent_as_enterprise_result(
    enterprise_type: EnterpriseType,
    agent: Any,
    problem: ProblemStatement,
    context: Dict[str, Any],
) -> EnhancedEnterpriseResult:
    """Adapt process_task agents to EnhancedEnterpriseResult shape."""
    task_context = TaskContext(
        task_id=str(uuid.uuid4()),
        problem_id=problem.id,
        enterprise=enterprise_type.value,
        department="runtime",
        current_agent=getattr(agent, "agent_id", enterprise_type.value),
        task_description=f"{problem.title}\n{problem.description}",
        input_data=_build_task_agent_input_data(enterprise_type, problem, context),
        metadata={"source": "agent_interactions_adapter"},
    )
    task_result = await agent.process_task(task_context)
    output = task_result.output if isinstance(task_result.output, dict) else {"output": task_result.output}
    return EnhancedEnterpriseResult(
        enterprise=enterprise_type,
        totem_personality=_build_totem_personality(enterprise_type),
        status="completed" if task_result.success else "failed",
        insights=output,
        recommendations=output.get("recommendations", []) if isinstance(output.get("recommendations"), list) else [],
        confidence_score=float(task_result.confidence),
        processing_time=float(task_result.processing_time),
        dependencies=output.get("dependencies", []) if isinstance(output.get("dependencies"), list) else [],
        next_actions=output.get("next_actions", []) if isinstance(output.get("next_actions"), list) else [],
        personality_response=f"{enterprise_type.value} processed the problem",
        applied_rules=[],
        wisdom_insights=[],
        questions_for_next_cycle=[],
        timestamp=datetime.now(timezone.utc),
    )


async def _process_agent_with_fallback(
    enterprise_type: EnterpriseType,
    agent: Any,
    problem: ProblemStatement,
    context: Dict[str, Any],
) -> Any:
    """Run enhanced-processing agent path with process_task fallback."""
    if hasattr(agent, "process_problem_enhanced"):
        return await agent.process_problem_enhanced(problem, context)
    if hasattr(agent, "process_task"):
        return await _run_task_agent_as_enterprise_result(enterprise_type, agent, problem, context)
    raise AttributeError("Agent does not support process_problem_enhanced or process_task")


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/", summary="List all available agents")
async def list_agents(
    current_user: str = Depends(get_current_user),
    rate_limit: None = Depends(enforce_rate_limit),
):
    """Get information about all available enterprise agents"""
    global _agent_list_cache
    
    try:
        start_time = perf_counter()
        started_at = datetime.now(timezone.utc)
        # Return cached response if available (static data)
        if _agent_list_cache is not None:
            # Update timestamp only
            cached_response = _agent_list_cache.copy()
            cached_response["timestamp"] = datetime.now(timezone.utc).isoformat()
            AGENT_API_CACHE_HITS.labels(endpoint="list_agents", enterprise="all").inc()
            AGENT_API_REQUESTS.labels(
                endpoint="list_agents", enterprise="all", status="cached"
            ).inc()
            AGENT_API_LATENCY.labels(endpoint="list_agents", enterprise="all").observe(
                perf_counter() - start_time
            )
            return cached_response
        
        # Build agent list (only on first request or cache miss)
        agent_list = []
        for enterprise_type, agent in agents.items():
            # Get visual identity
            visual_identity = CosmicCouncilIdentity.get_enterprise_identity(enterprise_type)
            personality = agent.personality if hasattr(agent, 'personality') else None
            
            agent_list.append({
                "enterprise": enterprise_type.value,
                "name": visual_identity.name if visual_identity else (personality.name if personality else enterprise_type.value.replace('_', ' ').title()),
                "animal": visual_identity.animal if visual_identity else (personality.animal if personality else ""),
                "animal_emoji": visual_identity.animal_emoji if visual_identity else "",
                "symbol": visual_identity.symbol if visual_identity else "",
                "color": {
                    "name": visual_identity.color_name if visual_identity else "",
                    "hex": visual_identity.color_hex if visual_identity else (personality.color if personality else ""),
                    "rgb": list(visual_identity.color_rgb) if visual_identity else []
                },
                "core_principle": visual_identity.core_principle if visual_identity else (personality.core_principle if personality else ""),
                "role": visual_identity.role if visual_identity else "",
                "position": {
                    "number": visual_identity.position if visual_identity else list(EnterpriseType).index(enterprise_type),
                    "location": visual_identity.shape if visual_identity else "",
                    "angle": (visual_identity.position * 60) if visual_identity else (list(EnterpriseType).index(enterprise_type) * 60)
                },
                "is_available": True,
                "processing_order": list(EnterpriseType).index(enterprise_type)
            })
        
        # Get hexagon structure
        hexagon_structure = CosmicCouncilIdentity.get_hexagon_structure()
        
        # Build response
        response = {
            "success": True,
            "message": f"Retrieved {len(agent_list)} agents",
            "data": {
                "cosmic_council": {
                    "structure": "Hexagonal",
                    "philosophy": "Six perspectives, one solution",
                    "processing_flow": "ROYGBV (Clockwise)"
                },
                "hexagon": hexagon_structure,
                "agents": agent_list,
                "total_count": len(agent_list),
                "color_spectrum": "ROYGBV (Red, Orange, Yellow, Green, Blue, Purple)"
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Cache the response (without timestamp for consistency)
        _agent_list_cache = response.copy()
        AGENT_API_REQUESTS.labels(
            endpoint="list_agents", enterprise="all", status="success"
        ).inc()
        AGENT_API_LATENCY.labels(endpoint="list_agents", enterprise="all").observe(
            perf_counter() - start_time
        )
        return response
    except HTTPException:
        # Re-raise HTTP exceptions (like 401 Unauthorized) as-is
        AGENT_API_REQUESTS.labels(
            endpoint="list_agents", enterprise="all", status="error"
        ).inc()
        raise
    except Exception as e:
        logger.error(f"Failed to list agents: {str(e)}")
        AGENT_API_REQUESTS.labels(
            endpoint="list_agents", enterprise="all", status="error"
        ).inc()
        raise HTTPException(status_code=500, detail=f"Failed to list agents: {str(e)}")


@router.get("/{enterprise}", response_model=AgentInfoResponse, summary="Get agent information")
async def get_agent_info(
    enterprise: str,
    current_user: str = Depends(get_current_user),
    rate_limit: None = Depends(enforce_rate_limit),
):
    """Get detailed information about a specific agent"""
    try:
        start_time = perf_counter()
        agent = get_agent(enterprise)
        enterprise_type = EnterpriseType(enterprise.lower())
        
        # Get visual identity
        visual_identity = CosmicCouncilIdentity.get_enterprise_identity(enterprise_type)
        
        # Get personality information
        personality = agent.personality if hasattr(agent, 'personality') else None
        
        # Use visual identity as fallback if personality not available
        if not personality and visual_identity:
            # Create a basic personality from visual identity
            from ..core.core import TotemPersonality
            personality = TotemPersonality(
                name=visual_identity.name,
                animal=visual_identity.animal,
                color=visual_identity.color_hex,
                core_principle=visual_identity.core_principle,
                communication_style="Direct",
                thinking_pattern="Systematic",
                strengths=["Analysis"],
                wisdom_approach="Structured",
                metaphor=f"A {visual_identity.animal} representing {visual_identity.core_principle}",
                greeting=f"Greetings from {visual_identity.name}",
                closing="May wisdom guide your path"
            )
        
        if not personality:
            raise HTTPException(
                status_code=404,
                detail=f"Agent {enterprise} does not have personality or visual identity information"
            )
        
        # Get applicable rules
        applicable_rules = agent.applicable_rules if hasattr(agent, 'applicable_rules') else []
        rule_names = [rule.value if isinstance(rule, CosmicCouncilRule) else str(rule) 
                     for rule in applicable_rules]
        
        response = AgentInfoResponse(
            enterprise=enterprise_type.value,
            name=visual_identity.name if visual_identity else personality.name,
            animal=visual_identity.animal if visual_identity else personality.animal,
            color=visual_identity.color_hex if visual_identity else personality.color,
            core_principle=visual_identity.core_principle if visual_identity else personality.core_principle,
            communication_style=personality.communication_style,
            thinking_pattern=personality.thinking_pattern,
            strengths=personality.strengths,
            expertise_areas=getattr(agent, 'expertise_areas', []),
            processing_order=list(EnterpriseType).index(enterprise_type),
            applicable_rules=rule_names,
            greeting=personality.greeting,
            closing=personality.closing
        )
        AGENT_API_REQUESTS.labels(
            endpoint="get_agent_info", enterprise=enterprise_type.value, status="success"
        ).inc()
        AGENT_API_LATENCY.labels(
            endpoint="get_agent_info", enterprise=enterprise_type.value
        ).observe(perf_counter() - start_time)
        return response
    except HTTPException:
        AGENT_API_REQUESTS.labels(
            endpoint="get_agent_info", enterprise=enterprise, status="error"
        ).inc()
        raise
    except Exception as e:
        logger.error(f"Failed to get agent info: {str(e)}")
        AGENT_API_REQUESTS.labels(
            endpoint="get_agent_info", enterprise=enterprise, status="error"
        ).inc()
        raise HTTPException(status_code=500, detail=f"Failed to get agent info: {str(e)}")


@router.post("/{enterprise}/process", response_model=AgentProcessResponse, summary="Process problem with agent")
async def process_with_agent(
    enterprise: str,
    request: AgentProcessRequest,
    response: Response,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user),
    rate_limit: None = Depends(enforce_rate_limit),
):
    """Process a problem using a specific enterprise agent"""
    try:
        start_time = perf_counter()
        started_at = datetime.now(timezone.utc)
        cache_key = None
        if not request.webhook_url:
            cache_key = _cache_key(enterprise, request)
            cached_response = _get_cached_response(cache_key)
            if cached_response:
                response.headers["X-Cache"] = "HIT"
                AGENT_API_CACHE_HITS.labels(endpoint="process", enterprise=enterprise).inc()
                AGENT_API_REQUESTS.labels(
                    endpoint="process", enterprise=enterprise, status="cached"
                ).inc()
                AGENT_API_LATENCY.labels(endpoint="process", enterprise=enterprise).observe(
                    perf_counter() - start_time
                )
                return cached_response
        response.headers["X-Cache"] = "MISS"

        agent = get_agent(enterprise)
        enterprise_type = EnterpriseType(enterprise.lower())
        
        # Convert request to ProblemStatement
        problem = ProblemStatement(
            title=request.title,
            description=request.description,
            domain=request.domain,
            complexity=ProblemComplexity(request.complexity),
            stakeholders=request.stakeholders,
            constraints=request.constraints,
            success_criteria=request.success_criteria
        )
        
        # Get analysis depth
        analysis_depth = get_analysis_depth(request.analysis_depth)
        
        # Set analysis depth if agent supports it
        if hasattr(agent, 'set_analysis_depth'):
            agent.set_analysis_depth(analysis_depth)
        
        # Process problem
        try:
            result = await _process_agent_with_fallback(enterprise_type, agent, problem, request.context)
        except HTTPException:
            # Re-raise HTTP exceptions (like 401 Unauthorized) as-is
            raise
        except AttributeError as e:
            logger.error(f"Agent {enterprise} missing method: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Agent {enterprise} is not properly initialized: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error processing with agent {enterprise}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error processing problem with agent {enterprise}: {str(e)}"
            )
        processing_time = (datetime.now(timezone.utc) - started_at).total_seconds()
        
        # Handle different result types (EnhancedResult vs EnhancedEnterpriseResult)
        if hasattr(result, 'specialized_analysis'):
            # EnhancedResult from working_enhanced_agents
            agent_name = getattr(agent, "name", enterprise_type.value.replace("_", " ").title())
            agent_animal = getattr(agent, "animal", "")
            if agent_animal:
                personality_response = f"{agent_name} ({agent_animal}) processed the problem"
            else:
                personality_response = f"{agent_name} processed the problem"
            payload = AgentProcessResponse(
                enterprise=enterprise_type.value,
                status=result.status,
                confidence_score=result.confidence_score,
                processing_time=processing_time,
                insights=result.specialized_analysis,
                recommendations=result.recommendations,
                next_actions=result.next_actions,
                dependencies=[],
                personality_response=personality_response,
                applied_rules=[],
                wisdom_insights=[],
                questions_for_next_cycle=[],
                timestamp=datetime.fromisoformat(result.timestamp) if isinstance(result.timestamp, str) else result.timestamp
            ).model_dump()
        else:
            # EnhancedEnterpriseResult from core.core
            payload = AgentProcessResponse(
                enterprise=enterprise_type.value,
                status=result.status,
                confidence_score=result.confidence_score,
                processing_time=processing_time,
                insights=result.insights,
                recommendations=result.recommendations,
                next_actions=result.next_actions,
                dependencies=result.dependencies,
                personality_response=result.personality_response,
                applied_rules=[rule.value if isinstance(rule, CosmicCouncilRule) else str(rule) 
                              for rule in result.applied_rules],
                wisdom_insights=result.wisdom_insights,
                questions_for_next_cycle=result.questions_for_next_cycle,
                timestamp=result.timestamp
            ).model_dump()

        if cache_key:
            _set_cached_response(cache_key, payload)

        if request.webhook_url:
            webhook_url = _validate_webhook_url(request.webhook_url)
            background_tasks.add_task(
                dispatch_webhook,
                webhook_url,
                {"event": "agent.processed", "enterprise": enterprise_type.value, "data": payload},
            )

        AGENT_API_REQUESTS.labels(
            endpoint="process", enterprise=enterprise_type.value, status="success"
        ).inc()
        AGENT_API_LATENCY.labels(endpoint="process", enterprise=enterprise_type.value).observe(
            perf_counter() - start_time
        )
        return payload
    except HTTPException:
        AGENT_API_REQUESTS.labels(
            endpoint="process", enterprise=enterprise, status="error"
        ).inc()
        raise
    except Exception as e:
        logger.error(f"Failed to process with agent {enterprise}: {str(e)}")
        AGENT_API_REQUESTS.labels(
            endpoint="process", enterprise=enterprise, status="error"
        ).inc()
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to process with agent {enterprise}: {str(e)}"
        )


@router.post("/sequence", response_model=AgentSequenceResponse, summary="Process through agent sequence")
async def process_agent_sequence(
    request: AgentSequenceRequest,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user),
    rate_limit: None = Depends(enforce_rate_limit),
):
    """Process a problem through a sequence of agents in order"""
    try:
        start_time = perf_counter()
        sequence_id = str(uuid.uuid4())
        started_at = datetime.now(timezone.utc)
        
        # Convert problem request to ProblemStatement
        problem = ProblemStatement(
            title=request.problem.title,
            description=request.problem.description,
            domain=request.problem.domain,
            complexity=ProblemComplexity(request.problem.complexity),
            stakeholders=request.problem.stakeholders,
            constraints=request.problem.constraints,
            success_criteria=request.problem.success_criteria
        )
        
        agent_results = {}
        context = request.problem.context.copy()
        
        # Process through sequence
        if request.parallel:
            # Process agents in parallel
            tasks = []
            for agent_name in request.agent_sequence:
                agent = get_agent(agent_name)
                enterprise_type = EnterpriseType(agent_name)
                tasks.append(_process_agent_with_fallback(enterprise_type, agent, problem, context))
            
            results = await asyncio.gather(*tasks)
            for agent_name, result in zip(request.agent_sequence, results):
                # Handle different result types (EnhancedResult vs EnhancedEnterpriseResult)
                if hasattr(result, 'specialized_analysis'):
                    # EnhancedResult from working_enhanced_agents
                    insights = result.specialized_analysis
                    recommendations = result.recommendations
                    next_actions = result.next_actions
                    dependencies = []
                    personality_response = f"{result.enterprise} processed the problem"
                    applied_rules = []
                    wisdom_insights = []
                    questions_for_next_cycle = []
                else:
                    # EnhancedEnterpriseResult from core.core
                    insights = result.insights if hasattr(result, 'insights') else {}
                    recommendations = result.recommendations if hasattr(result, 'recommendations') else []
                    next_actions = result.next_actions if hasattr(result, 'next_actions') else []
                    dependencies = result.dependencies if hasattr(result, 'dependencies') else []
                    personality_response = result.personality_response if hasattr(result, 'personality_response') else ""
                    applied_rules = [rule.value if isinstance(rule, CosmicCouncilRule) else str(rule) 
                                    for rule in (result.applied_rules if hasattr(result, 'applied_rules') else [])]
                    wisdom_insights = result.wisdom_insights if hasattr(result, 'wisdom_insights') else []
                    questions_for_next_cycle = result.questions_for_next_cycle if hasattr(result, 'questions_for_next_cycle') else []
                
                agent_results[agent_name] = AgentProcessResponse(
                    enterprise=agent_name,
                    status=result.status,
                    confidence_score=result.confidence_score,
                    processing_time=result.processing_time,
                    insights=insights,
                    recommendations=recommendations,
                    next_actions=next_actions,
                    dependencies=dependencies,
                    personality_response=personality_response,
                    applied_rules=applied_rules,
                    wisdom_insights=wisdom_insights,
                    questions_for_next_cycle=questions_for_next_cycle,
                    timestamp=result.timestamp if hasattr(result, 'timestamp') else datetime.now(timezone.utc).isoformat()
                )
        else:
            # Process agents sequentially
            for agent_name in request.agent_sequence:
                agent = get_agent(agent_name)
                enterprise_type = EnterpriseType(agent_name)
                result = await _process_agent_with_fallback(enterprise_type, agent, problem, context)
                
                # Handle different result types (EnhancedResult vs EnhancedEnterpriseResult)
                if hasattr(result, 'specialized_analysis'):
                    # EnhancedResult from working_enhanced_agents
                    insights = result.specialized_analysis
                    recommendations = result.recommendations
                    next_actions = result.next_actions
                    dependencies = []
                    personality_response = f"{result.enterprise} processed the problem"
                    applied_rules = []
                    wisdom_insights = []
                    questions_for_next_cycle = []
                else:
                    # EnhancedEnterpriseResult from core.core
                    insights = result.insights if hasattr(result, 'insights') else {}
                    recommendations = result.recommendations if hasattr(result, 'recommendations') else []
                    next_actions = result.next_actions if hasattr(result, 'next_actions') else []
                    dependencies = result.dependencies if hasattr(result, 'dependencies') else []
                    personality_response = result.personality_response if hasattr(result, 'personality_response') else ""
                    applied_rules = [rule.value if isinstance(rule, CosmicCouncilRule) else str(rule) 
                                    for rule in (result.applied_rules if hasattr(result, 'applied_rules') else [])]
                    wisdom_insights = result.wisdom_insights if hasattr(result, 'wisdom_insights') else []
                    questions_for_next_cycle = result.questions_for_next_cycle if hasattr(result, 'questions_for_next_cycle') else []
                
                agent_results[agent_name] = AgentProcessResponse(
                    enterprise=agent_name,
                    status=result.status,
                    confidence_score=result.confidence_score,
                    processing_time=result.processing_time,
                    insights=insights,
                    recommendations=recommendations,
                    next_actions=next_actions,
                    dependencies=dependencies,
                    personality_response=personality_response,
                    applied_rules=applied_rules,
                    wisdom_insights=wisdom_insights,
                    questions_for_next_cycle=questions_for_next_cycle,
                    timestamp=result.timestamp if hasattr(result, 'timestamp') else datetime.now(timezone.utc).isoformat()
                )
                
                # Update context with results for next agent
                context[f"{agent_name}_result"] = insights
                context[f"{agent_name}_recommendations"] = recommendations
        
        # Synthesize results if requested
        synthesis = None
        if request.synthesize and council:
            try:
                cycle_result = EnhancedCycleResult(
                    cycle_id=sequence_id,
                    problem=problem,
                    status="completed",
                    enterprise_results={
                        EnterpriseType(agent_name): result 
                        for agent_name, result in agent_results.items()
                    }
                )
                synthesis = await council._synthesize_results(cycle_result)
            except Exception as e:
                logger.warning(f"Failed to synthesize results: {str(e)}")
        
        # Calculate overall confidence
        confidences = [r.confidence_score for r in agent_results.values()]
        overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        # Determine next recommended agent
        next_agent = None
        if request.agent_sequence and len(request.agent_sequence) < 6:
            # Recommend next agent in ROYGBV order
            all_agents = ['red_owl', 'orange_orangutan', 'yellow_honeybee', 
                         'green_tortoise', 'blue_dolphin', 'purple_elephant']
            last_agent = request.agent_sequence[-1]
            if last_agent in all_agents:
                last_index = all_agents.index(last_agent)
                if last_index < len(all_agents) - 1:
                    next_agent = all_agents[last_index + 1]
        
        total_time = (datetime.now(timezone.utc) - started_at).total_seconds()

        payload = AgentSequenceResponse(
            sequence_id=sequence_id,
            status="completed",
            total_processing_time=total_time,
            agent_results=agent_results,
            synthesis=synthesis,
            overall_confidence=overall_confidence,
            next_recommended_agent=next_agent,
            timestamp=datetime.now(timezone.utc)
        ).model_dump()

        if request.webhook_url:
            webhook_url = _validate_webhook_url(request.webhook_url)
            background_tasks.add_task(
                dispatch_webhook,
                webhook_url,
                {"event": "agent.sequence_completed", "sequence_id": sequence_id, "data": payload},
            )

        AGENT_API_REQUESTS.labels(
            endpoint="sequence", enterprise="sequence", status="success"
        ).inc()
        AGENT_API_LATENCY.labels(endpoint="sequence", enterprise="sequence").observe(
            perf_counter() - start_time
        )
        return payload
    except HTTPException:
        # Re-raise HTTP exceptions (like 401 Unauthorized) as-is
        AGENT_API_REQUESTS.labels(
            endpoint="sequence", enterprise="sequence", status="error"
        ).inc()
        raise
    except Exception as e:
        logger.error(f"Failed to process agent sequence: {str(e)}")
        AGENT_API_REQUESTS.labels(
            endpoint="sequence", enterprise="sequence", status="error"
        ).inc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process agent sequence: {str(e)}"
        )


@router.post("/collaborate", response_model=AgentSequenceResponse, summary="Collaborate multiple agents")
async def collaborate_agents(
    request: AgentCollaborationRequest,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user),
    rate_limit: None = Depends(enforce_rate_limit),
):
    """Have multiple agents collaborate on a problem"""
    try:
        start_time = perf_counter()
        # Convert to sequence request
        sequence_request = AgentSequenceRequest(
            problem=request.problem,
            agent_sequence=request.collaborating_agents,
            parallel=(request.collaboration_mode == "parallel"),
            synthesize=True,
            webhook_url=request.webhook_url,
        )
        
        payload = await process_agent_sequence(sequence_request, background_tasks, current_user)
        AGENT_API_REQUESTS.labels(
            endpoint="collaborate", enterprise="collaborate", status="success"
        ).inc()
        AGENT_API_LATENCY.labels(endpoint="collaborate", enterprise="collaborate").observe(
            perf_counter() - start_time
        )
        return payload
    except HTTPException:
        # Re-raise HTTP exceptions (like 401 Unauthorized) as-is
        AGENT_API_REQUESTS.labels(
            endpoint="collaborate", enterprise="collaborate", status="error"
        ).inc()
        raise
    except Exception as e:
        logger.error(f"Failed to collaborate agents: {str(e)}")
        AGENT_API_REQUESTS.labels(
            endpoint="collaborate", enterprise="collaborate", status="error"
        ).inc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to collaborate agents: {str(e)}"
        )


@router.get("/{enterprise}/status", response_model=AgentStatusResponse, summary="Get agent status")
async def get_agent_status(
    enterprise: str,
    current_user: str = Depends(get_current_user),
    rate_limit: None = Depends(enforce_rate_limit),
):
    """Get current status and statistics for an agent"""
    try:
        start_time = perf_counter()
        agent = get_agent(enterprise)
        enterprise_type = EnterpriseType(enterprise.lower())
        
        # Get agent statistics (if available)
        stats = {
            "current_processing_count": getattr(agent, 'current_processing_count', 0),
            "total_processed": getattr(agent, 'total_processed', 0),
            "average_confidence": getattr(agent, 'average_confidence', 0.0),
            "average_processing_time": getattr(agent, 'average_processing_time', 0.0),
            "last_activity": getattr(agent, 'last_activity', None)
        }
        
        response = AgentStatusResponse(
            enterprise=enterprise_type.value,
            status="available" if agent else "unavailable",
            is_available=agent is not None,
            **stats
        )
        AGENT_API_REQUESTS.labels(
            endpoint="get_agent_status", enterprise=enterprise_type.value, status="success"
        ).inc()
        AGENT_API_LATENCY.labels(
            endpoint="get_agent_status", enterprise=enterprise_type.value
        ).observe(perf_counter() - start_time)
        return response
    except HTTPException:
        AGENT_API_REQUESTS.labels(
            endpoint="get_agent_status", enterprise=enterprise, status="error"
        ).inc()
        raise
    except Exception as e:
        logger.error(f"Failed to get agent status: {str(e)}")
        AGENT_API_REQUESTS.labels(
            endpoint="get_agent_status", enterprise=enterprise, status="error"
        ).inc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get agent status: {str(e)}"
        )


@router.post("/roygbv/cycle", summary="Execute full ROYGBV cycle")
async def execute_roygbv_cycle(
    request: AgentProcessRequest,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user),
    rate_limit: None = Depends(enforce_rate_limit),
):
    """Execute a complete ROYGBV cycle through all agents in order"""
    try:
        start_time = perf_counter()
        # Create sequence request with full ROYGBV order
        sequence_request = AgentSequenceRequest(
            problem=request,
            agent_sequence=['red_owl', 'orange_orangutan', 'yellow_honeybee',
                          'green_tortoise', 'blue_dolphin', 'purple_elephant'],
            parallel=False,
            synthesize=True,
            webhook_url=request.webhook_url,
        )
        
        payload = await process_agent_sequence(sequence_request, background_tasks, current_user)
        AGENT_API_REQUESTS.labels(
            endpoint="roygbv_cycle", enterprise="roygbv", status="success"
        ).inc()
        AGENT_API_LATENCY.labels(endpoint="roygbv_cycle", enterprise="roygbv").observe(
            perf_counter() - start_time
        )
        return payload
    except HTTPException:
        # Re-raise HTTP exceptions (like 401 Unauthorized) as-is
        AGENT_API_REQUESTS.labels(
            endpoint="roygbv_cycle", enterprise="roygbv", status="error"
        ).inc()
        raise
    except Exception as e:
        logger.error(f"Failed to execute ROYGBV cycle: {str(e)}")
        AGENT_API_REQUESTS.labels(
            endpoint="roygbv_cycle", enterprise="roygbv", status="error"
        ).inc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute ROYGBV cycle: {str(e)}"
        )


# ============================================================================
# Initialization Function
# ============================================================================

def initialize_agents(council_instance: Optional[CosmicCouncilHexagon] = None):
    """Initialize agent instances"""
    global agents, council, _agent_list_cache
    
    council = council_instance
    # Clear cache when agents are reinitialized
    _agent_list_cache = None
    
    # Initialize available agents with comprehensive analysis depth
    agents[EnterpriseType.RED_OWL] = WorkingEnhancedRedOwlAgent(AnalysisDepth.COMPREHENSIVE)
    agents[EnterpriseType.ORANGE_ORANGUTAN] = WorkingEnhancedOrangeOrangutanAgent(AnalysisDepth.COMPREHENSIVE)

    # Initialize recovered task-style agents (adapted at runtime via process_task fallback).
    from ..core.core import EnhancedEnterpriseAgent
    try:
        from ..agents.yellow_honeybee.agent import create_yellow_honeybee_agent
        from ..agents.green_turtle.agent import create_green_turtle_agent
        from ..agents.blue_dolphin.agent import create_blue_dolphin_agent
        from ..agents.purple_elephant.agent import create_purple_elephant_agent
        recovered_initializers = {
            EnterpriseType.YELLOW_HONEYBEE: ("Yellow Honeybee", create_yellow_honeybee_agent),
            EnterpriseType.GREEN_TORTOISE: ("Green Tortoise", create_green_turtle_agent),
            EnterpriseType.BLUE_DOLPHIN: ("Blue Dolphin", create_blue_dolphin_agent),
            EnterpriseType.PURPLE_ELEPHANT: ("Purple Elephant", create_purple_elephant_agent),
        }
    except Exception as exc:
        logger.warning(f"Recovered agent module imports failed: {exc}")
        recovered_initializers = {}

    for enterprise_type, (label, factory) in recovered_initializers.items():
        try:
            agents[enterprise_type] = factory()
            logger.info(f"Loaded recovered {label} agent")
        except Exception as exc:
            agents[enterprise_type] = EnhancedEnterpriseAgent(enterprise_type)
            logger.warning(f"Using base agent for {enterprise_type.value} (recovered initialization failed: {exc})")

    # Ensure all enterprises are initialized even if recovered imports failed.
    for enterprise_type in [
        EnterpriseType.YELLOW_HONEYBEE,
        EnterpriseType.GREEN_TORTOISE,
        EnterpriseType.BLUE_DOLPHIN,
        EnterpriseType.PURPLE_ELEPHANT,
    ]:
        if enterprise_type not in agents:
            agents[enterprise_type] = EnhancedEnterpriseAgent(enterprise_type)
            logger.warning(f"Using base agent for {enterprise_type.value} (recovered implementation unavailable)")

    enhanced_count = len(
        [
            a for a in agents.values()
            if isinstance(a, (WorkingEnhancedRedOwlAgent, WorkingEnhancedOrangeOrangutanAgent))
        ]
    )
    logger.info(f"Initialized {len(agents)} enterprise agents ({enhanced_count} working-enhanced, {len(agents) - enhanced_count} adapted/base)")

def pre_warm_agent_list_cache():
    """Pre-warm the agent list cache on startup"""
    global _agent_list_cache, agents
    
    try:
        if not agents:
            logger.warning("Cannot pre-warm cache: agents not initialized")
            return
        
        # Build agent list (same logic as list_agents endpoint)
        agent_list = []
        for enterprise_type, agent in agents.items():
            # Get visual identity
            visual_identity = CosmicCouncilIdentity.get_enterprise_identity(enterprise_type)
            personality = agent.personality if hasattr(agent, 'personality') else None
            
            agent_list.append({
                "enterprise": enterprise_type.value,
                "name": visual_identity.name if visual_identity else (personality.name if personality else enterprise_type.value.replace('_', ' ').title()),
                "animal": visual_identity.animal if visual_identity else (personality.animal if personality else ""),
                "animal_emoji": visual_identity.animal_emoji if visual_identity else "",
                "symbol": visual_identity.symbol if visual_identity else "",
                "color": {
                    "name": visual_identity.color_name if visual_identity else "",
                    "hex": visual_identity.color_hex if visual_identity else (personality.color if personality else ""),
                    "rgb": list(visual_identity.color_rgb) if visual_identity else []
                },
                "core_principle": visual_identity.core_principle if visual_identity else (personality.core_principle if personality else ""),
                "role": visual_identity.role if visual_identity else "",
                "position": {
                    "number": visual_identity.position if visual_identity else list(EnterpriseType).index(enterprise_type),
                    "location": visual_identity.shape if visual_identity else "",
                    "angle": (visual_identity.position * 60) if visual_identity else (list(EnterpriseType).index(enterprise_type) * 60)
                },
                "is_available": True,
                "processing_order": list(EnterpriseType).index(enterprise_type)
            })
        
        # Get hexagon structure
        hexagon_structure = CosmicCouncilIdentity.get_hexagon_structure()
        
        # Build response
        _agent_list_cache = {
            "success": True,
            "message": f"Retrieved {len(agent_list)} agents",
            "data": {
                "cosmic_council": {
                    "structure": "Hexagonal",
                    "philosophy": "Six perspectives, one solution",
                    "processing_flow": "ROYGBV (Clockwise)"
                },
                "hexagon": hexagon_structure,
                "agents": agent_list,
                "total_count": len(agent_list),
                "color_spectrum": "ROYGBV (Red, Orange, Yellow, Green, Blue, Purple)"
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info("Agent list cache pre-warmed successfully")
    except Exception as e:
        logger.warning(f"Failed to pre-warm agent list cache: {e}")

