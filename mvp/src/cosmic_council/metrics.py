"""
Cosmic Council Metrics and Monitoring
Prometheus metrics for production monitoring.
"""

import time
import logging
from typing import Dict, Any, Optional
from functools import wraps
from dataclasses import dataclass
from datetime import datetime

try:
    from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class MetricData:
    """Metric data structure."""
    name: str
    value: float
    labels: Dict[str, str]
    timestamp: datetime


class MetricsCollector:
    """Prometheus metrics collector for Cosmic Council."""
    
    def __init__(self):
        """Initialize metrics collector."""
        self.enabled = PROMETHEUS_AVAILABLE
        
        if self.enabled:
            self._initialize_metrics()
        else:
            logger.warning("Prometheus client not available, metrics disabled")
    
    def _initialize_metrics(self):
        """Initialize Prometheus metrics."""
        # Request metrics
        self.request_count = Counter(
            'cosmic_council_requests_total',
            'Total number of requests',
            ['method', 'endpoint', 'status_code']
        )
        
        self.request_duration = Histogram(
            'cosmic_council_request_duration_seconds',
            'Request duration in seconds',
            ['method', 'endpoint']
        )
        
        # Problem solving metrics
        self.problems_solved = Counter(
            'cosmic_council_problems_solved_total',
            'Total number of problems solved',
            ['complexity', 'domain']
        )
        
        self.problem_solving_duration = Histogram(
            'cosmic_council_problem_solving_duration_seconds',
            'Problem solving duration in seconds',
            ['complexity']
        )
        
        # Enterprise metrics
        self.enterprise_processing_time = Histogram(
            'cosmic_council_enterprise_processing_seconds',
            'Enterprise processing time in seconds',
            ['enterprise', 'enterprise_type']
        )
        
        self.enterprise_confidence = Histogram(
            'cosmic_council_enterprise_confidence',
            'Enterprise response confidence scores',
            ['enterprise']
        )
        
        # AI metrics
        self.ai_requests = Counter(
            'cosmic_council_ai_requests_total',
            'Total AI API requests',
            ['provider', 'model', 'status']
        )
        
        self.ai_tokens_used = Counter(
            'cosmic_council_ai_tokens_total',
            'Total AI tokens used',
            ['provider', 'model']
        )
        
        self.ai_cost = Counter(
            'cosmic_council_ai_cost_total',
            'Total AI costs in USD',
            ['provider', 'model']
        )
        
        # Database metrics
        self.database_operations = Counter(
            'cosmic_council_database_operations_total',
            'Total database operations',
            ['operation', 'table', 'status']
        )
        
        self.database_connection_pool = Gauge(
            'cosmic_council_database_connections_active',
            'Active database connections'
        )
        
        # Cache metrics
        self.cache_operations = Counter(
            'cosmic_council_cache_operations_total',
            'Total cache operations',
            ['operation', 'status']
        )
        
        self.cache_hit_rate = Gauge(
            'cosmic_council_cache_hit_rate',
            'Cache hit rate percentage'
        )
        
        # System metrics
        self.active_sessions = Gauge(
            'cosmic_council_active_sessions',
            'Number of active problem-solving sessions'
        )
        
        self.system_info = Info(
            'cosmic_council_system_info',
            'System information'
        )
        
        # Set system info
        self.system_info.info({
            'version': '2.0.0',
            'environment': 'production'
        })
        
        logger.info("✅ Prometheus metrics initialized")
    
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics."""
        if not self.enabled:
            return
        
        self.request_count.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code)
        ).inc()
        
        self.request_duration.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    def record_problem_solved(self, complexity: str, domain: str, duration: float):
        """Record problem solving metrics."""
        if not self.enabled:
            return
        
        self.problems_solved.labels(
            complexity=complexity,
            domain=domain or 'unknown'
        ).inc()
        
        self.problem_solving_duration.labels(
            complexity=complexity
        ).observe(duration)
    
    def record_enterprise_processing(self, enterprise: str, enterprise_type: str, 
                                   duration: float, confidence: float):
        """Record enterprise processing metrics."""
        if not self.enabled:
            return
        
        self.enterprise_processing_time.labels(
            enterprise=enterprise,
            enterprise_type=enterprise_type
        ).observe(duration)
        
        self.enterprise_confidence.labels(
            enterprise=enterprise
        ).observe(confidence)
    
    def record_ai_request(self, provider: str, model: str, status: str, 
                         tokens: int, cost: float):
        """Record AI API metrics."""
        if not self.enabled:
            return
        
        self.ai_requests.labels(
            provider=provider,
            model=model,
            status=status
        ).inc()
        
        self.ai_tokens_used.labels(
            provider=provider,
            model=model
        ).inc(tokens)
        
        self.ai_cost.labels(
            provider=provider,
            model=model
        ).inc(cost)
    
    def record_database_operation(self, operation: str, table: str, status: str):
        """Record database operation metrics."""
        if not self.enabled:
            return
        
        self.database_operations.labels(
            operation=operation,
            table=table,
            status=status
        ).inc()
    
    def set_database_connections(self, active_connections: int):
        """Set active database connections."""
        if not self.enabled:
            return
        
        self.database_connection_pool.set(active_connections)
    
    def record_cache_operation(self, operation: str, status: str):
        """Record cache operation metrics."""
        if not self.enabled:
            return
        
        self.cache_operations.labels(
            operation=operation,
            status=status
        ).inc()
    
    def set_cache_hit_rate(self, hit_rate: float):
        """Set cache hit rate."""
        if not self.enabled:
            return
        
        self.cache_hit_rate.set(hit_rate)
    
    def set_active_sessions(self, count: int):
        """Set number of active sessions."""
        if not self.enabled:
            return
        
        self.active_sessions.set(count)
    
    def get_metrics(self) -> str:
        """Get Prometheus metrics in text format."""
        if not self.enabled:
            return "# Prometheus metrics not available\n"
        
        return generate_latest()


# Global metrics collector
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


# Decorators for automatic metrics collection
def track_request_metrics(func):
    """Decorator to track request metrics."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        metrics = get_metrics_collector()
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            status_code = 200
            return result
        except Exception as e:
            status_code = 500
            raise
        finally:
            duration = time.time() - start_time
            # Extract method and endpoint from function name or args
            method = "POST" if "solve" in func.__name__ else "GET"
            endpoint = func.__name__
            
            metrics.record_request(method, endpoint, status_code, duration)
    
    return wrapper


def track_enterprise_metrics(enterprise_name: str, enterprise_type: str):
    """Decorator to track enterprise processing metrics."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            metrics = get_metrics_collector()
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                confidence = 0.8  # Default confidence
                
                # Try to extract confidence from result
                if hasattr(result, 'confidence'):
                    confidence = result.confidence
                elif isinstance(result, dict) and 'confidence' in result:
                    confidence = result['confidence']
                
                return result
            finally:
                duration = time.time() - start_time
                metrics.record_enterprise_processing(
                    enterprise_name, enterprise_type, duration, confidence
                )
        
        return wrapper
    return decorator


def track_ai_metrics(provider: str, model: str):
    """Decorator to track AI API metrics."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            metrics = get_metrics_collector()
            
            try:
                result = await func(*args, **kwargs)
                status = "success"
                
                # Extract tokens and cost from result
                tokens = 0
                cost = 0.0
                
                if hasattr(result, 'tokens_used'):
                    tokens = result.tokens_used
                if hasattr(result, 'cost'):
                    cost = result.cost
                
                metrics.record_ai_request(provider, model, status, tokens, cost)
                return result
            except Exception as e:
                metrics.record_ai_request(provider, model, "error", 0, 0.0)
                raise
        
        return wrapper
    return decorator


# Health check metrics
class HealthMetrics:
    """Health check metrics."""
    
    def __init__(self):
        self.metrics = get_metrics_collector()
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status."""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "metrics_enabled": self.metrics.enabled,
            "version": "2.0.0"
        }
