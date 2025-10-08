"""
Cosmic Council Refinement Engine - Real Monitoring & Telemetry
Implements comprehensive monitoring, metrics collection, and observability.
"""

import time
import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import os
from contextlib import asynccontextmanager
from functools import wraps
import traceback

import structlog
from prometheus_client import (
    Counter, Histogram, Gauge, Summary, Info, 
    CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST,
    start_http_server, push_to_gateway
)
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
import redis.asyncio as redis
from fastapi import Request, Response
import psutil


class MetricType(Enum):
    """Types of metrics."""
    COUNTER = "counter"
    HISTOGRAM = "histogram"
    GAUGE = "gauge"
    SUMMARY = "summary"
    INFO = "info"


@dataclass
class MetricDefinition:
    """Definition of a metric."""
    name: str
    description: str
    metric_type: MetricType
    labels: List[str] = field(default_factory=list)
    buckets: Optional[List[float]] = None
    quantiles: Optional[List[float]] = None


@dataclass
class PerformanceMetrics:
    """Performance metrics for a request."""
    request_id: str
    endpoint: str
    method: str
    status_code: int
    duration_ms: float
    memory_usage_mb: float
    cpu_usage_percent: float
    timestamp: datetime
    user_id: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class SystemMetrics:
    """System-level metrics."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_io_bytes: int
    active_connections: int
    process_count: int
    load_average: List[float]


class MetricsCollector:
    """
    Comprehensive metrics collector using Prometheus.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize metrics collector.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or self._get_default_config()
        self.logger = structlog.get_logger(__name__)
        
        # Create custom registry
        self.registry = CollectorRegistry()
        
        # Initialize metrics
        self.metrics = {}
        self._initialize_metrics()
        
        # Performance tracking
        self.performance_history: List[PerformanceMetrics] = []
        self.system_metrics_history: List[SystemMetrics] = []
        
        # Redis for distributed metrics
        self.redis_client = None
        
        # Start metrics server
        if self.config["enable_metrics_server"]:
            self._start_metrics_server()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "enable_metrics_server": True,
            "metrics_port": 9090,
            "enable_prometheus_push": False,
            "prometheus_gateway_url": "http://localhost:9091",
            "enable_redis_metrics": False,
            "redis_url": "redis://localhost:6379",
            "metrics_retention_days": 30,
            "enable_system_metrics": True,
            "system_metrics_interval": 60,  # seconds
            "enable_performance_tracking": True,
            "performance_history_size": 10000
        }
    
    def _initialize_metrics(self):
        """Initialize all Prometheus metrics."""
        # HTTP metrics
        self.metrics["http_requests_total"] = Counter(
            "cosmic_council_http_requests_total",
            "Total HTTP requests",
            ["method", "endpoint", "status_code"],
            registry=self.registry
        )
        
        self.metrics["http_request_duration"] = Histogram(
            "cosmic_council_http_request_duration_seconds",
            "HTTP request duration in seconds",
            ["method", "endpoint"],
            buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0],
            registry=self.registry
        )
        
        # Problem processing metrics
        self.metrics["problems_created_total"] = Counter(
            "cosmic_council_problems_created_total",
            "Total problems created",
            ["user_id", "initial_layer"],
            registry=self.registry
        )
        
        self.metrics["problems_resolved_total"] = Counter(
            "cosmic_council_problems_resolved_total",
            "Total problems resolved",
            ["final_layer", "resolution_type"],
            registry=self.registry
        )
        
        self.metrics["layer_runs_total"] = Counter(
            "cosmic_council_layer_runs_total",
            "Total layer runs executed",
            ["layer", "status"],
            registry=self.registry
        )
        
        self.metrics["layer_run_duration"] = Histogram(
            "cosmic_council_layer_run_duration_seconds",
            "Layer run duration in seconds",
            ["layer"],
            buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 300.0, 600.0],
            registry=self.registry
        )
        
        # AI service metrics
        self.metrics["ai_requests_total"] = Counter(
            "cosmic_council_ai_requests_total",
            "Total AI service requests",
            ["provider", "model", "status"],
            registry=self.registry
        )
        
        self.metrics["ai_request_duration"] = Histogram(
            "cosmic_council_ai_request_duration_seconds",
            "AI request duration in seconds",
            ["provider", "model"],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
            registry=self.registry
        )
        
        self.metrics["ai_request_cost"] = Histogram(
            "cosmic_council_ai_request_cost_usd",
            "AI request cost in USD",
            ["provider", "model"],
            buckets=[0.001, 0.01, 0.1, 0.5, 1.0, 5.0, 10.0, 50.0],
            registry=self.registry
        )
        
        # Database metrics
        self.metrics["database_queries_total"] = Counter(
            "cosmic_council_database_queries_total",
            "Total database queries",
            ["operation", "table", "status"],
            registry=self.registry
        )
        
        self.metrics["database_query_duration"] = Histogram(
            "cosmic_council_database_query_duration_seconds",
            "Database query duration in seconds",
            ["operation", "table"],
            buckets=[0.001, 0.01, 0.1, 0.5, 1.0, 2.0, 5.0],
            registry=self.registry
        )
        
        # Security metrics
        self.metrics["security_events_total"] = Counter(
            "cosmic_council_security_events_total",
            "Total security events",
            ["event_type", "severity"],
            registry=self.registry
        )
        
        self.metrics["failed_logins_total"] = Counter(
            "cosmic_council_failed_logins_total",
            "Total failed login attempts",
            ["username", "ip_address"],
            registry=self.registry
        )
        
        self.metrics["rate_limit_violations_total"] = Counter(
            "cosmic_council_rate_limit_violations_total",
            "Total rate limit violations",
            ["endpoint", "ip_address"],
            registry=self.registry
        )
        
        # System metrics
        self.metrics["system_cpu_percent"] = Gauge(
            "cosmic_council_system_cpu_percent",
            "System CPU usage percentage",
            registry=self.registry
        )
        
        self.metrics["system_memory_percent"] = Gauge(
            "cosmic_council_system_memory_percent",
            "System memory usage percentage",
            registry=self.registry
        )
        
        self.metrics["system_disk_percent"] = Gauge(
            "cosmic_council_system_disk_percent",
            "System disk usage percentage",
            ["device"],
            registry=self.registry
        )
        
        self.metrics["active_connections"] = Gauge(
            "cosmic_council_active_connections",
            "Number of active connections",
            registry=self.registry
        )
        
        # Business metrics
        self.metrics["active_problems"] = Gauge(
            "cosmic_council_active_problems",
            "Number of active problems",
            registry=self.registry
        )
        
        self.metrics["problems_per_hour"] = Gauge(
            "cosmic_council_problems_per_hour",
            "Problems created per hour",
            registry=self.registry
        )
        
        self.metrics["average_resolution_time"] = Gauge(
            "cosmic_council_average_resolution_time_seconds",
            "Average problem resolution time in seconds",
            registry=self.registry
        )
        
        # Error metrics
        self.metrics["errors_total"] = Counter(
            "cosmic_council_errors_total",
            "Total errors",
            ["error_type", "component", "severity"],
            registry=self.registry
        )
        
        self.metrics["error_rate"] = Gauge(
            "cosmic_council_error_rate",
            "Error rate (errors per minute)",
            registry=self.registry
        )
    
    def _start_metrics_server(self):
        """Start Prometheus metrics server."""
        try:
            start_http_server(
                self.config["metrics_port"],
                registry=self.registry
            )
            self.logger.info(f"Metrics server started on port {self.config['metrics_port']}")
        except Exception as e:
            self.logger.error(f"Failed to start metrics server: {e}")
    
    async def initialize_redis(self, redis_url: str):
        """Initialize Redis connection for distributed metrics."""
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            await self.redis_client.ping()
            self.logger.info("Redis connection established for metrics")
        except Exception as e:
            self.logger.warning(f"Redis connection failed: {e}")
            self.redis_client = None
    
    def record_http_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration: float,
        user_id: Optional[str] = None
    ):
        """Record HTTP request metrics."""
        # Record request count
        self.metrics["http_requests_total"].labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code)
        ).inc()
        
        # Record request duration
        self.metrics["http_request_duration"].labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        # Record performance metrics
        if self.config["enable_performance_tracking"]:
            performance_metrics = PerformanceMetrics(
                request_id="",  # Will be set by middleware
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                duration_ms=duration * 1000,
                memory_usage_mb=psutil.Process().memory_info().rss / 1024 / 1024,
                cpu_usage_percent=psutil.Process().cpu_percent(),
                timestamp=datetime.utcnow(),
                user_id=user_id
            )
            
            self.performance_history.append(performance_metrics)
            
            # Keep history size manageable
            if len(self.performance_history) > self.config["performance_history_size"]:
                self.performance_history = self.performance_history[-self.config["performance_history_size"]:]
    
    def record_problem_created(self, user_id: str, initial_layer: str):
        """Record problem creation."""
        self.metrics["problems_created_total"].labels(
            user_id=user_id,
            initial_layer=initial_layer
        ).inc()
    
    def record_problem_resolved(self, final_layer: str, resolution_type: str):
        """Record problem resolution."""
        self.metrics["problems_resolved_total"].labels(
            final_layer=final_layer,
            resolution_type=resolution_type
        ).inc()
    
    def record_layer_run(
        self,
        layer: str,
        status: str,
        duration: float,
        cost_usd: float = 0.0
    ):
        """Record layer run metrics."""
        # Record layer run count
        self.metrics["layer_runs_total"].labels(
            layer=layer,
            status=status
        ).inc()
        
        # Record layer run duration
        self.metrics["layer_run_duration"].labels(
            layer=layer
        ).observe(duration)
        
        # Record cost if available
        if cost_usd > 0:
            self.metrics["ai_request_cost"].labels(
                provider="unknown",
                model="unknown"
            ).observe(cost_usd)
    
    def record_ai_request(
        self,
        provider: str,
        model: str,
        status: str,
        duration: float,
        cost_usd: float = 0.0
    ):
        """Record AI service request metrics."""
        # Record request count
        self.metrics["ai_requests_total"].labels(
            provider=provider,
            model=model,
            status=status
        ).inc()
        
        # Record request duration
        self.metrics["ai_request_duration"].labels(
            provider=provider,
            model=model
        ).observe(duration)
        
        # Record cost
        if cost_usd > 0:
            self.metrics["ai_request_cost"].labels(
                provider=provider,
                model=model
            ).observe(cost_usd)
    
    def record_database_query(
        self,
        operation: str,
        table: str,
        status: str,
        duration: float
    ):
        """Record database query metrics."""
        # Record query count
        self.metrics["database_queries_total"].labels(
            operation=operation,
            table=table,
            status=status
        ).inc()
        
        # Record query duration
        self.metrics["database_query_duration"].labels(
            operation=operation,
            table=table
        ).observe(duration)
    
    def record_security_event(self, event_type: str, severity: str):
        """Record security event."""
        self.metrics["security_events_total"].labels(
            event_type=event_type,
            severity=severity
        ).inc()
    
    def record_failed_login(self, username: str, ip_address: str):
        """Record failed login attempt."""
        self.metrics["failed_logins_total"].labels(
            username=username,
            ip_address=ip_address
        ).inc()
    
    def record_rate_limit_violation(self, endpoint: str, ip_address: str):
        """Record rate limit violation."""
        self.metrics["rate_limit_violations_total"].labels(
            endpoint=endpoint,
            ip_address=ip_address
        ).inc()
    
    def record_error(self, error_type: str, component: str, severity: str):
        """Record error occurrence."""
        self.metrics["errors_total"].labels(
            error_type=error_type,
            component=component,
            severity=severity
        ).inc()
    
    def update_system_metrics(self):
        """Update system-level metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics["system_cpu_percent"].set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.metrics["system_memory_percent"].set(memory.percent)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.metrics["system_disk_percent"].labels(device="root").set(
                (disk.used / disk.total) * 100
            )
            
            # Network connections
            connections = len(psutil.net_connections())
            self.metrics["active_connections"].set(connections)
            
            # Store system metrics
            system_metrics = SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_usage_percent=(disk.used / disk.total) * 100,
                network_io_bytes=0,  # Would need to track over time
                active_connections=connections,
                process_count=len(psutil.pids()),
                load_average=psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
            )
            
            self.system_metrics_history.append(system_metrics)
            
            # Keep history size manageable
            if len(self.system_metrics_history) > 1000:
                self.system_metrics_history = self.system_metrics_history[-1000:]
                
        except Exception as e:
            self.logger.error(f"Failed to update system metrics: {e}")
    
    def update_business_metrics(self, active_problems: int, problems_per_hour: float, avg_resolution_time: float):
        """Update business metrics."""
        self.metrics["active_problems"].set(active_problems)
        self.metrics["problems_per_hour"].set(problems_per_hour)
        self.metrics["average_resolution_time"].set(avg_resolution_time)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "performance_metrics": {
                "total_requests": len(self.performance_history),
                "average_response_time": self._calculate_average_response_time(),
                "error_rate": self._calculate_error_rate(),
                "p95_response_time": self._calculate_percentile_response_time(95),
                "p99_response_time": self._calculate_percentile_response_time(99)
            },
            "system_metrics": {
                "cpu_percent": self.metrics["system_cpu_percent"]._value._value,
                "memory_percent": self.metrics["system_memory_percent"]._value._value,
                "disk_percent": self.metrics["system_disk_percent"]._value._value,
                "active_connections": self.metrics["active_connections"]._value._value
            },
            "business_metrics": {
                "active_problems": self.metrics["active_problems"]._value._value,
                "problems_per_hour": self.metrics["problems_per_hour"]._value._value,
                "average_resolution_time": self.metrics["average_resolution_time"]._value._value
            }
        }
        
        return summary
    
    def _calculate_average_response_time(self) -> float:
        """Calculate average response time."""
        if not self.performance_history:
            return 0.0
        
        total_duration = sum(metrics.duration_ms for metrics in self.performance_history)
        return total_duration / len(self.performance_history)
    
    def _calculate_error_rate(self) -> float:
        """Calculate error rate."""
        if not self.performance_history:
            return 0.0
        
        error_count = sum(1 for metrics in self.performance_history if metrics.status_code >= 400)
        return (error_count / len(self.performance_history)) * 100
    
    def _calculate_percentile_response_time(self, percentile: int) -> float:
        """Calculate percentile response time."""
        if not self.performance_history:
            return 0.0
        
        durations = sorted([metrics.duration_ms for metrics in self.performance_history])
        index = int((percentile / 100) * len(durations))
        return durations[min(index, len(durations) - 1)]
    
    async def push_metrics_to_gateway(self):
        """Push metrics to Prometheus gateway."""
        if not self.config["enable_prometheus_push"]:
            return
        
        try:
            push_to_gateway(
                self.config["prometheus_gateway_url"],
                job="cosmic-council-refinement-engine",
                registry=self.registry
            )
            self.logger.info("Metrics pushed to Prometheus gateway")
        except Exception as e:
            self.logger.error(f"Failed to push metrics to gateway: {e}")
    
    def generate_metrics_export(self) -> str:
        """Generate Prometheus metrics export."""
        return generate_latest(self.registry).decode('utf-8')


class SentryIntegration:
    """
    Sentry integration for error tracking and performance monitoring.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Sentry integration.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or self._get_default_config()
        self.logger = structlog.get_logger(__name__)
        
        if self.config["enable_sentry"]:
            self._initialize_sentry()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default Sentry configuration."""
        return {
            "enable_sentry": True,
            "sentry_dsn": os.getenv("SENTRY_DSN"),
            "environment": os.getenv("ENVIRONMENT", "development"),
            "release": os.getenv("RELEASE", "1.0.0"),
            "sample_rate": 1.0,
            "traces_sample_rate": 0.1,
            "profiles_sample_rate": 0.1,
            "enable_performance_monitoring": True,
            "enable_error_tracking": True
        }
    
    def _initialize_sentry(self):
        """Initialize Sentry SDK."""
        if not self.config["sentry_dsn"]:
            self.logger.warning("Sentry DSN not provided, skipping Sentry initialization")
            return
        
        try:
            sentry_sdk.init(
                dsn=self.config["sentry_dsn"],
                environment=self.config["environment"],
                release=self.config["release"],
                sample_rate=self.config["sample_rate"],
                traces_sample_rate=self.config["traces_sample_rate"],
                profiles_sample_rate=self.config["profiles_sample_rate"],
                integrations=[
                    FastApiIntegration(auto_enabling_instrumentations=True),
                    SqlalchemyIntegration(),
                    RedisIntegration()
                ],
                before_send=self._before_send,
                before_send_transaction=self._before_send_transaction
            )
            
            self.logger.info("Sentry initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Sentry: {e}")
    
    def _before_send(self, event, hint):
        """Filter events before sending to Sentry."""
        # Filter out certain error types
        if event.get("exception"):
            exc_type = event["exception"]["values"][0]["type"]
            if exc_type in ["KeyboardInterrupt", "SystemExit"]:
                return None
        
        # Add custom tags
        event.setdefault("tags", {})
        event["tags"]["component"] = "cosmic-council-refinement-engine"
        
        return event
    
    def _before_send_transaction(self, event, hint):
        """Filter transactions before sending to Sentry."""
        # Add custom tags
        event.setdefault("tags", {})
        event["tags"]["component"] = "cosmic-council-refinement-engine"
        
        return event
    
    def capture_exception(self, exception: Exception, **kwargs):
        """Capture an exception."""
        if self.config["enable_error_tracking"]:
            sentry_sdk.capture_exception(exception, **kwargs)
    
    def capture_message(self, message: str, level: str = "info", **kwargs):
        """Capture a message."""
        if self.config["enable_error_tracking"]:
            sentry_sdk.capture_message(message, level=level, **kwargs)
    
    def add_breadcrumb(self, message: str, category: str = "default", level: str = "info", **kwargs):
        """Add a breadcrumb."""
        if self.config["enable_error_tracking"]:
            sentry_sdk.add_breadcrumb(
                message=message,
                category=category,
                level=level,
                **kwargs
            )
    
    def set_user_context(self, user_id: str, username: str = None, email: str = None):
        """Set user context for error tracking."""
        if self.config["enable_error_tracking"]:
            sentry_sdk.set_user({
                "id": user_id,
                "username": username,
                "email": email
            })
    
    def set_tag(self, key: str, value: str):
        """Set a tag for error tracking."""
        if self.config["enable_error_tracking"]:
            sentry_sdk.set_tag(key, value)
    
    def set_context(self, key: str, value: Dict[str, Any]):
        """Set context for error tracking."""
        if self.config["enable_error_tracking"]:
            sentry_sdk.set_context(key, value)


class MonitoringMiddleware:
    """
    FastAPI middleware for request monitoring.
    """
    
    def __init__(self, metrics_collector: MetricsCollector, sentry: SentryIntegration):
        """
        Initialize monitoring middleware.
        
        Args:
            metrics_collector: Metrics collector instance
            sentry: Sentry integration instance
        """
        self.metrics_collector = metrics_collector
        self.sentry = sentry
        self.logger = structlog.get_logger(__name__)
    
    async def __call__(self, request: Request, call_next):
        """Process request with monitoring."""
        start_time = time.time()
        request_id = request.state.request_id if hasattr(request.state, 'request_id') else "unknown"
        
        # Set Sentry context
        self.sentry.set_tag("request_id", request_id)
        self.sentry.set_tag("endpoint", request.url.path)
        self.sentry.set_tag("method", request.method)
        
        # Add breadcrumb
        self.sentry.add_breadcrumb(
            message=f"{request.method} {request.url.path}",
            category="http",
            level="info",
            data={
                "method": request.method,
                "url": str(request.url),
                "user_agent": request.headers.get("user-agent", ""),
                "ip": request.client.host
            }
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Record metrics
            self.metrics_collector.record_http_request(
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code,
                duration=duration,
                user_id=getattr(request.state, 'user_id', None)
            )
            
            # Add performance headers
            response.headers["X-Response-Time"] = f"{duration:.3f}s"
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration = time.time() - start_time
            
            # Record error metrics
            self.metrics_collector.record_http_request(
                method=request.method,
                endpoint=request.url.path,
                status_code=500,
                duration=duration,
                user_id=getattr(request.state, 'user_id', None)
            )
            
            # Record error
            self.metrics_collector.record_error(
                error_type=type(e).__name__,
                component="api",
                severity="high"
            )
            
            # Capture exception in Sentry
            self.sentry.capture_exception(e)
            
            # Re-raise exception
            raise


# Global instances
_metrics_collector: Optional[MetricsCollector] = None
_sentry_integration: Optional[SentryIntegration] = None


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def get_sentry_integration() -> SentryIntegration:
    """Get the global Sentry integration instance."""
    global _sentry_integration
    if _sentry_integration is None:
        _sentry_integration = SentryIntegration()
    return _sentry_integration


def initialize_monitoring(config: Optional[Dict[str, Any]] = None) -> tuple[MetricsCollector, SentryIntegration]:
    """
    Initialize monitoring system.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Tuple of (metrics_collector, sentry_integration)
    """
    global _metrics_collector, _sentry_integration
    
    _metrics_collector = MetricsCollector(config)
    _sentry_integration = SentryIntegration(config)
    
    return _metrics_collector, _sentry_integration


# Decorators for monitoring
def monitor_function(component: str, operation: str):
    """Decorator to monitor function execution."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            metrics_collector = get_metrics_collector()
            sentry = get_sentry_integration()
            
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                # Record success metrics
                duration = time.time() - start_time
                metrics_collector.record_database_query(
                    operation=operation,
                    table=component,
                    status="success",
                    duration=duration
                )
                
                return result
                
            except Exception as e:
                # Record error metrics
                duration = time.time() - start_time
                metrics_collector.record_database_query(
                    operation=operation,
                    table=component,
                    status="error",
                    duration=duration
                )
                
                # Record error
                metrics_collector.record_error(
                    error_type=type(e).__name__,
                    component=component,
                    severity="medium"
                )
                
                # Capture exception
                sentry.capture_exception(e)
                
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            metrics_collector = get_metrics_collector()
            sentry = get_sentry_integration()
            
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                # Record success metrics
                duration = time.time() - start_time
                metrics_collector.record_database_query(
                    operation=operation,
                    table=component,
                    status="success",
                    duration=duration
                )
                
                return result
                
            except Exception as e:
                # Record error metrics
                duration = time.time() - start_time
                metrics_collector.record_database_query(
                    operation=operation,
                    table=component,
                    status="error",
                    duration=duration
                )
                
                # Record error
                metrics_collector.record_error(
                    error_type=type(e).__name__,
                    component=component,
                    severity="medium"
                )
                
                # Capture exception
                sentry.capture_exception(e)
                
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    async def test_monitoring():
        print("=== Monitoring System Test ===")
        
        # Initialize monitoring
        metrics_collector, sentry = initialize_monitoring()
        
        # Test metrics collection
        metrics_collector.record_http_request("GET", "/health", 200, 0.1)
        metrics_collector.record_problem_created("user123", "deci")
        metrics_collector.record_ai_request("openai", "gpt-4", "success", 2.5, 0.05)
        
        # Test system metrics
        metrics_collector.update_system_metrics()
        
        # Test business metrics
        metrics_collector.update_business_metrics(10, 5.5, 120.0)
        
        # Get metrics summary
        summary = metrics_collector.get_metrics_summary()
        print(f"Metrics summary: {json.dumps(summary, indent=2)}")
        
        # Test Sentry integration
        sentry.capture_message("Test message", level="info")
        sentry.set_user_context("user123", "testuser", "test@example.com")
        
        print("Monitoring system test completed")
    
    # Run the test
    asyncio.run(test_monitoring())
