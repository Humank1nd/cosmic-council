"""
Cosmic Council Caching Layer
Redis-based caching for performance optimization.
"""

import json
import logging
import hashlib
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import asyncio

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from .config import get_config

logger = logging.getLogger(__name__)


class CacheService:
    """Redis-based caching service for performance optimization."""
    
    def __init__(self):
        """Initialize the cache service."""
        self.config = get_config()
        self.redis_client: Optional[redis.Redis] = None
        self.enabled = self.config.performance.enable_caching and REDIS_AVAILABLE
        
        if self.enabled:
            self._initialize_redis()
        else:
            logger.warning("Caching disabled or Redis not available")
    
    def _initialize_redis(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.Redis(
                host='localhost',
                port=6379,
                db=0,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            logger.info("✅ Redis cache service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            self.enabled = False
            self.redis_client = None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        if not self.enabled or not self.redis_client:
            return None
        
        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set a value in cache with optional TTL."""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            if ttl is None:
                ttl = self.config.performance.cache_ttl_seconds
            
            serialized_value = json.dumps(value, default=str)
            await self.redis_client.setex(key, ttl, serialized_value)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            return await self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    def generate_key(self, prefix: str, *args) -> str:
        """Generate a cache key from prefix and arguments."""
        key_data = f"{prefix}:{':'.join(str(arg) for arg in args)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get_or_set(self, key: str, factory_func, ttl: int = None, *args, **kwargs) -> Any:
        """Get from cache or set using factory function."""
        # Try to get from cache first
        cached_value = await self.get(key)
        if cached_value is not None:
            logger.debug(f"Cache hit for key: {key}")
            return cached_value
        
        # Generate new value using factory function
        logger.debug(f"Cache miss for key: {key}, generating new value")
        try:
            if asyncio.iscoroutinefunction(factory_func):
                new_value = await factory_func(*args, **kwargs)
            else:
                new_value = factory_func(*args, **kwargs)
            
            # Cache the new value
            await self.set(key, new_value, ttl)
            return new_value
        except Exception as e:
            logger.error(f"Error in get_or_set for key {key}: {e}")
            raise
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching a pattern."""
        if not self.enabled or not self.redis_client:
            return 0
        
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                return await self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache pattern invalidation error for {pattern}: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self.enabled or not self.redis_client:
            return {"enabled": False}
        
        try:
            info = await self.redis_client.info()
            return {
                "enabled": True,
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "0B"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(info)
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"enabled": False, "error": str(e)}
    
    def _calculate_hit_rate(self, info: Dict) -> float:
        """Calculate cache hit rate."""
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0.0
    
    async def close(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis connection closed")


# Cache decorators
def cache_result(ttl: int = None, key_prefix: str = "result"):
    """Decorator to cache function results."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            cache = CacheService()
            
            # Generate cache key
            key = cache.generate_key(key_prefix, func.__name__, str(args), str(sorted(kwargs.items())))
            
            # Try to get from cache
            cached_result = await cache.get(key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            await cache.set(key, result, ttl)
            logger.debug(f"Cached result for {func.__name__}")
            return result
        
        return wrapper
    return decorator


def cache_ai_response(ttl: int = 3600):
    """Cache AI responses to avoid duplicate API calls."""
    return cache_result(ttl=ttl, key_prefix="ai_response")


def cache_research_results(ttl: int = 1800):
    """Cache research results."""
    return cache_result(ttl=ttl, key_prefix="research")


# Global cache instance
_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """Get the global cache service instance."""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service


async def close_cache_service():
    """Close the global cache service."""
    global _cache_service
    if _cache_service:
        await _cache_service.close()
        _cache_service = None
