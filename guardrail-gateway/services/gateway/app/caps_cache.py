"""
Budget Caps Cache Service
Provides fast access to budget caps for policy evaluation
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
from .storage import engine
from sqlalchemy import text

class BudgetCapsCache:
    """
    Cached budget caps service for fast policy evaluation
    """
    
    def __init__(self):
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes
        self._last_refresh = None
    
    async def get_budget_caps(self, enterprise: Optional[str] = None, 
                            resource_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get budget caps, optionally filtered by enterprise and resource type
        """
        # Check if cache needs refresh
        if self._should_refresh_cache():
            await self._refresh_cache()
        
        # Filter cache based on parameters
        filtered_caps = self._cache.copy()
        
        if enterprise:
            filtered_caps = {k: v for k, v in filtered_caps.items() 
                           if v.get('enterprise') == enterprise}
        
        if resource_type:
            filtered_caps = {k: v for k, v in filtered_caps.items() 
                           if v.get('resource_type') == resource_type}
        
        return {
            'caps': list(filtered_caps.values()),
            'cache_timestamp': self._last_refresh.isoformat() if self._last_refresh else None,
            'total_caps': len(filtered_caps)
        }
    
    async def get_cap_for_enterprise_resource(self, enterprise: str, 
                                            resource_type: str) -> Optional[Dict[str, Any]]:
        """
        Get specific budget cap for enterprise + resource type combination
        """
        if self._should_refresh_cache():
            await self._refresh_cache()
        
        cache_key = f"{enterprise}:{resource_type}"
        return self._cache.get(cache_key)
    
    def _should_refresh_cache(self) -> bool:
        """Check if cache needs refresh based on TTL"""
        if not self._last_refresh:
            return True
        
        return (datetime.now(timezone.utc) - self._last_refresh).total_seconds() > self._cache_ttl
    
    async def _refresh_cache(self):
        """Refresh cache from database"""
        try:
            e = engine()
            with e.begin() as conn:
                result = conn.execute(text("""
                    SELECT 
                        enterprise,
                        resource_type,
                        budget_cap,
                        currency,
                        period,
                        effective_from,
                        effective_until,
                        metadata
                    FROM budget_caps_cache
                    ORDER BY enterprise, resource_type, effective_from DESC
                """))
                
                self._cache = {}
                for row in result:
                    cache_key = f"{row[0]}:{row[1]}"
                    self._cache[cache_key] = {
                        'enterprise': row[0],
                        'resource_type': row[1],
                        'budget_cap': float(row[2]),
                        'currency': row[3],
                        'period': row[4],
                        'effective_from': row[5].isoformat() if row[5] else None,
                        'effective_until': row[6].isoformat() if row[6] else None,
                        'metadata': row[7] or {}
                    }
                
                self._last_refresh = datetime.now(timezone.utc)
                
        except Exception as e:
            print(f"Failed to refresh budget caps cache: {e}")
            # Keep existing cache if refresh fails
    
    async def update_cap(self, enterprise: str, resource_type: str, 
                        new_cap: float, period: str = 'monthly') -> bool:
        """
        Update a budget cap (admin function)
        """
        try:
            e = engine()
            with e.begin() as conn:
                # End current cap
                conn.execute(text("""
                    UPDATE finance_budget_caps 
                    SET effective_until = now()
                    WHERE enterprise = :enterprise 
                      AND resource_type = :resource_type
                      AND effective_until IS NULL
                """), {
                    'enterprise': enterprise,
                    'resource_type': resource_type
                })
                
                # Insert new cap
                conn.execute(text("""
                    INSERT INTO finance_budget_caps 
                    (enterprise, resource_type, budget_cap, period, effective_from)
                    VALUES (:enterprise, :resource_type, :budget_cap, :period, now())
                """), {
                    'enterprise': enterprise,
                    'resource_type': resource_type,
                    'budget_cap': new_cap,
                    'period': period
                })
                
                # Force cache refresh
                self._last_refresh = None
                await self._refresh_cache()
                
                return True
                
        except Exception as e:
            print(f"Failed to update budget cap: {e}")
            return False

# Global instance
budget_caps_cache = BudgetCapsCache()
