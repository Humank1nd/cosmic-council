"""
Database connection management for the Agent Orchestrator system.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, StaticPool
from sqlalchemy.exc import SQLAlchemyError

from ..utils.config import get_config

logger = logging.getLogger(__name__)

# Global connection instances
_connection: Optional['DatabaseConnection'] = None


class DatabaseConnection:
    """Database connection manager"""
    
    def __init__(self, database_url: str, config: Optional[Dict[str, Any]] = None):
        self.database_url = database_url
        self.config = config or {}
        self.engine = None
        self.async_engine = None
        self.SessionLocal = None
        self.AsyncSessionLocal = None
        self._initialized = False
    
    def initialize(self) -> None:
        """Initialize database connections"""
        if self._initialized:
            return
        
        try:
            # Create sync engine
            self.engine = create_engine(
                self.database_url,
                poolclass=QueuePool if 'sqlite' not in self.database_url else StaticPool,
                pool_size=self.config.get('pool_size', 10),
                max_overflow=self.config.get('max_overflow', 20),
                pool_pre_ping=True,
                echo=self.config.get('echo', False)
            )
            
            # Create async engine
            if self.database_url.startswith('sqlite'):
                # SQLite async configuration
                self.async_engine = create_async_engine(
                    self.database_url.replace('sqlite://', 'sqlite+aiosqlite://'),
                    poolclass=StaticPool,
                    connect_args={"check_same_thread": False},
                    echo=self.config.get('echo', False)
                )
            else:
                # PostgreSQL/MySQL async configuration
                self.async_engine = create_async_engine(
                    self.database_url,
                    pool_size=self.config.get('pool_size', 10),
                    max_overflow=self.config.get('max_overflow', 20),
                    pool_pre_ping=True,
                    echo=self.config.get('echo', False)
                )
            
            # Create session factories
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            self.AsyncSessionLocal = async_sessionmaker(
                self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            self._initialized = True
            logger.info("Database connection initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database connection: {e}")
            raise
    
    @asynccontextmanager
    async def get_async_session(self):
        """Get async database session"""
        if not self._initialized:
            self.initialize()
        
        async with self.AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    @asynccontextmanager
    def get_sync_session(self):
        """Get sync database session"""
        if not self._initialized:
            self.initialize()
        
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    async def create_tables(self) -> None:
        """Create all database tables"""
        try:
            from .models.base import Base
            async with self.async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
        except SQLAlchemyError as e:
            logger.error(f"Error creating database tables: {e}")
            raise
    
    async def drop_tables(self) -> None:
        """Drop all database tables"""
        try:
            from .models.base import Base
            async with self.async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
            logger.info("Database tables dropped successfully")
        except SQLAlchemyError as e:
            logger.error(f"Error dropping database tables: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check database connection health"""
        try:
            async with self.get_async_session() as session:
                await session.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def close(self) -> None:
        """Close database connections"""
        if self.engine:
            self.engine.dispose()
        if self.async_engine:
            asyncio.create_task(self.async_engine.dispose())
        logger.info("Database connections closed")


def get_database_connection() -> DatabaseConnection:
    """Get the global database connection instance"""
    global _connection
    
    if _connection is None:
        config = get_config()
        database_url = config.get('database_url', 'sqlite:///cosmic_council.db')
        db_config = {
            'pool_size': config.get('database_pool_size', 10),
            'max_overflow': config.get('database_max_overflow', 20),
            'echo': config.get('debug', False)
        }
        
        _connection = DatabaseConnection(database_url, db_config)
        _connection.initialize()
    
    return _connection


def set_database_connection(connection: DatabaseConnection) -> None:
    """Set the global database connection instance"""
    global _connection
    _connection = connection


async def initialize_database() -> None:
    """Initialize the database with tables"""
    connection = get_database_connection()
    await connection.create_tables()


async def close_database() -> None:
    """Close database connections"""
    global _connection
    if _connection:
        _connection.close()
        _connection = None
