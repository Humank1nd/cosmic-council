"""
Role-Aware Retrieval Engine
============================

Intelligent memory retrieval with role-specific ranking,
recency weighting, and confidence scoring.

Role Preferences:
- WHY: Root causes, evidence, supporting facts
- HOW: Methods, constraints, procedures
- WHAT: Specifications, prototypes, artifacts
- WHEN: Timelines, schedules, deadlines
- WHERE: Channels, targets, destinations
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

from .schemas import (
    MemoryEntity,
    MemoryFact,
    Relation,
    MemoryQuery,
    MemoryResult,
    EntityType,
    RelationType,
    MemoryLayer,
    ConfidenceLevel,
    ROLE_ENTITY_PREFERENCES,
    ROLE_RELATION_PREFERENCES,
)
from .store import GraphStore

logger = logging.getLogger(__name__)


class RankingStrategy(str, Enum):
    """Strategies for ranking retrieval results."""
    RELEVANCE = "relevance"          # Pure semantic similarity
    RECENCY = "recency"              # Prefer recent items
    CONFIDENCE = "confidence"        # Prefer high-confidence items
    BALANCED = "balanced"            # Mix of all factors
    ROLE_OPTIMIZED = "role_optimized"  # Role-specific ranking


@dataclass
class RetrievalConfig:
    """Configuration for retrieval engine."""
    # Ranking weights
    relevance_weight: float = 0.4
    recency_weight: float = 0.3
    confidence_weight: float = 0.3
    role_boost: float = 0.2  # Boost for role-preferred entities

    # Recency parameters
    recency_half_life_days: float = 7.0  # Time for 50% decay
    max_recency_age_days: float = 365.0  # Ignore recency beyond this

    # Filtering
    min_confidence: float = 0.1
    max_results: int = 20
    include_related: bool = True
    max_related_depth: int = 2

    # Deduplication
    dedup_threshold: float = 0.9  # Similarity threshold for dedup


@dataclass
class RetrievalResult:
    """Result from retrieval with scoring details."""
    entity: Optional[MemoryEntity] = None
    fact: Optional[MemoryFact] = None
    relation: Optional[Relation] = None

    # Scoring breakdown
    relevance_score: float = 0.0
    recency_score: float = 0.0
    confidence_score: float = 0.0
    role_boost_score: float = 0.0
    final_score: float = 0.0

    # Metadata
    retrieval_type: str = "entity"  # entity, fact, relation
    matched_query_terms: List[str] = field(default_factory=list)
    context_path: List[str] = field(default_factory=list)  # Path to this result

    def to_dict(self) -> Dict[str, Any]:
        item_dict = {}
        if self.entity:
            item_dict = self.entity.to_dict()
            self.retrieval_type = "entity"
        elif self.fact:
            item_dict = self.fact.to_dict()
            self.retrieval_type = "fact"
        elif self.relation:
            item_dict = self.relation.to_dict()
            self.retrieval_type = "relation"

        return {
            "item": item_dict,
            "retrieval_type": self.retrieval_type,
            "scores": {
                "relevance": self.relevance_score,
                "recency": self.recency_score,
                "confidence": self.confidence_score,
                "role_boost": self.role_boost_score,
                "final": self.final_score,
            },
            "matched_query_terms": self.matched_query_terms,
            "context_path": self.context_path,
        }


@dataclass
class RetrievalPolicy:
    """Policy defining retrieval behavior for a role."""
    role: str
    preferred_entity_types: List[EntityType]
    preferred_relation_types: List[RelationType]
    preferred_layers: List[MemoryLayer]
    min_confidence: float
    recency_preference: float  # 0-1, higher = prefer recent
    depth_preference: int  # How deep to traverse relations

    @classmethod
    def for_role(cls, role: str) -> "RetrievalPolicy":
        """Create policy for a specific agent role."""
        entity_prefs = ROLE_ENTITY_PREFERENCES.get(role, list(EntityType))
        relation_prefs = ROLE_RELATION_PREFERENCES.get(role, list(RelationType))

        # Role-specific tuning
        role_configs = {
            "WHY": {
                "min_confidence": 0.3,
                "recency_preference": 0.3,  # Less recency bias for root causes
                "depth_preference": 4,  # Deep traversal for causation
                "layers": [MemoryLayer.LONG_TERM, MemoryLayer.SHARED],
            },
            "HOW": {
                "min_confidence": 0.5,
                "recency_preference": 0.5,
                "depth_preference": 2,
                "layers": [MemoryLayer.LONG_TERM, MemoryLayer.SHARED],
            },
            "WHAT": {
                "min_confidence": 0.6,
                "recency_preference": 0.7,  # Prefer recent specs
                "depth_preference": 1,
                "layers": [MemoryLayer.LONG_TERM],
            },
            "WHEN": {
                "min_confidence": 0.4,
                "recency_preference": 0.8,  # Very recency-biased
                "depth_preference": 2,
                "layers": [MemoryLayer.SHORT_TERM, MemoryLayer.LONG_TERM],
            },
            "WHERE": {
                "min_confidence": 0.5,
                "recency_preference": 0.6,
                "depth_preference": 1,
                "layers": [MemoryLayer.LONG_TERM, MemoryLayer.SHARED],
            },
        }

        config = role_configs.get(role, {
            "min_confidence": 0.3,
            "recency_preference": 0.5,
            "depth_preference": 2,
            "layers": [MemoryLayer.LONG_TERM],
        })

        return cls(
            role=role,
            preferred_entity_types=entity_prefs,
            preferred_relation_types=relation_prefs,
            preferred_layers=config["layers"],
            min_confidence=config["min_confidence"],
            recency_preference=config["recency_preference"],
            depth_preference=config["depth_preference"],
        )


class RoleAwareRetriever:
    """
    Intelligent memory retrieval with role-specific ranking.

    Features:
    - Role-aware entity/relation preferences
    - Recency-weighted scoring with configurable decay
    - Confidence-based filtering and ranking
    - Semantic similarity (when embeddings available)
    - Deduplication of similar results
    - Related entity expansion
    """

    def __init__(
        self,
        store: GraphStore,
        config: Optional[RetrievalConfig] = None,
        embedding_fn: Optional[Callable[[str], List[float]]] = None,
    ):
        self.store = store
        self.config = config or RetrievalConfig()
        self.embedding_fn = embedding_fn  # Optional embedding function

    async def retrieve(
        self,
        query: MemoryQuery,
        role: Optional[str] = None,
        strategy: RankingStrategy = RankingStrategy.BALANCED,
    ) -> MemoryResult:
        """
        Retrieve memory items based on query with role-aware ranking.

        Args:
            query: Query parameters
            role: Agent role (WHY, HOW, WHAT, WHEN, WHERE)
            strategy: Ranking strategy to use

        Returns:
            MemoryResult with ranked entities, facts, and relations
        """
        start_time = time.time()

        # Get role policy
        policy = RetrievalPolicy.for_role(role) if role else None

        # Apply policy to query if present
        if policy:
            if not query.entity_types:
                query.entity_types = policy.preferred_entity_types
            if not query.layers:
                query.layers = policy.preferred_layers
            if query.min_confidence == 0:
                query.min_confidence = policy.min_confidence

        # Retrieve raw results
        entities = await self.store.query_entities(query)
        facts = await self.store.query_facts(query)

        # Score and rank results
        scored_results = []

        for entity in entities:
            result = self._score_entity(entity, query, policy, strategy)
            scored_results.append(result)

        for fact in facts:
            result = self._score_fact(fact, query, policy, strategy)
            scored_results.append(result)

        # Sort by final score
        scored_results.sort(key=lambda r: r.final_score, reverse=True)

        # Deduplicate similar results
        deduped_results = self._deduplicate(scored_results)

        # Expand with related entities if enabled
        if self.config.include_related and entities:
            related = await self._expand_related(
                [r.entity for r in deduped_results if r.entity],
                policy,
                query,
            )
            deduped_results.extend(related)
            deduped_results.sort(key=lambda r: r.final_score, reverse=True)

        # Limit results
        final_results = deduped_results[:self.config.max_results]

        # Collect relations between result entities
        entity_ids = [r.entity.id for r in final_results if r.entity]
        relations = []
        for eid in entity_ids[:10]:  # Limit relation queries
            rels = await self.store.get_relations(
                eid,
                direction="both",
                relation_types=policy.preferred_relation_types if policy else None,
            )
            relations.extend(rels)

        # Build result
        query_time_ms = (time.time() - start_time) * 1000
        relevance_scores = {
            r.entity.id if r.entity else r.fact.id if r.fact else "unknown": r.final_score
            for r in final_results
        }

        return MemoryResult(
            entities=[r.entity for r in final_results if r.entity],
            facts=[r.fact for r in final_results if r.fact],
            relations=relations,
            total_count=len(entities) + len(facts),
            query_time_ms=query_time_ms,
            relevance_scores=relevance_scores,
        )

    def _score_entity(
        self,
        entity: MemoryEntity,
        query: MemoryQuery,
        policy: Optional[RetrievalPolicy],
        strategy: RankingStrategy,
    ) -> RetrievalResult:
        """Score an entity based on query match and policy."""
        result = RetrievalResult(entity=entity, retrieval_type="entity")

        # Relevance score (text match)
        result.relevance_score = self._compute_relevance(
            query.query_text or "",
            f"{entity.name} {entity.description}",
        )
        if result.relevance_score > 0:
            result.matched_query_terms = self._get_matched_terms(
                query.query_text or "", f"{entity.name} {entity.description}"
            )

        # Recency score
        result.recency_score = self._compute_recency(entity.provenance.created_at)

        # Confidence score (normalized)
        result.confidence_score = entity.confidence

        # Role boost
        if policy and entity.entity_type in policy.preferred_entity_types:
            pref_idx = policy.preferred_entity_types.index(entity.entity_type)
            # Higher boost for entities earlier in preference list
            result.role_boost_score = 1.0 - (pref_idx * 0.15)
        else:
            result.role_boost_score = 0.0

        # Compute final score based on strategy
        result.final_score = self._compute_final_score(result, strategy, policy)

        return result

    def _score_fact(
        self,
        fact: MemoryFact,
        query: MemoryQuery,
        policy: Optional[RetrievalPolicy],
        strategy: RankingStrategy,
    ) -> RetrievalResult:
        """Score a fact based on query match and policy."""
        result = RetrievalResult(fact=fact, retrieval_type="fact")

        # Relevance score
        result.relevance_score = self._compute_relevance(
            query.query_text or "",
            f"{fact.summary} {fact.content}",
        )
        if result.relevance_score > 0:
            result.matched_query_terms = self._get_matched_terms(
                query.query_text or "", f"{fact.summary} {fact.content}"
            )

        # Recency score
        result.recency_score = self._compute_recency(fact.provenance.created_at)

        # Confidence score
        result.confidence_score = fact.confidence

        # Role boost (based on entity type)
        if policy and fact.entity_type in policy.preferred_entity_types:
            pref_idx = policy.preferred_entity_types.index(fact.entity_type)
            result.role_boost_score = 1.0 - (pref_idx * 0.15)
        else:
            result.role_boost_score = 0.0

        result.final_score = self._compute_final_score(result, strategy, policy)

        return result

    def _compute_relevance(self, query_text: str, target_text: str) -> float:
        """Compute relevance score between query and target text."""
        if not query_text:
            return 0.5  # Neutral score for no query

        # Simple term overlap scoring
        query_terms = set(query_text.lower().split())
        target_terms = set(target_text.lower().split())

        if not query_terms:
            return 0.5

        overlap = len(query_terms & target_terms)
        score = overlap / len(query_terms)

        return min(1.0, score)

    def _get_matched_terms(self, query_text: str, target_text: str) -> List[str]:
        """Get terms that matched between query and target."""
        query_terms = set(query_text.lower().split())
        target_terms = set(target_text.lower().split())
        return list(query_terms & target_terms)

    def _compute_recency(self, created_at: datetime) -> float:
        """
        Compute recency score with exponential decay.

        Score = 0.5 ^ (age_days / half_life_days)
        """
        now = datetime.now(timezone.utc)

        # Handle timezone-naive datetimes
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        age = now - created_at
        age_days = age.total_seconds() / (24 * 3600)

        if age_days > self.config.max_recency_age_days:
            return 0.0

        # Exponential decay
        score = 0.5 ** (age_days / self.config.recency_half_life_days)
        return score

    def _compute_final_score(
        self,
        result: RetrievalResult,
        strategy: RankingStrategy,
        policy: Optional[RetrievalPolicy],
    ) -> float:
        """Compute final score based on strategy."""
        if strategy == RankingStrategy.RELEVANCE:
            return result.relevance_score

        if strategy == RankingStrategy.RECENCY:
            return result.recency_score

        if strategy == RankingStrategy.CONFIDENCE:
            return result.confidence_score

        if strategy == RankingStrategy.ROLE_OPTIMIZED and policy:
            # Adjust weights based on role's recency preference
            recency_weight = policy.recency_preference * self.config.recency_weight
            relevance_weight = self.config.relevance_weight
            confidence_weight = self.config.confidence_weight
            role_boost = self.config.role_boost * result.role_boost_score

            total_weight = relevance_weight + recency_weight + confidence_weight
            normalized_relevance = relevance_weight / total_weight
            normalized_recency = recency_weight / total_weight
            normalized_confidence = confidence_weight / total_weight

            base_score = (
                result.relevance_score * normalized_relevance +
                result.recency_score * normalized_recency +
                result.confidence_score * normalized_confidence
            )
            return min(1.0, base_score + role_boost)

        # Default: BALANCED
        base_score = (
            result.relevance_score * self.config.relevance_weight +
            result.recency_score * self.config.recency_weight +
            result.confidence_score * self.config.confidence_weight
        )
        role_boost = self.config.role_boost * result.role_boost_score
        return min(1.0, base_score + role_boost)

    def _deduplicate(self, results: List[RetrievalResult]) -> List[RetrievalResult]:
        """Remove duplicate or near-duplicate results."""
        if not results:
            return results

        deduped = []
        seen_ids = set()

        for result in results:
            # Get item ID
            item_id = None
            if result.entity:
                item_id = result.entity.id
            elif result.fact:
                item_id = result.fact.id

            if item_id and item_id in seen_ids:
                continue

            if item_id:
                seen_ids.add(item_id)

            deduped.append(result)

        return deduped

    async def _expand_related(
        self,
        entities: List[MemoryEntity],
        policy: Optional[RetrievalPolicy],
        query: MemoryQuery,
    ) -> List[RetrievalResult]:
        """Expand retrieval with related entities."""
        related_results = []
        seen_ids = {e.id for e in entities}

        max_depth = policy.depth_preference if policy else self.config.max_related_depth

        for entity in entities[:5]:  # Limit expansion
            relations = await self.store.get_relations(
                entity.id,
                direction="outgoing",
                relation_types=policy.preferred_relation_types if policy else None,
            )

            for rel in relations[:3]:
                if rel.target_id in seen_ids:
                    continue

                related_entity = await self.store.get_entity(rel.target_id)
                if not related_entity:
                    continue

                seen_ids.add(related_entity.id)

                result = self._score_entity(
                    related_entity, query, policy, RankingStrategy.BALANCED
                )
                # Discount related items slightly
                result.final_score *= 0.8
                result.context_path = [entity.id, rel.relation_type.value]

                related_results.append(result)

        return related_results

    async def retrieve_for_problem(
        self,
        problem_id: str,
        role: Optional[str] = None,
        limit: int = 10,
    ) -> MemoryResult:
        """Retrieve all memory related to a specific problem."""
        query = MemoryQuery(
            problem_id=problem_id,
            limit=limit * 2,  # Fetch more to account for filtering
            requester_role=role,
        )

        return await self.retrieve(
            query,
            role=role,
            strategy=RankingStrategy.ROLE_OPTIMIZED if role else RankingStrategy.BALANCED,
        )

    async def retrieve_agent_history(
        self,
        agent_id: str,
        limit: int = 20,
    ) -> MemoryResult:
        """Retrieve memory history for a specific agent."""
        query = MemoryQuery(
            requester_agent=agent_id,
            limit=limit,
        )

        # Query entities created by this agent
        entities = await self.store.query_entities(query)

        # Filter to entities from this agent
        agent_entities = [
            e for e in entities
            if e.provenance.source_agent == agent_id
        ]

        # Get facts
        facts = await self.store.query_facts(query)
        agent_facts = [
            f for f in facts
            if f.provenance.source_agent == agent_id
        ]

        return MemoryResult(
            entities=agent_entities[:limit],
            facts=agent_facts[:limit],
            relations=[],
            total_count=len(agent_entities) + len(agent_facts),
            query_time_ms=0,
        )

    async def find_contradictions(
        self,
        entity_id: str,
    ) -> List[Tuple[MemoryEntity, Relation, MemoryEntity]]:
        """Find entities that contradict a given entity."""
        contradictions = []

        relations = await self.store.get_relations(
            entity_id,
            direction="both",
            relation_types=[RelationType.CONTRADICTS, RelationType.REFUTES],
        )

        for rel in relations:
            other_id = rel.target_id if rel.source_id == entity_id else rel.source_id
            other_entity = await self.store.get_entity(other_id)
            source_entity = await self.store.get_entity(entity_id)

            if other_entity and source_entity:
                contradictions.append((source_entity, rel, other_entity))

        return contradictions

    async def get_evidence_chain(
        self,
        truth_id: str,
        max_depth: int = 5,
    ) -> Dict[str, Any]:
        """Get the chain of evidence supporting a truth."""
        return await self.store.traverse(
            start_id=truth_id,
            relation_types=[
                RelationType.SUPPORTS,
                RelationType.DERIVED_FROM,
                RelationType.CONFIRMS,
            ],
            max_depth=max_depth,
            direction="incoming",  # Find what supports this truth
        )


class SemanticRetriever(RoleAwareRetriever):
    """
    Extended retriever with semantic similarity using embeddings.

    Requires an embedding function that converts text to vectors.
    """

    def __init__(
        self,
        store: GraphStore,
        embedding_fn: Callable[[str], List[float]],
        config: Optional[RetrievalConfig] = None,
    ):
        super().__init__(store, config, embedding_fn)

    def _compute_relevance(self, query_text: str, target_text: str) -> float:
        """Compute semantic similarity using embeddings."""
        if not query_text or not self.embedding_fn:
            return super()._compute_relevance(query_text, target_text)

        try:
            query_embedding = self.embedding_fn(query_text)
            target_embedding = self.embedding_fn(target_text)

            # Cosine similarity
            dot_product = sum(q * t for q, t in zip(query_embedding, target_embedding))
            query_norm = sum(q * q for q in query_embedding) ** 0.5
            target_norm = sum(t * t for t in target_embedding) ** 0.5

            if query_norm == 0 or target_norm == 0:
                return 0.0

            similarity = dot_product / (query_norm * target_norm)
            # Normalize to 0-1 range (cosine similarity is -1 to 1)
            return (similarity + 1) / 2

        except Exception as e:
            logger.warning(f"Embedding computation failed: {e}")
            return super()._compute_relevance(query_text, target_text)
