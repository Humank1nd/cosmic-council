"""
Memory API Endpoints
====================

REST API for memory query, graph traversal, and agent history.

Endpoints:
- POST /api/v1/memory/query - Query memory with filters
- GET /api/v1/memory/graph/{problem_id} - Get knowledge graph for problem
- GET /api/v1/memory/agent/{agent_id}/history - Get agent memory history
- GET /api/v1/memory/entity/{entity_id} - Get single entity
- GET /api/v1/memory/entity/{entity_id}/related - Get related entities
- POST /api/v1/memory/ingest - Ingest cycle output
- GET /api/v1/memory/stats - Get memory statistics
- GET /api/v1/memory/conflicts - List pending conflicts
- POST /api/v1/memory/conflicts/{conflict_id}/resolve - Resolve conflict
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field

from .schemas import (
    MemoryQuery,
    MemoryResult,
    EntityType,
    RelationType,
    MemoryLayer,
)
from .store import GraphStore, get_graph_store
from .retrieval import RoleAwareRetriever, RetrievalConfig, RankingStrategy
from .consolidation import MemoryPipeline, ConsolidationResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/memory", tags=["memory"])

# Global instances (should be dependency injected in production)
_store: Optional[GraphStore] = None
_retriever: Optional[RoleAwareRetriever] = None
_pipeline: Optional[MemoryPipeline] = None


async def get_store() -> GraphStore:
    """Get or initialize the graph store."""
    global _store
    if _store is None:
        _store = get_graph_store("sqlite", db_path="data/memory_graph.db")
        await _store.initialize()
    return _store


async def get_retriever() -> RoleAwareRetriever:
    """Get or initialize the retriever."""
    global _retriever
    if _retriever is None:
        store = await get_store()
        _retriever = RoleAwareRetriever(store, RetrievalConfig())
    return _retriever


async def get_pipeline() -> MemoryPipeline:
    """Get or initialize the pipeline."""
    global _pipeline
    if _pipeline is None:
        store = await get_store()
        _pipeline = MemoryPipeline(store)
    return _pipeline


# Request/Response Models

class MemoryQueryRequest(BaseModel):
    """Request model for memory queries."""
    query_text: Optional[str] = Field(None, description="Text to search for")
    entity_types: Optional[List[str]] = Field(None, description="Entity types to filter")
    layers: Optional[List[str]] = Field(None, description="Memory layers to search")
    tags: Optional[List[str]] = Field(None, description="Tags to filter by")
    min_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Minimum confidence")
    problem_id: Optional[str] = Field(None, description="Filter by problem ID")
    cycle_id: Optional[str] = Field(None, description="Filter by cycle ID")
    role: Optional[str] = Field(None, description="Agent role for role-aware ranking")
    strategy: str = Field("balanced", description="Ranking strategy")
    limit: int = Field(20, ge=1, le=100, description="Maximum results")
    offset: int = Field(0, ge=0, description="Result offset")
    include_archived: bool = Field(False, description="Include archived entities")


class MemoryQueryResponse(BaseModel):
    """Response model for memory queries."""
    entities: List[Dict[str, Any]]
    facts: List[Dict[str, Any]]
    relations: List[Dict[str, Any]]
    total_count: int
    query_time_ms: float
    relevance_scores: Dict[str, float]


class EntityResponse(BaseModel):
    """Response model for single entity."""
    entity: Dict[str, Any]


class RelatedEntitiesResponse(BaseModel):
    """Response model for related entities."""
    entity_id: str
    incoming: List[Dict[str, Any]]
    outgoing: List[Dict[str, Any]]
    relations: List[Dict[str, Any]]


class GraphResponse(BaseModel):
    """Response model for knowledge graph."""
    problem_id: str
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    depth_reached: int
    total_nodes: int
    total_edges: int


class AgentHistoryResponse(BaseModel):
    """Response model for agent history."""
    agent_id: str
    entities: List[Dict[str, Any]]
    facts: List[Dict[str, Any]]
    total_count: int


class IngestRequest(BaseModel):
    """Request model for ingesting cycle output."""
    cycle_id: str
    problem_id: str
    agent_reports: Dict[str, Dict[str, Any]]
    tenant_id: Optional[str] = None


class IngestResponse(BaseModel):
    """Response model for ingest operation."""
    success: bool
    entities_created: int
    facts_created: int
    relations_created: int
    duplicates_merged: int
    conflicts_detected: int
    duration_ms: float
    error: Optional[str] = None


class StatsResponse(BaseModel):
    """Response model for memory statistics."""
    total_entities: int
    total_relations: int
    total_facts: int
    entities_by_type: Dict[str, int]
    backend: str


class ConflictResponse(BaseModel):
    """Response model for conflict."""
    conflict_type: str
    entity_ids: List[str]
    description: str
    confidence: float
    requires_human_review: bool
    suggested_resolution: Optional[str]
    created_at: str


class ConflictsListResponse(BaseModel):
    """Response model for conflicts list."""
    conflicts: List[ConflictResponse]
    total_count: int


class ResolveConflictRequest(BaseModel):
    """Request for resolving a conflict."""
    resolution: str = Field(..., description="Resolution action: keep_first, keep_second, merge, archive_both")
    notes: Optional[str] = None


# Endpoints

@router.post("/query", response_model=MemoryQueryResponse)
async def query_memory(
    request: MemoryQueryRequest,
    retriever: RoleAwareRetriever = Depends(get_retriever),
):
    """
    Query memory with filters and role-aware ranking.

    Supports text search, entity type filtering, confidence thresholds,
    and role-specific ranking strategies.
    """
    try:
        # Build query
        entity_types = None
        if request.entity_types:
            entity_types = [EntityType(t) for t in request.entity_types]

        layers = None
        if request.layers:
            layers = [MemoryLayer(l) for l in request.layers]

        query = MemoryQuery(
            query_text=request.query_text,
            entity_types=entity_types,
            layers=layers,
            tags=request.tags,
            min_confidence=request.min_confidence,
            problem_id=request.problem_id,
            cycle_id=request.cycle_id,
            requester_role=request.role,
            limit=request.limit,
            offset=request.offset,
            include_archived=request.include_archived,
        )

        # Map strategy
        strategy_map = {
            "relevance": RankingStrategy.RELEVANCE,
            "recency": RankingStrategy.RECENCY,
            "confidence": RankingStrategy.CONFIDENCE,
            "balanced": RankingStrategy.BALANCED,
            "role_optimized": RankingStrategy.ROLE_OPTIMIZED,
        }
        strategy = strategy_map.get(request.strategy, RankingStrategy.BALANCED)

        # Execute query
        result = await retriever.retrieve(query, role=request.role, strategy=strategy)

        return MemoryQueryResponse(
            entities=[e.to_dict() for e in result.entities],
            facts=[f.to_dict() for f in result.facts],
            relations=[r.to_dict() for r in result.relations],
            total_count=result.total_count,
            query_time_ms=result.query_time_ms,
            relevance_scores=result.relevance_scores,
        )

    except Exception as e:
        logger.error(f"Query error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/graph/{problem_id}", response_model=GraphResponse)
async def get_problem_graph(
    problem_id: str,
    max_depth: int = Query(3, ge=1, le=5),
    relation_types: Optional[str] = Query(None, description="Comma-separated relation types"),
    store: GraphStore = Depends(get_store),
):
    """
    Get the knowledge graph for a specific problem.

    Returns all entities and relations connected to the problem,
    up to the specified depth.
    """
    try:
        # Parse relation types
        rel_types = None
        if relation_types:
            rel_types = [RelationType(t.strip()) for t in relation_types.split(",")]

        # Find problem entity
        from .schemas import MemoryQuery
        query = MemoryQuery(
            entity_types=[EntityType.PROBLEM],
            query_text=problem_id,
            limit=1,
        )
        problems = await store.query_entities(query)

        if not problems:
            # Try to find cycle with this problem_id
            query = MemoryQuery(
                entity_types=[EntityType.CYCLE],
                limit=50,
            )
            cycles = await store.query_entities(query)
            start_entity = None
            for cycle in cycles:
                if cycle.properties.get("problem_id") == problem_id:
                    start_entity = cycle
                    break

            if not start_entity:
                raise HTTPException(status_code=404, detail=f"Problem {problem_id} not found")
        else:
            start_entity = problems[0]

        # Traverse graph
        graph = await store.traverse(
            start_id=start_entity.id,
            relation_types=rel_types,
            max_depth=max_depth,
            direction="outgoing",
        )

        return GraphResponse(
            problem_id=problem_id,
            nodes=graph["nodes"],
            edges=graph["edges"],
            depth_reached=graph["depth_reached"],
            total_nodes=len(graph["nodes"]),
            total_edges=len(graph["edges"]),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Graph traversal error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agent/{agent_id}/history", response_model=AgentHistoryResponse)
async def get_agent_history(
    agent_id: str,
    limit: int = Query(20, ge=1, le=100),
    retriever: RoleAwareRetriever = Depends(get_retriever),
):
    """
    Get memory history for a specific agent.

    Returns all entities and facts created by this agent.
    """
    try:
        result = await retriever.retrieve_agent_history(agent_id, limit=limit)

        return AgentHistoryResponse(
            agent_id=agent_id,
            entities=[e.to_dict() for e in result.entities],
            facts=[f.to_dict() for f in result.facts],
            total_count=result.total_count,
        )

    except Exception as e:
        logger.error(f"Agent history error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entity/{entity_id}", response_model=EntityResponse)
async def get_entity(
    entity_id: str,
    store: GraphStore = Depends(get_store),
):
    """Get a single entity by ID."""
    try:
        entity = await store.get_entity(entity_id)
        if not entity:
            raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")

        return EntityResponse(entity=entity.to_dict())

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Entity fetch error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entity/{entity_id}/related", response_model=RelatedEntitiesResponse)
async def get_related_entities(
    entity_id: str,
    store: GraphStore = Depends(get_store),
):
    """Get entities related to the specified entity."""
    try:
        entity = await store.get_entity(entity_id)
        if not entity:
            raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")

        # Get incoming and outgoing relations
        incoming_rels = await store.get_relations(entity_id, direction="incoming")
        outgoing_rels = await store.get_relations(entity_id, direction="outgoing")

        # Fetch related entities
        incoming_entities = []
        for rel in incoming_rels:
            related = await store.get_entity(rel.source_id)
            if related:
                incoming_entities.append(related.to_dict())

        outgoing_entities = []
        for rel in outgoing_rels:
            related = await store.get_entity(rel.target_id)
            if related:
                outgoing_entities.append(related.to_dict())

        return RelatedEntitiesResponse(
            entity_id=entity_id,
            incoming=incoming_entities,
            outgoing=outgoing_entities,
            relations=[r.to_dict() for r in incoming_rels + outgoing_rels],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Related entities error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest", response_model=IngestResponse)
async def ingest_cycle_output(
    request: IngestRequest,
    pipeline: MemoryPipeline = Depends(get_pipeline),
):
    """
    Ingest cycle output into memory.

    Processes agent reports, creates entities and relations,
    and runs consolidation.
    """
    try:
        result = await pipeline.ingest_cycle_output(
            cycle_id=request.cycle_id,
            problem_id=request.problem_id,
            agent_reports=request.agent_reports,
            tenant_id=request.tenant_id,
        )

        return IngestResponse(
            success=result.success,
            entities_created=result.entities_created,
            facts_created=result.facts_created,
            relations_created=result.relations_created,
            duplicates_merged=result.duplicates_merged,
            conflicts_detected=result.conflicts_detected,
            duration_ms=result.duration_ms,
            error=result.error,
        )

    except Exception as e:
        logger.error(f"Ingest error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=StatsResponse)
async def get_memory_stats(
    store: GraphStore = Depends(get_store),
):
    """Get memory storage statistics."""
    try:
        stats = await store.get_stats()

        return StatsResponse(
            total_entities=stats["total_entities"],
            total_relations=stats["total_relations"],
            total_facts=stats["total_facts"],
            entities_by_type=stats["entities_by_type"],
            backend=stats["backend"],
        )

    except Exception as e:
        logger.error(f"Stats error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conflicts", response_model=ConflictsListResponse)
async def list_conflicts(
    pending_only: bool = Query(True, description="Only show pending conflicts"),
    limit: int = Query(50, ge=1, le=200),
):
    """List detected conflicts requiring review."""
    # In production, this would query a conflicts table
    # For now, return empty list
    return ConflictsListResponse(
        conflicts=[],
        total_count=0,
    )


@router.post("/conflicts/{conflict_id}/resolve")
async def resolve_conflict(
    conflict_id: str,
    request: ResolveConflictRequest,
    store: GraphStore = Depends(get_store),
):
    """Resolve a detected conflict."""
    # In production, this would update the conflict status
    # and apply the resolution
    return {
        "conflict_id": conflict_id,
        "resolution": request.resolution,
        "status": "resolved",
    }


@router.post("/consolidate")
async def trigger_consolidation(
    pipeline: MemoryPipeline = Depends(get_pipeline),
):
    """Manually trigger consolidation job."""
    try:
        result = await pipeline.run_scheduled_consolidation()

        return {
            "success": result.success,
            "duplicates_merged": result.duplicates_merged,
            "conflicts_detected": result.conflicts_detected,
            "truths_crystallized": result.truths_crystallized,
            "duration_ms": result.duration_ms,
        }

    except Exception as e:
        logger.error(f"Consolidation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check(
    store: GraphStore = Depends(get_store),
):
    """Health check for memory service."""
    try:
        stats = await store.get_stats()
        return {
            "status": "healthy",
            "backend": stats["backend"],
            "entity_count": stats["total_entities"],
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }
