"""
Collective Memory & Knowledge Graph
====================================

Multi-layer memory system for agent knowledge management.

Memory Layers:
- Short-term: Per-cycle working context (ephemeral)
- Long-term: Durable facts, decisions, outcomes
- Shared: Cross-agent knowledge with access controls

Knowledge Graph:
- Entities: Problem, Cycle, Agent, Decision, Evidence, Artifact, Truth, Outcome
- Relations: causes, supports, contradicts, derived_from, used_in, resolved_by

Components:
- schemas: Entity and relation definitions
- store: Pluggable graph storage backends
- retrieval: Role-aware memory retrieval
- consolidation: Memory pipeline and truth crystallization
- api: REST API endpoints
- metrics: Observability and monitoring
"""

from .system import MemoryManager

# Import schema types
from .schemas import (
    # Enums
    MemoryLayer,
    EntityType,
    RelationType,
    ConfidenceLevel,
    AccessLevel,
    # Core structures
    MemoryScope,
    Provenance,
    MemoryEntity,
    Relation,
    MemoryFact,
    MemoryQuery,
    MemoryResult,
    # Entity types
    Problem,
    Cycle,
    Agent,
    Decision,
    Evidence,
    Artifact,
    Truth,
    Outcome,
    # Role preferences
    ROLE_ENTITY_PREFERENCES,
    ROLE_RELATION_PREFERENCES,
)

# Import store backends
from .store import (
    GraphStore,
    SQLiteGraphStore,
    PostgresGraphStore,
    get_graph_store,
)

# Import retrieval components
from .retrieval import (
    RankingStrategy,
    RetrievalConfig,
    RetrievalResult,
    RetrievalPolicy,
    RoleAwareRetriever,
    SemanticRetriever,
)

# Import consolidation components
from .consolidation import (
    ConflictType,
    ConflictReport,
    ConsolidationResult,
    ConflictResolver,
    TruthCrystallizer,
    MemoryPipeline,
    ConsolidationJob,
)

# Import API router
from .api import router

__all__ = [
    # Legacy
    "MemoryManager",
    # Enums
    "MemoryLayer",
    "EntityType",
    "RelationType",
    "ConfidenceLevel",
    "AccessLevel",
    # Core structures
    "MemoryScope",
    "Provenance",
    "MemoryEntity",
    "Relation",
    "MemoryFact",
    "MemoryQuery",
    "MemoryResult",
    # Entity types
    "Problem",
    "Cycle",
    "Agent",
    "Decision",
    "Evidence",
    "Artifact",
    "Truth",
    "Outcome",
    # Preferences
    "ROLE_ENTITY_PREFERENCES",
    "ROLE_RELATION_PREFERENCES",
    # Store
    "GraphStore",
    "SQLiteGraphStore",
    "PostgresGraphStore",
    "get_graph_store",
    # Retrieval
    "RankingStrategy",
    "RetrievalConfig",
    "RetrievalResult",
    "RetrievalPolicy",
    "RoleAwareRetriever",
    "SemanticRetriever",
    # Consolidation
    "ConflictType",
    "ConflictReport",
    "ConsolidationResult",
    "ConflictResolver",
    "TruthCrystallizer",
    "MemoryPipeline",
    "ConsolidationJob",
    # API
    "router",
]
