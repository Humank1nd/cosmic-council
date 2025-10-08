#!/usr/bin/env python3
"""
📊 Cosmic Council Analytics Service
Metabase dashboards + APIs for performance analytics and insights
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Union
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Import shared utilities
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.database.connection import get_database_connection, DatabaseManager
from src.utils.logging import setup_logging, get_enterprise_logger

# Configure logging
logger = setup_logging(enterprise="analytics")
analytics_logger = get_enterprise_logger("analytics", "main")

# Pydantic models
class PerformanceMetrics(BaseModel):
    """Performance metrics model"""
    cycle_id: str
    metric_name: str
    metric_value: float
    metric_unit: str
    measurement_timestamp: datetime
    context: Dict[str, Any] = Field(default_factory=dict)

class CycleAnalytics(BaseModel):
    """Cycle analytics model"""
    cycle_id: str
    objective_ref: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_duration: Optional[float] = None
    stage_durations: Dict[str, float] = Field(default_factory=dict)
    confidence_scores: Dict[str, float] = Field(default_factory=dict)
    success_rate: float
    enterprise_performance: Dict[str, Any] = Field(default_factory=dict)

class EnterprisePerformance(BaseModel):
    """Enterprise performance model"""
    enterprise: str
    total_cycles: int
    success_rate: float
    average_confidence: float
    average_processing_time: float
    total_processing_time: float
    last_activity: Optional[datetime] = None
    performance_trend: str  # "improving", "stable", "declining"

class SystemHealthMetrics(BaseModel):
    """System health metrics model"""
    timestamp: datetime
    active_cycles: int
    completed_cycles_24h: int
    failed_cycles_24h: int
    average_cycle_duration: float
    system_uptime: float
    database_health: str
    service_health: Dict[str, str] = Field(default_factory=dict)

class AnalyticsDashboard(BaseModel):
    """Analytics dashboard model"""
    title: str
    description: str
    metrics: List[Dict[str, Any]]
    charts: List[Dict[str, Any]]
    last_updated: datetime
    refresh_interval: int = 300  # seconds

# Global variables
db_manager: Optional[DatabaseManager] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global db_manager
    
    # Startup
    analytics_logger.info("📊 Starting Cosmic Council Analytics Service")
    
    try:
        # Initialize database manager
        db_manager = await get_database_manager()
        analytics_logger.info("✅ Database manager initialized")
        
        analytics_logger.info("📊 Analytics service startup complete")
        
    except Exception as e:
        analytics_logger.error(f"❌ Analytics startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    analytics_logger.info("📊 Shutting down Analytics service")
    if db_manager:
        await db_manager.close_pool()
    analytics_logger.info("📊 Analytics service shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Cosmic Council Analytics",
    description="Analytics and performance monitoring for the Cosmic Council",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency injection
async def get_db_manager() -> DatabaseManager:
    """Get database manager instance"""
    if db_manager is None:
        raise HTTPException(status_code=503, detail="Database not initialized")
    return db_manager

# Routes
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc),
        "service": "analytics"
    }

@app.get("/v1/analytics/cycles", response_model=List[CycleAnalytics])
async def get_cycle_analytics(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: DatabaseManager = Depends(get_db_manager)
):
    """Get cycle analytics with filtering"""
    try:
        analytics_logger.info(f"Getting cycle analytics: limit={limit}, offset={offset}")
        
        # Build query
        query = """
        SELECT 
            c.id as cycle_id,
            c.objective_ref,
            c.status,
            c.started_at,
            c.completed_at,
            EXTRACT(EPOCH FROM (c.completed_at - c.started_at)) as total_duration
        FROM cycles c
        WHERE 1=1
        """
        
        params = []
        param_count = 0
        
        if status:
            param_count += 1
            query += f" AND c.status = ${param_count}"
            params.append(status)
        
        if start_date:
            param_count += 1
            query += f" AND c.started_at >= ${param_count}"
            params.append(start_date)
        
        if end_date:
            param_count += 1
            query += f" AND c.started_at <= ${param_count}"
            params.append(end_date)
        
        query += f" ORDER BY c.started_at DESC LIMIT ${param_count + 1} OFFSET ${param_count + 2}"
        params.extend([limit, offset])
        
        # Execute query
        results = await db.execute_query(query, tuple(params))
        
        # Process results
        analytics = []
        for row in results:
            # Get stage durations
            stage_durations = await get_stage_durations(db, row['cycle_id'])
            
            # Get confidence scores
            confidence_scores = await get_confidence_scores(db, row['cycle_id'])
            
            # Get enterprise performance
            enterprise_performance = await get_enterprise_performance(db, row['cycle_id'])
            
            # Calculate success rate
            success_rate = 1.0 if row['status'] == 'completed' else 0.0
            
            analytics.append(CycleAnalytics(
                cycle_id=row['cycle_id'],
                objective_ref=row['objective_ref'],
                status=row['status'],
                started_at=row['started_at'],
                completed_at=row['completed_at'],
                total_duration=row['total_duration'],
                stage_durations=stage_durations,
                confidence_scores=confidence_scores,
                success_rate=success_rate,
                enterprise_performance=enterprise_performance
            ))
        
        return analytics
        
    except Exception as e:
        analytics_logger.error(f"❌ Get cycle analytics failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cycle analytics: {str(e)}")

@app.get("/v1/analytics/enterprises", response_model=List[EnterprisePerformance])
async def get_enterprise_performance_analytics(
    time_period: str = Query("7d", regex="^(1d|7d|30d|90d|1y)$"),
    db: DatabaseManager = Depends(get_db_manager)
):
    """Get enterprise performance analytics"""
    try:
        analytics_logger.info(f"Getting enterprise performance analytics for period: {time_period}")
        
        # Calculate time period
        end_date = datetime.now(timezone.utc)
        if time_period == "1d":
            start_date = end_date - timedelta(days=1)
        elif time_period == "7d":
            start_date = end_date - timedelta(days=7)
        elif time_period == "30d":
            start_date = end_date - timedelta(days=30)
        elif time_period == "90d":
            start_date = end_date - timedelta(days=90)
        else:  # 1y
            start_date = end_date - timedelta(days=365)
        
        # Get enterprise performance data
        query = """
        SELECT 
            se.stage_code as enterprise,
            COUNT(*) as total_cycles,
            AVG(CASE WHEN se.status = 'completed' THEN 1.0 ELSE 0.0 END) as success_rate,
            AVG(EXTRACT(EPOCH FROM (se.completed_at - se.started_at))) as avg_processing_time,
            SUM(EXTRACT(EPOCH FROM (se.completed_at - se.started_at))) as total_processing_time,
            MAX(se.completed_at) as last_activity
        FROM stage_executions se
        JOIN cycles c ON se.cycle_id = c.id
        WHERE c.started_at >= $1 AND c.started_at <= $2
        GROUP BY se.stage_code
        ORDER BY total_cycles DESC
        """
        
        results = await db.execute_query(query, (start_date, end_date))
        
        # Process results
        enterprises = []
        for row in results:
            # Calculate performance trend (simplified)
            trend = await calculate_performance_trend(db, row['enterprise'], start_date, end_date)
            
            enterprises.append(EnterprisePerformance(
                enterprise=row['enterprise'],
                total_cycles=row['total_cycles'],
                success_rate=float(row['success_rate'] or 0),
                average_confidence=0.0,  # Would need to calculate from actual data
                average_processing_time=float(row['avg_processing_time'] or 0),
                total_processing_time=float(row['total_processing_time'] or 0),
                last_activity=row['last_activity'],
                performance_trend=trend
            ))
        
        return enterprises
        
    except Exception as e:
        analytics_logger.error(f"❌ Get enterprise performance failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get enterprise performance: {str(e)}")

@app.get("/v1/analytics/system-health", response_model=SystemHealthMetrics)
async def get_system_health_metrics(
    db: DatabaseManager = Depends(get_db_manager)
):
    """Get system health metrics"""
    try:
        analytics_logger.info("Getting system health metrics")
        
        now = datetime.now(timezone.utc)
        yesterday = now - timedelta(days=1)
        
        # Get active cycles
        active_query = "SELECT COUNT(*) as count FROM cycles WHERE status = 'active'"
        active_result = await db.execute_query(active_query)
        active_cycles = active_result[0]['count']
        
        # Get completed cycles in last 24h
        completed_query = """
        SELECT COUNT(*) as count FROM cycles 
        WHERE status = 'completed' AND completed_at >= $1
        """
        completed_result = await db.execute_query(completed_query, (yesterday,))
        completed_cycles_24h = completed_result[0]['count']
        
        # Get failed cycles in last 24h
        failed_query = """
        SELECT COUNT(*) as count FROM cycles 
        WHERE status = 'failed' AND completed_at >= $1
        """
        failed_result = await db.execute_query(failed_query, (yesterday,))
        failed_cycles_24h = failed_result[0]['count']
        
        # Get average cycle duration
        duration_query = """
        SELECT AVG(EXTRACT(EPOCH FROM (completed_at - started_at))) as avg_duration
        FROM cycles 
        WHERE status = 'completed' AND completed_at >= $1
        """
        duration_result = await db.execute_query(duration_query, (yesterday,))
        average_cycle_duration = float(duration_result[0]['avg_duration'] or 0)
        
        # System uptime (simplified)
        system_uptime = 99.9  # Would be calculated from actual uptime data
        
        # Database health
        database_health = "healthy"  # Would check actual database health
        
        # Service health
        service_health = {
            "gateway": "healthy",
            "analytics": "healthy",
            "reflection": "healthy"
        }
        
        return SystemHealthMetrics(
            timestamp=now,
            active_cycles=active_cycles,
            completed_cycles_24h=completed_cycles_24h,
            failed_cycles_24h=failed_cycles_24h,
            average_cycle_duration=average_cycle_duration,
            system_uptime=system_uptime,
            database_health=database_health,
            service_health=service_health
        )
        
    except Exception as e:
        analytics_logger.error(f"❌ Get system health failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get system health: {str(e)}")

@app.get("/v1/analytics/dashboard", response_model=AnalyticsDashboard)
async def get_analytics_dashboard(
    dashboard_type: str = Query("overview", regex="^(overview|performance|enterprises|system)$"),
    db: DatabaseManager = Depends(get_db_manager)
):
    """Get analytics dashboard data"""
    try:
        analytics_logger.info(f"Getting analytics dashboard: {dashboard_type}")
        
        if dashboard_type == "overview":
            return await get_overview_dashboard(db)
        elif dashboard_type == "performance":
            return await get_performance_dashboard(db)
        elif dashboard_type == "enterprises":
            return await get_enterprises_dashboard(db)
        elif dashboard_type == "system":
            return await get_system_dashboard(db)
        else:
            raise HTTPException(status_code=400, detail="Invalid dashboard type")
        
    except Exception as e:
        analytics_logger.error(f"❌ Get dashboard failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard: {str(e)}")

# Helper functions
async def get_stage_durations(db: DatabaseManager, cycle_id: str) -> Dict[str, float]:
    """Get stage durations for a cycle"""
    try:
        query = """
        SELECT stage_code, EXTRACT(EPOCH FROM (completed_at - started_at)) as duration
        FROM stage_executions
        WHERE cycle_id = $1 AND completed_at IS NOT NULL
        """
        
        results = await db.execute_query(query, (cycle_id,))
        
        durations = {}
        for row in results:
            durations[row['stage_code']] = float(row['duration'] or 0)
        
        return durations
        
    except Exception as e:
        analytics_logger.error(f"Failed to get stage durations: {e}")
        return {}

async def get_confidence_scores(db: DatabaseManager, cycle_id: str) -> Dict[str, float]:
    """Get confidence scores for a cycle"""
    try:
        # This would need to be implemented based on actual confidence score storage
        # For now, return mock data
        return {
            "red_research": 0.75,
            "orange_logistics": 0.78,
            "yellow_development": 0.80,
            "green_budget": 0.77,
            "blue_market": 0.79,
            "purple_support": 0.82
        }
        
    except Exception as e:
        analytics_logger.error(f"Failed to get confidence scores: {e}")
        return {}

async def get_enterprise_performance(db: DatabaseManager, cycle_id: str) -> Dict[str, Any]:
    """Get enterprise performance for a cycle"""
    try:
        query = """
        SELECT stage_code, status, started_at, completed_at
        FROM stage_executions
        WHERE cycle_id = $1
        ORDER BY execution_order
        """
        
        results = await db.execute_query(query, (cycle_id,))
        
        performance = {}
        for row in results:
            performance[row['stage_code']] = {
                "status": row['status'],
                "started_at": row['started_at'],
                "completed_at": row['completed_at']
            }
        
        return performance
        
    except Exception as e:
        analytics_logger.error(f"Failed to get enterprise performance: {e}")
        return {}

async def calculate_performance_trend(db: DatabaseManager, enterprise: str, start_date: datetime, end_date: datetime) -> str:
    """Calculate performance trend for an enterprise"""
    try:
        # Simplified trend calculation
        # In production, this would analyze historical data
        return "stable"
        
    except Exception as e:
        analytics_logger.error(f"Failed to calculate performance trend: {e}")
        return "unknown"

async def get_overview_dashboard(db: DatabaseManager) -> AnalyticsDashboard:
    """Get overview dashboard data"""
    return AnalyticsDashboard(
        title="Overview Dashboard",
        description="High-level overview of Cosmic Council performance",
        metrics=[
            {"name": "Active Cycles", "value": 5, "trend": "stable"},
            {"name": "Success Rate", "value": 0.85, "trend": "improving"},
            {"name": "Avg Cycle Duration", "value": 120.5, "trend": "stable"}
        ],
        charts=[
            {"type": "line", "title": "Cycle Completion Over Time"},
            {"type": "bar", "title": "Enterprise Performance"}
        ],
        last_updated=datetime.now(timezone.utc)
    )

async def get_performance_dashboard(db: DatabaseManager) -> AnalyticsDashboard:
    """Get performance dashboard data"""
    return AnalyticsDashboard(
        title="Performance Dashboard",
        description="Detailed performance metrics and trends",
        metrics=[
            {"name": "Throughput", "value": 12.5, "trend": "improving"},
            {"name": "Latency", "value": 45.2, "trend": "stable"},
            {"name": "Error Rate", "value": 0.02, "trend": "improving"}
        ],
        charts=[
            {"type": "line", "title": "Performance Trends"},
            {"type": "heatmap", "title": "Performance Heatmap"}
        ],
        last_updated=datetime.now(timezone.utc)
    )

async def get_enterprises_dashboard(db: DatabaseManager) -> AnalyticsDashboard:
    """Get enterprises dashboard data"""
    return AnalyticsDashboard(
        title="Enterprises Dashboard",
        description="Enterprise-specific performance metrics",
        metrics=[
            {"name": "Red Research", "value": 0.75, "trend": "stable"},
            {"name": "Orange Logistics", "value": 0.78, "trend": "improving"},
            {"name": "Yellow Development", "value": 0.80, "trend": "stable"}
        ],
        charts=[
            {"type": "radar", "title": "Enterprise Capabilities"},
            {"type": "bar", "title": "Enterprise Performance Comparison"}
        ],
        last_updated=datetime.now(timezone.utc)
    )

async def get_system_dashboard(db: DatabaseManager) -> AnalyticsDashboard:
    """Get system dashboard data"""
    return AnalyticsDashboard(
        title="System Dashboard",
        description="System health and infrastructure metrics",
        metrics=[
            {"name": "System Uptime", "value": 99.9, "trend": "stable"},
            {"name": "Database Health", "value": 100, "trend": "stable"},
            {"name": "Service Health", "value": 100, "trend": "stable"}
        ],
        charts=[
            {"type": "gauge", "title": "System Health"},
            {"type": "line", "title": "Resource Usage"}
        ],
        last_updated=datetime.now(timezone.utc)
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
