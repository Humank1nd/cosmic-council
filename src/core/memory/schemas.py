"""
Memory Schema Definitions
=========================

Knowledge graph entities, relations, and memory facts for the
collective memory system.

Entities: Problem, Cycle, Agent, Decision, Evidence, Artifact, Truth, Outcome
Relations: causes, supports, contradicts, derived_from, used_in, resolved_by
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set
import hashlib
import json
import uuid


class MemoryLayer(str, Enum):
    """Memory layer classification."""
    SHORT_TERM = "short_term"      # Per-cycle working context (ephemeral)
    LONG_TERM = "long_term"        # Durable facts, decisions, outcomes
    SHARED = "shared"              # Cross-agent, cross-service knowledge


class EntityType(str, Enum):
    """Knowledge graph entity types."""
    PROBLEM = "problem"            # A problem statement being solved
    CYCLE = "cycle"                # A triangle cycle execution
    AGENT = "agent"                # An agent that contributed
    DECISION = "decision"          # A decision made during solving
    EVIDENCE = "evidence"          # Supporting evidence for a claim
    ARTIFACT = "artifact"          # Generated artifact (code, spec, etc.)
    TRUTH = "truth"                # Crystallized fact from evidence
    OUTCOME = "outcome"            # Result of a cycle or decision


class RelationType(str, Enum):
    """Knowledge graph relation types."""
    # Causal relations
    CAUSES = "causes"              # X causes Y
    PREVENTS = "prevents"          # X prevents Y

    # Epistemic relations
    SUPPORTS = "supports"          # Evidence supports claim
    CONTRADICTS = "contradicts"    # Evidence contradicts claim
    CONFIRMS = "confirms"          # Later evidence confirms earlier
    REFUTES = "refutes"            # Later evidence refutes earlier

    # Derivation relations
    DERIVED_FROM = "derived_from"  # Y is derived from X
    SYNTHESIZES = "synthesizes"    # Y combines multiple X sources

    # Usage relations
    USED_IN = "used_in"            # Entity used in cycle/decision
    PRODUCED_BY = "produced_by"    # Entity produced by cycle

    # Resolution relations
    RESOLVED_BY = "resolved_by"    # Problem resolved by outcome
    ADDRESSES = "addresses"        # Decision addresses problem

    # Temporal relations
    FOLLOWS = "follows"            # Y follows X temporally
    PRECEDES = "precedes"          # X precedes Y temporally

    # Hierarchical relations
    PART_OF = "part_of"            # X is part of Y
    CONTAINS = "contains"          # Y contains X


class ConfidenceLevel(str, Enum):
    """Confidence levels for facts and relations."""
    SPECULATIVE = "speculative"    # 0-25%: Hypothesis, unverified
    LOW = "low"                    # 25-50%: Some evidence, uncertain
    MEDIUM = "medium"              # 50-75%: Reasonable evidence
    HIGH = "high"                  # 75-95%: Strong evidence
    VERIFIED = "verified"          # 95-100%: Confirmed, crystallized truth

    @classmethod
    def from_score(cls, score: float) -> "ConfidenceLevel":
        """Convert numeric confidence to level."""
        if score < 0.25:
            return cls.SPECULATIVE
        elif score < 0.5:
            return cls.LOW
        elif score < 0.75:
            return cls.MEDIUM
        elif score < 0.95:
            return cls.HIGH
        else:
            return cls.VERIFIED


class AccessLevel(str, Enum):
    """Access control levels for memory."""
    PRIVATE = "private"            # Only source agent
    TEAM = "team"                  # Same agent role family
    TENANT = "tenant"              # Same tenant
    GLOBAL = "global"              # All agents, all tenants


@dataclass
class MemoryScope:
    """Defines access scope for memory entities."""
    access_level: AccessLevel
    tenant_id: Optional[str] = None
    allowed_roles: Optional[Set[str]] = None
    allowed_agents: Optional[Set[str]] = None

    def can_access(
        self,
        requester_agent: str,
        requester_role: str,
        requester_tenant: Optional[str] = None,
    ) -> bool:
        """Check if requester can access this scope."""
        if self.access_level == AccessLevel.GLOBAL:
            return True

        if self.access_level == AccessLevel.TENANT:
            return requester_tenant == self.tenant_id

        if self.access_level == AccessLevel.TEAM:
            if self.allowed_roles and requester_role in self.allowed_roles:
                return True
            return False

        if self.access_level == AccessLevel.PRIVATE:
            if self.allowed_agents and requester_agent in self.allowed_agents:
                return True
            return False

        return False


@dataclass
class Provenance:
    """Tracks origin and lineage of memory entities."""
    source_agent: str              # Agent that created this
    source_cycle: Optional[str]    # Cycle ID if from a cycle
    source_problem: Optional[str]  # Problem ID if related
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: Optional[datetime] = None
    version: int = 1
    parent_ids: List[str] = field(default_factory=list)  # Derived from these

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_agent": self.source_agent,
            "source_cycle": self.source_cycle,
            "source_problem": self.source_problem,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
            "version": self.version,
            "parent_ids": self.parent_ids,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Provenance":
        return cls(
            source_agent=data["source_agent"],
            source_cycle=data.get("source_cycle"),
            source_problem=data.get("source_problem"),
            created_at=datetime.fromisoformat(data["created_at"]),
            modified_at=datetime.fromisoformat(data["modified_at"]) if data.get("modified_at") else None,
            version=data.get("version", 1),
            parent_ids=data.get("parent_ids", []),
        )


@dataclass
class MemoryEntity:
    """Base class for all knowledge graph entities."""
    id: str
    entity_type: EntityType
    name: str
    description: str
    layer: MemoryLayer
    provenance: Provenance
    confidence: float              # 0.0 to 1.0
    scope: MemoryScope
    properties: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    ttl_days: Optional[int] = None  # Time-to-live for retention
    is_archived: bool = False

    def __post_init__(self):
        if not self.id:
            self.id = self._generate_id()

    def _generate_id(self) -> str:
        """Generate unique ID based on content hash."""
        content = f"{self.entity_type.value}:{self.name}:{self.description}"
        hash_val = hashlib.sha256(content.encode()).hexdigest()[:16]
        return f"{self.entity_type.value}_{hash_val}"

    @property
    def confidence_level(self) -> ConfidenceLevel:
        return ConfidenceLevel.from_score(self.confidence)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "entity_type": self.entity_type.value,
            "name": self.name,
            "description": self.description,
            "layer": self.layer.value,
            "provenance": self.provenance.to_dict(),
            "confidence": self.confidence,
            "confidence_level": self.confidence_level.value,
            "scope": {
                "access_level": self.scope.access_level.value,
                "tenant_id": self.scope.tenant_id,
                "allowed_roles": list(self.scope.allowed_roles) if self.scope.allowed_roles else None,
                "allowed_agents": list(self.scope.allowed_agents) if self.scope.allowed_agents else None,
            },
            "properties": self.properties,
            "tags": self.tags,
            "ttl_days": self.ttl_days,
            "is_archived": self.is_archived,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryEntity":
        scope_data = data.get("scope", {})
        return cls(
            id=data["id"],
            entity_type=EntityType(data["entity_type"]),
            name=data["name"],
            description=data["description"],
            layer=MemoryLayer(data["layer"]),
            provenance=Provenance.from_dict(data["provenance"]),
            confidence=data["confidence"],
            scope=MemoryScope(
                access_level=AccessLevel(scope_data.get("access_level", "global")),
                tenant_id=scope_data.get("tenant_id"),
                allowed_roles=set(scope_data["allowed_roles"]) if scope_data.get("allowed_roles") else None,
                allowed_agents=set(scope_data["allowed_agents"]) if scope_data.get("allowed_agents") else None,
            ),
            properties=data.get("properties", {}),
            tags=data.get("tags", []),
            ttl_days=data.get("ttl_days"),
            is_archived=data.get("is_archived", False),
        )


@dataclass
class Problem(MemoryEntity):
    """A problem statement being solved."""

    def __init__(
        self,
        name: str,
        description: str,
        provenance: Provenance,
        problem_statement: str,
        domain: str = "general",
        complexity: str = "medium",
        **kwargs,
    ):
        super().__init__(
            id=kwargs.get("id", ""),
            entity_type=EntityType.PROBLEM,
            name=name,
            description=description,
            layer=MemoryLayer.LONG_TERM,
            provenance=provenance,
            confidence=kwargs.get("confidence", 1.0),
            scope=kwargs.get("scope", MemoryScope(AccessLevel.TENANT)),
            properties={
                "problem_statement": problem_statement,
                "domain": domain,
                "complexity": complexity,
            },
            tags=kwargs.get("tags", [domain]),
        )


@dataclass
class Cycle(MemoryEntity):
    """A triangle cycle execution."""

    def __init__(
        self,
        name: str,
        description: str,
        provenance: Provenance,
        cycle_id: str,
        problem_id: str,
        status: str,
        phase: int = 0,
        **kwargs,
    ):
        super().__init__(
            id=kwargs.get("id", f"cycle_{cycle_id}"),
            entity_type=EntityType.CYCLE,
            name=name,
            description=description,
            layer=MemoryLayer.LONG_TERM,
            provenance=provenance,
            confidence=kwargs.get("confidence", 1.0),
            scope=kwargs.get("scope", MemoryScope(AccessLevel.TENANT)),
            properties={
                "cycle_id": cycle_id,
                "problem_id": problem_id,
                "status": status,
                "phase": phase,
            },
            tags=kwargs.get("tags", ["cycle"]),
        )


@dataclass
class Agent(MemoryEntity):
    """An agent that contributed to knowledge."""

    def __init__(
        self,
        name: str,
        description: str,
        provenance: Provenance,
        agent_id: str,
        role: str,  # WHY, HOW, WHAT, WHEN, WHERE
        capabilities: List[str] = None,
        **kwargs,
    ):
        super().__init__(
            id=kwargs.get("id", f"agent_{agent_id}"),
            entity_type=EntityType.AGENT,
            name=name,
            description=description,
            layer=MemoryLayer.SHARED,
            provenance=provenance,
            confidence=kwargs.get("confidence", 1.0),
            scope=kwargs.get("scope", MemoryScope(AccessLevel.GLOBAL)),
            properties={
                "agent_id": agent_id,
                "role": role,
                "capabilities": capabilities or [],
            },
            tags=kwargs.get("tags", [role]),
        )


@dataclass
class Decision(MemoryEntity):
    """A decision made during problem solving."""

    def __init__(
        self,
        name: str,
        description: str,
        provenance: Provenance,
        decision_text: str,
        rationale: str,
        alternatives_considered: List[str] = None,
        impact: str = "unknown",
        **kwargs,
    ):
        super().__init__(
            id=kwargs.get("id", ""),
            entity_type=EntityType.DECISION,
            name=name,
            description=description,
            layer=MemoryLayer.LONG_TERM,
            provenance=provenance,
            confidence=kwargs.get("confidence", 0.8),
            scope=kwargs.get("scope", MemoryScope(AccessLevel.TENANT)),
            properties={
                "decision_text": decision_text,
                "rationale": rationale,
                "alternatives_considered": alternatives_considered or [],
                "impact": impact,
            },
            tags=kwargs.get("tags", ["decision"]),
        )


@dataclass
class Evidence(MemoryEntity):
    """Supporting evidence for a claim."""

    def __init__(
        self,
        name: str,
        description: str,
        provenance: Provenance,
        claim: str,
        evidence_type: str,  # observation, measurement, testimony, document
        source: str,
        strength: float = 0.5,
        **kwargs,
    ):
        super().__init__(
            id=kwargs.get("id", ""),
            entity_type=EntityType.EVIDENCE,
            name=name,
            description=description,
            layer=MemoryLayer.LONG_TERM,
            provenance=provenance,
            confidence=kwargs.get("confidence", strength),
            scope=kwargs.get("scope", MemoryScope(AccessLevel.TENANT)),
            properties={
                "claim": claim,
                "evidence_type": evidence_type,
                "source": source,
                "strength": strength,
            },
            tags=kwargs.get("tags", [evidence_type]),
        )


@dataclass
class Artifact(MemoryEntity):
    """A generated artifact (code, spec, design, etc.)."""

    def __init__(
        self,
        name: str,
        description: str,
        provenance: Provenance,
        artifact_type: str,  # code, spec, design, document, config
        content_hash: str,
        location: Optional[str] = None,
        version: str = "1.0",
        **kwargs,
    ):
        super().__init__(
            id=kwargs.get("id", ""),
            entity_type=EntityType.ARTIFACT,
            name=name,
            description=description,
            layer=MemoryLayer.LONG_TERM,
            provenance=provenance,
            confidence=kwargs.get("confidence", 1.0),
            scope=kwargs.get("scope", MemoryScope(AccessLevel.TENANT)),
            properties={
                "artifact_type": artifact_type,
                "content_hash": content_hash,
                "location": location,
                "version": version,
            },
            tags=kwargs.get("tags", [artifact_type]),
        )


@dataclass
class Truth(MemoryEntity):
    """A crystallized fact from accumulated evidence."""

    def __init__(
        self,
        name: str,
        description: str,
        provenance: Provenance,
        statement: str,
        evidence_ids: List[str],
        domain: str = "general",
        validity_period: Optional[int] = None,  # days until re-verification needed
        **kwargs,
    ):
        super().__init__(
            id=kwargs.get("id", ""),
            entity_type=EntityType.TRUTH,
            name=name,
            description=description,
            layer=MemoryLayer.SHARED,
            provenance=provenance,
            confidence=kwargs.get("confidence", 0.95),
            scope=kwargs.get("scope", MemoryScope(AccessLevel.GLOBAL)),
            properties={
                "statement": statement,
                "evidence_ids": evidence_ids,
                "domain": domain,
                "validity_period": validity_period,
            },
            tags=kwargs.get("tags", [domain, "truth"]),
        )


@dataclass
class Outcome(MemoryEntity):
    """Result of a cycle or decision."""

    def __init__(
        self,
        name: str,
        description: str,
        provenance: Provenance,
        outcome_type: str,  # success, failure, partial, deferred
        metrics: Dict[str, Any] = None,
        lessons_learned: List[str] = None,
        **kwargs,
    ):
        super().__init__(
            id=kwargs.get("id", ""),
            entity_type=EntityType.OUTCOME,
            name=name,
            description=description,
            layer=MemoryLayer.LONG_TERM,
            provenance=provenance,
            confidence=kwargs.get("confidence", 1.0),
            scope=kwargs.get("scope", MemoryScope(AccessLevel.TENANT)),
            properties={
                "outcome_type": outcome_type,
                "metrics": metrics or {},
                "lessons_learned": lessons_learned or [],
            },
            tags=kwargs.get("tags", [outcome_type]),
        )


@dataclass
class Relation:
    """A relation between two entities in the knowledge graph."""
    id: str
    relation_type: RelationType
    source_id: str
    target_id: str
    confidence: float
    provenance: Provenance
    properties: Dict[str, Any] = field(default_factory=dict)
    is_bidirectional: bool = False

    def __post_init__(self):
        if not self.id:
            self.id = self._generate_id()

    def _generate_id(self) -> str:
        content = f"{self.relation_type.value}:{self.source_id}:{self.target_id}"
        hash_val = hashlib.sha256(content.encode()).hexdigest()[:16]
        return f"rel_{hash_val}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "relation_type": self.relation_type.value,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "confidence": self.confidence,
            "provenance": self.provenance.to_dict(),
            "properties": self.properties,
            "is_bidirectional": self.is_bidirectional,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Relation":
        return cls(
            id=data["id"],
            relation_type=RelationType(data["relation_type"]),
            source_id=data["source_id"],
            target_id=data["target_id"],
            confidence=data["confidence"],
            provenance=Provenance.from_dict(data["provenance"]),
            properties=data.get("properties", {}),
            is_bidirectional=data.get("is_bidirectional", False),
        )


@dataclass
class MemoryFact:
    """A structured memory fact for the pipeline."""
    id: str
    content: str
    summary: str
    layer: MemoryLayer
    entity_type: EntityType
    confidence: float
    provenance: Provenance
    scope: MemoryScope
    embedding: Optional[List[float]] = None  # Vector embedding
    metadata: Dict[str, Any] = field(default_factory=dict)
    related_entity_ids: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "summary": self.summary,
            "layer": self.layer.value,
            "entity_type": self.entity_type.value,
            "confidence": self.confidence,
            "provenance": self.provenance.to_dict(),
            "scope": {
                "access_level": self.scope.access_level.value,
                "tenant_id": self.scope.tenant_id,
            },
            "embedding": self.embedding,
            "metadata": self.metadata,
            "related_entity_ids": self.related_entity_ids,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryFact":
        scope_data = data.get("scope", {})
        return cls(
            id=data["id"],
            content=data["content"],
            summary=data["summary"],
            layer=MemoryLayer(data["layer"]),
            entity_type=EntityType(data["entity_type"]),
            confidence=data["confidence"],
            provenance=Provenance.from_dict(data["provenance"]),
            scope=MemoryScope(
                access_level=AccessLevel(scope_data.get("access_level", "global")),
                tenant_id=scope_data.get("tenant_id"),
            ),
            embedding=data.get("embedding"),
            metadata=data.get("metadata", {}),
            related_entity_ids=data.get("related_entity_ids", []),
        )


@dataclass
class MemoryQuery:
    """Query parameters for memory retrieval."""
    query_text: Optional[str] = None
    query_embedding: Optional[List[float]] = None
    entity_types: Optional[List[EntityType]] = None
    layers: Optional[List[MemoryLayer]] = None
    tags: Optional[List[str]] = None
    min_confidence: float = 0.0
    requester_agent: Optional[str] = None
    requester_role: Optional[str] = None
    requester_tenant: Optional[str] = None
    problem_id: Optional[str] = None
    cycle_id: Optional[str] = None
    time_range_start: Optional[datetime] = None
    time_range_end: Optional[datetime] = None
    limit: int = 10
    offset: int = 0
    include_archived: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query_text": self.query_text,
            "entity_types": [t.value for t in self.entity_types] if self.entity_types else None,
            "layers": [l.value for l in self.layers] if self.layers else None,
            "tags": self.tags,
            "min_confidence": self.min_confidence,
            "requester_agent": self.requester_agent,
            "requester_role": self.requester_role,
            "requester_tenant": self.requester_tenant,
            "problem_id": self.problem_id,
            "cycle_id": self.cycle_id,
            "time_range_start": self.time_range_start.isoformat() if self.time_range_start else None,
            "time_range_end": self.time_range_end.isoformat() if self.time_range_end else None,
            "limit": self.limit,
            "offset": self.offset,
            "include_archived": self.include_archived,
        }


@dataclass
class MemoryResult:
    """Result of a memory query."""
    entities: List[MemoryEntity]
    facts: List[MemoryFact]
    relations: List[Relation]
    total_count: int
    query_time_ms: float
    relevance_scores: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entities": [e.to_dict() for e in self.entities],
            "facts": [f.to_dict() for f in self.facts],
            "relations": [r.to_dict() for r in self.relations],
            "total_count": self.total_count,
            "query_time_ms": self.query_time_ms,
            "relevance_scores": self.relevance_scores,
        }


# Role-specific entity filters for retrieval
ROLE_ENTITY_PREFERENCES: Dict[str, List[EntityType]] = {
    "WHY": [EntityType.EVIDENCE, EntityType.TRUTH, EntityType.DECISION],  # Root causes
    "HOW": [EntityType.DECISION, EntityType.ARTIFACT, EntityType.TRUTH],  # Methods
    "WHAT": [EntityType.ARTIFACT, EntityType.OUTCOME, EntityType.DECISION],  # Specs
    "WHEN": [EntityType.CYCLE, EntityType.OUTCOME, EntityType.DECISION],  # Timelines
    "WHERE": [EntityType.ARTIFACT, EntityType.OUTCOME, EntityType.AGENT],  # Channels
}

# Relation types relevant to each role
ROLE_RELATION_PREFERENCES: Dict[str, List[RelationType]] = {
    "WHY": [RelationType.CAUSES, RelationType.SUPPORTS, RelationType.CONTRADICTS],
    "HOW": [RelationType.DERIVED_FROM, RelationType.USED_IN, RelationType.ADDRESSES],
    "WHAT": [RelationType.PRODUCED_BY, RelationType.CONTAINS, RelationType.PART_OF],
    "WHEN": [RelationType.FOLLOWS, RelationType.PRECEDES, RelationType.RESOLVED_BY],
    "WHERE": [RelationType.USED_IN, RelationType.PRODUCED_BY, RelationType.ADDRESSES],
}
