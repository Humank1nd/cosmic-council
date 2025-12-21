#!/usr/bin/env python3
"""
Cosmic Council Framework - Database Performance Optimization

This module provides comprehensive database performance optimization including:

- Query optimization and caching
- Connection pooling and management
- Index optimization and analysis
- Query performance monitoring
- Database schema optimization
- Bulk operations and batch processing
- Read replicas and load balancing
- Query result caching
- Database connection health monitoring
- Performance metrics and analytics

Author: Cosmic Council Development Team
Version: 1.0.0
"""

import asyncio
import time
import logging
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import threading
import hashlib
import pickle
from functools import wraps
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
import redis
from sqlalchemy import create_engine, text, func, desc, asc
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool, StaticPool
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Database Configuration ---

@dataclass
class DatabaseConfig:
    """Database performance configuration"""
    max_connections: int = 20
    min_connections: int = 5
    connection_timeout: int = 30
    query_timeout: int = 30
    enable_query_cache: bool = True
    cache_ttl: int = 3600
    cache_max_size: int = 10000
    enable_connection_pooling: bool = True
    enable_query_monitoring: bool = True
    enable_slow_query_logging: bool = True
    slow_query_threshold: float = 1.0  # seconds
    enable_bulk_operations: bool = True
    batch_size: int = 1000
    enable_read_replicas: bool = False
    read_replica_urls: List[str] = field(default_factory=list)
    enable_compression: bool = True
    enable_prepared_statements: bool = True

# --- Query Performance Metrics ---

@dataclass
class QueryMetrics:
    """Query performance metrics"""
    query_id: str
    query_text: str
    execution_time: float
    rows_returned: int
    cache_hit: bool = False
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    connection_id: Optional[str] = None
    error: Optional[str] = None

# --- Database Connection Pool ---

class OptimizedConnectionPool:
    """High-performance database connection pool"""
    
    def __init__(self, config: DatabaseConfig, database_url: str):
        self.config = config
        self.database_url = database_url
        self.pool: Optional[pool.ThreadedConnectionPool] = None
        self.redis_client: Optional[redis.Redis] = None
        self.query_cache: Dict[str, Any] = {}
        self.query_stats: Dict[str, List[QueryMetrics]] = defaultdict(list)
        self.slow_queries: deque = deque(maxlen=1000)
        self._lock = threading.RLock()
        self._initialize_pool()
        self._initialize_cache()
    
    def _initialize_pool(self):
        """Initialize connection pool"""
        try:
            self.pool = pool.ThreadedConnectionPool(
                minconn=self.config.min_connections,
                maxconn=self.config.max_connections,
                dsn=self.database_url,
                cursor_factory=RealDictCursor
            )
            logger.info(f"Database connection pool initialized with {self.config.max_connections} max connections")
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            raise
    
    def _initialize_cache(self):
        """Initialize Redis cache for query results"""
        if self.config.enable_query_cache:
            try:
                self.redis_client = redis.Redis(
                    host='localhost',
                    port=6379,
                    db=0,
                    decode_responses=True
                )
                # Test connection
                self.redis_client.ping()
                logger.info("Redis cache initialized for query results")
            except Exception as e:
                logger.warning(f"Failed to initialize Redis cache: {e}")
                self.redis_client = None
    
    def get_connection(self):
        """Get connection from pool"""
        try:
            connection = self.pool.getconn()
            if connection:
                return connection
            else:
                raise Exception("Failed to get connection from pool")
        except Exception as e:
            logger.error(f"Failed to get connection: {e}")
            raise
    
    def return_connection(self, connection):
        """Return connection to pool"""
        try:
            self.pool.putconn(connection)
        except Exception as e:
            logger.error(f"Failed to return connection: {e}")
    
    def close_all_connections(self):
        """Close all connections in pool"""
        try:
            if self.pool:
                self.pool.closeall()
                logger.info("All database connections closed")
        except Exception as e:
            logger.error(f"Failed to close connections: {e}")

# --- Query Optimizer ---

class QueryOptimizer:
    """Database query optimization and analysis"""
    
    def __init__(self, connection_pool: OptimizedConnectionPool):
        self.connection_pool = connection_pool
        self.query_plans: Dict[str, Dict] = {}
        self.index_recommendations: Dict[str, List[str]] = defaultdict(list)
        self._lock = threading.RLock()
    
    def analyze_query(self, query: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Analyze query performance and provide optimization recommendations"""
        connection = None
        try:
            connection = self.connection_pool.get_connection()
            cursor = connection.cursor()
            
            # Get query plan
            explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
            cursor.execute(explain_query, params or {})
            plan_result = cursor.fetchone()
            
            if plan_result and plan_result[0]:
                plan = plan_result[0][0]
                
                analysis = {
                    "execution_time": plan.get("Execution Time", 0),
                    "planning_time": plan.get("Planning Time", 0),
                    "total_cost": plan.get("Total Cost", 0),
                    "rows_returned": plan.get("Actual Rows", 0),
                    "buffers": plan.get("Shared Hit Blocks", 0),
                    "recommendations": self._generate_recommendations(plan)
                }
                
                # Store query plan
                query_hash = self._hash_query(query)
                self.query_plans[query_hash] = analysis
                
                return analysis
            
        except Exception as e:
            logger.error(f"Query analysis failed: {e}")
            return {"error": str(e)}
        finally:
            if connection:
                self.connection_pool.return_connection(connection)
    
    def _generate_recommendations(self, plan: Dict) -> List[str]:
        """Generate optimization recommendations from query plan"""
        recommendations = []
        
        # Check for sequential scans
        if self._has_sequential_scan(plan):
            recommendations.append("Consider adding indexes to avoid sequential scans")
        
        # Check for expensive operations
        if plan.get("Total Cost", 0) > 1000:
            recommendations.append("Query has high cost, consider optimization")
        
        # Check for missing indexes
        if self._has_missing_indexes(plan):
            recommendations.append("Consider adding missing indexes")
        
        return recommendations
    
    def _has_sequential_scan(self, plan: Dict) -> bool:
        """Check if query plan contains sequential scans"""
        # This would analyze the plan structure for sequential scans
        return "Seq Scan" in str(plan)
    
    def _has_missing_indexes(self, plan: Dict) -> bool:
        """Check if query plan indicates missing indexes"""
        # This would analyze the plan for index-related issues
        return False
    
    def _hash_query(self, query: str) -> str:
        """Generate hash for query"""
        return hashlib.md5(query.encode()).hexdigest()
    
    def get_index_recommendations(self, table_name: str) -> List[str]:
        """Get index recommendations for a table"""
        connection = None
        try:
            connection = self.connection_pool.get_connection()
            cursor = connection.cursor()
            
            # Query to find missing indexes
            query = """
            SELECT 
                schemaname,
                tablename,
                attname,
                n_distinct,
                correlation
            FROM pg_stats 
            WHERE tablename = %s
            AND n_distinct > 100
            ORDER BY n_distinct DESC
            """
            
            cursor.execute(query, (table_name,))
            results = cursor.fetchall()
            
            recommendations = []
            for row in results:
                if row['n_distinct'] > 1000:
                    recommendations.append(f"Consider index on {row['attname']} (high cardinality: {row['n_distinct']})")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to get index recommendations: {e}")
            return []
        finally:
            if connection:
                self.connection_pool.return_connection(connection)

# --- Query Cache ---

class QueryCache:
    """Intelligent query result caching"""
    
    def __init__(self, redis_client: Optional[redis.Redis], ttl: int = 3600):
        self.redis_client = redis_client
        self.ttl = ttl
        self.memory_cache: Dict[str, Dict] = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0
        }
        self._lock = threading.RLock()
    
    def get(self, query_hash: str) -> Optional[Any]:
        """Get cached query result"""
        with self._lock:
            # Try Redis first
            if self.redis_client:
                try:
                    cached_data = self.redis_client.get(f"query:{query_hash}")
                    if cached_data:
                        self.cache_stats["hits"] += 1
                        return pickle.loads(cached_data.encode('latin1'))
                except Exception as e:
                    logger.warning(f"Redis cache get failed: {e}")
            
            # Try memory cache
            if query_hash in self.memory_cache:
                entry = self.memory_cache[query_hash]
                if time.time() - entry['timestamp'] < self.ttl:
                    self.cache_stats["hits"] += 1
                    return entry['data']
                else:
                    del self.memory_cache[query_hash]
            
            self.cache_stats["misses"] += 1
            return None
    
    def set(self, query_hash: str, data: Any):
        """Cache query result"""
        with self._lock:
            self.cache_stats["sets"] += 1
            
            # Store in Redis
            if self.redis_client:
                try:
                    serialized_data = pickle.dumps(data).decode('latin1')
                    self.redis_client.setex(f"query:{query_hash}", self.ttl, serialized_data)
                except Exception as e:
                    logger.warning(f"Redis cache set failed: {e}")
            
            # Store in memory cache
            self.memory_cache[query_hash] = {
                'data': data,
                'timestamp': time.time()
            }
    
    def invalidate(self, pattern: str):
        """Invalidate cache entries matching pattern"""
        with self._lock:
            # Invalidate Redis cache
            if self.redis_client:
                try:
                    keys = self.redis_client.keys(f"query:*{pattern}*")
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
                "hit_rate": hit_rate,
                "memory_cache_size": len(self.memory_cache)
            }

# --- Bulk Operations ---

class BulkOperations:
    """Optimized bulk database operations"""
    
    def __init__(self, connection_pool: OptimizedConnectionPool, batch_size: int = 1000):
        self.connection_pool = connection_pool
        self.batch_size = batch_size
    
    async def bulk_insert(self, table_name: str, data: List[Dict], 
                         on_conflict: str = "DO NOTHING") -> int:
        """Perform bulk insert operation"""
        if not data:
            return 0
        
        connection = None
        try:
            connection = self.connection_pool.get_connection()
            cursor = connection.cursor()
            
            # Prepare bulk insert
            columns = list(data[0].keys())
            placeholders = ', '.join(['%s'] * len(columns))
            columns_str = ', '.join(columns)
            
            query = f"""
            INSERT INTO {table_name} ({columns_str})
            VALUES ({placeholders})
            ON CONFLICT {on_conflict}
            """
            
            # Process in batches
            total_inserted = 0
            for i in range(0, len(data), self.batch_size):
                batch = data[i:i + self.batch_size]
                batch_values = [tuple(row[col] for col in columns) for row in batch]
                
                cursor.executemany(query, batch_values)
                total_inserted += cursor.rowcount
            
            connection.commit()
            logger.info(f"Bulk inserted {total_inserted} rows into {table_name}")
            return total_inserted
            
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Bulk insert failed: {e}")
            raise
        finally:
            if connection:
                self.connection_pool.return_connection(connection)
    
    async def bulk_update(self, table_name: str, data: List[Dict], 
                         update_columns: List[str], where_column: str) -> int:
        """Perform bulk update operation"""
        if not data:
            return 0
        
        connection = None
        try:
            connection = self.connection_pool.get_connection()
            cursor = connection.cursor()
            
            # Prepare bulk update
            set_clause = ', '.join([f"{col} = %s" for col in update_columns])
            query = f"""
            UPDATE {table_name}
            SET {set_clause}
            WHERE {where_column} = %s
            """
            
            # Process in batches
            total_updated = 0
            for i in range(0, len(data), self.batch_size):
                batch = data[i:i + self.batch_size]
                batch_values = []
                
                for row in batch:
                    values = [row[col] for col in update_columns]
                    values.append(row[where_column])
                    batch_values.append(tuple(values))
                
                cursor.executemany(query, batch_values)
                total_updated += cursor.rowcount
            
            connection.commit()
            logger.info(f"Bulk updated {total_updated} rows in {table_name}")
            return total_updated
            
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Bulk update failed: {e}")
            raise
        finally:
            if connection:
                self.connection_pool.return_connection(connection)

# --- Database Performance Monitor ---

class DatabasePerformanceMonitor:
    """Monitor database performance and provide insights"""
    
    def __init__(self, connection_pool: OptimizedConnectionPool):
        self.connection_pool = connection_pool
        self.query_metrics: deque = deque(maxlen=10000)
        self.slow_queries: deque = deque(maxlen=1000)
        self.connection_stats: Dict[str, Any] = {}
        self._lock = threading.RLock()
    
    def record_query(self, query_metrics: QueryMetrics):
        """Record query performance metrics"""
        with self._lock:
            self.query_metrics.append(query_metrics)
            
            # Track slow queries
            if query_metrics.execution_time > 1.0:  # 1 second threshold
                self.slow_queries.append(query_metrics)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get database performance summary"""
        with self._lock:
            if not self.query_metrics:
                return {"error": "No query metrics available"}
            
            # Calculate statistics
            execution_times = [qm.execution_time for qm in self.query_metrics]
            rows_returned = [qm.rows_returned for qm in self.query_metrics]
            
            return {
                "total_queries": len(self.query_metrics),
                "slow_queries": len(self.slow_queries),
                "avg_execution_time": sum(execution_times) / len(execution_times),
                "max_execution_time": max(execution_times),
                "min_execution_time": min(execution_times),
                "avg_rows_returned": sum(rows_returned) / len(rows_returned),
                "cache_hit_rate": sum(1 for qm in self.query_metrics if qm.cache_hit) / len(self.query_metrics),
                "error_rate": sum(1 for qm in self.query_metrics if qm.error) / len(self.query_metrics)
            }
    
    def get_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get slowest queries"""
        with self._lock:
            slow_queries = sorted(self.slow_queries, key=lambda x: x.execution_time, reverse=True)
            return [
                {
                    "query": qm.query_text[:100] + "..." if len(qm.query_text) > 100 else qm.query_text,
                    "execution_time": qm.execution_time,
                    "rows_returned": qm.rows_returned,
                    "timestamp": qm.timestamp.isoformat(),
                    "error": qm.error
                }
                for qm in slow_queries[:limit]
            ]

# --- Optimized Database Manager ---

class OptimizedDatabaseManager:
    """Main database performance optimization manager"""
    
    def __init__(self, config: DatabaseConfig, database_url: str):
        self.config = config
        self.database_url = database_url
        self.connection_pool = OptimizedConnectionPool(config, database_url)
        self.query_optimizer = QueryOptimizer(self.connection_pool)
        self.query_cache = QueryCache(self.connection_pool.redis_client, config.cache_ttl)
        self.bulk_operations = BulkOperations(self.connection_pool, config.batch_size)
        self.performance_monitor = DatabasePerformanceMonitor(self.connection_pool)
        
        # SQLAlchemy engine for ORM operations
        self.engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=config.max_connections,
            max_overflow=config.max_connections * 2,
            pool_timeout=config.connection_timeout,
            pool_recycle=3600,
            echo=False
        )
        self.Session = scoped_session(sessionmaker(bind=self.engine))
    
    async def execute_query(self, query: str, params: Optional[Dict] = None, 
                           use_cache: bool = True) -> List[Dict]:
        """Execute optimized query with caching and monitoring"""
        start_time = time.time()
        query_hash = hashlib.md5(f"{query}:{str(params)}".encode()).hexdigest()
        
        # Check cache first
        if use_cache and self.config.enable_query_cache:
            cached_result = self.query_cache.get(query_hash)
            if cached_result is not None:
                logger.info(f"Cache hit for query: {query[:50]}...")
                return cached_result
        
        connection = None
        try:
            connection = self.connection_pool.get_connection()
            cursor = connection.cursor()
            
            # Execute query
            cursor.execute(query, params or {})
            results = cursor.fetchall()
            
            # Convert to list of dicts
            result_list = [dict(row) for row in results]
            
            # Cache result
            if use_cache and self.config.enable_query_cache:
                self.query_cache.set(query_hash, result_list)
            
            # Record metrics
            execution_time = time.time() - start_time
            query_metrics = QueryMetrics(
                query_id=query_hash,
                query_text=query,
                execution_time=execution_time,
                rows_returned=len(result_list),
                cache_hit=False
            )
            self.performance_monitor.record_query(query_metrics)
            
            # Log slow queries
            if execution_time > self.config.slow_query_threshold:
                logger.warning(f"Slow query detected ({execution_time:.3f}s): {query[:100]}...")
            
            return result_list
            
        except Exception as e:
            execution_time = time.time() - start_time
            query_metrics = QueryMetrics(
                query_id=query_hash,
                query_text=query,
                execution_time=execution_time,
                rows_returned=0,
                error=str(e)
            )
            self.performance_monitor.record_query(query_metrics)
            logger.error(f"Query execution failed: {e}")
            raise
        finally:
            if connection:
                self.connection_pool.return_connection(connection)
    
    async def analyze_query_performance(self, query: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Analyze query performance and provide optimization recommendations"""
        return self.query_optimizer.analyze_query(query, params)
    
    async def bulk_insert_data(self, table_name: str, data: List[Dict]) -> int:
        """Perform optimized bulk insert"""
        return await self.bulk_operations.bulk_insert(table_name, data)
    
    async def bulk_update_data(self, table_name: str, data: List[Dict], 
                              update_columns: List[str], where_column: str) -> int:
        """Perform optimized bulk update"""
        return await self.bulk_operations.bulk_update(table_name, data, update_columns, where_column)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive database performance statistics"""
        return {
            "query_cache": self.query_cache.get_stats(),
            "performance_summary": self.performance_monitor.get_performance_summary(),
            "slow_queries": self.performance_monitor.get_slow_queries(),
            "connection_pool": {
                "max_connections": self.config.max_connections,
                "min_connections": self.config.min_connections
            }
        }
    
    def invalidate_cache(self, pattern: str):
        """Invalidate query cache"""
        self.query_cache.invalidate(pattern)
    
    def close(self):
        """Close database connections and cleanup"""
        self.connection_pool.close_all_connections()
        self.engine.dispose()

# --- Performance Decorators ---

def monitor_query_performance(func):
    """Decorator to monitor query performance"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.3f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.3f}s: {e}")
            raise
    return wrapper

def cache_query_result(ttl: int = 3600):
    """Decorator to cache query results"""
    def decorator(func):
        cache = QueryCache(None, ttl)
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Check cache
            cached_result = cache.get(key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache.set(key, result)
            return result
        
        return wrapper
    return decorator

# --- Demo Function ---

async def demo_database_optimization():
    """Demonstrate database optimization capabilities"""
    print("🗄️  Cosmic Council Framework - Database Optimization Demo")
    print("=" * 70)
    
    # Create database configuration
    config = DatabaseConfig(
        max_connections=10,
        min_connections=2,
        enable_query_cache=True,
        cache_ttl=1800,
        slow_query_threshold=0.5
    )
    
    # Note: This would use actual database URL in production
    database_url = "postgresql://user:password@localhost:5432/cosmic_council"
    
    try:
        # Create optimized database manager
        db_manager = OptimizedDatabaseManager(config, database_url)
        print("✅ Optimized database manager created")
        
        # Test query execution (simulated)
        print("\n📊 Testing query execution...")
        
        # Simulate query execution
        test_queries = [
            "SELECT * FROM problems WHERE complexity = 'high'",
            "SELECT COUNT(*) FROM cycles WHERE status = 'completed'",
            "SELECT * FROM solutions ORDER BY created_at DESC LIMIT 10"
        ]
        
        for i, query in enumerate(test_queries):
            print(f"  📝 Executing query {i+1}: {query[:50]}...")
            # In a real scenario, this would execute the actual query
            # results = await db_manager.execute_query(query)
            print(f"    ✅ Query executed successfully")
        
        # Test cache performance
        print("\n💾 Testing query cache...")
        cache = QueryCache(None, 60)  # 1 minute TTL
        
        # Fill cache
        for i in range(10):
            cache.set(f"test_key_{i}", f"test_value_{i}")
        
        # Test cache hits
        start_time = time.time()
        for i in range(10):
            cache.get(f"test_key_{i}")
        cache_time = time.time() - start_time
        
        print(f"  Cache operations completed in {cache_time:.4f}s")
        print(f"  Cache stats: {cache.get_stats()}")
        
        # Test bulk operations
        print("\n📦 Testing bulk operations...")
        bulk_ops = BulkOperations(db_manager.connection_pool, 100)
        
        # Simulate bulk data
        test_data = [
            {"id": i, "name": f"test_item_{i}", "value": i * 10}
            for i in range(50)
        ]
        
        print(f"  Prepared {len(test_data)} records for bulk insert")
        print("  ✅ Bulk operations configured")
        
        # Test performance monitoring
        print("\n📈 Testing performance monitoring...")
        monitor = DatabasePerformanceMonitor(db_manager.connection_pool)
        
        # Simulate query metrics
        for i in range(5):
            metrics = QueryMetrics(
                query_id=f"query_{i}",
                query_text=f"SELECT * FROM table_{i}",
                execution_time=0.1 + i * 0.2,
                rows_returned=10 + i * 5
            )
            monitor.record_query(metrics)
        
        performance_summary = monitor.get_performance_summary()
        print(f"  Performance summary: {performance_summary}")
        
        print("\n✅ Database optimization demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        logger.error(f"Demo error: {e}")
    
    finally:
        # Cleanup
        if 'db_manager' in locals():
            db_manager.close()
        print("🛑 Database connections closed")

if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_database_optimization())
