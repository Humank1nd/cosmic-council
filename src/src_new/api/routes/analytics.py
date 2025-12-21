"""
Analytics API routes.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, Any, Optional
import logging

from ...core.services.analytics_service import AnalyticsService
from ..main import get_analytics_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/system", response_model=Dict[str, Any])
async def get_system_metrics(
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Get overall system metrics"""
    try:
        metrics = await analytics_service.get_system_metrics()
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/problems/{problem_id}", response_model=Dict[str, Any])
async def get_problem_analytics(
    problem_id: str,
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Get analytics for a specific problem"""
    try:
        analytics = await analytics_service.get_problem_analytics(problem_id)
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting problem analytics: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/supra_enterprise/{enterprise_type}", response_model=Dict[str, Any])
async def get_enterprise_performance(
    enterprise_type: str,
    days: int = 30,
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Get performance metrics for a specific enterprise"""
    try:
        performance = await analytics_service.get_enterprise_performance(enterprise_type, days)
        return performance
        
    except Exception as e:
        logger.error(f"Error getting enterprise performance: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/cycles/{cycle_id}", response_model=Dict[str, Any])
async def get_cycle_analytics(
    cycle_id: str,
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Get detailed analytics for a specific cycle"""
    try:
        analytics = await analytics_service.get_cycle_analytics(cycle_id)
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting cycle analytics: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/trends", response_model=Dict[str, Any])
async def get_performance_trends(
    days: int = 30,
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Get performance trends over time"""
    try:
        trends = await analytics_service.get_performance_trends(days)
        return trends
        
    except Exception as e:
        logger.error(f"Error getting performance trends: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
