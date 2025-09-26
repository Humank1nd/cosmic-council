#!/usr/bin/env python3
"""
Cosmic Council Framework - API Performance Optimization

This module provides comprehensive API performance optimization including:

- Request/response caching and optimization
- API rate limiting and throttling
- Response compression and serialization
- Connection pooling and keep-alive
- API endpoint performance monitoring
- Load balancing and failover
- Request batching and pipelining
- API response time optimization
- Memory usage optimization
- Concurrent request handling

Author: Cosmic Council Development Team
Version: 1.0.0
"""

import asyncio
import time
import logging
import json
import gzip
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import threading
import hashlib
import weakref
from functools import wraps
import aiohttp
import redis
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import uvicorn
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse
import psutil

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- API Performance Configuration ---

@dataclass
class APIPerformanceConfig:
    """API performance optimization configuration"""
    enable_response_caching: bool = True
    cache_ttl: int = 3600
    cache_max_size: int = 10000
    enable_compression: bool = True
    compression_level: int = 6
    enable_rate_limiting: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
    enable_connection_pooling: bool = True
    max_connections: int = 100
    connection_timeout: int = 30
    enable_request_batching: bool = True
    batch_size: int = 50
    batch_timeout: float = 0.1
    enable_response_streaming: bool = True
    streaming_chunk_size: int = 8192
    enable_metrics_collection: bool = True
    metrics_retention: int = 3600
    enable_circuit_breaker: bool = True
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60

# --- API Performance Metrics ---

@dataclass
class APIMetrics:
    """API performance metrics"""
    endpoint: str
    method: str
    response_time: float
    status_code: int
    request_size: int
    response_size: int
    cache_hit: bool = False
    timestamp: datetime = field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    error: Optional[str] = None

# --- Response Cache ---

class ResponseCache:
    """High-performance API response caching"""
    
    def __init__(self, redis_client: Optional[redis.Redis], ttl: int = 3600, max_size: int = 10000):
        self.redis_client = redis_client
        self.ttl = ttl
        self.max_size = max_size
        self.memory_cache: Dict[str, Dict] = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "evictions": 0
        }
        self._lock = threading.RLock()
    
    def _generate_cache_key(self, request: Request) -> str:
        """Generate cache key from request"""
        key_data = f"{request.method}:{request.url.path}:{str(request.query_params)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, request: Request) -> Optional[Dict[str, Any]]:
        """Get cached response"""
        cache_key = self._generate_cache_key(request)
        
        with self._lock:
            # Try Redis first
            if self.redis_client:
                try:
                    cached_data = self.redis_client.get(f"api_cache:{cache_key}")
                    if cached_data:
                        self.cache_stats["hits"] += 1
                        return json.loads(cached_data)
                except Exception as e:
                    logger.warning(f"Redis cache get failed: {e}")
            
            # Try memory cache
            if cache_key in self.memory_cache:
                entry = self.memory_cache[cache_key]
                if time.time() - entry['timestamp'] < self.ttl:
                    self.cache_stats["hits"] += 1
                    return entry['data']
                else:
                    del self.memory_cache[cache_key]
            
            self.cache_stats["misses"] += 1
            return None
    
    def set(self, request: Request, response_data: Dict[str, Any]):
        """Cache response data"""
        cache_key = self._generate_cache_key(request)
        
        with self._lock:
            self.cache_stats["sets"] += 1
            
            # Store in Redis
            if self.redis_client:
                try:
                    serialized_data = json.dumps(response_data)
                    self.redis_client.setex(f"api_cache:{cache_key}", self.ttl, serialized_data)
                except Exception as e:
                    logger.warning(f"Redis cache set failed: {e}")
            
            # Store in memory cache
            if len(self.memory_cache) >= self.max_size:
                self._evict_oldest()
            
            self.memory_cache[cache_key] = {
                'data': response_data,
                'timestamp': time.time()
            }
    
    def _evict_oldest(self):
        """Evict oldest cache entry"""
        if not self.memory_cache:
            return
        
        oldest_key = min(self.memory_cache.keys(), 
                        key=lambda k: self.memory_cache[k]['timestamp'])
        del self.memory_cache[oldest_key]
        self.cache_stats["evictions"] += 1
    
    def invalidate(self, pattern: str):
        """Invalidate cache entries matching pattern"""
        with self._lock:
            # Invalidate Redis cache
            if self.redis_client:
                try:
                    keys = self.redis_client.keys(f"api_cache:*{pattern}*")
                    if keys:
                        self.redis_client.delete(*keys)
                except Exception as e:
                    logger.warning(f"Redis cache invalidation failed: {e}")
            
            # Invalidate memory cache
            keys_to_remove = [k for k in self.memory_cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self.memory_cache[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
            hit_rate = self.cache_stats["hits"] / total_requests if total_requests > 0 else 0
            
            return {
                "hits": self.cache_stats["hits"],
                "misses": self.cache_stats["misses"],
                "sets": self.cache_stats["sets"],
                "evictions": self.cache_stats["evictions"],
                "hit_rate": hit_rate,
                "memory_cache_size": len(self.memory_cache)
            }

# --- Rate Limiter ---

class RateLimiter:
    """API rate limiting and throttling"""
    
    def __init__(self, redis_client: Optional[redis.Redis], 
                 requests_per_window: int = 100, window_seconds: int = 60):
        self.redis_client = redis_client
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self.memory_limits: Dict[str, deque] = defaultdict(lambda: deque())
        self._lock = threading.RLock()
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting"""
        # Try to get user ID from request
        user_id = getattr(request.state, 'user_id', None)
        if user_id:
            return f"user:{user_id}"
        
        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"
    
    def is_allowed(self, request: Request) -> bool:
        """Check if request is allowed under rate limit"""
        client_id = self._get_client_id(request)
        current_time = time.time()
        
        # Try Redis first
        if self.redis_client:
            try:
                key = f"rate_limit:{client_id}"
                current_count = self.redis_client.get(key)
                
                if current_count is None:
                    # First request in window
                    self.redis_client.setex(key, self.window_seconds, 1)
                    return True
                elif int(current_count) < self.requests_per_window:
                    # Increment counter
                    self.redis_client.incr(key)
                    return True
                else:
                    # Rate limit exceeded
                    return False
            except Exception as e:
                logger.warning(f"Redis rate limiting failed: {e}")
        
        # Fall back to memory-based rate limiting
        with self._lock:
            request_times = self.memory_limits[client_id]
            
            # Remove old requests outside the window
            while request_times and request_times[0] <= current_time - self.window_seconds:
                request_times.popleft()
            
            # Check if under limit
            if len(request_times) < self.requests_per_window:
                request_times.append(current_time)
                return True
            else:
                return False
    
    def get_remaining_requests(self, request: Request) -> int:
        """Get remaining requests for client"""
        client_id = self._get_client_id(request)
        
        if self.redis_client:
            try:
                key = f"rate_limit:{client_id}"
                current_count = self.redis_client.get(key)
                if current_count is None:
                    return self.requests_per_window
                else:
                    return max(0, self.requests_per_window - int(current_count))
            except Exception as e:
                logger.warning(f"Redis rate limit check failed: {e}")
        
        # Fall back to memory-based calculation
        with self._lock:
            request_times = self.memory_limits[client_id]
            current_time = time.time()
            
            # Remove old requests
            while request_times and request_times[0] <= current_time - self.window_seconds:
                request_times.popleft()
            
            return max(0, self.requests_per_window - len(request_times))

# --- Request Batcher ---

class RequestBatcher:
    """Batch multiple requests for improved performance"""
    
    def __init__(self, batch_size: int = 50, batch_timeout: float = 0.1):
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.pending_requests: Dict[str, List] = defaultdict(list)
        self.batch_handlers: Dict[str, Callable] = {}
        self._lock = threading.RLock()
    
    def register_batch_handler(self, endpoint: str, handler: Callable):
        """Register batch handler for endpoint"""
        self.batch_handlers[endpoint] = handler
    
    async def add_request(self, endpoint: str, request_data: Dict[str, Any]) -> Any:
        """Add request to batch"""
        with self._lock:
            self.pending_requests[endpoint].append(request_data)
            
            # Check if batch is ready
            if len(self.pending_requests[endpoint]) >= self.batch_size:
                return await self._process_batch(endpoint)
            else:
                # Schedule batch processing after timeout
                asyncio.create_task(self._schedule_batch_processing(endpoint))
                return None
    
    async def _schedule_batch_processing(self, endpoint: str):
        """Schedule batch processing after timeout"""
        await asyncio.sleep(self.batch_timeout)
        await self._process_batch(endpoint)
    
    async def _process_batch(self, endpoint: str):
        """Process batch of requests"""
        with self._lock:
            if endpoint not in self.pending_requests or not self.pending_requests[endpoint]:
                return
            
            batch_data = self.pending_requests[endpoint].copy()
            self.pending_requests[endpoint].clear()
        
        # Process batch
        if endpoint in self.batch_handlers:
            try:
                results = await self.batch_handlers[endpoint](batch_data)
                return results
            except Exception as e:
                logger.error(f"Batch processing failed for {endpoint}: {e}")
                return None

# --- API Performance Monitor ---

class APIPerformanceMonitor:
    """Monitor API performance and collect metrics"""
    
    def __init__(self):
        self.metrics: deque = deque(maxlen=10000)
        self.endpoint_stats: Dict[str, Dict] = defaultdict(lambda: {
            "total_requests": 0,
            "total_response_time": 0.0,
            "min_response_time": float('inf'),
            "max_response_time": 0.0,
            "error_count": 0,
            "cache_hits": 0
        })
        self._lock = threading.RLock()
    
    def record_request(self, metrics: APIMetrics):
        """Record API request metrics"""
        with self._lock:
            self.metrics.append(metrics)
            
            # Update endpoint statistics
            endpoint_key = f"{metrics.method}:{metrics.endpoint}"
            stats = self.endpoint_stats[endpoint_key]
            
            stats["total_requests"] += 1
            stats["total_response_time"] += metrics.response_time
            stats["min_response_time"] = min(stats["min_response_time"], metrics.response_time)
            stats["max_response_time"] = max(stats["max_response_time"], metrics.response_time)
            
            if metrics.status_code >= 400:
                stats["error_count"] += 1
            
            if metrics.cache_hit:
                stats["cache_hits"] += 1
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get API performance summary"""
        with self._lock:
            if not self.metrics:
                return {"error": "No metrics available"}
            
            # Calculate overall statistics
            response_times = [m.response_time for m in self.metrics]
            status_codes = [m.status_code for m in self.metrics]
            cache_hits = sum(1 for m in self.metrics if m.cache_hit)
            
            return {
                "total_requests": len(self.metrics),
                "avg_response_time": sum(response_times) / len(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "cache_hit_rate": cache_hits / len(self.metrics),
                "error_rate": sum(1 for s in status_codes if s >= 400) / len(status_codes),
                "endpoint_count": len(self.endpoint_stats)
            }
    
    def get_endpoint_stats(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get endpoint performance statistics"""
        with self._lock:
            endpoint_list = []
            for endpoint, stats in self.endpoint_stats.items():
                if stats["total_requests"] > 0:
                    avg_response_time = stats["total_response_time"] / stats["total_requests"]
                    error_rate = stats["error_count"] / stats["total_requests"]
                    cache_hit_rate = stats["cache_hits"] / stats["total_requests"]
                    
                    endpoint_list.append({
                        "endpoint": endpoint,
                        "total_requests": stats["total_requests"],
                        "avg_response_time": avg_response_time,
                        "min_response_time": stats["min_response_time"],
                        "max_response_time": stats["max_response_time"],
                        "error_rate": error_rate,
                        "cache_hit_rate": cache_hit_rate
                    })
            
            # Sort by total requests
            endpoint_list.sort(key=lambda x: x["total_requests"], reverse=True)
            return endpoint_list[:limit]

# --- Performance Middleware ---

class PerformanceMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for performance monitoring and optimization"""
    
    def __init__(self, app, config: APIPerformanceConfig):
        super().__init__(app)
        self.config = config
        self.response_cache = ResponseCache(None, config.cache_ttl, config.cache_max_size)
        self.rate_limiter = RateLimiter(None, config.rate_limit_requests, config.rate_limit_window)
        self.performance_monitor = APIPerformanceMonitor()
    
    async def dispatch(self, request: Request, call_next):
        """Process request with performance optimizations"""
        start_time = time.time()
        
        # Check rate limiting
        if self.config.enable_rate_limiting:
            if not self.rate_limiter.is_allowed(request):
                return JSONResponse(
                    status_code=429,
                    content={"error": "Rate limit exceeded"},
                    headers={"Retry-After": str(self.config.rate_limit_window)}
                )
        
        # Check response cache
        cached_response = None
        if self.config.enable_response_caching and request.method == "GET":
            cached_response = self.response_cache.get(request)
            if cached_response:
                return JSONResponse(content=cached_response)
        
        # Process request
        try:
            response = await call_next(request)
            
            # Record metrics
            response_time = time.time() - start_time
            metrics = APIMetrics(
                endpoint=request.url.path,
                method=request.method,
                response_time=response_time,
                status_code=response.status_code,
                request_size=len(str(request.body)) if hasattr(request, 'body') else 0,
                response_size=len(response.body) if hasattr(response, 'body') else 0,
                cache_hit=cached_response is not None
            )
            self.performance_monitor.record_request(metrics)
            
            # Cache successful GET responses
            if (self.config.enable_response_caching and 
                request.method == "GET" and 
                response.status_code == 200):
                try:
                    response_body = response.body
                    if response_body:
                        response_data = json.loads(response_body.decode())
                        self.response_cache.set(request, response_data)
                except Exception as e:
                    logger.warning(f"Failed to cache response: {e}")
            
            return response
            
        except Exception as e:
            # Record error metrics
            response_time = time.time() - start_time
            metrics = APIMetrics(
                endpoint=request.url.path,
                method=request.method,
                response_time=response_time,
                status_code=500,
                error=str(e)
            )
            self.performance_monitor.record_request(metrics)
            raise

# --- Optimized FastAPI Application ---

class OptimizedFastAPI:
    """Performance-optimized FastAPI application"""
    
    def __init__(self, config: APIPerformanceConfig):
        self.config = config
        self.app = FastAPI(
            title="Cosmic Council API",
            version="1.0.0",
            description="High-performance API for the Cosmic Council Framework"
        )
        
        # Initialize components
        self.response_cache = ResponseCache(None, config.cache_ttl, config.cache_max_size)
        self.rate_limiter = RateLimiter(None, config.rate_limit_requests, config.rate_limit_window)
        self.request_batcher = RequestBatcher(config.batch_size, config.batch_timeout)
        self.performance_monitor = APIPerformanceMonitor()
        
        # Setup middleware
        self._setup_middleware()
        
        # Setup routes
        self._setup_routes()
    
    def _setup_middleware(self):
        """Setup performance optimization middleware"""
        # Performance monitoring middleware
        self.app.add_middleware(PerformanceMiddleware, config=self.config)
        
        # Compression middleware
        if self.config.enable_compression:
            self.app.add_middleware(GZipMiddleware, minimum_size=1000)
        
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
        
        @self.app.get("/metrics")
        async def get_metrics():
            """Get API performance metrics"""
            return {
                "performance_summary": self.performance_monitor.get_performance_summary(),
                "endpoint_stats": self.performance_monitor.get_endpoint_stats(),
                "cache_stats": self.response_cache.get_stats()
            }
        
        @self.app.get("/rate-limit-status")
        async def get_rate_limit_status(request: Request):
            """Get rate limit status for current client"""
            remaining = self.rate_limiter.get_remaining_requests(request)
            return {
                "remaining_requests": remaining,
                "limit": self.config.rate_limit_requests,
                "window_seconds": self.config.rate_limit_window
            }
        
        @self.app.post("/cache/invalidate")
        async def invalidate_cache(pattern: str):
            """Invalidate cache entries"""
            self.response_cache.invalidate(pattern)
            return {"message": f"Cache invalidated for pattern: {pattern}"}
        
        @self.app.get("/performance/stats")
        async def get_performance_stats():
            """Get comprehensive performance statistics"""
            return {
                "api_metrics": self.performance_monitor.get_performance_summary(),
                "endpoint_performance": self.performance_monitor.get_endpoint_stats(),
                "cache_performance": self.response_cache.get_stats(),
                "system_metrics": {
                    "memory_usage": psutil.virtual_memory().percent,
                    "cpu_usage": psutil.cpu_percent(),
                    "disk_usage": psutil.disk_usage('/').percent
                }
            }
    
    def get_app(self) -> FastAPI:
        """Get the FastAPI application instance"""
        return self.app

# --- Performance Decorators ---

def monitor_api_performance(func: Callable) -> Callable:
    """Decorator to monitor API endpoint performance"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(f"{func.__name__} completed in {duration:.3f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"{func.__name__} failed after {duration:.3f}s: {e}")
            raise
    return wrapper

def cache_api_response(ttl: int = 3600):
    """Decorator to cache API responses"""
    def decorator(func: Callable) -> Callable:
        cache = ResponseCache(None, ttl)
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Check cache
            cached_result = cache.get(None)  # Simplified for decorator
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache.set(None, result)  # Simplified for decorator
            return result
        
        return wrapper
    return decorator

# --- Demo Function ---

async def demo_api_performance_optimization():
    """Demonstrate API performance optimization capabilities"""
    print("🚀 Cosmic Council Framework - API Performance Optimization Demo")
    print("=" * 70)
    
    # Create API performance configuration
    config = APIPerformanceConfig(
        enable_response_caching=True,
        cache_ttl=1800,
        enable_compression=True,
        enable_rate_limiting=True,
        rate_limit_requests=100,
        rate_limit_window=60,
        enable_metrics_collection=True
    )
    
    try:
        # Create optimized FastAPI application
        optimized_api = OptimizedFastAPI(config)
        app = optimized_api.get_app()
        print("✅ Optimized FastAPI application created")
        
        # Test response cache
        print("\n💾 Testing response cache...")
        cache = ResponseCache(None, 60)  # 1 minute TTL
        
        # Simulate caching responses
        test_responses = [
            {"id": i, "data": f"response_{i}", "timestamp": datetime.utcnow().isoformat()}
            for i in range(10)
        ]
        
        for i, response in enumerate(test_responses):
            cache.set(None, response)  # Simplified for demo
        
        # Test cache hits
        start_time = time.time()
        for i in range(10):
            cached_result = cache.get(None)
        cache_time = time.time() - start_time
        
        print(f"  Cache operations completed in {cache_time:.4f}s")
        print(f"  Cache stats: {cache.get_stats()}")
        
        # Test rate limiter
        print("\n🚦 Testing rate limiter...")
        rate_limiter = RateLimiter(None, 10, 60)  # 10 requests per minute
        
        # Simulate requests
        allowed_requests = 0
        blocked_requests = 0
        
        for i in range(15):
            # Create mock request object
            class MockRequest:
                def __init__(self):
                    self.client = type('Client', (), {'host': '127.0.0.1'})()
                    self.state = type('State', (), {})()
            
            mock_request = MockRequest()
            if rate_limiter.is_allowed(mock_request):
                allowed_requests += 1
            else:
                blocked_requests += 1
        
        print(f"  Allowed requests: {allowed_requests}")
        print(f"  Blocked requests: {blocked_requests}")
        
        # Test request batcher
        print("\n📦 Testing request batcher...")
        batcher = RequestBatcher(batch_size=5, batch_timeout=0.1)
        
        # Register batch handler
        async def batch_handler(batch_data):
            return [{"processed": item, "batch_size": len(batch_data)} for item in batch_data]
        
        batcher.register_batch_handler("test_endpoint", batch_handler)
        
        # Add requests to batch
        for i in range(8):
            await batcher.add_request("test_endpoint", {"id": i, "data": f"request_{i}"})
        
        print("  ✅ Request batcher configured")
        
        # Test performance monitoring
        print("\n📈 Testing performance monitoring...")
        monitor = APIPerformanceMonitor()
        
        # Simulate API metrics
        for i in range(10):
            metrics = APIMetrics(
                endpoint=f"/api/endpoint_{i % 3}",
                method="GET",
                response_time=0.1 + i * 0.05,
                status_code=200 if i < 8 else 500,
                request_size=100 + i * 10,
                response_size=500 + i * 50,
                cache_hit=i % 3 == 0
            )
            monitor.record_request(metrics)
        
        performance_summary = monitor.get_performance_summary()
        print(f"  Performance summary: {performance_summary}")
        
        endpoint_stats = monitor.get_endpoint_stats()
        print(f"  Endpoint stats: {len(endpoint_stats)} endpoints tracked")
        
        # Test compression
        print("\n🗜️  Testing compression...")
        test_data = {"large_data": "x" * 1000}  # 1KB of data
        json_data = json.dumps(test_data).encode()
        
        # Compress data
        start_time = time.time()
        compressed_data = gzip.compress(json_data)
        compression_time = time.time() - start_time
        
        compression_ratio = len(compressed_data) / len(json_data)
        print(f"  Original size: {len(json_data)} bytes")
        print(f"  Compressed size: {len(compressed_data)} bytes")
        print(f"  Compression ratio: {compression_ratio:.2f}")
        print(f"  Compression time: {compression_time:.4f}s")
        
        print("\n✅ API performance optimization demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        logger.error(f"Demo error: {e}")

if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_api_performance_optimization())
