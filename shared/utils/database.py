#!/usr/bin/env python3
"""
🔧 Shared Database Utilities
Common database connection and repository patterns
"""

import os
import logging
from typing import Dict, Any, List, Optional, Union
from contextlib import contextmanager
import asyncpg
import psycopg2
from psycopg2.extras import RealDictCursor
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str
    port: int
    database: str
    username: str
    password: str
    ssl_mode: str = "prefer"
    pool_size: int = 10
    max_overflow: int = 20

class DatabaseManager:
    """Centralized database connection manager"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._pool = None
    
    async def initialize_pool(self):
        """Initialize async connection pool"""
        try:
            self._pool = await asyncpg.create_pool(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.username,
                password=self.config.password,
                ssl=self.config.ssl_mode,
                min_size=1,
                max_size=self.config.pool_size
            )
            logger.info("Database connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise
    
    async def close_pool(self):
        """Close connection pool"""
        if self._pool:
            await self._pool.close()
            logger.info("Database connection pool closed")
    
    @contextmanager
    def get_sync_connection(self):
        """Get synchronous database connection"""
        conn = None
        try:
            conn = psycopg2.connect(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.username,
                password=self.config.password,
                sslmode=self.config.ssl_mode,
                cursor_factory=RealDictCursor
            )
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    async def get_async_connection(self):
        """Get async database connection"""
        if not self._pool:
            await self.initialize_pool()
        return self._pool.acquire()
    
    async def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute async query and return results"""
        async with self.get_async_connection() as conn:
            try:
                if params:
                    rows = await conn.fetch(query, *params)
                else:
                    rows = await conn.fetch(query)
                return [dict(row) for row in rows]
            except Exception as e:
                logger.error(f"Query execution error: {e}")
                raise
    
    async def execute_command(self, command: str, params: tuple = None) -> str:
        """Execute async command and return result"""
        async with self.get_async_connection() as conn:
            try:
                if params:
                    result = await conn.execute(command, *params)
                else:
                    result = await conn.execute(command)
                return result
            except Exception as e:
                logger.error(f"Command execution error: {e}")
                raise

class BaseRepository:
    """Base repository class with common patterns"""
    
    def __init__(self, db_manager: DatabaseManager, table_name: str):
        self.db = db_manager
        self.table_name = table_name
    
    async def create(self, data: Dict[str, Any]) -> str:
        """Create a new record"""
        columns = list(data.keys())
        values = list(data.values())
        placeholders = [f"${i+1}" for i in range(len(values))]
        
        query = f"""
        INSERT INTO {self.table_name} ({', '.join(columns)})
        VALUES ({', '.join(placeholders)})
        RETURNING id
        """
        
        result = await self.db.execute_query(query, tuple(values))
        return result[0]['id'] if result else None
    
    async def get_by_id(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Get record by ID"""
        query = f"SELECT * FROM {self.table_name} WHERE id = $1"
        result = await self.db.execute_query(query, (record_id,))
        return result[0] if result else None
    
    async def update(self, record_id: str, data: Dict[str, Any]) -> bool:
        """Update record by ID"""
        set_clauses = [f"{key} = ${i+2}" for i, key in enumerate(data.keys())]
        values = list(data.values()) + [record_id]
        
        query = f"""
        UPDATE {self.table_name}
        SET {', '.join(set_clauses)}, updated_at = NOW()
        WHERE id = $1
        """
        
        result = await self.db.execute_command(query, tuple(values))
        return "UPDATE 1" in result
    
    async def delete(self, record_id: str) -> bool:
        """Soft delete record by ID"""
        query = f"""
        UPDATE {self.table_name}
        SET status = 'deleted', updated_at = NOW()
        WHERE id = $1
        """
        
        result = await self.db.execute_command(query, (record_id,))
        return "UPDATE 1" in result
    
    async def list(self, filters: Dict[str, Any] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List records with optional filters"""
        query = f"SELECT * FROM {self.table_name}"
        params = []
        
        if filters:
            where_clauses = []
            for i, (key, value) in enumerate(filters.items()):
                where_clauses.append(f"{key} = ${i+1}")
                params.append(value)
            
            if where_clauses:
                query += f" WHERE {' AND '.join(where_clauses)}"
        
        query += f" ORDER BY created_at DESC LIMIT ${len(params)+1} OFFSET ${len(params)+2}"
        params.extend([limit, offset])
        
        return await self.db.execute_query(query, tuple(params))

def get_database_config() -> DatabaseConfig:
    """Get database configuration from environment variables"""
    return DatabaseConfig(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '5432')),
        database=os.getenv('DB_NAME', 'cosmic_council'),
        username=os.getenv('DB_USER', 'cosmic_council'),
        password=os.getenv('DB_PASSWORD', ''),
        ssl_mode=os.getenv('DB_SSL_MODE', 'prefer'),
        pool_size=int(os.getenv('DB_POOL_SIZE', '10')),
        max_overflow=int(os.getenv('DB_MAX_OVERFLOW', '20'))
    )

# Global database manager instance
_db_manager = None

async def get_database_manager() -> DatabaseManager:
    """Get global database manager instance"""
    global _db_manager
    if _db_manager is None:
        config = get_database_config()
        _db_manager = DatabaseManager(config)
        await _db_manager.initialize_pool()
    return _db_manager

async def close_database_manager():
    """Close global database manager"""
    global _db_manager
    if _db_manager:
        await _db_manager.close_pool()
        _db_manager = None
