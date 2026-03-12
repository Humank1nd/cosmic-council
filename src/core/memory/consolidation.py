"""
Memory Consolidation Pipeline
=============================

Processes raw cycle outputs and analytics events into structured
memory entities with:
- Normalization and summarization
- Embedding generation
- Graph edge linking
- Duplicate detection
- Contradiction handling
- Truth crystallization
"""

import asyncio
import hashlib
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from .schemas import (
    MemoryEntity,
    MemoryFact,
    Relation,
    EntityType,
    RelationType,
    MemoryLayer,
    MemoryScope,
    AccessLevel,
    Provenance,
    ConfidenceLevel,
    Problem,
    Cycle,
    Decision,
    Evidence,
    Artifact,
    Truth,
    Outcome,
)
from .store import GraphStore

logger = logging.getLogger(__name__)


class ConflictType(str, Enum):
    """Types of conflicts detected during consolidation."""
    DUPLICATE = "duplicate"          # Near-identical entries
    CONTRADICTION = "contradiction"  # Conflicting claims
    STALENESS = "staleness"          # Outdated information
    AMBIGUITY = "ambiguity"          # Unclear or vague


@dataclass
class ConflictReport:
    """Report of a detected conflict."""
    conflict_type: ConflictType
    entity_ids: List[str]
    description: str
    confidence: float
    requires_human_review: bool
    suggested_resolution: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "conflict_type": self.conflict_type.value,
            "entity_ids": self.entity_ids,
            "description": self.description,
            "confidence": self.confidence,
            "requires_human_review": self.requires_human_review,
            "suggested_resolution": self.suggested_resolution,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class ConsolidationResult:
    """Result of a consolidation job run."""
    success: bool
    entities_created: int = 0
    entities_updated: int = 0
    relations_created: int = 0
    facts_created: int = 0
    duplicates_merged: int = 0
    conflicts_detected: int = 0
    truths_crystallized: int = 0
    duration_ms: float = 0
    conflicts: List[ConflictReport] = field(default_factory=list)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "entities_created": self.entities_created,
            "entities_updated": self.entities_updated,
            "relations_created": self.relations_created,
            "facts_created": self.facts_created,
            "duplicates_merged": self.duplicates_merged,
            "conflicts_detected": self.conflicts_detected,
            "truths_crystallized": self.truths_crystallized,
            "duration_ms": self.duration_ms,
            "conflicts": [c.to_dict() for c in self.conflicts],
            "error": self.error,
        }


class ConflictResolver:
    """
    Detects and resolves conflicts in memory entries.

    Strategies:
    - Duplicates: Merge with confidence aggregation
    - Contradictions: Mark for review, optionally auto-resolve by recency/confidence
    - Staleness: Archive old entries
    """

    def __init__(
        self,
        store: GraphStore,
        similarity_threshold: float = 0.85,
        auto_resolve_threshold: float = 0.9,
    ):
        self.store = store
        self.similarity_threshold = similarity_threshold
        self.auto_resolve_threshold = auto_resolve_threshold

    async def find_duplicates(
        self,
        entity: MemoryEntity,
    ) -> List[Tuple[MemoryEntity, float]]:
        """Find potential duplicate entities."""
        from .schemas import MemoryQuery

        # Query similar entities
        query = MemoryQuery(
            entity_types=[entity.entity_type],
            layers=[entity.layer],
            query_text=entity.name,
            limit=20,
        )
        candidates = await self.store.query_entities(query)

        duplicates = []
        for candidate in candidates:
            if candidate.id == entity.id:
                continue

            similarity = self._compute_similarity(entity, candidate)
            if similarity >= self.similarity_threshold:
                duplicates.append((candidate, similarity))

        return sorted(duplicates, key=lambda x: x[1], reverse=True)

    def _compute_similarity(
        self,
        entity1: MemoryEntity,
        entity2: MemoryEntity,
    ) -> float:
        """Compute similarity between two entities."""
        # Simple Jaccard similarity on text
        text1 = f"{entity1.name} {entity1.description}".lower()
        text2 = f"{entity2.name} {entity2.description}".lower()

        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    async def merge_duplicates(
        self,
        primary: MemoryEntity,
        duplicates: List[MemoryEntity],
    ) -> MemoryEntity:
        """Merge duplicate entities into primary."""
        # Aggregate confidence
        total_confidence = primary.confidence
        for dup in duplicates:
            total_confidence += dup.confidence * 0.5  # Diminishing returns

        primary.confidence = min(1.0, total_confidence)

        # Merge tags
        all_tags = set(primary.tags)
        for dup in duplicates:
            all_tags.update(dup.tags)
        primary.tags = list(all_tags)

        # Merge properties (prefer primary)
        for dup in duplicates:
            for key, value in dup.properties.items():
                if key not in primary.properties:
                    primary.properties[key] = value

        # Update provenance
        primary.provenance.parent_ids.extend([d.id for d in duplicates])
        primary.provenance.version += 1
        primary.provenance.modified_at = datetime.now(timezone.utc)

        # Save merged entity
        await self.store.update_entity(primary)

        # Archive duplicates
        for dup in duplicates:
            dup.is_archived = True
            await self.store.update_entity(dup)

        return primary

    async def detect_contradictions(
        self,
        entity: MemoryEntity,
    ) -> List[ConflictReport]:
        """Detect entities that contradict the given entity."""
        conflicts = []

        # Get entities with similar topics but potentially conflicting content
        from .schemas import MemoryQuery

        query = MemoryQuery(
            entity_types=[entity.entity_type],
            tags=entity.tags[:3] if entity.tags else None,
            limit=50,
        )
        candidates = await self.store.query_entities(query)

        for candidate in candidates:
            if candidate.id == entity.id:
                continue

            # Check for contradiction indicators
            contradiction_score = self._check_contradiction(entity, candidate)
            if contradiction_score > 0.5:
                requires_human = contradiction_score > 0.7 and \
                    min(entity.confidence, candidate.confidence) > 0.5

                conflict = ConflictReport(
                    conflict_type=ConflictType.CONTRADICTION,
                    entity_ids=[entity.id, candidate.id],
                    description=f"Potential contradiction between '{entity.name}' and '{candidate.name}'",
                    confidence=contradiction_score,
                    requires_human_review=requires_human,
                    suggested_resolution=self._suggest_resolution(entity, candidate),
                )
                conflicts.append(conflict)

                # Create contradiction relation
                relation = Relation(
                    id="",
                    relation_type=RelationType.CONTRADICTS,
                    source_id=entity.id,
                    target_id=candidate.id,
                    confidence=contradiction_score,
                    provenance=entity.provenance,
                    is_bidirectional=True,
                )
                await self.store.save_relation(relation)

        return conflicts

    def _check_contradiction(
        self,
        entity1: MemoryEntity,
        entity2: MemoryEntity,
    ) -> float:
        """Check if two entities might contradict each other."""
        # Look for negation patterns
        negation_words = {"not", "no", "never", "cannot", "won't", "don't", "isn't", "aren't"}

        text1 = entity1.description.lower()
        text2 = entity2.description.lower()

        # Count negation differences
        neg1 = len([w for w in text1.split() if w in negation_words])
        neg2 = len([w for w in text2.split() if w in negation_words])

        # Similar topic but different negation = potential contradiction
        topic_similarity = self._compute_similarity(entity1, entity2)

        if topic_similarity > 0.5 and abs(neg1 - neg2) > 0:
            return min(1.0, topic_similarity + 0.2)

        return 0.0

    def _suggest_resolution(
        self,
        entity1: MemoryEntity,
        entity2: MemoryEntity,
    ) -> str:
        """Suggest how to resolve a contradiction."""
        if entity1.confidence > entity2.confidence + 0.2:
            return f"Keep '{entity1.name}' (higher confidence: {entity1.confidence:.2f})"
        if entity2.confidence > entity1.confidence + 0.2:
            return f"Keep '{entity2.name}' (higher confidence: {entity2.confidence:.2f})"

        # Check recency
        if entity1.provenance.created_at > entity2.provenance.created_at:
            return f"Keep '{entity1.name}' (more recent)"
        if entity2.provenance.created_at > entity1.provenance.created_at:
            return f"Keep '{entity2.name}' (more recent)"

        return "Manual review required - entities have similar confidence and recency"


class TruthCrystallizer:
    """
    Crystallizes verified facts into durable truths.

    A truth is crystallized when:
    - Multiple independent evidence sources support it
    - No significant contradictions exist
    - Confidence threshold is met
    - Sufficient time has passed for validation
    """

    def __init__(
        self,
        store: GraphStore,
        min_evidence_count: int = 3,
        min_confidence: float = 0.8,
        min_age_hours: int = 24,
        contradiction_threshold: float = 0.3,
    ):
        self.store = store
        self.min_evidence_count = min_evidence_count
        self.min_confidence = min_confidence
        self.min_age_hours = min_age_hours
        self.contradiction_threshold = contradiction_threshold

    async def find_crystallization_candidates(self) -> List[MemoryEntity]:
        """Find entities that are candidates for truth crystallization."""
        from .schemas import MemoryQuery

        cutoff = datetime.now(timezone.utc) - timedelta(hours=self.min_age_hours)

        query = MemoryQuery(
            entity_types=[EntityType.EVIDENCE, EntityType.DECISION],
            min_confidence=self.min_confidence,
            time_range_end=cutoff,
            limit=100,
        )
        candidates = await self.store.query_entities(query)

        return candidates

    async def crystallize(
        self,
        entity: MemoryEntity,
    ) -> Optional[MemoryEntity]:
        """Attempt to crystallize an entity into a truth."""
        # Check supporting evidence
        support_relations = await self.store.get_relations(
            entity.id,
            direction="incoming",
            relation_types=[RelationType.SUPPORTS, RelationType.CONFIRMS],
        )

        if len(support_relations) < self.min_evidence_count:
            logger.debug(
                f"Entity {entity.id} has insufficient evidence ({len(support_relations)})"
            )
            return None

        # Check for contradictions
        contra_relations = await self.store.get_relations(
            entity.id,
            direction="both",
            relation_types=[RelationType.CONTRADICTS, RelationType.REFUTES],
        )

        contradiction_weight = sum(r.confidence for r in contra_relations)
        support_weight = sum(r.confidence for r in support_relations)

        if support_weight > 0:
            contradiction_ratio = contradiction_weight / (support_weight + contradiction_weight)
            if contradiction_ratio > self.contradiction_threshold:
                logger.debug(
                    f"Entity {entity.id} has too many contradictions ({contradiction_ratio:.2f})"
                )
                return None

        # Calculate truth confidence
        evidence_ids = [r.source_id for r in support_relations]
        aggregated_confidence = min(1.0, entity.confidence + (len(support_relations) * 0.05))

        # Create truth entity
        truth = Truth(
            name=f"Truth: {entity.name}",
            description=entity.description,
            provenance=Provenance(
                source_agent="truth_crystallizer",
                source_cycle=entity.provenance.source_cycle,
                source_problem=entity.provenance.source_problem,
                parent_ids=[entity.id],
            ),
            statement=entity.description,
            evidence_ids=evidence_ids,
            domain=entity.tags[0] if entity.tags else "general",
            confidence=aggregated_confidence,
        )

        # Save truth
        await self.store.save_entity(truth)

        # Create derived_from relation
        derived_relation = Relation(
            id="",
            relation_type=RelationType.DERIVED_FROM,
            source_id=truth.id,
            target_id=entity.id,
            confidence=1.0,
            provenance=truth.provenance,
        )
        await self.store.save_relation(derived_relation)

        logger.info(f"Crystallized truth {truth.id} from entity {entity.id}")
        return truth


class MemoryPipeline:
    """
    Main memory consolidation pipeline.

    Pipeline stages:
    1. Ingest: Accept raw cycle outputs and events
    2. Normalize: Extract structured entities and facts
    3. Embed: Generate vector embeddings (optional)
    4. Link: Create graph relations
    5. Dedupe: Merge duplicates
    6. Validate: Check for conflicts
    7. Crystallize: Promote to truths
    """

    def __init__(
        self,
        store: GraphStore,
        embedding_fn: Optional[Callable[[str], List[float]]] = None,
    ):
        self.store = store
        self.embedding_fn = embedding_fn
        self.conflict_resolver = ConflictResolver(store)
        self.truth_crystallizer = TruthCrystallizer(store)

    async def ingest_cycle_output(
        self,
        cycle_id: str,
        problem_id: str,
        agent_reports: Dict[str, Dict[str, Any]],
        tenant_id: Optional[str] = None,
    ) -> ConsolidationResult:
        """
        Ingest outputs from a triangle cycle.

        Args:
            cycle_id: Unique cycle identifier
            problem_id: Problem being solved
            agent_reports: Reports from each agent {role: report_data}
            tenant_id: Optional tenant scope

        Returns:
            ConsolidationResult with processing statistics
        """
        import time
        start_time = time.time()

        result = ConsolidationResult(success=True)

        try:
            # Create cycle entity
            cycle_entity = await self._create_cycle_entity(
                cycle_id, problem_id, agent_reports, tenant_id
            )
            result.entities_created += 1

            # Process each agent's report
            for role, report in agent_reports.items():
                entities, facts, relations = await self._process_agent_report(
                    role, report, cycle_id, problem_id, tenant_id
                )

                result.entities_created += len(entities)
                result.facts_created += len(facts)
                result.relations_created += len(relations)

                # Link to cycle
                for entity in entities:
                    rel = Relation(
                        id="",
                        relation_type=RelationType.PRODUCED_BY,
                        source_id=entity.id,
                        target_id=cycle_entity.id,
                        confidence=1.0,
                        provenance=entity.provenance,
                    )
                    await self.store.save_relation(rel)
                    result.relations_created += 1

            # Run deduplication
            dedup_count = await self._run_deduplication()
            result.duplicates_merged = dedup_count

            # Run conflict detection
            conflicts = await self._run_conflict_detection()
            result.conflicts = conflicts
            result.conflicts_detected = len(conflicts)

            # Run truth crystallization
            crystallized = await self._run_crystallization()
            result.truths_crystallized = crystallized

        except Exception as e:
            logger.error(f"Pipeline error: {e}", exc_info=True)
            result.success = False
            result.error = str(e)

        result.duration_ms = (time.time() - start_time) * 1000
        return result

    async def _create_cycle_entity(
        self,
        cycle_id: str,
        problem_id: str,
        agent_reports: Dict[str, Dict[str, Any]],
        tenant_id: Optional[str],
    ) -> MemoryEntity:
        """Create entity representing the cycle."""
        # Determine cycle status from reports
        statuses = [r.get("status", "unknown") for r in agent_reports.values()]
        overall_status = "completed" if all(s == "completed" for s in statuses) else "partial"

        cycle = Cycle(
            name=f"Cycle {cycle_id[:8]}",
            description=f"Triangle cycle for problem {problem_id}",
            provenance=Provenance(
                source_agent="memory_pipeline",
                source_cycle=cycle_id,
                source_problem=problem_id,
            ),
            cycle_id=cycle_id,
            problem_id=problem_id,
            status=overall_status,
            phase=len(agent_reports),
            scope=MemoryScope(
                access_level=AccessLevel.TENANT if tenant_id else AccessLevel.GLOBAL,
                tenant_id=tenant_id,
            ),
        )

        await self.store.save_entity(cycle)
        return cycle

    async def _process_agent_report(
        self,
        role: str,
        report: Dict[str, Any],
        cycle_id: str,
        problem_id: str,
        tenant_id: Optional[str],
    ) -> Tuple[List[MemoryEntity], List[MemoryFact], List[Relation]]:
        """Process an individual agent's report."""
        entities = []
        facts = []
        relations = []

        provenance = Provenance(
            source_agent=f"agent-{role.lower()}",
            source_cycle=cycle_id,
            source_problem=problem_id,
        )

        scope = MemoryScope(
            access_level=AccessLevel.TENANT if tenant_id else AccessLevel.GLOBAL,
            tenant_id=tenant_id,
        )

        # Extract decisions
        if "decisions" in report:
            for dec in report["decisions"]:
                decision = Decision(
                    name=dec.get("title", "Decision"),
                    description=dec.get("description", ""),
                    provenance=provenance,
                    decision_text=dec.get("text", ""),
                    rationale=dec.get("rationale", ""),
                    alternatives_considered=dec.get("alternatives", []),
                    impact=dec.get("impact", "unknown"),
                    confidence=dec.get("confidence", 0.7),
                    scope=scope,
                    tags=[role, "decision"],
                )
                await self.store.save_entity(decision)
                entities.append(decision)

        # Extract evidence
        if "evidence" in report:
            for ev in report["evidence"]:
                evidence = Evidence(
                    name=ev.get("claim", "Evidence")[:50],
                    description=ev.get("description", ""),
                    provenance=provenance,
                    claim=ev.get("claim", ""),
                    evidence_type=ev.get("type", "observation"),
                    source=ev.get("source", role),
                    strength=ev.get("strength", 0.5),
                    confidence=ev.get("confidence", 0.6),
                    scope=scope,
                    tags=[role, "evidence"],
                )
                await self.store.save_entity(evidence)
                entities.append(evidence)

        # Extract artifacts
        if "artifacts" in report:
            for art in report["artifacts"]:
                content = art.get("content", "")
                content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]

                artifact = Artifact(
                    name=art.get("name", "Artifact"),
                    description=art.get("description", ""),
                    provenance=provenance,
                    artifact_type=art.get("type", "document"),
                    content_hash=content_hash,
                    location=art.get("location"),
                    version=art.get("version", "1.0"),
                    confidence=1.0,
                    scope=scope,
                    tags=[role, art.get("type", "artifact")],
                )
                await self.store.save_entity(artifact)
                entities.append(artifact)

        # Create memory facts from report summary
        if "summary" in report:
            fact = MemoryFact(
                id="",
                content=report["summary"],
                summary=report["summary"][:200],
                layer=MemoryLayer.LONG_TERM,
                entity_type=EntityType.DECISION,  # Default
                confidence=report.get("confidence", 0.7),
                provenance=provenance,
                scope=scope,
                metadata={"role": role, "cycle_id": cycle_id},
                related_entity_ids=[e.id for e in entities],
            )

            # Generate embedding if available
            if self.embedding_fn:
                try:
                    fact.embedding = self.embedding_fn(fact.content)
                except Exception as e:
                    logger.warning(f"Embedding generation failed: {e}")

            await self.store.save_fact(fact)
            facts.append(fact)

        # Create relations between entities
        for i, entity in enumerate(entities[:-1]):
            for j, other in enumerate(entities[i + 1:], i + 1):
                # Create FOLLOWS relation for sequential entities
                rel = Relation(
                    id="",
                    relation_type=RelationType.FOLLOWS,
                    source_id=other.id,
                    target_id=entity.id,
                    confidence=0.8,
                    provenance=provenance,
                )
                await self.store.save_relation(rel)
                relations.append(rel)

        return entities, facts, relations

    async def _run_deduplication(self) -> int:
        """Run deduplication across recent entities."""
        from .schemas import MemoryQuery

        merged_count = 0

        # Get recent entities
        query = MemoryQuery(
            layers=[MemoryLayer.LONG_TERM],
            limit=100,
            time_range_start=datetime.now(timezone.utc) - timedelta(hours=24),
        )
        recent_entities = await self.store.query_entities(query)

        processed_ids: Set[str] = set()

        for entity in recent_entities:
            if entity.id in processed_ids:
                continue

            duplicates = await self.conflict_resolver.find_duplicates(entity)
            if duplicates:
                dup_entities = [d[0] for d in duplicates]
                await self.conflict_resolver.merge_duplicates(entity, dup_entities)
                merged_count += len(duplicates)
                processed_ids.update(d.id for d in dup_entities)

            processed_ids.add(entity.id)

        return merged_count

    async def _run_conflict_detection(self) -> List[ConflictReport]:
        """Detect conflicts in recent entities."""
        from .schemas import MemoryQuery

        all_conflicts = []

        query = MemoryQuery(
            entity_types=[EntityType.EVIDENCE, EntityType.DECISION, EntityType.TRUTH],
            limit=50,
            time_range_start=datetime.now(timezone.utc) - timedelta(hours=24),
        )
        entities = await self.store.query_entities(query)

        for entity in entities:
            conflicts = await self.conflict_resolver.detect_contradictions(entity)
            all_conflicts.extend(conflicts)

        return all_conflicts

    async def _run_crystallization(self) -> int:
        """Run truth crystallization on eligible entities."""
        candidates = await self.truth_crystallizer.find_crystallization_candidates()
        crystallized = 0

        for candidate in candidates:
            truth = await self.truth_crystallizer.crystallize(candidate)
            if truth:
                crystallized += 1

        return crystallized

    async def run_scheduled_consolidation(self) -> ConsolidationResult:
        """Run periodic consolidation job."""
        import time
        start_time = time.time()

        result = ConsolidationResult(success=True)

        try:
            # Deduplication
            result.duplicates_merged = await self._run_deduplication()

            # Conflict detection
            result.conflicts = await self._run_conflict_detection()
            result.conflicts_detected = len(result.conflicts)

            # Crystallization
            result.truths_crystallized = await self._run_crystallization()

            # Cleanup expired entities
            await self._cleanup_expired()

        except Exception as e:
            logger.error(f"Scheduled consolidation error: {e}", exc_info=True)
            result.success = False
            result.error = str(e)

        result.duration_ms = (time.time() - start_time) * 1000
        return result

    async def _cleanup_expired(self) -> int:
        """Archive entities past their TTL."""
        from .schemas import MemoryQuery

        query = MemoryQuery(limit=500)
        entities = await self.store.query_entities(query)

        archived = 0
        now = datetime.now(timezone.utc)

        for entity in entities:
            if entity.ttl_days and not entity.is_archived:
                age = (now - entity.provenance.created_at).days
                if age > entity.ttl_days:
                    await self.store.delete_entity(entity.id, hard_delete=False)
                    archived += 1

        return archived


class ConsolidationJob:
    """
    Scheduled consolidation job runner.

    Runs periodically to:
    - Process pending cycle outputs
    - Merge duplicates
    - Detect and flag conflicts
    - Crystallize truths
    - Clean up expired data
    """

    def __init__(
        self,
        pipeline: MemoryPipeline,
        interval_seconds: int = 300,  # 5 minutes
    ):
        self.pipeline = pipeline
        self.interval_seconds = interval_seconds
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Start the consolidation job."""
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("Consolidation job started")

    async def stop(self) -> None:
        """Stop the consolidation job."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Consolidation job stopped")

    async def _run_loop(self) -> None:
        """Main job loop."""
        while self._running:
            try:
                result = await self.pipeline.run_scheduled_consolidation()
                logger.info(
                    f"Consolidation completed: "
                    f"merged={result.duplicates_merged}, "
                    f"conflicts={result.conflicts_detected}, "
                    f"truths={result.truths_crystallized}, "
                    f"duration={result.duration_ms:.1f}ms"
                )
            except Exception as e:
                logger.error(f"Consolidation job error: {e}", exc_info=True)

            await asyncio.sleep(self.interval_seconds)

    async def run_once(self) -> ConsolidationResult:
        """Run consolidation once (for testing or manual trigger)."""
        return await self.pipeline.run_scheduled_consolidation()
