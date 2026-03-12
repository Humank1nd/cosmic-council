"""
Visual Identity API Endpoints
Provides endpoints for Agent Orchestrator visual identity, colors, shapes, and symbols
"""

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from .cosmic_identity import CosmicCouncilIdentity
from ..core.core import EnterpriseType

router = APIRouter(prefix="/api/v1/cosmic", tags=["Agent Orchestrator Identity"])

security = HTTPBearer()

# Cache for static visual identity data
_identity_cache: Optional[Dict[str, Any]] = None
_hexagon_cache: Optional[Dict[str, Any]] = None
_colors_cache: Optional[Dict[str, Any]] = None
_animals_cache: Optional[Dict[str, Any]] = None
_enterprise_visual_cache: Dict[str, Dict[str, Any]] = {}

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Get current user from authorization token"""
    return credentials.credentials if credentials else "demo_user"


@router.get("/identity", summary="Get complete Agent Orchestrator visual identity")
async def get_complete_identity(current_user: str = Depends(get_current_user)):
    """Get the complete visual identity system including colors, animals, shapes, and structure"""
    global _identity_cache
    
    if _identity_cache is None:
        _identity_cache = {
            "success": True,
            "message": "Agent Orchestrator visual identity",
            "data": CosmicCouncilIdentity.get_complete_identity(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    # Update timestamp only
    response = _identity_cache.copy()
    response["timestamp"] = datetime.now(timezone.utc).isoformat()
    return response


@router.get("/hexagon", summary="Get hexagonal structure information")
async def get_hexagon_structure(current_user: str = Depends(get_current_user)):
    """Get information about the hexagonal structure and layout"""
    global _hexagon_cache
    
    if _hexagon_cache is None:
        _hexagon_cache = {
            "success": True,
            "message": "Hexagonal structure information",
            "data": CosmicCouncilIdentity.get_hexagon_structure(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    # Update timestamp only
    response = _hexagon_cache.copy()
    response["timestamp"] = datetime.now(timezone.utc).isoformat()
    return response


@router.get("/colors", summary="Get color palette")
async def get_color_palette(current_user: str = Depends(get_current_user)):
    """Get the complete color palette for all enterprises"""
    global _colors_cache
    
    if _colors_cache is None:
        _colors_cache = {
            "success": True,
            "message": "Agent Orchestrator color palette",
            "data": CosmicCouncilIdentity.get_color_palette(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    # Update timestamp only
    response = _colors_cache.copy()
    response["timestamp"] = datetime.now(timezone.utc).isoformat()
    return response


@router.get("/animals", summary="Get animal symbols")
async def get_animal_symbols(current_user: str = Depends(get_current_user)):
    """Get all animal symbols and their meanings"""
    global _animals_cache
    
    if _animals_cache is None:
        _animals_cache = {
            "success": True,
            "message": "Animal symbols and meanings",
            "data": CosmicCouncilIdentity.get_animal_symbols(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    # Update timestamp only
    response = _animals_cache.copy()
    response["timestamp"] = datetime.now(timezone.utc).isoformat()
    return response


@router.get("/supra_enterprise/{enterprise}/visual", summary="Get visual identity for specific enterprise")
async def get_enterprise_visual(
    enterprise: str,
    current_user: str = Depends(get_current_user)
):
    """Get complete visual identity for a specific enterprise"""
    global _enterprise_visual_cache
    
    try:
        enterprise_key = enterprise.lower()
        
        # Check cache first
        if enterprise_key in _enterprise_visual_cache:
            response = _enterprise_visual_cache[enterprise_key].copy()
            response["timestamp"] = datetime.now(timezone.utc).isoformat()
            return response
        
        enterprise_type = EnterpriseType(enterprise_key)
        identity = CosmicCouncilIdentity.get_enterprise_identity(enterprise_type)
        
        if not identity:
            return {
                "success": False,
                "message": f"Visual identity not found for {enterprise}",
                "data": None
            }
        
        response = {
            "success": True,
            "message": f"Visual identity for {identity.name}",
            "data": {
                "enterprise": enterprise_type.value,
                "name": identity.name,
                "animal": identity.animal,
                "animal_emoji": identity.animal_emoji,
                "symbol": identity.symbol,
                "color": {
                    "name": identity.color_name,
                    "hex": identity.color_hex,
                    "rgb": list(identity.color_rgb)
                },
                "core_principle": identity.core_principle,
                "role": identity.role,
                "position": {
                    "number": identity.position,
                    "location": identity.shape,
                    "angle": identity.position * 60
                }
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Cache the response
        _enterprise_visual_cache[enterprise_key] = response.copy()
        
        return response
    except ValueError:
        return {
            "success": False,
            "message": f"Invalid enterprise: {enterprise}",
            "data": None
        }

