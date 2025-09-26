#!/usr/bin/env python3
"""
Cosmic Council Framework - Performance Monitoring and Analytics

This module provides comprehensive performance monitoring and analytics including:

- Real-time performance metrics collection
- System resource monitoring
- Application performance tracking
- Database performance monitoring
- API performance analytics
- User experience metrics
- Performance alerting and notifications
- Performance trend analysis
- Performance reporting and dashboards
- Performance optimization recommendations

Author: Cosmic Council Development Team
Version: 1.0.0
"""

import asyncio
import time
import logging
import json
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import weakref
import sqlite3
import pickle
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from functools import wraps
import aiohttp
import redis

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Performance Metrics Types ---

class MetricType(Enum):
    """Types of performance metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"

class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

# --- Performance Metrics ---

@dataclass
class PerformanceMetric:
    """Individual performance metric"""
    name: str
    value: Union[int, float]
    metric_type: MetricType
    timestamp: datetime = field(default_factory=datetime.utcnow)
    tags: Dict[str, str] = field(default_factory=dict)
    unit: Optional[str] = None
    description: Optional[str] = None

@dataclass
class PerformanceAlert:
    """Performance alert"""
    id: str
    name: str
    level: AlertLevel
    message: str
    metric_name: str
    threshold: float
    current_value: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False
    resolved_at: Optional[datetime] = None

@dataclass
class PerformanceReport:
    """Performance report"""
    id: str
    title: str
    start_time: datetime
    end_time: datetime
    metrics: Dict[str, List[PerformanceMetric]]
    alerts: List[PerformanceAlert]
    summary: Dict[str, Any]
    recommendations: List[str]

# --- Metrics Storage ---

class MetricsStorage:
    """High-performance metrics storage with SQLite backend"""
    
    def __init__(self, db_path: str = "performance_metrics.db"):
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("PRAGMA synchronous=NORMAL")
        self._initialize_tables()
        self._lock = threading.RLock()
    
    def _initialize_tables(self):
        """Initialize database tables"""
        cursor = self.connection.cursor()
        
        # Metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                value REAL NOT NULL,
                metric_type TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                tags TEXT,
                unit TEXT,
                description TEXT,
                INDEX idx_name_timestamp (name, timestamp),
                INDEX idx_timestamp (timestamp)
            )
        """)
        
        # Alerts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                threshold REAL NOT NULL,
                current_value REAL NOT NULL,
                timestamp DATETIME NOT NULL,
                resolved BOOLEAN DEFAULT FALSE,
                resolved_at DATETIME
            )
        """)
        
        # Reports table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                start_time DATETIME NOT NULL,
                end_time DATETIME NOT NULL,
                summary TEXT NOT NULL,
                recommendations TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.connection.commit()
    
    def store_metric(self, metric: PerformanceMetric):
        """Store performance metric"""
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO metrics (name, value, metric_type, timestamp, tags, unit, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                metric.name,
                metric.value,
                metric.metric_type.value,
                metric.timestamp.isoformat(),
                json.dumps(metric.tags),
                metric.unit,
                metric.description
            ))
            self.connection.commit()
    
    def store_alert(self, alert: PerformanceAlert):
        """Store performance alert"""
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO alerts 
                (id, name, level, message, metric_name, threshold, current_value, timestamp, resolved, resolved_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                alert.id,
                alert.name,
                alert.level.value,
                alert.message,
                alert.metric_name,
                alert.threshold,
                alert.current_value,
                alert.timestamp.isoformat(),
                alert.resolved,
                alert.resolved_at.isoformat() if alert.resolved_at else None
            ))
            self.connection.commit()
    
    def get_metrics(self, name: str, start_time: datetime, end_time: datetime) -> List[PerformanceMetric]:
        """Get metrics for a specific name and time range"""
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT name, value, metric_type, timestamp, tags, unit, description
                FROM metrics
                WHERE name = ? AND timestamp BETWEEN ? AND ?
                ORDER BY timestamp
            """, (name, start_time.isoformat(), end_time.isoformat()))
            
            metrics = []
            for row in cursor.fetchall():
                metric = PerformanceMetric(
                    name=row[0],
                    value=row[1],
                    metric_type=MetricType(row[2]),
                    timestamp=datetime.fromisoformat(row[3]),
                    tags=json.loads(row[4]) if row[4] else {},
                    unit=row[5],
                    description=row[6]
                )
                metrics.append(metric)
            
            return metrics
    
    def get_active_alerts(self) -> List[PerformanceAlert]:
        """Get active (unresolved) alerts"""
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT id, name, level, message, metric_name, threshold, current_value, timestamp, resolved, resolved_at
                FROM alerts
                WHERE resolved = FALSE
                ORDER BY timestamp DESC
            """)
            
            alerts = []
            for row in cursor.fetchall():
                alert = PerformanceAlert(
                    id=row[0],
                    name=row[1],
                    level=AlertLevel(row[2]),
                    message=row[3],
                    metric_name=row[4],
                    threshold=row[5],
                    current_value=row[6],
                    timestamp=datetime.fromisoformat(row[7]),
                    resolved=bool(row[8]),
                    resolved_at=datetime.fromisoformat(row[9]) if row[9] else None
                )
                alerts.append(alert)
            
            return alerts
    
    def cleanup_old_metrics(self, days: int = 30):
        """Clean up old metrics"""
        with self._lock:
            cursor = self.connection.cursor()
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            cursor.execute("DELETE FROM metrics WHERE timestamp < ?", (cutoff_date.isoformat(),))
            deleted_count = cursor.rowcount
            self.connection.commit()
            logger.info(f"Cleaned up {deleted_count} old metrics")
            return deleted_count

# --- System Monitor ---

class SystemMonitor:
    """Monitor system performance metrics"""
    
    def __init__(self, storage: MetricsStorage):
        self.storage = storage
        self.is_monitoring = False
        self.monitor_task: Optional[asyncio.Task] = None
    
    async def start_monitoring(self, interval: float = 1.0):
        """Start system monitoring"""
        if self.is_monitoring:
            logger.warning("System monitoring already running")
            return
        
        self.is_monitoring = True
        self.monitor_task = asyncio.create_task(self._monitor_loop(interval))
        logger.info("System monitoring started")
    
    async def stop_monitoring(self):
        """Stop system monitoring"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("System monitoring stopped")
    
    async def _monitor_loop(self, interval: float):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in system monitoring: {e}")
                await asyncio.sleep(interval)
    
    async def _collect_system_metrics(self):
        """Collect system performance metrics"""
        timestamp = datetime.utcnow()
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        self.storage.store_metric(PerformanceMetric(
            name="system.cpu.percent",
            value=cpu_percent,
            metric_type=MetricType.GAUGE,
            timestamp=timestamp,
            unit="percent",
            description="CPU usage percentage"
        ))
        
        self.storage.store_metric(PerformanceMetric(
            name="system.cpu.count",
            value=cpu_count,
            metric_type=MetricType.GAUGE,
            timestamp=timestamp,
            description="Number of CPU cores"
        ))
        
        if cpu_freq:
            self.storage.store_metric(PerformanceMetric(
                name="system.cpu.frequency",
                value=cpu_freq.current,
                metric_type=MetricType.GAUGE,
                timestamp=timestamp,
                unit="MHz",
                description="Current CPU frequency"
            ))
        
        # Memory metrics
        memory = psutil.virtual_memory()
        self.storage.store_metric(PerformanceMetric(
            name="system.memory.percent",
            value=memory.percent,
            metric_type=MetricType.GAUGE,
            timestamp=timestamp,
            unit="percent",
            description="Memory usage percentage"
        ))
        
        self.storage.store_metric(PerformanceMetric(
            name="system.memory.used",
            value=memory.used,
            metric_type=MetricType.GAUGE,
            timestamp=timestamp,
            unit="bytes",
            description="Used memory in bytes"
        ))
        
        self.storage.store_metric(PerformanceMetric(
            name="system.memory.available",
            value=memory.available,
            metric_type=MetricType.GAUGE,
            timestamp=timestamp,
            unit="bytes",
            description="Available memory in bytes"
        ))
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        self.storage.store_metric(PerformanceMetric(
            name="system.disk.percent",
            value=(disk.used / disk.total) * 100,
            metric_type=MetricType.GAUGE,
            timestamp=timestamp,
            unit="percent",
            description="Disk usage percentage"
        ))
        
        self.storage.store_metric(PerformanceMetric(
            name="system.disk.free",
            value=disk.free,
            metric_type=MetricType.GAUGE,
            timestamp=timestamp,
            unit="bytes",
            description="Free disk space in bytes"
        ))
        
        # Network metrics
        network = psutil.net_io_counters()
        self.storage.store_metric(PerformanceMetric(
            name="system.network.bytes_sent",
            value=network.bytes_sent,
            metric_type=MetricType.COUNTER,
            timestamp=timestamp,
            unit="bytes",
            description="Network bytes sent"
        ))
        
        self.storage.store_metric(PerformanceMetric(
            name="system.network.bytes_recv",
            value=network.bytes_recv,
            metric_type=MetricType.COUNTER,
            timestamp=timestamp,
            unit="bytes",
            description="Network bytes received"
        ))

# --- Application Monitor ---

class ApplicationMonitor:
    """Monitor application performance metrics"""
    
    def __init__(self, storage: MetricsStorage):
        self.storage = storage
        self.request_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.error_counts: Dict[str, int] = defaultdict(int)
        self._lock = threading.RLock()
    
    def record_request(self, endpoint: str, method: str, response_time: float, 
                      status_code: int, request_size: int = 0, response_size: int = 0):
        """Record API request metrics"""
        timestamp = datetime.utcnow()
        
        # Store request metrics
        self.storage.store_metric(PerformanceMetric(
            name="app.requests.response_time",
            value=response_time,
            metric_type=MetricType.TIMER,
            timestamp=timestamp,
            tags={"endpoint": endpoint, "method": method, "status_code": str(status_code)},
            unit="seconds",
            description="API request response time"
        ))
        
        self.storage.store_metric(PerformanceMetric(
            name="app.requests.count",
            value=1,
            metric_type=MetricType.COUNTER,
            timestamp=timestamp,
            tags={"endpoint": endpoint, "method": method, "status_code": str(status_code)},
            description="API request count"
        ))
        
        if request_size > 0:
            self.storage.store_metric(PerformanceMetric(
                name="app.requests.size",
                value=request_size,
                metric_type=MetricType.GAUGE,
                timestamp=timestamp,
                tags={"endpoint": endpoint, "method": method},
                unit="bytes",
                description="API request size"
            ))
        
        if response_size > 0:
            self.storage.store_metric(PerformanceMetric(
                name="app.responses.size",
                value=response_size,
                metric_type=MetricType.GAUGE,
                timestamp=timestamp,
                tags={"endpoint": endpoint, "method": method},
                unit="bytes",
                description="API response size"
            ))
        
        # Track errors
        if status_code >= 400:
            with self._lock:
                self.error_counts[f"{endpoint}:{method}"] += 1
        
        # Store in memory for quick access
        with self._lock:
            self.request_metrics[f"{endpoint}:{method}"].append({
                "response_time": response_time,
                "status_code": status_code,
                "timestamp": timestamp
            })
    
    def record_database_query(self, query: str, execution_time: float, rows_returned: int, 
                             cache_hit: bool = False):
        """Record database query metrics"""
        timestamp = datetime.utcnow()
        
        self.storage.store_metric(PerformanceMetric(
            name="app.database.query_time",
            value=execution_time,
            metric_type=MetricType.TIMER,
            timestamp=timestamp,
            tags={"cache_hit": str(cache_hit)},
            unit="seconds",
            description="Database query execution time"
        ))
        
        self.storage.store_metric(PerformanceMetric(
            name="app.database.rows_returned",
            value=rows_returned,
            metric_type=MetricType.GAUGE,
            timestamp=timestamp,
            description="Number of rows returned by query"
        ))
    
    def record_cycle_execution(self, cycle_id: str, duration: float, success: bool, 
                              enterprise_type: str = None):
        """Record problem-solving cycle execution metrics"""
        timestamp = datetime.utcnow()
        
        self.storage.store_metric(PerformanceMetric(
            name="app.cycles.duration",
            value=duration,
            metric_type=MetricType.TIMER,
            timestamp=timestamp,
            tags={"cycle_id": cycle_id, "success": str(success), "enterprise": enterprise_type or "unknown"},
            unit="seconds",
            description="Problem-solving cycle execution duration"
        ))
        
        self.storage.store_metric(PerformanceMetric(
            name="app.cycles.count",
            value=1,
            metric_type=MetricType.COUNTER,
            timestamp=timestamp,
            tags={"success": str(success), "enterprise": enterprise_type or "unknown"},
            description="Problem-solving cycle count"
        ))
    
    def get_request_stats(self, endpoint: str, method: str) -> Dict[str, Any]:
        """Get request statistics for specific endpoint"""
        with self._lock:
            key = f"{endpoint}:{method}"
            if key not in self.request_metrics:
                return {}
            
            metrics = list(self.request_metrics[key])
            if not metrics:
                return {}
            
            response_times = [m["response_time"] for m in metrics]
            status_codes = [m["status_code"] for m in metrics]
            
            return {
                "total_requests": len(metrics),
                "avg_response_time": sum(response_times) / len(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "error_count": sum(1 for s in status_codes if s >= 400),
                "error_rate": sum(1 for s in status_codes if s >= 400) / len(status_codes)
            }

# --- Alert Manager ---

class AlertManager:
    """Manage performance alerts and notifications"""
    
    def __init__(self, storage: MetricsStorage):
        self.storage = storage
        self.alert_rules: Dict[str, Dict] = {}
        self.alert_handlers: List[Callable] = []
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize default alert rules"""
        self.alert_rules = {
            "high_cpu_usage": {
                "metric": "system.cpu.percent",
                "threshold": 80.0,
                "operator": ">",
                "level": AlertLevel.WARNING,
                "message": "High CPU usage detected"
            },
            "high_memory_usage": {
                "metric": "system.memory.percent",
                "threshold": 85.0,
                "operator": ">",
                "level": AlertLevel.WARNING,
                "message": "High memory usage detected"
            },
            "low_disk_space": {
                "metric": "system.disk.percent",
                "threshold": 90.0,
                "operator": ">",
                "level": AlertLevel.ERROR,
                "message": "Low disk space detected"
            },
            "slow_api_response": {
                "metric": "app.requests.response_time",
                "threshold": 2.0,
                "operator": ">",
                "level": AlertLevel.WARNING,
                "message": "Slow API response time detected"
            },
            "high_error_rate": {
                "metric": "app.requests.error_rate",
                "threshold": 0.1,
                "operator": ">",
                "level": AlertLevel.ERROR,
                "message": "High error rate detected"
            }
        }
    
    def add_alert_rule(self, name: str, metric: str, threshold: float, 
                      operator: str, level: AlertLevel, message: str):
        """Add custom alert rule"""
        self.alert_rules[name] = {
            "metric": metric,
            "threshold": threshold,
            "operator": operator,
            "level": level,
            "message": message
        }
    
    def add_alert_handler(self, handler: Callable):
        """Add alert notification handler"""
        self.alert_handlers.append(handler)
    
    async def check_alerts(self, metric: PerformanceMetric):
        """Check if metric triggers any alerts"""
        for rule_name, rule in self.alert_rules.items():
            if rule["metric"] == metric.name:
                if self._evaluate_condition(metric.value, rule["threshold"], rule["operator"]):
                    await self._trigger_alert(rule_name, rule, metric)
    
    def _evaluate_condition(self, value: float, threshold: float, operator: str) -> bool:
        """Evaluate alert condition"""
        if operator == ">":
            return value > threshold
        elif operator == ">=":
            return value >= threshold
        elif operator == "<":
            return value < threshold
        elif operator == "<=":
            return value <= threshold
        elif operator == "==":
            return value == threshold
        elif operator == "!=":
            return value != threshold
        else:
            return False
    
    async def _trigger_alert(self, rule_name: str, rule: Dict, metric: PerformanceMetric):
        """Trigger alert"""
        alert = PerformanceAlert(
            id=f"{rule_name}_{int(time.time())}",
            name=rule_name,
            level=rule["level"],
            message=rule["message"],
            metric_name=metric.name,
            threshold=rule["threshold"],
            current_value=metric.value,
            timestamp=datetime.utcnow()
        )
        
        # Store alert
        self.storage.store_alert(alert)
        
        # Notify handlers
        for handler in self.alert_handlers:
            try:
                await handler(alert)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")
        
        logger.warning(f"Alert triggered: {alert.message} (value: {alert.current_value}, threshold: {alert.threshold})")

# --- Performance Analytics ---

class PerformanceAnalytics:
    """Analyze performance data and generate insights"""
    
    def __init__(self, storage: MetricsStorage):
        self.storage = storage
    
    def generate_performance_report(self, start_time: datetime, end_time: datetime) -> PerformanceReport:
        """Generate comprehensive performance report"""
        report_id = f"report_{int(time.time())}"
        
        # Collect metrics
        metrics = {}
        metric_names = [
            "system.cpu.percent",
            "system.memory.percent",
            "system.disk.percent",
            "app.requests.response_time",
            "app.requests.count",
            "app.cycles.duration"
        ]
        
        for metric_name in metric_names:
            metrics[metric_name] = self.storage.get_metrics(metric_name, start_time, end_time)
        
        # Get active alerts
        alerts = self.storage.get_active_alerts()
        
        # Generate summary
        summary = self._generate_summary(metrics, alerts)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metrics, summary)
        
        return PerformanceReport(
            id=report_id,
            title=f"Performance Report ({start_time.date()} - {end_time.date()})",
            start_time=start_time,
            end_time=end_time,
            metrics=metrics,
            alerts=alerts,
            summary=summary,
            recommendations=recommendations
        )
    
    def _generate_summary(self, metrics: Dict[str, List[PerformanceMetric]], 
                         alerts: List[PerformanceAlert]) -> Dict[str, Any]:
        """Generate performance summary"""
        summary = {
            "total_alerts": len(alerts),
            "critical_alerts": len([a for a in alerts if a.level == AlertLevel.CRITICAL]),
            "warning_alerts": len([a for a in alerts if a.level == AlertLevel.WARNING]),
            "system_health": "healthy",
            "performance_trends": {}
        }
        
        # Analyze CPU trends
        cpu_metrics = metrics.get("system.cpu.percent", [])
        if cpu_metrics:
            cpu_values = [m.value for m in cpu_metrics]
            summary["performance_trends"]["cpu"] = {
                "avg": sum(cpu_values) / len(cpu_values),
                "max": max(cpu_values),
                "min": min(cpu_values),
                "trend": "stable"  # Could implement trend analysis
            }
        
        # Analyze memory trends
        memory_metrics = metrics.get("system.memory.percent", [])
        if memory_metrics:
            memory_values = [m.value for m in memory_metrics]
            summary["performance_trends"]["memory"] = {
                "avg": sum(memory_values) / len(memory_values),
                "max": max(memory_values),
                "min": min(memory_values),
                "trend": "stable"
            }
        
        # Analyze API performance
        response_time_metrics = metrics.get("app.requests.response_time", [])
        if response_time_metrics:
            response_times = [m.value for m in response_time_metrics]
            summary["performance_trends"]["api_response_time"] = {
                "avg": sum(response_times) / len(response_times),
                "max": max(response_times),
                "min": min(response_times),
                "p95": sorted(response_times)[int(len(response_times) * 0.95)] if response_times else 0
            }
        
        # Determine overall system health
        if summary["critical_alerts"] > 0:
            summary["system_health"] = "critical"
        elif summary["warning_alerts"] > 3:
            summary["system_health"] = "warning"
        elif summary["total_alerts"] > 0:
            summary["system_health"] = "caution"
        
        return summary
    
    def _generate_recommendations(self, metrics: Dict[str, List[PerformanceMetric]], 
                                 summary: Dict[str, Any]) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        # CPU recommendations
        cpu_trend = summary.get("performance_trends", {}).get("cpu", {})
        if cpu_trend.get("avg", 0) > 70:
            recommendations.append("Consider optimizing CPU-intensive operations or scaling horizontally")
        
        # Memory recommendations
        memory_trend = summary.get("performance_trends", {}).get("memory", {})
        if memory_trend.get("avg", 0) > 80:
            recommendations.append("Consider optimizing memory usage or increasing available memory")
        
        # API performance recommendations
        api_trend = summary.get("performance_trends", {}).get("api_response_time", {})
        if api_trend.get("avg", 0) > 1.0:
            recommendations.append("Consider optimizing API endpoints or implementing caching")
        
        if api_trend.get("p95", 0) > 2.0:
            recommendations.append("95th percentile response time is high, investigate slow queries")
        
        # General recommendations
        if summary["critical_alerts"] > 0:
            recommendations.append("Address critical alerts immediately to prevent system instability")
        
        if summary["warning_alerts"] > 5:
            recommendations.append("Multiple warning alerts detected, review system configuration")
        
        return recommendations

# --- Main Performance Monitor ---

class PerformanceMonitor:
    """Main performance monitoring coordinator"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.storage = MetricsStorage()
        self.system_monitor = SystemMonitor(self.storage)
        self.app_monitor = ApplicationMonitor(self.storage)
        self.alert_manager = AlertManager(self.storage)
        self.analytics = PerformanceAnalytics(self.storage)
        self.is_running = False
    
    async def start(self):
        """Start performance monitoring"""
        if self.is_running:
            logger.warning("Performance monitoring already running")
            return
        
        logger.info("Starting performance monitoring")
        
        # Start system monitoring
        await self.system_monitor.start_monitoring(interval=1.0)
        
        # Setup alert handlers
        self.alert_manager.add_alert_handler(self._log_alert)
        self.alert_manager.add_alert_handler(self._send_notification)
        
        self.is_running = True
        logger.info("Performance monitoring started")
    
    async def stop(self):
        """Stop performance monitoring"""
        if not self.is_running:
            return
        
        logger.info("Stopping performance monitoring")
        
        # Stop system monitoring
        await self.system_monitor.stop_monitoring()
        
        self.is_running = False
        logger.info("Performance monitoring stopped")
    
    async def _log_alert(self, alert: PerformanceAlert):
        """Log alert to console"""
        logger.warning(f"ALERT [{alert.level.value.upper()}] {alert.message} - "
                      f"Metric: {alert.metric_name}, Value: {alert.current_value}, "
                      f"Threshold: {alert.threshold}")
    
    async def _send_notification(self, alert: PerformanceAlert):
        """Send alert notification (placeholder for actual notification system)"""
        # This would integrate with actual notification systems (email, Slack, etc.)
        logger.info(f"Notification sent for alert: {alert.name}")
    
    def record_metric(self, metric: PerformanceMetric):
        """Record performance metric"""
        self.storage.store_metric(metric)
        
        # Check for alerts
        if self.is_running:
            asyncio.create_task(self.alert_manager.check_alerts(metric))
    
    def record_request(self, endpoint: str, method: str, response_time: float, 
                      status_code: int, request_size: int = 0, response_size: int = 0):
        """Record API request metrics"""
        self.app_monitor.record_request(endpoint, method, response_time, status_code, 
                                       request_size, response_size)
    
    def record_cycle(self, cycle_id: str, duration: float, success: bool, 
                    enterprise_type: str = None):
        """Record cycle execution metrics"""
        self.app_monitor.record_cycle_execution(cycle_id, duration, success, enterprise_type)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get current performance summary"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=1)
        
        # Get recent metrics
        cpu_metrics = self.storage.get_metrics("system.cpu.percent", start_time, end_time)
        memory_metrics = self.storage.get_metrics("system.memory.percent", start_time, end_time)
        response_time_metrics = self.storage.get_metrics("app.requests.response_time", start_time, end_time)
        
        # Calculate summary
        summary = {
            "timestamp": end_time.isoformat(),
            "system_metrics": {
                "cpu_usage": cpu_metrics[-1].value if cpu_metrics else 0,
                "memory_usage": memory_metrics[-1].value if memory_metrics else 0
            },
            "application_metrics": {
                "avg_response_time": sum(m.value for m in response_time_metrics) / len(response_time_metrics) if response_time_metrics else 0,
                "total_requests": len(response_time_metrics)
            },
            "active_alerts": len(self.storage.get_active_alerts())
        }
        
        return summary
    
    def generate_report(self, hours: int = 24) -> PerformanceReport:
        """Generate performance report for specified time period"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        return self.analytics.generate_performance_report(start_time, end_time)

# --- Demo Function ---

async def demo_performance_monitoring():
    """Demonstrate performance monitoring capabilities"""
    print("📊 Cosmic Council Framework - Performance Monitoring Demo")
    print("=" * 70)
    
    try:
        # Create performance monitor
        monitor = PerformanceMonitor()
        print("✅ Performance monitor created")
        
        # Start monitoring
        await monitor.start()
        print("✅ Performance monitoring started")
        
        # Simulate some metrics
        print("\n📈 Simulating performance metrics...")
        
        # Record some API requests
        for i in range(10):
            response_time = 0.1 + (i * 0.05)
            status_code = 200 if i < 8 else 500
            monitor.record_request(f"/api/endpoint_{i % 3}", "GET", response_time, status_code)
            print(f"  📝 Recorded request to /api/endpoint_{i % 3} ({response_time:.3f}s, {status_code})")
        
        # Record some cycle executions
        for i in range(5):
            duration = 2.0 + (i * 0.5)
            success = i < 4
            enterprise = ["red_owl", "orange_orangutan", "yellow_honeybee"][i % 3]
            monitor.record_cycle(f"cycle_{i}", duration, success, enterprise)
            print(f"  🔄 Recorded cycle {i} ({duration:.1f}s, {'success' if success else 'failed'}, {enterprise})")
        
        # Wait for metrics to be collected
        print("\n⏳ Waiting for system metrics collection...")
        await asyncio.sleep(3)
        
        # Get performance summary
        print("\n📊 Performance Summary:")
        summary = monitor.get_performance_summary()
        for key, value in summary.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for sub_key, sub_value in value.items():
                    print(f"    {sub_key}: {sub_value}")
            else:
                print(f"  {key}: {value}")
        
        # Generate performance report
        print("\n📋 Generating performance report...")
        report = monitor.generate_report(hours=1)
        print(f"  Report ID: {report.id}")
        print(f"  Title: {report.title}")
        print(f"  System Health: {report.summary['system_health']}")
        print(f"  Total Alerts: {report.summary['total_alerts']}")
        print(f"  Recommendations: {len(report.recommendations)}")
        
        if report.recommendations:
            print("  Recommendations:")
            for i, rec in enumerate(report.recommendations, 1):
                print(f"    {i}. {rec}")
        
        # Test alert system
        print("\n🚨 Testing alert system...")
        
        # Trigger high CPU alert
        high_cpu_metric = PerformanceMetric(
            name="system.cpu.percent",
            value=85.0,  # Above threshold
            metric_type=MetricType.GAUGE,
            description="High CPU usage test"
        )
        monitor.record_metric(high_cpu_metric)
        print("  📢 Triggered high CPU alert")
        
        # Check active alerts
        active_alerts = monitor.storage.get_active_alerts()
        print(f"  Active alerts: {len(active_alerts)}")
        
        for alert in active_alerts:
            print(f"    - {alert.name}: {alert.message} (Level: {alert.level.value})")
        
        print("\n✅ Performance monitoring demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        logger.error(f"Demo error: {e}")
    
    finally:
        # Stop monitoring
        if 'monitor' in locals():
            await monitor.stop()
        print("🛑 Performance monitoring stopped")

if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_performance_monitoring())
