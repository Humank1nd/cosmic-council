"""
Cosmic Council Refinement Engine - Monitoring Dashboard API
Provides monitoring endpoints, metrics, and health check APIs.
"""

from typing import Dict, Any, Optional, List
import json
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBearer
import structlog

try:
    from .monitoring import get_metrics_collector, get_sentry_integration
except ImportError:
    # For testing
    from monitoring import get_metrics_collector, get_sentry_integration
try:
    from .health_checks import get_health_checker, HealthStatus
    from .security import get_current_user, User, Permission, require_permission
    from .error_handling import get_error_handler
except ImportError:
    # For testing
    from health_checks import get_health_checker, HealthStatus
    from security import get_current_user, User, Permission, require_permission
    from error_handling import get_error_handler


# Initialize FastAPI app for monitoring
app = FastAPI(
    title="Cosmic Council Refinement Engine - Monitoring API",
    description="Monitoring, metrics, and health check endpoints",
    version="1.0.0"
)

# Security
security = HTTPBearer()

# Structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


# Health check endpoints
@app.get("/health", response_model=Dict[str, Any])
async def health_check():
    """
    Basic health check endpoint.
    """
    try:
        health_checker = get_health_checker()
        system_health = await health_checker.run_all_checks()
        
        return {
            "status": system_health.status.value,
            "timestamp": system_health.timestamp.isoformat(),
            "uptime_seconds": system_health.uptime_seconds,
            "version": system_health.version,
            "environment": system_health.environment,
            "checks": {
                "total": system_health.total_checks,
                "healthy": system_health.healthy_checks,
                "degraded": system_health.degraded_checks,
                "unhealthy": system_health.unhealthy_checks
            }
        }
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=500, detail="Health check failed")


@app.get("/health/detailed", response_model=Dict[str, Any])
@require_permission(Permission.VIEW_ANALYTICS)
async def detailed_health_check(current_user: User = Depends(get_current_user)):
    """
    Detailed health check with individual check results.
    """
    try:
        health_checker = get_health_checker()
        system_health = await health_checker.run_all_checks()
        
        return {
            "status": system_health.status.value,
            "timestamp": system_health.timestamp.isoformat(),
            "uptime_seconds": system_health.uptime_seconds,
            "version": system_health.version,
            "environment": system_health.environment,
            "checks": {
                "total": system_health.total_checks,
                "healthy": system_health.healthy_checks,
                "degraded": system_health.degraded_checks,
                "unhealthy": system_health.unhealthy_checks
            },
            "individual_checks": [
                {
                    "name": check.name,
                    "status": check.status.value,
                    "message": check.message,
                    "response_time_ms": check.response_time_ms,
                    "timestamp": check.timestamp.isoformat(),
                    "details": check.details,
                    "error": check.error
                }
                for check in system_health.checks
            ]
        }
        
    except Exception as e:
        logger.error("Detailed health check failed", error=str(e))
        raise HTTPException(status_code=500, detail="Detailed health check failed")


@app.get("/health/history", response_model=List[Dict[str, Any]])
@require_permission(Permission.VIEW_ANALYTICS)
async def health_check_history(current_user: User = Depends(get_current_user)):
    """
    Get health check history.
    """
    try:
        health_checker = get_health_checker()
        history = health_checker.get_health_history()
        
        return [
            {
                "status": health.status.value,
                "timestamp": health.timestamp.isoformat(),
                "uptime_seconds": health.uptime_seconds,
                "checks": {
                    "total": health.total_checks,
                    "healthy": health.healthy_checks,
                    "degraded": health.degraded_checks,
                    "unhealthy": health.unhealthy_checks
                }
            }
            for health in history
        ]
        
    except Exception as e:
        logger.error("Health check history failed", error=str(e))
        raise HTTPException(status_code=500, detail="Health check history failed")


@app.get("/health/summary", response_model=Dict[str, Any])
@require_permission(Permission.VIEW_ANALYTICS)
async def health_check_summary(current_user: User = Depends(get_current_user)):
    """
    Get health check summary with trends.
    """
    try:
        health_checker = get_health_checker()
        summary = health_checker.get_health_summary()
        
        return summary
        
    except Exception as e:
        logger.error("Health check summary failed", error=str(e))
        raise HTTPException(status_code=500, detail="Health check summary failed")


# Metrics endpoints
@app.get("/metrics")
async def prometheus_metrics():
    """
    Prometheus metrics endpoint.
    """
    try:
        metrics_collector = get_metrics_collector()
        metrics_data = metrics_collector.generate_metrics_export()
        
        return Response(
            content=metrics_data,
            media_type="text/plain; version=0.0.4; charset=utf-8"
        )
        
    except Exception as e:
        logger.error("Metrics export failed", error=str(e))
        raise HTTPException(status_code=500, detail="Metrics export failed")


@app.get("/metrics/summary", response_model=Dict[str, Any])
@require_permission(Permission.VIEW_ANALYTICS)
async def metrics_summary(current_user: User = Depends(get_current_user)):
    """
    Get metrics summary.
    """
    try:
        metrics_collector = get_metrics_collector()
        summary = metrics_collector.get_metrics_summary()
        
        return summary
        
    except Exception as e:
        logger.error("Metrics summary failed", error=str(e))
        raise HTTPException(status_code=500, detail="Metrics summary failed")


@app.get("/metrics/performance", response_model=Dict[str, Any])
@require_permission(Permission.VIEW_ANALYTICS)
async def performance_metrics(current_user: User = Depends(get_current_user)):
    """
    Get performance metrics.
    """
    try:
        metrics_collector = get_metrics_collector()
        summary = metrics_collector.get_metrics_summary()
        
        return {
            "performance": summary.get("performance_metrics", {}),
            "system": summary.get("system_metrics", {}),
            "business": summary.get("business_metrics", {})
        }
        
    except Exception as e:
        logger.error("Performance metrics failed", error=str(e))
        raise HTTPException(status_code=500, detail="Performance metrics failed")


# Error tracking endpoints
@app.get("/errors/summary", response_model=Dict[str, Any])
@require_permission(Permission.VIEW_ANALYTICS)
async def error_summary(current_user: User = Depends(get_current_user)):
    """
    Get error tracking summary.
    """
    try:
        error_handler = get_error_handler()
        analytics = error_handler.get_error_analytics()
        
        return analytics
        
    except Exception as e:
        logger.error("Error summary failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error summary failed")


@app.get("/errors/recent", response_model=List[Dict[str, Any]])
@require_permission(Permission.VIEW_ANALYTICS)
async def recent_errors(current_user: User = Depends(get_current_user)):
    """
    Get recent errors.
    """
    try:
        error_handler = get_error_handler()
        recent_errors = error_handler.error_history[-50:]  # Last 50 errors
        
        return [
            {
                "error_id": error.error_id,
                "timestamp": error.timestamp.isoformat(),
                "severity": error.severity.value,
                "category": error.category.value,
                "component": error.component,
                "operation": error.operation,
                "error_message": error.error_message,
                "is_recoverable": error.is_recoverable
            }
            for error in recent_errors
        ]
        
    except Exception as e:
        logger.error("Recent errors failed", error=str(e))
        raise HTTPException(status_code=500, detail="Recent errors failed")


# System information endpoints
@app.get("/system/info", response_model=Dict[str, Any])
@require_permission(Permission.VIEW_ANALYTICS)
async def system_info(current_user: User = Depends(get_current_user)):
    """
    Get system information.
    """
    try:
        import psutil
        import platform
        
        return {
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor()
            },
            "python": {
                "version": platform.python_version(),
                "implementation": platform.python_implementation()
            },
            "process": {
                "pid": psutil.Process().pid,
                "create_time": datetime.fromtimestamp(psutil.Process().create_time()).isoformat(),
                "memory_info": {
                    "rss_mb": psutil.Process().memory_info().rss / 1024 / 1024,
                    "vms_mb": psutil.Process().memory_info().vms / 1024 / 1024
                },
                "cpu_percent": psutil.Process().cpu_percent()
            },
            "system": {
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": psutil.virtual_memory().total / (1024**3),
                "disk_total_gb": psutil.disk_usage('/').total / (1024**3)
            }
        }
        
    except Exception as e:
        logger.error("System info failed", error=str(e))
        raise HTTPException(status_code=500, detail="System info failed")


@app.get("/system/resources", response_model=Dict[str, Any])
@require_permission(Permission.VIEW_ANALYTICS)
async def system_resources(current_user: User = Depends(get_current_user)):
    """
    Get current system resource usage.
    """
    try:
        import psutil
        
        return {
            "cpu": {
                "percent": psutil.cpu_percent(interval=1),
                "count": psutil.cpu_count(),
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
            },
            "memory": {
                "total_gb": psutil.virtual_memory().total / (1024**3),
                "available_gb": psutil.virtual_memory().available / (1024**3),
                "used_gb": psutil.virtual_memory().used / (1024**3),
                "percent": psutil.virtual_memory().percent
            },
            "disk": {
                "total_gb": psutil.disk_usage('/').total / (1024**3),
                "free_gb": psutil.disk_usage('/').free / (1024**3),
                "used_gb": psutil.disk_usage('/').used / (1024**3),
                "percent": (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100
            },
            "network": {
                "connections": len(psutil.net_connections()),
                "interfaces": list(psutil.net_if_addrs().keys())
            }
        }
        
    except Exception as e:
        logger.error("System resources failed", error=str(e))
        raise HTTPException(status_code=500, detail="System resources failed")


# Monitoring dashboard
@app.get("/dashboard", response_class=HTMLResponse)
@require_permission(Permission.VIEW_ANALYTICS)
async def monitoring_dashboard(current_user: User = Depends(get_current_user)):
    """
    Monitoring dashboard HTML page.
    """
    try:
        # Get current health status
        health_checker = get_health_checker()
        system_health = await health_checker.run_all_checks()
        
        # Get metrics summary
        metrics_collector = get_metrics_collector()
        metrics_summary = metrics_collector.get_metrics_summary()
        
        # Generate HTML dashboard
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Cosmic Council Refinement Engine - Monitoring Dashboard</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                .header {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    margin-bottom: 20px;
                }}
                .status {{
                    display: inline-block;
                    padding: 4px 12px;
                    border-radius: 20px;
                    font-weight: bold;
                    text-transform: uppercase;
                    font-size: 12px;
                }}
                .status.healthy {{
                    background-color: #d4edda;
                    color: #155724;
                }}
                .status.degraded {{
                    background-color: #fff3cd;
                    color: #856404;
                }}
                .status.unhealthy {{
                    background-color: #f8d7da;
                    color: #721c24;
                }}
                .grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                }}
                .card {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .card h3 {{
                    margin-top: 0;
                    color: #333;
                }}
                .metric {{
                    display: flex;
                    justify-content: space-between;
                    margin: 10px 0;
                    padding: 10px 0;
                    border-bottom: 1px solid #eee;
                }}
                .metric:last-child {{
                    border-bottom: none;
                }}
                .metric-label {{
                    font-weight: 500;
                    color: #666;
                }}
                .metric-value {{
                    font-weight: bold;
                    color: #333;
                }}
                .refresh-btn {{
                    background: #007bff;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 14px;
                }}
                .refresh-btn:hover {{
                    background: #0056b3;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Cosmic Council Refinement Engine</h1>
                    <h2>Monitoring Dashboard</h2>
                    <p>Status: <span class="status {system_health.status.value}">{system_health.status.value}</span></p>
                    <p>Uptime: {system_health.uptime_seconds:.0f} seconds</p>
                    <p>Last Updated: {system_health.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <button class="refresh-btn" onclick="location.reload()">Refresh</button>
                </div>
                
                <div class="grid">
                    <div class="card">
                        <h3>Health Checks</h3>
                        <div class="metric">
                            <span class="metric-label">Total Checks</span>
                            <span class="metric-value">{system_health.total_checks}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Healthy</span>
                            <span class="metric-value" style="color: #28a745;">{system_health.healthy_checks}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Degraded</span>
                            <span class="metric-value" style="color: #ffc107;">{system_health.degraded_checks}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Unhealthy</span>
                            <span class="metric-value" style="color: #dc3545;">{system_health.unhealthy_checks}</span>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h3>Performance Metrics</h3>
                        <div class="metric">
                            <span class="metric-label">Total Requests</span>
                            <span class="metric-value">{metrics_summary.get('performance_metrics', {}).get('total_requests', 0)}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Avg Response Time</span>
                            <span class="metric-value">{metrics_summary.get('performance_metrics', {}).get('average_response_time', 0):.2f}ms</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Error Rate</span>
                            <span class="metric-value">{metrics_summary.get('performance_metrics', {}).get('error_rate', 0):.2f}%</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">P95 Response Time</span>
                            <span class="metric-value">{metrics_summary.get('performance_metrics', {}).get('p95_response_time', 0):.2f}ms</span>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h3>System Resources</h3>
                        <div class="metric">
                            <span class="metric-label">CPU Usage</span>
                            <span class="metric-value">{metrics_summary.get('system_metrics', {}).get('cpu_percent', 0):.1f}%</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Memory Usage</span>
                            <span class="metric-value">{metrics_summary.get('system_metrics', {}).get('memory_percent', 0):.1f}%</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Disk Usage</span>
                            <span class="metric-value">{metrics_summary.get('system_metrics', {}).get('disk_percent', 0):.1f}%</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Active Connections</span>
                            <span class="metric-value">{metrics_summary.get('system_metrics', {}).get('active_connections', 0)}</span>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h3>Business Metrics</h3>
                        <div class="metric">
                            <span class="metric-label">Active Problems</span>
                            <span class="metric-value">{metrics_summary.get('business_metrics', {}).get('active_problems', 0)}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Problems/Hour</span>
                            <span class="metric-value">{metrics_summary.get('business_metrics', {}).get('problems_per_hour', 0):.1f}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Avg Resolution Time</span>
                            <span class="metric-value">{metrics_summary.get('business_metrics', {}).get('average_resolution_time', 0):.1f}s</span>
                        </div>
                    </div>
                </div>
                
                <div class="card" style="margin-top: 20px;">
                    <h3>Individual Health Checks</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="background-color: #f8f9fa;">
                                <th style="padding: 10px; text-align: left; border-bottom: 1px solid #dee2e6;">Check</th>
                                <th style="padding: 10px; text-align: left; border-bottom: 1px solid #dee2e6;">Status</th>
                                <th style="padding: 10px; text-align: left; border-bottom: 1px solid #dee2e6;">Response Time</th>
                                <th style="padding: 10px; text-align: left; border-bottom: 1px solid #dee2e6;">Message</th>
                            </tr>
                        </thead>
                        <tbody>
        """
        
        for check in system_health.checks:
            html_content += f"""
                            <tr>
                                <td style="padding: 10px; border-bottom: 1px solid #dee2e6;">{check.name}</td>
                                <td style="padding: 10px; border-bottom: 1px solid #dee2e6;">
                                    <span class="status {check.status.value}">{check.status.value}</span>
                                </td>
                                <td style="padding: 10px; border-bottom: 1px solid #dee2e6;">{check.response_time_ms:.2f}ms</td>
                                <td style="padding: 10px; border-bottom: 1px solid #dee2e6;">{check.message}</td>
                            </tr>
            """
        
        html_content += """
                        </tbody>
                    </table>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error("Dashboard failed", error=str(e))
        raise HTTPException(status_code=500, detail="Dashboard failed")


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize monitoring on startup."""
    logger.info("Cosmic Council Refinement Engine Monitoring API started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Cosmic Council Refinement Engine Monitoring API shutting down")


# Example usage and testing
if __name__ == "__main__":
    import uvicorn
    
    # Run the monitoring API server
    uvicorn.run(
        "refinement_engine.monitoring_api:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
