"""
Health check API routes.
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=Dict[str, Any])
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "cosmic-council-api",
        "version": "2.0.0"
    }


@router.get("/ready", response_model=Dict[str, Any])
async def readiness_check():
    """Readiness check endpoint"""
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "cosmic-council-api",
        "version": "2.0.0"
    }


@router.get("/live", response_model=Dict[str, Any])
async def liveness_check():
    """Liveness check endpoint"""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "cosmic-council-api",
        "version": "2.0.0"
    }
