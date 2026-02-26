"""
RED OWL - Evidence Gatherer.

Gathers evidence to support or refute hypotheses from:
- Knowledge base documents
- System logs and metrics
- Crystallized truths (past solved problems)
- Pattern matching against known issue signatures

The key insight: crystallized truths are the mechanism for compounding.
Each solved problem becomes evidence for future analyses.
"""

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import structlog

from .models import (
    AnalysisDepth,
    Evidence,
    EvidenceType,
    EvidenceWeight,
    Hypothesis,
)

logger = structlog.get_logger(__name__)


@dataclass
class EvidenceGatheringResult:
    """Result of gathering evidence for hypotheses."""
    evidence: List[Evidence] = field(default_factory=list)
    crystallization_hits: int = 0
    sources_queried: List[str] = field(default_factory=list)
    duration_ms: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CrystallizedTruth:
    """A crystallized truth from past problem solving."""
    id: str
    problem_signature: str
    root_cause: str
    resolution: str
    confidence: float
    domain: str
    tags: List[str] = field(default_factory=list)
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class EvidenceGatherer:
    """
    Gathers evidence from multiple sources to evaluate hypotheses.

    Sources:
    - KB (Knowledge Base): Documentation, runbooks, known issues
    - Logs: System logs that match hypothesis patterns
    - Metrics: Prometheus/monitoring data
    - Crystallized: Past solved problems (THE KEY TO COMPOUNDING)
    - Patterns: Known issue signatures
    """

    # Known issue patterns by problem type
    ISSUE_PATTERNS = {
        "performance": {
            "high_cpu": {
                "indicators": ["cpu > 90%", "load average high", "throttling"],
                "weight": EvidenceWeight.STRONG_SUPPORT,
            },
            "memory_leak": {
                "indicators": ["memory growth", "OOM", "heap exhaustion"],
                "weight": EvidenceWeight.STRONG_SUPPORT,
            },
            "connection_exhaustion": {
                "indicators": ["connection pool", "max connections", "socket exhaustion"],
                "weight": EvidenceWeight.MODERATE_SUPPORT,
            },
            "gc_pressure": {
                "indicators": ["gc pause", "heap size", "allocation rate"],
                "weight": EvidenceWeight.MODERATE_SUPPORT,
            },
        },
        "availability": {
            "crash_loop": {
                "indicators": ["CrashLoopBackOff", "restart", "exit code"],
                "weight": EvidenceWeight.STRONG_SUPPORT,
            },
            "dependency_down": {
                "indicators": ["connection refused", "timeout", "unreachable"],
                "weight": EvidenceWeight.STRONG_SUPPORT,
            },
            "network_partition": {
                "indicators": ["split brain", "quorum", "network unreachable"],
                "weight": EvidenceWeight.MODERATE_SUPPORT,
            },
        },
        "security": {
            "auth_failure": {
                "indicators": ["401", "403", "authentication failed", "invalid token"],
                "weight": EvidenceWeight.STRONG_SUPPORT,
            },
            "injection": {
                "indicators": ["sql injection", "xss", "command injection"],
                "weight": EvidenceWeight.STRONG_SUPPORT,
            },
        },
        "data": {
            "corruption": {
                "indicators": ["checksum", "invalid data", "parse error"],
                "weight": EvidenceWeight.STRONG_SUPPORT,
            },
            "replication_lag": {
                "indicators": ["lag", "replica behind", "sync delay"],
                "weight": EvidenceWeight.MODERATE_SUPPORT,
            },
        },
    }

    def __init__(
        self,
        kb_client: Optional[Any] = None,
        log_client: Optional[Any] = None,
        metrics_client: Optional[Any] = None,
        crystallization_store: Optional[Any] = None,
    ):
        """
        Initialize the evidence gatherer.

        Args:
            kb_client: Client for knowledge base queries
            log_client: Client for log searches (Loki, Elasticsearch, etc.)
            metrics_client: Client for metrics queries (Prometheus, etc.)
            crystallization_store: Store for crystallized truths (vector DB)
        """
        self.kb_client = kb_client
        self.log_client = log_client
        self.metrics_client = metrics_client
        self.crystallization_store = crystallization_store
        logger.info(
            "evidence_gatherer_initialized",
            has_kb=kb_client is not None,
            has_logs=log_client is not None,
            has_metrics=metrics_client is not None,
            has_crystallization=crystallization_store is not None,
        )

    async def gather(
        self,
        hypotheses: List[Hypothesis],
        problem_type: str,
        problem_statement: str,
        depth: AnalysisDepth,
        max_evidence_per_hypothesis: int = 10,
        search_crystallized: bool = True,
    ) -> EvidenceGatheringResult:
        """
        Gather evidence for the given hypotheses.

        Args:
            hypotheses: Hypotheses to find evidence for
            problem_type: Type of problem (performance, availability, etc.)
            problem_statement: Original problem statement
            depth: Current analysis depth
            max_evidence_per_hypothesis: Max evidence items per hypothesis
            search_crystallized: Whether to search crystallized truths

        Returns:
            EvidenceGatheringResult with gathered evidence
        """
        start_time = time.time()
        result = EvidenceGatheringResult()

        for hypothesis in hypotheses:
            # 1. Pattern matching (always available)
            pattern_evidence = self._match_patterns(
                hypothesis, problem_type
            )
            result.evidence.extend(pattern_evidence)

            # 2. Crystallized truths (THE KEY TO COMPOUNDING)
            if search_crystallized:
                crystallized_evidence = await self._search_crystallized(
                    hypothesis, problem_statement, max_evidence_per_hypothesis
                )
                result.evidence.extend(crystallized_evidence)
                result.crystallization_hits += len(crystallized_evidence)
                if crystallized_evidence:
                    result.sources_queried.append("crystallized_truths")

            # 3. Knowledge base
            if self.kb_client:
                kb_evidence = await self._search_kb(
                    hypothesis, problem_statement, max_evidence_per_hypothesis
                )
                result.evidence.extend(kb_evidence)
                result.sources_queried.append("knowledge_base")

            # 4. Logs
            if self.log_client:
                log_evidence = await self._search_logs(
                    hypothesis, problem_type, max_evidence_per_hypothesis
                )
                result.evidence.extend(log_evidence)
                result.sources_queried.append("logs")

            # 5. Metrics
            if self.metrics_client:
                metrics_evidence = await self._query_metrics(
                    hypothesis, problem_type, max_evidence_per_hypothesis
                )
                result.evidence.extend(metrics_evidence)
                result.sources_queried.append("metrics")

        # Deduplicate sources
        result.sources_queried = list(set(result.sources_queried))
        result.duration_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "evidence_gathered",
            hypothesis_count=len(hypotheses),
            evidence_count=len(result.evidence),
            crystallization_hits=result.crystallization_hits,
            sources=result.sources_queried,
            duration_ms=result.duration_ms,
        )

        return result

    def _match_patterns(
        self,
        hypothesis: Hypothesis,
        problem_type: str,
    ) -> List[Evidence]:
        """Match hypothesis against known issue patterns."""
        evidence = []
        statement_lower = hypothesis.statement.lower()

        type_patterns = self.ISSUE_PATTERNS.get(problem_type, {})

        for pattern_name, pattern_info in type_patterns.items():
            indicators = pattern_info["indicators"]
            matched_indicators = [
                ind for ind in indicators
                if ind.lower() in statement_lower
            ]

            if matched_indicators:
                evidence.append(Evidence(
                    type=EvidenceType.PATTERN_MATCH,
                    source=f"pattern:{pattern_name}",
                    content=f"Matched pattern '{pattern_name}' with indicators: {matched_indicators}",
                    summary=f"Pattern match: {pattern_name}",
                    weight=pattern_info["weight"],
                    relevance=len(matched_indicators) / len(indicators),
                    hypothesis_ids=[hypothesis.id],
                    metadata={
                        "pattern_name": pattern_name,
                        "matched_indicators": matched_indicators,
                        "total_indicators": len(indicators),
                    },
                ))

        return evidence

    async def _search_crystallized(
        self,
        hypothesis: Hypothesis,
        problem_statement: str,
        limit: int,
    ) -> List[Evidence]:
        """
        Search crystallized truths for similar past problems.

        This is THE mechanism for compounding. Each solved problem
        becomes evidence for future analyses.
        """
        evidence = []

        if not self.crystallization_store:
            # Fallback: no crystallization store, return empty
            return evidence

        try:
            # Search by semantic similarity
            query = f"{hypothesis.statement} {problem_statement}"
            results = await self.crystallization_store.search(
                query=query,
                limit=limit,
                threshold=0.7,  # Minimum similarity
            )

            for result in results:
                # Higher similarity = stronger support
                similarity = result.get("similarity", 0.5)
                if similarity >= 0.9:
                    weight = EvidenceWeight.STRONG_SUPPORT
                elif similarity >= 0.8:
                    weight = EvidenceWeight.MODERATE_SUPPORT
                else:
                    weight = EvidenceWeight.WEAK_SUPPORT

                evidence.append(Evidence(
                    type=EvidenceType.CRYSTALLIZED_TRUTH,
                    source=f"crystallized:{result.get('id', 'unknown')}",
                    content=f"Past problem: {result.get('problem', 'Unknown')}\n"
                           f"Root cause: {result.get('root_cause', 'Unknown')}\n"
                           f"Resolution: {result.get('resolution', 'Unknown')}",
                    summary=f"Similar past case: {result.get('root_cause', 'Unknown')[:100]}",
                    weight=weight,
                    relevance=similarity,
                    hypothesis_ids=[hypothesis.id],
                    is_crystallized=True,
                    crystallization_id=result.get("id"),
                    metadata={
                        "similarity": similarity,
                        "domain": result.get("domain"),
                        "tags": result.get("tags", []),
                    },
                ))

            logger.debug(
                "crystallized_search_complete",
                query_length=len(query),
                results_found=len(evidence),
            )

        except Exception as e:
            logger.warning("crystallized_search_failed", error=str(e))

        return evidence

    async def _search_kb(
        self,
        hypothesis: Hypothesis,
        problem_statement: str,
        limit: int,
    ) -> List[Evidence]:
        """Search knowledge base for relevant documentation."""
        evidence = []

        if not self.kb_client:
            return evidence

        try:
            query = f"{hypothesis.statement} {problem_statement}"
            results = await self.kb_client.search(query=query, limit=limit)

            for result in results:
                relevance = result.get("score", 0.5)

                # Determine weight based on document type and relevance
                doc_type = result.get("type", "unknown")
                if doc_type == "runbook" and relevance > 0.8:
                    weight = EvidenceWeight.STRONG_SUPPORT
                elif doc_type in ["documentation", "known_issue"]:
                    weight = EvidenceWeight.MODERATE_SUPPORT
                else:
                    weight = EvidenceWeight.WEAK_SUPPORT

                evidence.append(Evidence(
                    type=EvidenceType.KB_DOCUMENT,
                    source=f"kb:{result.get('id', 'unknown')}",
                    content=result.get("content", "")[:2000],  # Truncate
                    summary=result.get("title", "KB Document"),
                    weight=weight,
                    relevance=relevance,
                    hypothesis_ids=[hypothesis.id],
                    metadata={
                        "doc_type": doc_type,
                        "path": result.get("path"),
                    },
                ))

        except Exception as e:
            logger.warning("kb_search_failed", error=str(e))

        return evidence

    async def _search_logs(
        self,
        hypothesis: Hypothesis,
        problem_type: str,
        limit: int,
    ) -> List[Evidence]:
        """Search logs for evidence supporting the hypothesis."""
        evidence = []

        if not self.log_client:
            return evidence

        try:
            # Extract keywords from hypothesis
            keywords = self._extract_keywords(hypothesis.statement)

            results = await self.log_client.search(
                keywords=keywords,
                limit=limit,
                time_range="1h",  # Recent logs
            )

            for result in results:
                # Log severity affects weight
                severity = result.get("level", "info").lower()
                if severity in ["error", "fatal", "critical"]:
                    weight = EvidenceWeight.STRONG_SUPPORT
                elif severity == "warning":
                    weight = EvidenceWeight.MODERATE_SUPPORT
                else:
                    weight = EvidenceWeight.WEAK_SUPPORT

                evidence.append(Evidence(
                    type=EvidenceType.LOG_ENTRY,
                    source=f"log:{result.get('source', 'unknown')}",
                    content=result.get("message", "")[:1000],
                    summary=f"[{severity.upper()}] {result.get('message', '')[:100]}",
                    weight=weight,
                    relevance=result.get("relevance", 0.5),
                    hypothesis_ids=[hypothesis.id],
                    metadata={
                        "timestamp": result.get("timestamp"),
                        "level": severity,
                        "service": result.get("service"),
                    },
                ))

        except Exception as e:
            logger.warning("log_search_failed", error=str(e))

        return evidence

    async def _query_metrics(
        self,
        hypothesis: Hypothesis,
        problem_type: str,
        limit: int,
    ) -> List[Evidence]:
        """Query metrics for evidence supporting the hypothesis."""
        evidence = []

        if not self.metrics_client:
            return evidence

        try:
            # Get relevant metrics based on problem type
            metric_queries = self._get_metric_queries(problem_type)

            for query_name, query in metric_queries.items():
                result = await self.metrics_client.query(query)

                if result and self._is_anomalous(result):
                    evidence.append(Evidence(
                        type=EvidenceType.METRIC,
                        source=f"metric:{query_name}",
                        content=f"Metric {query_name}: {result.get('value')}",
                        summary=f"Anomalous metric: {query_name}",
                        weight=EvidenceWeight.MODERATE_SUPPORT,
                        relevance=0.7,
                        hypothesis_ids=[hypothesis.id],
                        metadata={
                            "metric_name": query_name,
                            "value": result.get("value"),
                            "threshold": result.get("threshold"),
                        },
                    ))

                    if len(evidence) >= limit:
                        break

        except Exception as e:
            logger.warning("metrics_query_failed", error=str(e))

        return evidence

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract search keywords from text."""
        import re
        # Remove common words, keep meaningful terms
        stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "must", "shall",
            "can", "need", "dare", "ought", "used", "to", "of", "in",
            "for", "on", "with", "at", "by", "from", "as", "into",
            "through", "during", "before", "after", "above", "below",
            "between", "under", "again", "further", "then", "once",
            "and", "but", "or", "nor", "so", "yet", "both", "either",
            "neither", "not", "only", "same", "than", "too", "very",
            "just", "also", "now", "here", "there", "when", "where",
            "why", "how", "all", "each", "every", "both", "few", "more",
            "most", "other", "some", "such", "no", "any", "this", "that",
        }

        words = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', text.lower())
        keywords = [w for w in words if w not in stopwords and len(w) > 2]

        return list(dict.fromkeys(keywords))[:10]  # Dedupe, limit to 10

    def _get_metric_queries(self, problem_type: str) -> Dict[str, str]:
        """Get relevant metric queries for problem type."""
        base_queries = {
            "performance": {
                "cpu_usage": "avg(rate(process_cpu_seconds_total[5m])) * 100",
                "memory_usage": "avg(process_resident_memory_bytes / 1024 / 1024)",
                "request_latency": "histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))",
                "error_rate": "sum(rate(http_requests_total{status=~\"5..\"}[5m])) / sum(rate(http_requests_total[5m]))",
            },
            "availability": {
                "up_status": "up",
                "restart_count": "sum(increase(kube_pod_container_status_restarts_total[1h]))",
                "ready_replicas": "kube_deployment_status_replicas_ready",
            },
            "security": {
                "auth_failures": "sum(rate(auth_failures_total[5m]))",
                "blocked_requests": "sum(rate(waf_blocked_requests_total[5m]))",
            },
            "data": {
                "replication_lag": "max(mysql_slave_seconds_behind_master)",
                "disk_usage": "avg(disk_used_percent)",
            },
        }

        return base_queries.get(problem_type, base_queries["performance"])

    def _is_anomalous(self, result: Dict[str, Any]) -> bool:
        """Check if metric result is anomalous."""
        value = result.get("value")
        threshold = result.get("threshold")

        if value is None:
            return False

        # Simple threshold check
        if threshold is not None:
            return value > threshold

        # Default: consider high values anomalous
        return value > 0.9 if isinstance(value, float) and value <= 1 else value > 90


# Factory function
def create_evidence_gatherer(
    kb_client: Optional[Any] = None,
    log_client: Optional[Any] = None,
    metrics_client: Optional[Any] = None,
    crystallization_store: Optional[Any] = None,
) -> EvidenceGatherer:
    """Create an evidence gatherer instance."""
    return EvidenceGatherer(
        kb_client=kb_client,
        log_client=log_client,
        metrics_client=metrics_client,
        crystallization_store=crystallization_store,
    )
