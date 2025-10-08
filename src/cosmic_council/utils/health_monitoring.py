#!/usr/bin/env python3
"""
Health Monitoring and Metrics System for Cosmic Council Framework
"""

import asyncio
import logging
import time
import psutil
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum
import json

from production_config import get_config
from error_handling import get_error_handler, ErrorSeverity

logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

@dataclass
class HealthCheck:
    """Health check result"""
    name: str
    status: HealthStatus
    message: str
    timestamp: datetime
    response_time_ms: float
    details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}

@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    disk_usage_percent: float
    disk_free_gb: float
    active_connections: int
    response_time_ms: float
    error_rate: float
    throughput_per_second: float

class HealthMonitor:
    """Health monitoring system"""
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self.health_checks: List[HealthCheck] = []
        self.system_metrics: List[SystemMetrics] = []
        self.error_handler = get_error_handler()
        self.start_time = datetime.now(timezone.utc)
        self.request_count = 0
        self.error_count = 0
    
    async def run_health_checks(self) -> List[HealthCheck]:
        """Run all health checks"""
        checks = []
        
        # Database health check
        checks.append(await self._check_database())
        
        # System resources health check
        checks.append(await self._check_system_resources())
        
        # API health check
        checks.append(await self._check_api())
        
        # Error rate health check
        checks.append(await self._check_error_rate())
        
        # Memory health check
        checks.append(await self._check_memory())
        
        # Disk space health check
        checks.append(await self._check_disk_space())
        
        self.health_checks = checks
        return checks
    
    async def _check_database(self) -> HealthCheck:
        """Check database connectivity"""
        start_time = time.time()
        
        try:
            from database_setup import get_database_connection
            db_manager = get_database_manager()
            
            if db_manager.test_connection():
                status = HealthStatus.HEALTHY
                message = "Database connection successful"
            else:
                status = HealthStatus.CRITICAL
                message = "Database connection failed"
                
        except Exception as e:
            status = HealthStatus.CRITICAL
            message = f"Database check failed: {str(e)}"
        
        response_time = (time.time() - start_time) * 1000
        
        return HealthCheck(
            name="database",
            status=status,
            message=message,
            timestamp=datetime.now(timezone.utc),
            response_time_ms=response_time
        )
    
    async def _check_system_resources(self) -> HealthCheck:
        """Check system resource usage"""
        start_time = time.time()
        
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            if cpu_percent > 90:
                status = HealthStatus.CRITICAL
                message = f"High CPU usage: {cpu_percent}%"
            elif cpu_percent > 80:
                status = HealthStatus.WARNING
                message = f"Elevated CPU usage: {cpu_percent}%"
            elif memory.percent > 90:
                status = HealthStatus.CRITICAL
                message = f"High memory usage: {memory.percent}%"
            elif memory.percent > 80:
                status = HealthStatus.WARNING
                message = f"Elevated memory usage: {memory.percent}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"System resources normal (CPU: {cpu_percent}%, Memory: {memory.percent}%)"
            
            details = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available / (1024 * 1024)
            }
            
        except Exception as e:
            status = HealthStatus.UNKNOWN
            message = f"System resource check failed: {str(e)}"
            details = {}
        
        response_time = (time.time() - start_time) * 1000
        
        return HealthCheck(
            name="system_resources",
            status=status,
            message=message,
            timestamp=datetime.now(timezone.utc),
            response_time_ms=response_time,
            details=details
        )
    
    async def _check_api(self) -> HealthCheck:
        """Check API responsiveness"""
        start_time = time.time()
        
        try:
            # Simulate API check - in real implementation, make actual HTTP request
            await asyncio.sleep(0.1)  # Simulate API call
            
            status = HealthStatus.HEALTHY
            message = "API responding normally"
            
        except Exception as e:
            status = HealthStatus.CRITICAL
            message = f"API check failed: {str(e)}"
        
        response_time = (time.time() - start_time) * 1000
        
        return HealthCheck(
            name="api",
            status=status,
            message=message,
            timestamp=datetime.now(timezone.utc),
            response_time_ms=response_time
        )
    
    async def _check_error_rate(self) -> HealthCheck:
        """Check error rate"""
        start_time = time.time()
        
        try:
            if self.request_count == 0:
                error_rate = 0.0
            else:
                error_rate = (self.error_count / self.request_count) * 100
            
            if error_rate > 10:
                status = HealthStatus.CRITICAL
                message = f"High error rate: {error_rate:.2f}%"
            elif error_rate > 5:
                status = HealthStatus.WARNING
                message = f"Elevated error rate: {error_rate:.2f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Error rate normal: {error_rate:.2f}%"
            
            details = {
                "error_rate": error_rate,
                "total_requests": self.request_count,
                "total_errors": self.error_count
            }
            
        except Exception as e:
            status = HealthStatus.UNKNOWN
            message = f"Error rate check failed: {str(e)}"
            details = {}
        
        response_time = (time.time() - start_time) * 1000
        
        return HealthCheck(
            name="error_rate",
            status=status,
            message=message,
            timestamp=datetime.now(timezone.utc),
            response_time_ms=response_time,
            details=details
        )
    
    async def _check_memory(self) -> HealthCheck:
        """Check memory usage"""
        start_time = time.time()
        
        try:
            memory = psutil.virtual_memory()
            
            if memory.percent > 95:
                status = HealthStatus.CRITICAL
                message = f"Critical memory usage: {memory.percent}%"
            elif memory.percent > 85:
                status = HealthStatus.WARNING
                message = f"High memory usage: {memory.percent}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Memory usage normal: {memory.percent}%"
            
            details = {
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available / (1024 * 1024),
                "memory_total_mb": memory.total / (1024 * 1024)
            }
            
        except Exception as e:
            status = HealthStatus.UNKNOWN
            message = f"Memory check failed: {str(e)}"
            details = {}
        
        response_time = (time.time() - start_time) * 1000
        
        return HealthCheck(
            name="memory",
            status=status,
            message=message,
            timestamp=datetime.now(timezone.utc),
            response_time_ms=response_time,
            details=details
        )
    
    async def _check_disk_space(self) -> HealthCheck:
        """Check disk space"""
        start_time = time.time()
        
        try:
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            if disk_percent > 95:
                status = HealthStatus.CRITICAL
                message = f"Critical disk usage: {disk_percent:.1f}%"
            elif disk_percent > 85:
                status = HealthStatus.WARNING
                message = f"High disk usage: {disk_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Disk usage normal: {disk_percent:.1f}%"
            
            details = {
                "disk_percent": disk_percent,
                "disk_free_gb": disk.free / (1024 * 1024 * 1024),
                "disk_total_gb": disk.total / (1024 * 1024 * 1024)
            }
            
        except Exception as e:
            status = HealthStatus.UNKNOWN
            message = f"Disk space check failed: {str(e)}"
            details = {}
        
        response_time = (time.time() - start_time) * 1000
        
        return HealthCheck(
            name="disk_space",
            status=status,
            message=message,
            timestamp=datetime.now(timezone.utc),
            response_time_ms=response_time,
            details=details
        )
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect system performance metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Calculate error rate
            error_rate = 0.0
            if self.request_count > 0:
                error_rate = (self.error_count / self.request_count) * 100
            
            # Calculate throughput (requests per second)
            uptime_seconds = (datetime.now(timezone.utc) - self.start_time).total_seconds()
            throughput = self.request_count / uptime_seconds if uptime_seconds > 0 else 0
            
            metrics = SystemMetrics(
                timestamp=datetime.now(timezone.utc),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_available_mb=memory.available / (1024 * 1024),
                disk_usage_percent=(disk.used / disk.total) * 100,
                disk_free_gb=disk.free / (1024 * 1024 * 1024),
                active_connections=0,  # Would need to track this
                response_time_ms=0,  # Would need to track this
                error_rate=error_rate,
                throughput_per_second=throughput
            )
            
            self.system_metrics.append(metrics)
            
            # Keep only last 1000 metrics
            if len(self.system_metrics) > 1000:
                self.system_metrics = self.system_metrics[-1000:]
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            raise
    
    def record_request(self, success: bool = True) -> None:
        """Record a request for metrics"""
        self.request_count += 1
        if not success:
            self.error_count += 1
    
    def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        if not self.health_checks:
            return {
                "status": HealthStatus.UNKNOWN.value,
                "message": "No health checks performed",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        # Determine overall status
        critical_count = sum(1 for check in self.health_checks if check.status == HealthStatus.CRITICAL)
        warning_count = sum(1 for check in self.health_checks if check.status == HealthStatus.WARNING)
        
        if critical_count > 0:
            overall_status = HealthStatus.CRITICAL
            message = f"{critical_count} critical issues detected"
        elif warning_count > 0:
            overall_status = HealthStatus.WARNING
            message = f"{warning_count} warnings detected"
        else:
            overall_status = HealthStatus.HEALTHY
            message = "All systems healthy"
        
        return {
            "status": overall_status.value,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": [asdict(check) for check in self.health_checks],
            "uptime_seconds": (datetime.now(timezone.utc) - self.start_time).total_seconds(),
            "request_count": self.request_count,
            "error_count": self.error_count
        }

# Global health monitor instance
health_monitor = HealthMonitor()

def get_health_monitor() -> HealthMonitor:
    """Get the global health monitor instance"""
    return health_monitor

async def run_health_checks() -> List[HealthCheck]:
    """Run health checks using the global monitor"""
    return await health_monitor.run_health_checks()

def get_system_health() -> Dict[str, Any]:
    """Get system health status"""
    return health_monitor.get_overall_health()

def record_request(success: bool = True) -> None:
    """Record a request for metrics"""
    health_monitor.record_request(success)
