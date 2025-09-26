"""
Database connection management for the Cosmic Council system.
Provides async PostgreSQL connection pooling and management.
"""

import asyncio
import asyncpg
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
import logging
from ..config import get_settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections and connection pooling."""
    
    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None
        self._settings = get_settings()
    
    async def initialize(self) -> None:
        """Initialize the database connection pool."""
        try:
            self._pool = await asyncpg.create_pool(
                host=self._settings.db_host,
                port=self._settings.db_port,
                database=self._settings.db_name,
                user=self._settings.db_user,
                password=self._settings.db_password,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            logger.info("Database connection pool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            raise
    
    async def close(self) -> None:
        """Close the database connection pool."""
        if self._pool:
            await self._pool.close()
            logger.info("Database connection pool closed")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get a database connection from the pool."""
        if not self._pool:
            await self.initialize()
        
        async with self._pool.acquire() as connection:
            yield connection
    
    async def execute(self, query: str, *args) -> str:
        """Execute a query and return the result."""
        async with self.get_connection() as conn:
            return await conn.execute(query, *args)
    
    async def fetch(self, query: str, *args) -> list:
        """Fetch rows from a query."""
        async with self.get_connection() as conn:
            return await conn.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args) -> Optional[asyncpg.Record]:
        """Fetch a single row from a query."""
        async with self.get_connection() as conn:
            return await conn.fetchrow(query, *args)
    
    async def fetchval(self, query: str, *args) -> Any:
        """Fetch a single value from a query."""
        async with self.get_connection() as conn:
            return await conn.fetchval(query, *args)
    
    async def health_check(self) -> bool:
        """Check if the database is healthy."""
        try:
            result = await self.fetchval("SELECT 1")
            return result == 1
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

# Global database manager instance
_db_manager: Optional[DatabaseManager] = None

async def get_db_manager() -> DatabaseManager:
    """Get the global database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
        await _db_manager.initialize()
    return _db_manager

async def get_db_connection():
    """Get a database connection from the global pool."""
    db_manager = await get_db_manager()
    return db_manager.get_connection()

async def close_db_connection() -> None:
    """Close the global database connection pool."""
    global _db_manager
    if _db_manager:
        await _db_manager.close()
        _db_manager = None

# FastAPI dependency for database connections
async def get_db():
    """FastAPI dependency for database connections."""
    async with get_db_connection() as conn:
        yield conn
