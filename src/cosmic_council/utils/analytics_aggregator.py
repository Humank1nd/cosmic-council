"""
Analytics Aggregation Service for Agent Orchestrator.

Pulls data from repositories and provides aggregated metrics
for dashboards and real-time streaming.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from prometheus_client import Counter, Gauge, Histogram

logger = logging.getLogger(__name__)


# ============== Prometheus Metrics ==============

AGGREGATION_REQUESTS = Counter(
    "analytics_aggregation_requests_total",
    "Total aggregation requests",
    ["metric_type"],
)

AGGREGATION_LATENCY = Histogram(
    "analytics_aggregation_latency_seconds",
    "Aggregation request latency",
    ["metric_type"],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

CACHE_HITS = Counter(
    "analytics_cache_hits_total",
    "Cache hit count",
    ["metric_type"],
)


# ============== Enums ==============

class MetricType(Enum):
    """Types of aggregated metrics."""
    CYCLES = "cycles"
    PROBLEMS = "problems"
    SOLUTIONS = "solutions"
    ENTERPRISES = "enterprises"
    RECURSIONS = "recursions"
    KPIS = "kpis"
    TRENDS = "trends"


class TimeGranularity(Enum):
    """Time granularity for aggregations."""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


# ============== Cache Entry ==============

@dataclass
class CacheEntry:
    """Cached aggregation result."""
    data: Dict[str, Any]
    timestamp: datetime
    ttl_seconds: int

    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        age = (datetime.utcnow() - self.timestamp).total_seconds()
        return age > self.ttl_seconds


# ============== Aggregated Metrics ==============

@dataclass
class AggregatedMetrics:
    """Container for aggregated analytics data."""
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Cycle metrics
    total_cycles: int = 0
    completed_cycles: int = 0
    failed_cycles: int = 0
    in_progress_cycles: int = 0
    cycle_success_rate: float = 0.0
    avg_cycle_duration: float = 0.0

    # Problem metrics
    total_problems: int = 0
    solved_problems: int = 0
    problem_solve_rate: float = 0.0

    # Solution metrics
    total_solutions: int = 0
    avg_solution_quality: float = 0.0
    implementation_rate: float = 0.0

    # Enterprise metrics
    enterprise_performance: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # KPIs
    kpis: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "cycles": {
                "total": self.total_cycles,
                "completed": self.completed_cycles,
                "failed": self.failed_cycles,
                "in_progress": self.in_progress_cycles,
                "success_rate": self.cycle_success_rate,
                "avg_duration": self.avg_cycle_duration,
            },
            "problems": {
                "total": self.total_problems,
                "solved": self.solved_problems,
                "solve_rate": self.problem_solve_rate,
            },
            "solutions": {
                "total": self.total_solutions,
                "avg_quality": self.avg_solution_quality,
                "implementation_rate": self.implementation_rate,
            },
            "enterprises": self.enterprise_performance,
            "kpis": self.kpis,
        }


# ============== Analytics Aggregator ==============

class AnalyticsAggregator:
    """
    Service for aggregating analytics data.

    Features:
    - Pulls from multiple data sources
    - Caches results with configurable TTL
    - Provides real-time metrics updates
    - Supports different time granularities
    """

    def __init__(
        self,
        repository=None,
        redis_client=None,
        cache_ttl: int = 300,  # 5 minutes default
    ):
        self._repository = repository
        self._redis = redis_client
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._update_callbacks: List[Callable[[AggregatedMetrics], None]] = []

    def set_repository(self, repository) -> None:
        """Set the analytics repository."""
        self._repository = repository

    def set_redis_client(self, client) -> None:
        """Set Redis client for distributed caching."""
        self._redis = client

    def on_update(self, callback: Callable[[AggregatedMetrics], None]) -> None:
        """Register callback for metrics updates."""
        self._update_callbacks.append(callback)

    # ============== Main Aggregation ==============

    async def get_aggregated_metrics(
        self,
        time_range_days: int = 1,
        use_cache: bool = True,
    ) -> AggregatedMetrics:
        """
        Get all aggregated metrics.

        Args:
            time_range_days: Number of days to aggregate
            use_cache: Whether to use cached results

        Returns:
            AggregatedMetrics with all data
        """
        cache_key = f"aggregated:{time_range_days}"

        # Check cache
        if use_cache:
            cached = self._get_from_cache(cache_key)
            if cached:
                CACHE_HITS.labels(metric_type="aggregated").inc()
                return AggregatedMetrics(**cached)

        AGGREGATION_REQUESTS.labels(metric_type="aggregated").inc()

        with AGGREGATION_LATENCY.labels(metric_type="aggregated").time():
            metrics = await self._aggregate_all(time_range_days)

        # Cache result
        self._set_cache(cache_key, metrics.to_dict())

        # Notify callbacks
        await self._notify_callbacks(metrics)

        return metrics

    async def _aggregate_all(self, time_range_days: int) -> AggregatedMetrics:
        """Aggregate all metrics from repository."""
        metrics = AggregatedMetrics()

        if not self._repository:
            logger.warning("No repository configured, returning empty metrics")
            return metrics

        try:
            # Import here to avoid circular imports
            from ...database.repositories.analytics_repository import TimeRange

            time_range = TimeRange.custom(time_range_days)

            # Fetch all metrics in parallel
            cycle_task = self._repository.get_cycle_metrics(time_range)
            problem_task = self._repository.get_problem_metrics(time_range)
            solution_task = self._repository.get_solution_metrics(time_range)
            enterprise_task = self._repository.get_enterprise_performance(time_range=time_range)
            kpi_task = self._repository.get_kpis(time_range)

            results = await asyncio.gather(
                cycle_task,
                problem_task,
                solution_task,
                enterprise_task,
                kpi_task,
                return_exceptions=True,
            )

            # Process cycle metrics
            if not isinstance(results[0], Exception):
                cycle_data = results[0]
                metrics.total_cycles = cycle_data.get("total_cycles", 0)
                metrics.completed_cycles = cycle_data.get("completed_cycles", 0)
                metrics.failed_cycles = cycle_data.get("failed_cycles", 0)
                metrics.in_progress_cycles = cycle_data.get("in_progress_cycles", 0)
                metrics.cycle_success_rate = cycle_data.get("success_rate", 0)
                metrics.avg_cycle_duration = cycle_data.get("avg_duration_seconds", 0)

            # Process problem metrics
            if not isinstance(results[1], Exception):
                problem_data = results[1]
                metrics.total_problems = problem_data.get("total_problems", 0)
                metrics.solved_problems = problem_data.get("solved_problems", 0)
                total = metrics.total_problems
                metrics.problem_solve_rate = (
                    metrics.solved_problems / total * 100 if total > 0 else 0
                )

            # Process solution metrics
            if not isinstance(results[2], Exception):
                solution_data = results[2]
                metrics.total_solutions = solution_data.get("total_solutions", 0)
                metrics.avg_solution_quality = solution_data.get("avg_quality_score", 0)
                metrics.implementation_rate = solution_data.get("implementation_rate", 0)

            # Process enterprise metrics
            if not isinstance(results[3], Exception):
                metrics.enterprise_performance = results[3]

            # Process KPIs
            if not isinstance(results[4], Exception):
                metrics.kpis = results[4]

        except Exception as e:
            logger.error(f"Aggregation failed: {e}")

        return metrics

    # ============== Specific Metric Getters ==============

    async def get_cycle_metrics(
        self,
        time_range_days: int = 1,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """Get cycle-specific metrics."""
        cache_key = f"cycles:{time_range_days}"

        if use_cache:
            cached = self._get_from_cache(cache_key)
            if cached:
                CACHE_HITS.labels(metric_type="cycles").inc()
                return cached

        AGGREGATION_REQUESTS.labels(metric_type="cycles").inc()

        if not self._repository:
            return {}

        from ...database.repositories.analytics_repository import TimeRange
        time_range = TimeRange.custom(time_range_days)

        with AGGREGATION_LATENCY.labels(metric_type="cycles").time():
            data = await self._repository.get_cycle_metrics(time_range)

        self._set_cache(cache_key, data)
        return data

    async def get_enterprise_metrics(
        self,
        enterprise: Optional[str] = None,
        time_range_days: int = 1,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """Get enterprise-specific metrics."""
        cache_key = f"enterprise:{enterprise or 'all'}:{time_range_days}"

        if use_cache:
            cached = self._get_from_cache(cache_key)
            if cached:
                CACHE_HITS.labels(metric_type="enterprises").inc()
                return cached

        AGGREGATION_REQUESTS.labels(metric_type="enterprises").inc()

        if not self._repository:
            return {}

        from ...database.repositories.analytics_repository import TimeRange
        time_range = TimeRange.custom(time_range_days)

        with AGGREGATION_LATENCY.labels(metric_type="enterprises").time():
            data = await self._repository.get_enterprise_performance(
                enterprise=enterprise,
                time_range=time_range,
            )

        self._set_cache(cache_key, data)
        return data

    async def get_kpis(
        self,
        time_range_days: int = 1,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """Get KPI metrics."""
        cache_key = f"kpis:{time_range_days}"

        if use_cache:
            cached = self._get_from_cache(cache_key)
            if cached:
                CACHE_HITS.labels(metric_type="kpis").inc()
                return cached

        AGGREGATION_REQUESTS.labels(metric_type="kpis").inc()

        if not self._repository:
            return {}

        from ...database.repositories.analytics_repository import TimeRange
        time_range = TimeRange.custom(time_range_days)

        with AGGREGATION_LATENCY.labels(metric_type="kpis").time():
            data = await self._repository.get_kpis(time_range)

        self._set_cache(cache_key, data)
        return data

    async def get_trend_data(
        self,
        metric: str,
        time_range_days: int = 7,
        granularity: str = "day",
        use_cache: bool = True,
    ) -> List[Dict[str, Any]]:
        """Get trend data for a metric."""
        cache_key = f"trends:{metric}:{time_range_days}:{granularity}"

        if use_cache:
            cached = self._get_from_cache(cache_key)
            if cached:
                CACHE_HITS.labels(metric_type="trends").inc()
                return cached

        AGGREGATION_REQUESTS.labels(metric_type="trends").inc()

        if not self._repository:
            return []

        from ...database.repositories.analytics_repository import TimeRange
        time_range = TimeRange.custom(time_range_days)

        with AGGREGATION_LATENCY.labels(metric_type="trends").time():
            data = await self._repository.get_trend_data(
                metric=metric,
                time_range=time_range,
                granularity=granularity,
            )

        self._set_cache(cache_key, data)
        return data

    # ============== Cache Management ==============

    def _get_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Get data from cache if not expired."""
        # Try local cache first
        if key in self._cache:
            entry = self._cache[key]
            if not entry.is_expired():
                return entry.data
            else:
                del self._cache[key]

        # TODO: Try Redis cache if available
        return None

    def _set_cache(self, key: str, data: Any) -> None:
        """Set data in cache."""
        self._cache[key] = CacheEntry(
            data=data,
            timestamp=datetime.utcnow(),
            ttl_seconds=self.cache_ttl,
        )

        # TODO: Set in Redis cache if available

    def invalidate_cache(self, pattern: Optional[str] = None) -> int:
        """
        Invalidate cache entries.

        Args:
            pattern: Optional pattern to match (None = all)

        Returns:
            Number of entries invalidated
        """
        if pattern is None:
            count = len(self._cache)
            self._cache.clear()
            return count

        keys_to_delete = [
            k for k in self._cache.keys()
            if pattern in k
        ]
        for key in keys_to_delete:
            del self._cache[key]

        return len(keys_to_delete)

    # ============== Callbacks ==============

    async def _notify_callbacks(self, metrics: AggregatedMetrics) -> None:
        """Notify registered callbacks of metrics update."""
        for callback in self._update_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(metrics)
                else:
                    callback(metrics)
            except Exception as e:
                logger.error(f"Callback error: {e}")

    # ============== Background Refresh ==============

    async def start_background_refresh(
        self,
        interval_seconds: int = 60,
    ) -> asyncio.Task:
        """
        Start background task to refresh metrics.

        Args:
            interval_seconds: Refresh interval

        Returns:
            Background task
        """
        async def refresh_loop():
            while True:
                try:
                    await self.get_aggregated_metrics(use_cache=False)
                    logger.debug("Background metrics refresh completed")
                except Exception as e:
                    logger.error(f"Background refresh failed: {e}")

                await asyncio.sleep(interval_seconds)

        task = asyncio.create_task(refresh_loop())
        logger.info(f"Started background refresh every {interval_seconds}s")
        return task


# ============== Factory Functions ==============

_default_aggregator: Optional[AnalyticsAggregator] = None


def get_aggregator() -> AnalyticsAggregator:
    """Get the global analytics aggregator."""
    global _default_aggregator
    if _default_aggregator is None:
        _default_aggregator = AnalyticsAggregator()
    return _default_aggregator


def set_aggregator(aggregator: AnalyticsAggregator) -> None:
    """Set the global analytics aggregator."""
    global _default_aggregator
    _default_aggregator = aggregator


def create_aggregator(
    repository=None,
    redis_client=None,
    cache_ttl: int = 300,
) -> AnalyticsAggregator:
    """
    Create a new analytics aggregator.

    Args:
        repository: Analytics repository instance
        redis_client: Optional Redis client for distributed caching
        cache_ttl: Cache TTL in seconds

    Returns:
        Configured AnalyticsAggregator
    """
    return AnalyticsAggregator(
        repository=repository,
        redis_client=redis_client,
        cache_ttl=cache_ttl,
    )
