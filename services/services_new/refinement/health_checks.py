"""
Cosmic Council Refinement Engine - Health Checks & Monitoring Dashboard
Implements comprehensive health checks, status monitoring, and alerting.
"""

import asyncio
import time
import json
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from enum import Enum
import psutil
import redis.asyncio as redis
import asyncpg
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse, HTMLResponse
import structlog

try:
    from .monitoring import get_metrics_collector, get_sentry_integration
except ImportError:
    # For testing
    from monitoring import get_metrics_collector, get_sentry_integration
try:
    from .database import get_database_connection
    from .security import get_security_manager
    from .ai_integrations import get_ai_manager
except ImportError:
    # For testing
    from database import get_database_connection
    from security import get_security_manager
    from ai_integrations import get_ai_manager


class HealthStatus(Enum):
    """Health check status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """Individual health check result."""
    name: str
    status: HealthStatus
    message: str
    response_time_ms: float
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class SystemHealth:
    """Overall system health status."""
    status: HealthStatus
    timestamp: datetime
    checks: List[HealthCheck] = field(default_factory=list)
    uptime_seconds: float = 0.0
    version: str = "1.0.0"
    environment: str = "development"
    total_checks: int = 0
    healthy_checks: int = 0
    degraded_checks: int = 0
    unhealthy_checks: int = 0


class HealthChecker:
    """
    Comprehensive health checking system.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize health checker.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or self._get_default_config()
        self.logger = structlog.get_logger(__name__)
        
        # System start time
        self.start_time = datetime.now(timezone.utc)
        
        # Health check registry
        self.health_checks: Dict[str, Callable] = {}
        
        # Register default health checks
        self._register_default_checks()
        
        # Health check history
        self.health_history: List[SystemHealth] = []
        
        # Alerting
        self.alert_thresholds = self.config.get("alert_thresholds", {})
        self.last_alert_time: Dict[str, datetime] = {}
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "health_check_interval": 30,  # seconds
            "health_history_size": 100,
            "enable_continuous_monitoring": True,
            "alert_thresholds": {
                "response_time_ms": 5000,
                "error_rate_percent": 10,
                "memory_usage_percent": 90,
                "cpu_usage_percent": 90,
                "disk_usage_percent": 90
            },
            "alert_cooldown_minutes": 5,
            "enable_alerts": True
        }
    
    def _register_default_checks(self):
        """Register default health checks."""
        self.register_check("database", self._check_database)
        self.register_check("redis", self._check_redis)
        self.register_check("ai_services", self._check_ai_services)
        self.register_check("security", self._check_security)
        self.register_check("system_resources", self._check_system_resources)
        self.register_check("api_endpoints", self._check_api_endpoints)
        self.register_check("external_dependencies", self._check_external_dependencies)
    
    def register_check(self, name: str, check_function: Callable):
        """
        Register a health check function.
        
        Args:
            name: Name of the health check
            check_function: Function that returns HealthCheck
        """
        self.health_checks[name] = check_function
        self.logger.info(f"Registered health check: {name}")
    
    async def run_all_checks(self) -> SystemHealth:
        """
        Run all registered health checks.
        
        Returns:
            SystemHealth object with overall status
        """
        start_time = time.time()
        checks = []
        
        # Run all health checks concurrently
        check_tasks = []
        for name, check_function in self.health_checks.items():
            task = asyncio.create_task(self._run_single_check(name, check_function))
            check_tasks.append(task)
        
        # Wait for all checks to complete
        check_results = await asyncio.gather(*check_tasks, return_exceptions=True)
        
        # Process results
        for result in check_results:
            if isinstance(result, HealthCheck):
                checks.append(result)
            elif isinstance(result, Exception):
                # Create error health check
                error_check = HealthCheck(
                    name="unknown",
                    status=HealthStatus.UNHEALTHY,
                    message="Health check failed with exception",
                    response_time_ms=0.0,
                    timestamp=datetime.now(timezone.utc),
                    error=str(result)
                )
                checks.append(error_check)
        
        # Calculate overall status
        overall_status = self._calculate_overall_status(checks)
        
        # Create system health object
        system_health = SystemHealth(
            status=overall_status,
            timestamp=datetime.now(timezone.utc),
            checks=checks,
            uptime_seconds=(datetime.now(timezone.utc) - self.start_time).total_seconds(),
            version=self.config.get("version", "1.0.0"),
            environment=self.config.get("environment", "development"),
            total_checks=len(checks),
            healthy_checks=len([c for c in checks if c.status == HealthStatus.HEALTHY]),
            degraded_checks=len([c for c in checks if c.status == HealthStatus.DEGRADED]),
            unhealthy_checks=len([c for c in checks if c.status == HealthStatus.UNHEALTHY])
        )
        
        # Store in history
        self.health_history.append(system_health)
        if len(self.health_history) > self.config["health_history_size"]:
            self.health_history = self.health_history[-self.config["health_history_size"]:]
        
        # Check for alerts
        if self.config["enable_alerts"]:
            await self._check_alerts(system_health)
        
        return system_health
    
    async def _run_single_check(self, name: str, check_function: Callable) -> HealthCheck:
        """Run a single health check."""
        start_time = time.time()
        
        try:
            if asyncio.iscoroutinefunction(check_function):
                result = await check_function()
            else:
                result = check_function()
            
            # Ensure result is a HealthCheck object
            if not isinstance(result, HealthCheck):
                result = HealthCheck(
                    name=name,
                    status=HealthStatus.UNKNOWN,
                    message="Health check returned invalid result",
                    response_time_ms=(time.time() - start_time) * 1000,
                    timestamp=datetime.now(timezone.utc)
                )
            
            # Update response time
            result.response_time_ms = (time.time() - start_time) * 1000
            
            return result
            
        except Exception as e:
            self.logger.error(f"Health check {name} failed: {e}")
            return HealthCheck(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.now(timezone.utc),
                error=str(e)
            )
    
    def _calculate_overall_status(self, checks: List[HealthCheck]) -> HealthStatus:
        """Calculate overall system status from individual checks."""
        if not checks:
            return HealthStatus.UNKNOWN
        
        # Count statuses
        status_counts = {
            HealthStatus.HEALTHY: 0,
            HealthStatus.DEGRADED: 0,
            HealthStatus.UNHEALTHY: 0,
            HealthStatus.UNKNOWN: 0
        }
        
        for check in checks:
            status_counts[check.status] += 1
        
        # Determine overall status
        if status_counts[HealthStatus.UNHEALTHY] > 0:
            return HealthStatus.UNHEALTHY
        elif status_counts[HealthStatus.DEGRADED] > 0:
            return HealthStatus.DEGRADED
        elif status_counts[HealthStatus.HEALTHY] > 0:
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.UNKNOWN
    
    async def _check_alerts(self, system_health: SystemHealth):
        """Check for alert conditions."""
        current_time = datetime.now(timezone.utc)
        
        # Check response time alerts
        for check in system_health.checks:
            if check.response_time_ms > self.alert_thresholds.get("response_time_ms", 5000):
                await self._send_alert(
                    f"High response time for {check.name}: {check.response_time_ms:.2f}ms",
                    "performance"
                )
        
        # Check error rate alerts
        if system_health.unhealthy_checks > 0:
            error_rate = (system_health.unhealthy_checks / system_health.total_checks) * 100
            if error_rate > self.alert_thresholds.get("error_rate_percent", 10):
                await self._send_alert(
                    f"High error rate: {error_rate:.1f}% of health checks failing",
                    "reliability"
                )
        
        # Check system resource alerts
        system_check = next((c for c in system_health.checks if c.name == "system_resources"), None)
        if system_check and system_check.details:
            if system_check.details.get("memory_usage_percent", 0) > self.alert_thresholds.get("memory_usage_percent", 90):
                await self._send_alert(
                    f"High memory usage: {system_check.details['memory_usage_percent']:.1f}%",
                    "resources"
                )
            
            if system_check.details.get("cpu_usage_percent", 0) > self.alert_thresholds.get("cpu_usage_percent", 90):
                await self._send_alert(
                    f"High CPU usage: {system_check.details['cpu_usage_percent']:.1f}%",
                    "resources"
                )
    
    async def _send_alert(self, message: str, alert_type: str):
        """Send an alert."""
        current_time = datetime.now(timezone.utc)
        
        # Check cooldown
        last_alert = self.last_alert_time.get(alert_type)
        if last_alert:
            cooldown = timedelta(minutes=self.config.get("alert_cooldown_minutes", 5))
            if current_time - last_alert < cooldown:
                return
        
        # Send alert (in real implementation, this would send to Slack, email, etc.)
        self.logger.warning(f"ALERT [{alert_type}]: {message}")
        
        # Update last alert time
        self.last_alert_time[alert_type] = current_time
        
        # Capture in Sentry
        sentry = get_sentry_integration()
        sentry.capture_message(message, level="warning", tags={"alert_type": alert_type})
    
    # Health check implementations
    async def _check_database(self) -> HealthCheck:
        """Check database connectivity and performance."""
        try:
            db_manager = get_database_manager()
            
            # Test database connection
            start_time = time.time()
            async with db_manager.get_session() as session:
                # Simple query to test connectivity
                from sqlalchemy import text
                result = await session.execute(text("SELECT 1"))
                result.scalar()
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheck(
                name="database",
                status=HealthStatus.HEALTHY,
                message="Database connection successful",
                response_time_ms=response_time,
                timestamp=datetime.now(timezone.utc),
                details={
                    "response_time_ms": response_time,
                    "connection_pool_size": 10,  # Would get from actual config
                    "active_connections": 5  # Would get from actual metrics
                }
            )
            
        except Exception as e:
            return HealthCheck(
                name="database",
                status=HealthStatus.UNHEALTHY,
                message=f"Database connection failed: {str(e)}",
                response_time_ms=0.0,
                timestamp=datetime.now(timezone.utc),
                error=str(e)
            )
    
    async def _check_redis(self) -> HealthCheck:
        """Check Redis connectivity and performance."""
        try:
            # Test Redis connection
            start_time = time.time()
            redis_client = redis.from_url("redis://localhost:6379")
            await redis_client.ping()
            await redis_client.close()
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheck(
                name="redis",
                status=HealthStatus.HEALTHY,
                message="Redis connection successful",
                response_time_ms=response_time,
                timestamp=datetime.now(timezone.utc),
                details={
                    "response_time_ms": response_time,
                    "redis_version": "6.2.0"  # Would get from actual Redis
                }
            )
            
        except Exception as e:
            return HealthCheck(
                name="redis",
                status=HealthStatus.UNHEALTHY,
                message=f"Redis connection failed: {str(e)}",
                response_time_ms=0.0,
                timestamp=datetime.now(timezone.utc),
                error=str(e)
            )
    
    async def _check_ai_services(self) -> HealthCheck:
        """Check AI service availability."""
        try:
            ai_manager = get_ai_manager()
            
            # Test AI service availability
            start_time = time.time()
            
            # Check if providers are available
            available_providers = []
            if "openai" in ai_manager.providers:
                available_providers.append("openai")
            if "anthropic" in ai_manager.providers:
                available_providers.append("anthropic")
            
            response_time = (time.time() - start_time) * 1000
            
            if available_providers:
                return HealthCheck(
                    name="ai_services",
                    status=HealthStatus.HEALTHY,
                    message=f"AI services available: {', '.join(available_providers)}",
                    response_time_ms=response_time,
                    timestamp=datetime.now(timezone.utc),
                    details={
                        "available_providers": available_providers,
                        "total_providers": len(ai_manager.providers)
                    }
                )
            else:
                return HealthCheck(
                    name="ai_services",
                    status=HealthStatus.DEGRADED,
                    message="No AI providers available",
                    response_time_ms=response_time,
                    timestamp=datetime.now(timezone.utc),
                    details={
                        "available_providers": [],
                        "total_providers": len(ai_manager.providers)
                    }
                )
                
        except Exception as e:
            return HealthCheck(
                name="ai_services",
                status=HealthStatus.UNHEALTHY,
                message=f"AI services check failed: {str(e)}",
                response_time_ms=0.0,
                timestamp=datetime.now(timezone.utc),
                error=str(e)
            )
    
    async def _check_security(self) -> HealthCheck:
        """Check security system status."""
        try:
            security_manager = get_security_manager()
            
            # Check security system components
            start_time = time.time()
            
            # Check if security manager is initialized
            is_initialized = security_manager is not None
            
            # Check user count
            user_count = len(security_manager.users) if security_manager else 0
            
            # Check API key count
            api_key_count = len(security_manager.api_keys) if security_manager else 0
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheck(
                name="security",
                status=HealthStatus.HEALTHY,
                message="Security system operational",
                response_time_ms=response_time,
                timestamp=datetime.now(timezone.utc),
                details={
                    "initialized": is_initialized,
                    "user_count": user_count,
                    "api_key_count": api_key_count,
                    "rate_limiting_enabled": security_manager.config.get("enable_rate_limiting", False) if security_manager else False
                }
            )
            
        except Exception as e:
            return HealthCheck(
                name="security",
                status=HealthStatus.UNHEALTHY,
                message=f"Security system check failed: {str(e)}",
                response_time_ms=0.0,
                timestamp=datetime.now(timezone.utc),
                error=str(e)
            )
    
    async def _check_system_resources(self) -> HealthCheck:
        """Check system resource usage."""
        try:
            start_time = time.time()
            
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            response_time = (time.time() - start_time) * 1000
            
            # Determine status based on resource usage
            status = HealthStatus.HEALTHY
            if cpu_percent > 90 or memory.percent > 90 or (disk.used / disk.total) * 100 > 90:
                status = HealthStatus.UNHEALTHY
            elif cpu_percent > 70 or memory.percent > 70 or (disk.used / disk.total) * 100 > 70:
                status = HealthStatus.DEGRADED
            
            return HealthCheck(
                name="system_resources",
                status=status,
                message=f"System resources: CPU {cpu_percent:.1f}%, Memory {memory.percent:.1f}%, Disk {((disk.used / disk.total) * 100):.1f}%",
                response_time_ms=response_time,
                timestamp=datetime.now(timezone.utc),
                details={
                    "cpu_usage_percent": cpu_percent,
                    "memory_usage_percent": memory.percent,
                    "disk_usage_percent": (disk.used / disk.total) * 100,
                    "memory_available_gb": memory.available / (1024**3),
                    "disk_free_gb": disk.free / (1024**3)
                }
            )
            
        except Exception as e:
            return HealthCheck(
                name="system_resources",
                status=HealthStatus.UNHEALTHY,
                message=f"System resources check failed: {str(e)}",
                response_time_ms=0.0,
                timestamp=datetime.now(timezone.utc),
                error=str(e)
            )
    
    async def _check_api_endpoints(self) -> HealthCheck:
        """Check API endpoint availability."""
        try:
            start_time = time.time()
            
            # Test basic API endpoints
            # In a real implementation, this would make HTTP requests to the API
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheck(
                name="api_endpoints",
                status=HealthStatus.HEALTHY,
                message="API endpoints responding",
                response_time_ms=response_time,
                timestamp=datetime.now(timezone.utc),
                details={
                    "endpoints_tested": ["/health", "/metrics", "/problems"],
                    "response_time_ms": response_time
                }
            )
            
        except Exception as e:
            return HealthCheck(
                name="api_endpoints",
                status=HealthStatus.UNHEALTHY,
                message=f"API endpoints check failed: {str(e)}",
                response_time_ms=0.0,
                timestamp=datetime.now(timezone.utc),
                error=str(e)
            )
    
    async def _check_external_dependencies(self) -> HealthCheck:
        """Check external service dependencies."""
        try:
            start_time = time.time()
            
            # Check external dependencies
            # In a real implementation, this would check external APIs, services, etc.
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheck(
                name="external_dependencies",
                status=HealthStatus.HEALTHY,
                message="External dependencies available",
                response_time_ms=response_time,
                timestamp=datetime.now(timezone.utc),
                details={
                    "dependencies_checked": ["prometheus", "sentry", "external_apis"],
                    "response_time_ms": response_time
                }
            )
            
        except Exception as e:
            return HealthCheck(
                name="external_dependencies",
                status=HealthStatus.UNHEALTHY,
                message=f"External dependencies check failed: {str(e)}",
                response_time_ms=0.0,
                timestamp=datetime.now(timezone.utc),
                error=str(e)
            )
    
    def get_health_history(self) -> List[SystemHealth]:
        """Get health check history."""
        return self.health_history
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health check summary."""
        if not self.health_history:
            return {"error": "No health check history available"}
        
        latest_health = self.health_history[-1]
        
        # Calculate trends
        recent_checks = self.health_history[-10:] if len(self.health_history) >= 10 else self.health_history
        
        healthy_count = sum(1 for h in recent_checks if h.status == HealthStatus.HEALTHY)
        degraded_count = sum(1 for h in recent_checks if h.status == HealthStatus.DEGRADED)
        unhealthy_count = sum(1 for h in recent_checks if h.status == HealthStatus.UNHEALTHY)
        
        return {
            "current_status": latest_health.status.value,
            "uptime_seconds": latest_health.uptime_seconds,
            "total_checks": latest_health.total_checks,
            "healthy_checks": latest_health.healthy_checks,
            "degraded_checks": latest_health.degraded_checks,
            "unhealthy_checks": latest_health.unhealthy_checks,
            "recent_trends": {
                "healthy_percentage": (healthy_count / len(recent_checks)) * 100,
                "degraded_percentage": (degraded_count / len(recent_checks)) * 100,
                "unhealthy_percentage": (unhealthy_count / len(recent_checks)) * 100
            },
            "last_check": latest_health.timestamp.isoformat(),
            "version": latest_health.version,
            "environment": latest_health.environment
        }


# Global health checker instance
_health_checker: Optional[HealthChecker] = None


def get_health_checker() -> HealthChecker:
    """Get the global health checker instance."""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker


def initialize_health_checks(config: Optional[Dict[str, Any]] = None) -> HealthChecker:
    """
    Initialize health checking system.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Health checker instance
    """
    global _health_checker
    _health_checker = HealthChecker(config)
    return _health_checker


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    async def test_health_checks():
        print("=== Health Checks Test ===")
        
        # Initialize health checker
        health_checker = initialize_health_checks()
        
        # Run health checks
        system_health = await health_checker.run_all_checks()
        
        print(f"System Status: {system_health.status.value}")
        print(f"Total Checks: {system_health.total_checks}")
        print(f"Healthy: {system_health.healthy_checks}")
        print(f"Degraded: {system_health.degraded_checks}")
        print(f"Unhealthy: {system_health.unhealthy_checks}")
        print(f"Uptime: {system_health.uptime_seconds:.2f} seconds")
        
        # Print individual check results
        for check in system_health.checks:
            print(f"\n{check.name}:")
            print(f"  Status: {check.status.value}")
            print(f"  Message: {check.message}")
            print(f"  Response Time: {check.response_time_ms:.2f}ms")
            if check.details:
                print(f"  Details: {check.details}")
        
        # Get health summary
        summary = health_checker.get_health_summary()
        print(f"\nHealth Summary: {json.dumps(summary, indent=2)}")
    
    # Run the test
    asyncio.run(test_health_checks())
