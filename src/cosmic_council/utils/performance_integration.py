#!/usr/bin/env python3
"""
Cosmic Council Framework - Performance Integration System

This module integrates all performance optimization components into a unified system:

- Performance optimization coordinator
- System-wide performance management
- Integration with existing Cosmic Council components
- Performance optimization strategies
- Real-time performance tuning
- Performance benchmarking and testing
- Performance optimization recommendations
- Performance monitoring dashboard integration
- Performance optimization automation
- Performance metrics aggregation and analysis

Author: Cosmic Council Development Team
Version: 1.0.0
"""

import asyncio
import time
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import threading
import weakref
from functools import wraps
import psutil
import gc

# Import performance optimization modules
from performance_optimization import PerformanceOptimizer, PerformanceConfig, OptimizedCycleExecutor
from database_optimization import OptimizedDatabaseManager, DatabaseConfig
from api_performance_optimization import OptimizedFastAPI, APIPerformanceConfig
from performance_monitoring import PerformanceMonitor, PerformanceMetric, MetricType, AlertLevel

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Performance Integration Configuration ---

@dataclass
class PerformanceIntegrationConfig:
    """Configuration for integrated performance optimization"""
    # Core performance settings
    enable_performance_optimization: bool = True
    enable_database_optimization: bool = True
    enable_api_optimization: bool = True
    enable_monitoring: bool = True
    
    # Performance thresholds
    cpu_threshold: float = 0.7
    memory_threshold: float = 0.8
    response_time_threshold: float = 2.0
    error_rate_threshold: float = 0.05
    
    # Optimization intervals
    optimization_check_interval: float = 30.0
    metrics_collection_interval: float = 1.0
    alert_check_interval: float = 5.0
    
    # Auto-scaling settings
    enable_auto_scaling: bool = True
    min_workers: int = 2
    max_workers: int = 20
    scale_up_threshold: float = 0.8
    scale_down_threshold: float = 0.3
    
    # Caching settings
    enable_response_caching: bool = True
    enable_query_caching: bool = True
    cache_ttl: int = 3600
    
    # Database settings
    database_url: str = "postgresql://user:password@localhost:5432/cosmic_council"
    max_db_connections: int = 20
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    max_api_connections: int = 100

# --- Performance Integration Manager ---

class PerformanceIntegrationManager:
    """Main performance integration coordinator"""
    
    def __init__(self, config: PerformanceIntegrationConfig):
        self.config = config
        self.is_running = False
        
        # Initialize performance components
        self.performance_optimizer: Optional[PerformanceOptimizer] = None
        self.database_manager: Optional[OptimizedDatabaseManager] = None
        self.api_optimizer: Optional[OptimizedFastAPI] = None
        self.performance_monitor: Optional[PerformanceMonitor] = None
        
        # Performance tracking
        self.performance_metrics: Dict[str, Any] = {}
        self.optimization_history: deque = deque(maxlen=1000)
        self.performance_trends: Dict[str, List[float]] = defaultdict(list)
        
        # Auto-scaling state
        self.current_workers = config.min_workers
        self.last_scale_time = 0
        self.scale_cooldown = 60  # seconds
        
        # Performance optimization tasks
        self.optimization_task: Optional[asyncio.Task] = None
        self.monitoring_task: Optional[asyncio.Task] = None
        self.alerting_task: Optional[asyncio.Task] = None
        
        self._lock = threading.RLock()
    
    async def initialize(self):
        """Initialize all performance optimization components"""
        logger.info("Initializing performance integration system")
        
        try:
            # Initialize performance optimizer
            if self.config.enable_performance_optimization:
                perf_config = PerformanceConfig(
                    max_concurrent_cycles=100,
                    max_workers=self.config.max_workers,
                    cache_ttl=self.config.cache_ttl,
                    enable_auto_scaling=self.config.enable_auto_scaling
                )
                self.performance_optimizer = PerformanceOptimizer(perf_config)
                await self.performance_optimizer.start()
                logger.info("✅ Performance optimizer initialized")
            
            # Initialize database manager
            if self.config.enable_database_optimization:
                db_config = DatabaseConfig(
                    max_connections=self.config.max_db_connections,
                    enable_query_cache=self.config.enable_query_caching,
                    cache_ttl=self.config.cache_ttl
                )
                self.database_manager = OptimizedDatabaseManager(db_config, self.config.database_url)
                logger.info("✅ Database optimizer initialized")
            
            # Initialize API optimizer
            if self.config.enable_api_optimization:
                api_config = APIPerformanceConfig(
                    enable_response_caching=self.config.enable_response_caching,
                    cache_ttl=self.config.cache_ttl,
                    max_connections=self.config.max_api_connections
                )
                self.api_optimizer = OptimizedFastAPI(api_config)
                logger.info("✅ API optimizer initialized")
            
            # Initialize performance monitor
            if self.config.enable_monitoring:
                self.performance_monitor = PerformanceMonitor()
                await self.performance_monitor.start()
                logger.info("✅ Performance monitor initialized")
            
            logger.info("🎉 Performance integration system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize performance integration system: {e}")
            raise
    
    async def start(self):
        """Start the performance integration system"""
        if self.is_running:
            logger.warning("Performance integration system already running")
            return
        
        logger.info("Starting performance integration system")
        
        # Start optimization tasks
        self.optimization_task = asyncio.create_task(self._optimization_loop())
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.alerting_task = asyncio.create_task(self._alerting_loop())
        
        self.is_running = True
        logger.info("🚀 Performance integration system started")
    
    async def stop(self):
        """Stop the performance integration system"""
        if not self.is_running:
            return
        
        logger.info("Stopping performance integration system")
        
        # Cancel tasks
        if self.optimization_task:
            self.optimization_task.cancel()
        if self.monitoring_task:
            self.monitoring_task.cancel()
        if self.alerting_task:
            self.alerting_task.cancel()
        
        # Stop components
        if self.performance_optimizer:
            await self.performance_optimizer.stop()
        
        if self.performance_monitor:
            await self.performance_monitor.stop()
        
        if self.database_manager:
            self.database_manager.close()
        
        self.is_running = False
        logger.info("🛑 Performance integration system stopped")
    
    async def _optimization_loop(self):
        """Main optimization loop"""
        while self.is_running:
            try:
                await self._perform_optimization()
                await asyncio.sleep(self.config.optimization_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in optimization loop: {e}")
                await asyncio.sleep(5)
    
    async def _monitoring_loop(self):
        """Performance monitoring loop"""
        while self.is_running:
            try:
                await self._collect_performance_metrics()
                await asyncio.sleep(self.config.metrics_collection_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(1)
    
    async def _alerting_loop(self):
        """Alert checking loop"""
        while self.is_running:
            try:
                await self._check_performance_alerts()
                await asyncio.sleep(self.config.alert_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in alerting loop: {e}")
                await asyncio.sleep(5)
    
    async def _perform_optimization(self):
        """Perform system-wide performance optimization"""
        with self._lock:
            optimization_start = time.time()
            optimizations_applied = []
            
            try:
                # Check system resources
                cpu_usage = psutil.cpu_percent()
                memory_usage = psutil.virtual_memory().percent / 100.0
                
                # CPU optimization
                if cpu_usage > self.config.cpu_threshold:
                    await self._optimize_cpu_usage()
                    optimizations_applied.append("cpu_optimization")
                
                # Memory optimization
                if memory_usage > self.config.memory_threshold:
                    await self._optimize_memory_usage()
                    optimizations_applied.append("memory_optimization")
                
                # Auto-scaling
                if self.config.enable_auto_scaling:
                    await self._check_auto_scaling()
                
                # Database optimization
                if self.database_manager:
                    await self._optimize_database()
                    optimizations_applied.append("database_optimization")
                
                # Cache optimization
                await self._optimize_caches()
                optimizations_applied.append("cache_optimization")
                
                # Record optimization
                optimization_duration = time.time() - optimization_start
                self.optimization_history.append({
                    "timestamp": datetime.utcnow(),
                    "duration": optimization_duration,
                    "optimizations": optimizations_applied,
                    "cpu_usage": cpu_usage,
                    "memory_usage": memory_usage
                })
                
                if optimizations_applied:
                    logger.info(f"Applied optimizations: {', '.join(optimizations_applied)}")
                
            except Exception as e:
                logger.error(f"Optimization failed: {e}")
    
    async def _collect_performance_metrics(self):
        """Collect comprehensive performance metrics"""
        try:
            # System metrics
            cpu_usage = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Application metrics
            app_metrics = {}
            if self.performance_optimizer:
                app_metrics.update(self.performance_optimizer.get_performance_stats())
            
            if self.database_manager:
                app_metrics.update(self.database_manager.get_performance_stats())
            
            # Store metrics
            self.performance_metrics = {
                "timestamp": datetime.utcnow().isoformat(),
                "system": {
                    "cpu_usage": cpu_usage,
                    "memory_usage": memory.percent,
                    "memory_available": memory.available,
                    "disk_usage": (disk.used / disk.total) * 100,
                    "disk_free": disk.free
                },
                "application": app_metrics
            }
            
            # Update trends
            self.performance_trends["cpu"].append(cpu_usage)
            self.performance_trends["memory"].append(memory.percent)
            
            # Keep only recent trends (last 100 points)
            for key in self.performance_trends:
                if len(self.performance_trends[key]) > 100:
                    self.performance_trends[key] = self.performance_trends[key][-100:]
            
            # Record metrics in performance monitor
            if self.performance_monitor:
                self.performance_monitor.record_metric(PerformanceMetric(
                    name="integration.cpu_usage",
                    value=cpu_usage,
                    metric_type=MetricType.GAUGE,
                    unit="percent"
                ))
                
                self.performance_monitor.record_metric(PerformanceMetric(
                    name="integration.memory_usage",
                    value=memory.percent,
                    metric_type=MetricType.GAUGE,
                    unit="percent"
                ))
            
        except Exception as e:
            logger.error(f"Failed to collect performance metrics: {e}")
    
    async def _check_performance_alerts(self):
        """Check for performance alerts and take action"""
        try:
            if not self.performance_monitor:
                return
            
            # Get active alerts
            active_alerts = self.performance_monitor.storage.get_active_alerts()
            
            for alert in active_alerts:
                if alert.level in [AlertLevel.ERROR, AlertLevel.CRITICAL]:
                    await self._handle_critical_alert(alert)
                elif alert.level == AlertLevel.WARNING:
                    await self._handle_warning_alert(alert)
            
        except Exception as e:
            logger.error(f"Failed to check performance alerts: {e}")
    
    async def _handle_critical_alert(self, alert: PerformanceAlert):
        """Handle critical performance alerts"""
        logger.critical(f"CRITICAL ALERT: {alert.message}")
        
        # Take immediate action based on alert type
        if "cpu" in alert.metric_name.lower():
            await self._emergency_cpu_optimization()
        elif "memory" in alert.metric_name.lower():
            await self._emergency_memory_optimization()
        elif "disk" in alert.metric_name.lower():
            await self._emergency_disk_cleanup()
    
    async def _handle_warning_alert(self, alert: PerformanceAlert):
        """Handle warning performance alerts"""
        logger.warning(f"WARNING ALERT: {alert.message}")
        
        # Take preventive action
        if "response_time" in alert.metric_name.lower():
            await self._optimize_response_times()
        elif "error_rate" in alert.metric_name.lower():
            await self._optimize_error_handling()
    
    async def _optimize_cpu_usage(self):
        """Optimize CPU usage"""
        logger.info("Optimizing CPU usage")
        
        # Trigger garbage collection
        collected = gc.collect()
        logger.info(f"Garbage collection collected {collected} objects")
        
        # Optimize thread pool
        if self.performance_optimizer and hasattr(self.performance_optimizer, 'executor'):
            # Adjust worker pool size based on CPU usage
            current_cpu = psutil.cpu_percent()
            if current_cpu > 80:
                # Reduce workers to lower CPU usage
                new_workers = max(self.config.min_workers, self.current_workers - 1)
                if new_workers != self.current_workers:
                    self.current_workers = new_workers
                    logger.info(f"Reduced workers to {new_workers} due to high CPU usage")
    
    async def _optimize_memory_usage(self):
        """Optimize memory usage"""
        logger.info("Optimizing memory usage")
        
        # Clear caches
        if self.database_manager:
            self.database_manager.invalidate_cache("")
        
        # Trigger garbage collection
        collected = gc.collect()
        logger.info(f"Memory optimization collected {collected} objects")
        
        # Clear old optimization history
        if len(self.optimization_history) > 500:
            # Keep only recent history
            self.optimization_history = deque(list(self.optimization_history)[-250:], maxlen=1000)
    
    async def _check_auto_scaling(self):
        """Check and perform auto-scaling"""
        current_time = time.time()
        
        # Check cooldown period
        if current_time - self.last_scale_time < self.scale_cooldown:
            return
        
        # Get current metrics
        cpu_usage = psutil.cpu_percent() / 100.0
        memory_usage = psutil.virtual_memory().percent / 100.0
        
        # Scale up if needed
        if (cpu_usage > self.config.scale_up_threshold or 
            memory_usage > self.config.scale_up_threshold):
            if self.current_workers < self.config.max_workers:
                self.current_workers += 1
                self.last_scale_time = current_time
                logger.info(f"Scaled up to {self.current_workers} workers")
        
        # Scale down if possible
        elif (cpu_usage < self.config.scale_down_threshold and 
              memory_usage < self.config.scale_down_threshold):
            if self.current_workers > self.config.min_workers:
                self.current_workers -= 1
                self.last_scale_time = current_time
                logger.info(f"Scaled down to {self.current_workers} workers")
    
    async def _optimize_database(self):
        """Optimize database performance"""
        if not self.database_manager:
            return
        
        logger.info("Optimizing database performance")
        
        # Clean up old metrics
        self.database_manager.storage.cleanup_old_metrics(days=7)
        
        # Optimize query cache
        cache_stats = self.database_manager.query_cache.get_stats()
        if cache_stats["hit_rate"] < 0.7:
            logger.info("Database cache hit rate is low, optimizing cache")
    
    async def _optimize_caches(self):
        """Optimize all caches"""
        logger.info("Optimizing caches")
        
        # Database cache optimization
        if self.database_manager:
            cache_stats = self.database_manager.query_cache.get_stats()
            if cache_stats["memory_cache_size"] > 8000:  # Near max size
                # Clear some old entries
                self.database_manager.query_cache.invalidate("old_")
        
        # API cache optimization
        if self.api_optimizer:
            cache_stats = self.api_optimizer.response_cache.get_stats()
            if cache_stats["memory_cache_size"] > 8000:
                self.api_optimizer.response_cache.invalidate("old_")
    
    async def _emergency_cpu_optimization(self):
        """Emergency CPU optimization"""
        logger.critical("Performing emergency CPU optimization")
        
        # Aggressive garbage collection
        for _ in range(3):
            gc.collect()
        
        # Reduce workers to minimum
        self.current_workers = self.config.min_workers
        
        # Clear all caches
        if self.database_manager:
            self.database_manager.invalidate_cache("")
        
        if self.api_optimizer:
            self.api_optimizer.response_cache.invalidate("")
    
    async def _emergency_memory_optimization(self):
        """Emergency memory optimization"""
        logger.critical("Performing emergency memory optimization")
        
        # Clear all caches
        if self.database_manager:
            self.database_manager.query_cache.clear()
        
        if self.api_optimizer:
            self.api_optimizer.response_cache.clear()
        
        # Aggressive garbage collection
        for _ in range(5):
            gc.collect()
    
    async def _emergency_disk_cleanup(self):
        """Emergency disk cleanup"""
        logger.critical("Performing emergency disk cleanup")
        
        # Clean up old metrics
        if self.database_manager:
            self.database_manager.storage.cleanup_old_metrics(days=1)
        
        # Clear optimization history
        self.optimization_history.clear()
    
    async def _optimize_response_times(self):
        """Optimize API response times"""
        logger.info("Optimizing API response times")
        
        # Enable more aggressive caching
        if self.api_optimizer:
            # Increase cache TTL temporarily
            pass
    
    async def _optimize_error_handling(self):
        """Optimize error handling"""
        logger.info("Optimizing error handling")
        
        # Implement circuit breaker patterns
        # Add retry logic
        # Improve error logging
    
    def get_performance_dashboard_data(self) -> Dict[str, Any]:
        """Get data for performance dashboard"""
        with self._lock:
            return {
                "current_metrics": self.performance_metrics,
                "performance_trends": dict(self.performance_trends),
                "optimization_history": list(self.optimization_history)[-10:],  # Last 10 optimizations
                "current_workers": self.current_workers,
                "system_health": self._calculate_system_health(),
                "recommendations": self._generate_recommendations()
            }
    
    def _calculate_system_health(self) -> str:
        """Calculate overall system health"""
        if not self.performance_metrics:
            return "unknown"
        
        system_metrics = self.performance_metrics.get("system", {})
        cpu_usage = system_metrics.get("cpu_usage", 0)
        memory_usage = system_metrics.get("memory_usage", 0)
        
        if cpu_usage > 90 or memory_usage > 90:
            return "critical"
        elif cpu_usage > 80 or memory_usage > 80:
            return "warning"
        elif cpu_usage > 70 or memory_usage > 70:
            return "caution"
        else:
            return "healthy"
    
    def _generate_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        if not self.performance_metrics:
            return recommendations
        
        system_metrics = self.performance_metrics.get("system", {})
        cpu_usage = system_metrics.get("cpu_usage", 0)
        memory_usage = system_metrics.get("memory_usage", 0)
        
        if cpu_usage > 80:
            recommendations.append("Consider scaling horizontally or optimizing CPU-intensive operations")
        
        if memory_usage > 80:
            recommendations.append("Consider increasing memory or optimizing memory usage")
        
        if self.current_workers < self.config.max_workers and cpu_usage > 70:
            recommendations.append("Consider scaling up workers to handle increased load")
        
        if len(self.optimization_history) > 0:
            recent_optimizations = list(self.optimization_history)[-5:]
            if len(recent_optimizations) > 3:
                recommendations.append("Frequent optimizations detected, consider reviewing system configuration")
        
        return recommendations

# --- Performance Integration Decorators ---

def performance_optimized(func: Callable) -> Callable:
    """Decorator to optimize function performance"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Record performance metric
            if hasattr(wrapper, '_performance_manager'):
                wrapper._performance_manager.performance_monitor.record_metric(
                    PerformanceMetric(
                        name=f"function.{func.__name__}.duration",
                        value=duration,
                        metric_type=MetricType.TIMER,
                        unit="seconds"
                    )
                )
            
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"{func.__name__} failed after {duration:.3f}s: {e}")
            raise
    return wrapper

def performance_monitored(manager: PerformanceIntegrationManager):
    """Decorator to add performance monitoring to functions"""
    def decorator(func: Callable) -> Callable:
        func._performance_manager = manager
        return performance_optimized(func)
    return decorator

# --- Demo Function ---

async def demo_performance_integration():
    """Demonstrate integrated performance optimization"""
    print("🚀 Cosmic Council Framework - Performance Integration Demo")
    print("=" * 70)
    
    # Create performance integration configuration
    config = PerformanceIntegrationConfig(
        enable_performance_optimization=True,
        enable_database_optimization=True,
        enable_api_optimization=True,
        enable_monitoring=True,
        enable_auto_scaling=True,
        min_workers=2,
        max_workers=10,
        optimization_check_interval=5.0,
        metrics_collection_interval=1.0
    )
    
    # Create performance integration manager
    manager = PerformanceIntegrationManager(config)
    
    try:
        # Initialize system
        print("🔧 Initializing performance integration system...")
        await manager.initialize()
        print("✅ Performance integration system initialized")
        
        # Start system
        print("\n🚀 Starting performance integration system...")
        await manager.start()
        print("✅ Performance integration system started")
        
        # Simulate some load
        print("\n📊 Simulating system load...")
        
        # Simulate API requests
        for i in range(20):
            if manager.api_optimizer:
                # Simulate request metrics
                manager.performance_monitor.record_request(
                    f"/api/endpoint_{i % 5}",
                    "GET",
                    0.1 + (i * 0.02),
                    200 if i < 18 else 500
                )
            print(f"  📝 Simulated request {i+1}")
        
        # Simulate cycle executions
        for i in range(10):
            if manager.performance_optimizer:
                # Simulate cycle metrics
                manager.performance_monitor.record_cycle(
                    f"cycle_{i}",
                    1.0 + (i * 0.1),
                    i < 9,
                    ["red_owl", "orange_orangutan", "yellow_honeybee"][i % 3]
                )
            print(f"  🔄 Simulated cycle {i+1}")
        
        # Wait for optimization cycles
        print("\n⏳ Waiting for optimization cycles...")
        await asyncio.sleep(10)
        
        # Get performance dashboard data
        print("\n📈 Performance Dashboard Data:")
        dashboard_data = manager.get_performance_dashboard_data()
        
        print(f"  System Health: {dashboard_data['system_health']}")
        print(f"  Current Workers: {dashboard_data['current_workers']}")
        print(f"  Recommendations: {len(dashboard_data['recommendations'])}")
        
        if dashboard_data['recommendations']:
            print("  Recommendations:")
            for i, rec in enumerate(dashboard_data['recommendations'], 1):
                print(f"    {i}. {rec}")
        
        # Show performance trends
        trends = dashboard_data['performance_trends']
        if trends:
            print(f"  Performance Trends:")
            for metric, values in trends.items():
                if values:
                    avg_value = sum(values) / len(values)
                    print(f"    {metric}: {avg_value:.2f} (avg of {len(values)} samples)")
        
        # Show optimization history
        history = dashboard_data['optimization_history']
        if history:
            print(f"  Recent Optimizations: {len(history)}")
            for opt in history[-3:]:  # Show last 3
                print(f"    - {opt['timestamp'].strftime('%H:%M:%S')}: {', '.join(opt['optimizations'])}")
        
        # Test performance monitoring
        print("\n📊 Performance Monitoring:")
        if manager.performance_monitor:
            summary = manager.performance_monitor.get_performance_summary()
            print(f"  System Metrics:")
            for key, value in summary.get('system_metrics', {}).items():
                print(f"    {key}: {value}")
            
            print(f"  Application Metrics:")
            for key, value in summary.get('application_metrics', {}).items():
                print(f"    {key}: {value}")
            
            print(f"  Active Alerts: {summary.get('active_alerts', 0)}")
        
        # Test auto-scaling
        print("\n⚖️  Auto-scaling Test:")
        print(f"  Current workers: {manager.current_workers}")
        print(f"  Min workers: {config.min_workers}")
        print(f"  Max workers: {config.max_workers}")
        
        # Simulate high load to trigger scaling
        print("  Simulating high load...")
        for _ in range(5):
            # Simulate high CPU usage
            manager.performance_monitor.record_metric(PerformanceMetric(
                name="system.cpu.percent",
                value=85.0,  # High CPU
                metric_type=MetricType.GAUGE
            ))
        
        await asyncio.sleep(2)  # Wait for optimization cycle
        print(f"  Workers after high load: {manager.current_workers}")
        
        print("\n✅ Performance integration demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        logger.error(f"Demo error: {e}")
    
    finally:
        # Stop system
        print("\n🛑 Stopping performance integration system...")
        await manager.stop()
        print("✅ Performance integration system stopped")

if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_performance_integration())
