"""
Memory Observability Metrics
============================

Prometheus metrics for monitoring the memory system.

Metrics:
- memory_facts_total: Total facts stored by layer and type
- memory_entities_total: Total entities by type
- memory_relations_total: Total relations by type
- memory_recall_latency: Query latency histogram
- memory_recall_results: Results returned per query
- memory_hit_rate: Cache hit rate (when caching enabled)
- memory_conflict_rate: Rate of conflicts detected
- memory_crystallization_rate: Rate of truth crystallization
- memory_consolidation_duration: Consolidation job duration
"""

import time
from contextlib import contextmanager
from functools import wraps
from typing import Callable, Optional

try:
    from prometheus_client import Counter, Histogram, Gauge, Summary
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


# Metrics definitions (only create if prometheus_client is available)
if PROMETHEUS_AVAILABLE:
    # Fact metrics
    MEMORY_FACTS_TOTAL = Gauge(
        "memory_facts_total",
        "Total number of memory facts",
        ["layer", "entity_type"],
    )

    MEMORY_FACTS_CREATED = Counter(
        "memory_facts_created_total",
        "Total facts created",
        ["layer", "entity_type", "agent_role"],
    )

    # Entity metrics
    MEMORY_ENTITIES_TOTAL = Gauge(
        "memory_entities_total",
        "Total number of entities",
        ["entity_type", "layer"],
    )

    MEMORY_ENTITIES_CREATED = Counter(
        "memory_entities_created_total",
        "Total entities created",
        ["entity_type", "agent_role"],
    )

    MEMORY_ENTITIES_ARCHIVED = Counter(
        "memory_entities_archived_total",
        "Total entities archived",
        ["entity_type"],
    )

    # Relation metrics
    MEMORY_RELATIONS_TOTAL = Gauge(
        "memory_relations_total",
        "Total number of relations",
        ["relation_type"],
    )

    MEMORY_RELATIONS_CREATED = Counter(
        "memory_relations_created_total",
        "Total relations created",
        ["relation_type"],
    )

    # Query/retrieval metrics
    MEMORY_RECALL_LATENCY = Histogram(
        "memory_recall_latency_seconds",
        "Memory retrieval latency in seconds",
        ["role", "strategy"],
        buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
    )

    MEMORY_RECALL_RESULTS = Histogram(
        "memory_recall_results",
        "Number of results returned per query",
        ["role"],
        buckets=[1, 5, 10, 20, 50, 100],
    )

    MEMORY_QUERIES_TOTAL = Counter(
        "memory_queries_total",
        "Total memory queries",
        ["role", "strategy", "status"],
    )

    # Cache metrics (for future use)
    MEMORY_CACHE_HITS = Counter(
        "memory_cache_hits_total",
        "Cache hits for memory queries",
        ["cache_type"],
    )

    MEMORY_CACHE_MISSES = Counter(
        "memory_cache_misses_total",
        "Cache misses for memory queries",
        ["cache_type"],
    )

    # Conflict metrics
    MEMORY_CONFLICTS_DETECTED = Counter(
        "memory_conflicts_detected_total",
        "Total conflicts detected",
        ["conflict_type"],
    )

    MEMORY_CONFLICTS_RESOLVED = Counter(
        "memory_conflicts_resolved_total",
        "Total conflicts resolved",
        ["conflict_type", "resolution"],
    )

    MEMORY_CONFLICTS_PENDING = Gauge(
        "memory_conflicts_pending",
        "Number of pending conflicts",
        ["conflict_type"],
    )

    # Crystallization metrics
    MEMORY_CRYSTALLIZATIONS = Counter(
        "memory_crystallizations_total",
        "Total truths crystallized",
        ["domain"],
    )

    MEMORY_CRYSTALLIZATION_CANDIDATES = Gauge(
        "memory_crystallization_candidates",
        "Number of crystallization candidates",
    )

    # Consolidation metrics
    MEMORY_CONSOLIDATION_DURATION = Histogram(
        "memory_consolidation_duration_seconds",
        "Consolidation job duration",
        buckets=[1, 5, 10, 30, 60, 120, 300],
    )

    MEMORY_CONSOLIDATION_RUNS = Counter(
        "memory_consolidation_runs_total",
        "Total consolidation runs",
        ["status"],
    )

    MEMORY_DUPLICATES_MERGED = Counter(
        "memory_duplicates_merged_total",
        "Total duplicates merged",
    )

    # Ingest metrics
    MEMORY_INGEST_DURATION = Histogram(
        "memory_ingest_duration_seconds",
        "Cycle ingest duration",
        buckets=[0.1, 0.5, 1, 2, 5, 10],
    )

    MEMORY_INGEST_CYCLES = Counter(
        "memory_ingest_cycles_total",
        "Total cycles ingested",
        ["status"],
    )

    # Store metrics
    MEMORY_STORE_OPERATIONS = Counter(
        "memory_store_operations_total",
        "Total store operations",
        ["operation", "backend"],
    )

    MEMORY_STORE_LATENCY = Histogram(
        "memory_store_latency_seconds",
        "Store operation latency",
        ["operation", "backend"],
        buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5],
    )

else:
    # Dummy implementations when prometheus_client is not available
    class DummyMetric:
        def labels(self, *args, **kwargs):
            return self

        def inc(self, *args, **kwargs):
            pass

        def dec(self, *args, **kwargs):
            pass

        def set(self, *args, **kwargs):
            pass

        def observe(self, *args, **kwargs):
            pass

    MEMORY_FACTS_TOTAL = DummyMetric()
    MEMORY_FACTS_CREATED = DummyMetric()
    MEMORY_ENTITIES_TOTAL = DummyMetric()
    MEMORY_ENTITIES_CREATED = DummyMetric()
    MEMORY_ENTITIES_ARCHIVED = DummyMetric()
    MEMORY_RELATIONS_TOTAL = DummyMetric()
    MEMORY_RELATIONS_CREATED = DummyMetric()
    MEMORY_RECALL_LATENCY = DummyMetric()
    MEMORY_RECALL_RESULTS = DummyMetric()
    MEMORY_QUERIES_TOTAL = DummyMetric()
    MEMORY_CACHE_HITS = DummyMetric()
    MEMORY_CACHE_MISSES = DummyMetric()
    MEMORY_CONFLICTS_DETECTED = DummyMetric()
    MEMORY_CONFLICTS_RESOLVED = DummyMetric()
    MEMORY_CONFLICTS_PENDING = DummyMetric()
    MEMORY_CRYSTALLIZATIONS = DummyMetric()
    MEMORY_CRYSTALLIZATION_CANDIDATES = DummyMetric()
    MEMORY_CONSOLIDATION_DURATION = DummyMetric()
    MEMORY_CONSOLIDATION_RUNS = DummyMetric()
    MEMORY_DUPLICATES_MERGED = DummyMetric()
    MEMORY_INGEST_DURATION = DummyMetric()
    MEMORY_INGEST_CYCLES = DummyMetric()
    MEMORY_STORE_OPERATIONS = DummyMetric()
    MEMORY_STORE_LATENCY = DummyMetric()


@contextmanager
def track_recall_latency(role: str = "unknown", strategy: str = "balanced"):
    """Context manager to track recall latency."""
    start = time.time()
    try:
        yield
        MEMORY_QUERIES_TOTAL.labels(role=role, strategy=strategy, status="success").inc()
    except Exception:
        MEMORY_QUERIES_TOTAL.labels(role=role, strategy=strategy, status="error").inc()
        raise
    finally:
        duration = time.time() - start
        MEMORY_RECALL_LATENCY.labels(role=role, strategy=strategy).observe(duration)


@contextmanager
def track_consolidation():
    """Context manager to track consolidation job."""
    start = time.time()
    try:
        yield
        MEMORY_CONSOLIDATION_RUNS.labels(status="success").inc()
    except Exception:
        MEMORY_CONSOLIDATION_RUNS.labels(status="error").inc()
        raise
    finally:
        duration = time.time() - start
        MEMORY_CONSOLIDATION_DURATION.observe(duration)


@contextmanager
def track_ingest():
    """Context manager to track cycle ingest."""
    start = time.time()
    try:
        yield
        MEMORY_INGEST_CYCLES.labels(status="success").inc()
    except Exception:
        MEMORY_INGEST_CYCLES.labels(status="error").inc()
        raise
    finally:
        duration = time.time() - start
        MEMORY_INGEST_DURATION.observe(duration)


@contextmanager
def track_store_operation(operation: str, backend: str = "sqlite"):
    """Context manager to track store operations."""
    start = time.time()
    try:
        yield
        MEMORY_STORE_OPERATIONS.labels(operation=operation, backend=backend).inc()
    finally:
        duration = time.time() - start
        MEMORY_STORE_LATENCY.labels(operation=operation, backend=backend).observe(duration)


def track_entity_created(entity_type: str, agent_role: str = "unknown"):
    """Record entity creation."""
    MEMORY_ENTITIES_CREATED.labels(entity_type=entity_type, agent_role=agent_role).inc()


def track_fact_created(layer: str, entity_type: str, agent_role: str = "unknown"):
    """Record fact creation."""
    MEMORY_FACTS_CREATED.labels(
        layer=layer, entity_type=entity_type, agent_role=agent_role
    ).inc()


def track_relation_created(relation_type: str):
    """Record relation creation."""
    MEMORY_RELATIONS_CREATED.labels(relation_type=relation_type).inc()


def track_conflict_detected(conflict_type: str):
    """Record conflict detection."""
    MEMORY_CONFLICTS_DETECTED.labels(conflict_type=conflict_type).inc()


def track_conflict_resolved(conflict_type: str, resolution: str):
    """Record conflict resolution."""
    MEMORY_CONFLICTS_RESOLVED.labels(
        conflict_type=conflict_type, resolution=resolution
    ).inc()


def track_crystallization(domain: str = "general"):
    """Record truth crystallization."""
    MEMORY_CRYSTALLIZATIONS.labels(domain=domain).inc()


def track_duplicates_merged(count: int = 1):
    """Record duplicates merged."""
    for _ in range(count):
        MEMORY_DUPLICATES_MERGED.inc()


def track_recall_results(count: int, role: str = "unknown"):
    """Record number of results returned."""
    MEMORY_RECALL_RESULTS.labels(role=role).observe(count)


def update_entity_gauge(entity_type: str, layer: str, count: int):
    """Update entity count gauge."""
    MEMORY_ENTITIES_TOTAL.labels(entity_type=entity_type, layer=layer).set(count)


def update_fact_gauge(layer: str, entity_type: str, count: int):
    """Update fact count gauge."""
    MEMORY_FACTS_TOTAL.labels(layer=layer, entity_type=entity_type).set(count)


def update_relation_gauge(relation_type: str, count: int):
    """Update relation count gauge."""
    MEMORY_RELATIONS_TOTAL.labels(relation_type=relation_type).set(count)


def update_conflicts_pending(conflict_type: str, count: int):
    """Update pending conflicts gauge."""
    MEMORY_CONFLICTS_PENDING.labels(conflict_type=conflict_type).set(count)


def update_crystallization_candidates(count: int):
    """Update crystallization candidates gauge."""
    MEMORY_CRYSTALLIZATION_CANDIDATES.set(count)


def instrument_retriever(retriever_class):
    """Class decorator to instrument retriever with metrics."""

    original_retrieve = retriever_class.retrieve

    @wraps(original_retrieve)
    async def instrumented_retrieve(self, query, role=None, strategy=None):
        strategy_name = strategy.value if strategy else "balanced"
        role_name = role or "unknown"

        with track_recall_latency(role=role_name, strategy=strategy_name):
            result = await original_retrieve(self, query, role, strategy)

        track_recall_results(len(result.entities) + len(result.facts), role=role_name)
        return result

    retriever_class.retrieve = instrumented_retrieve
    return retriever_class


def instrument_pipeline(pipeline_class):
    """Class decorator to instrument pipeline with metrics."""

    original_ingest = pipeline_class.ingest_cycle_output

    @wraps(original_ingest)
    async def instrumented_ingest(self, *args, **kwargs):
        with track_ingest():
            result = await original_ingest(self, *args, **kwargs)

        # Track created entities
        # (assuming result has these attributes)
        if hasattr(result, 'duplicates_merged'):
            track_duplicates_merged(result.duplicates_merged)

        if hasattr(result, 'conflicts'):
            for conflict in result.conflicts:
                track_conflict_detected(conflict.conflict_type.value)

        return result

    pipeline_class.ingest_cycle_output = instrumented_ingest
    return pipeline_class
