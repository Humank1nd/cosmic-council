"""
Unified Database Manager for Cosmic Council System
Consolidates database connection, operations, setup, and management functionality.

This is the primary and only database management file - all other database management files
should import from this unified implementation.
"""

import os
import asyncio
import logging
from typing import Optional, Generator, Dict, Any, List, Tuple
from contextlib import contextmanager, asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
import uuid

from sqlalchemy import create_engine, text, and_, or_, desc, asc, func
from sqlalchemy.orm import sessionmaker, Session, joinedload
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import QueuePool, StaticPool
from sqlalchemy.exc import SQLAlchemyError
import sqlite3

# Import the unified database models and service
from ..core.models import Base
from .unified_database_service import UnifiedDatabaseService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UnifiedDatabaseManager:
    """Unified database connection, session, and operations management"""
    
    def __init__(self, database_url: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize unified database manager
        
        Args:
            database_url: Database connection URL. If None, uses environment variables or defaults
            config: Configuration dictionary for database settings
        """
        self.database_url = database_url or self._get_database_url()
        self.config = config or {}
        self.engine = None
        self.async_engine = None
        self.SessionLocal = None
        self.AsyncSessionLocal = None
        self.unified_service = None
        self._initialize_engines()
    
    def _get_database_url(self) -> str:
        """Get database URL from environment variables or use default"""
        # Try to get from environment variables
        db_url = os.getenv('DATABASE_URL')
        if db_url:
            return db_url
        
        # Get individual components
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432')
        db_name = os.getenv('DB_NAME', 'cosmic_council')
        db_user = os.getenv('DB_USER', 'cosmic_council')
        db_password = os.getenv('DB_PASSWORD', 'cosmic_council')
        
        # Use SQLite for development (no external database required)
        return "sqlite+aiosqlite:///./cosmic_council.db"
    
    def _initialize_engines(self):
        """Initialize database engines"""
        try:
            if self.database_url.startswith("sqlite"):
                self._setup_sqlite()
            else:
                self._setup_postgresql()
            
            # Initialize unified service
            self.unified_service = UnifiedDatabaseService(self.database_url)
            
            logger.info("✅ Unified Database Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise
    
    def _setup_sqlite(self):
        """Setup SQLite database"""
        # Normalize file path from URL
        url = self.database_url
        if url.startswith("sqlite+aiosqlite:///"):
            raw_path = url[len("sqlite+aiosqlite:///"):]
        elif url.startswith("sqlite:///"):
            raw_path = url[len("sqlite///"):]
        else:
            # Fallback: take part after scheme
            raw_path = url.split("://")[-1]

        db_path = Path(raw_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        # Create synchronous engine (use sqlite:/// path)
        if url.startswith("sqlite+aiosqlite:///"):
            sync_url = "sqlite:///" + raw_path
        else:
            sync_url = url
        self.engine = create_engine(
            sync_url,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
            echo=self.config.get('echo', False)
        )

        # Create async engine (use sqlite+aiosqlite:/// path)
        if url.startswith("sqlite+aiosqlite:///"):
            async_url = url
        elif url.startswith("sqlite:///"):
            async_url = url.replace("sqlite///", "sqlite+aiosqlite///")
        else:
            async_url = "sqlite+aiosqlite:///" + raw_path
        self.async_engine = create_async_engine(
            async_url,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
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
        
        logger.info("✅ SQLite database engines initialized")
    
    def _setup_postgresql(self):
        """Setup PostgreSQL database"""
        # Create synchronous engine
        self.engine = create_engine(
            self.database_url,
            poolclass=QueuePool,
            pool_size=self.config.get('pool_size', 10),
            max_overflow=self.config.get('max_overflow', 20),
            pool_pre_ping=True,
            echo=self.config.get('echo', False)
        )
        
        # Create async engine
        async_url = self.database_url.replace("postgresql://", "postgresql+asyncpg://")
        self.async_engine = create_async_engine(
            async_url,
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
        
        logger.info("✅ PostgreSQL database engines initialized")
    
    # ============================================================================
    # SESSION MANAGEMENT
    # ============================================================================
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get a synchronous database session"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    @asynccontextmanager
    async def get_async_session(self) -> Generator[AsyncSession, None, None]:
        """Get an asynchronous database session"""
        session = self.AsyncSessionLocal()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    # ============================================================================
    # DATABASE SETUP AND MIGRATION
    # ============================================================================
    
    async def create_tables(self):
        """Create all database tables"""
        try:
            # Use the unified service to create tables
            await self.unified_service.create_tables()
            logger.info("✅ All database tables created successfully")
        except SQLAlchemyError as e:
            logger.error(f"❌ Error creating database tables: {e}")
            raise
    
    async def drop_tables(self):
        """Drop all database tables"""
        try:
            # Use the unified service to drop tables
            await self.unified_service.drop_tables()
            logger.info("✅ All database tables dropped successfully")
        except SQLAlchemyError as e:
            logger.error(f"❌ Error dropping database tables: {e}")
            raise
    
    def setup_database(self):
        """Setup database connection and create tables if needed"""
        try:
            # Test connection
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            
            logger.info("✅ Database setup completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Database setup failed: {e}")
            raise
    
    # ============================================================================
    # HEALTH CHECK AND MONITORING
    # ============================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a comprehensive health check on the database"""
        try:
            # Use the unified service health check
            health_status = await self.unified_service.health_check()
            
            # Add additional checks
            with self.get_session() as session:
                # Test basic connectivity
                result = session.execute(text("SELECT 1"))
                basic_connectivity = result.scalar() == 1
                
                # Test table access (dialect-aware)
                if self.database_url.startswith('sqlite'):
                    result = session.execute(text("SELECT COUNT(*) FROM sqlite_master WHERE type='table'"))
                else:
                    result = session.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"))
                table_count = result.scalar() or 0
            
            health_status.update({
                'basic_connectivity': basic_connectivity,
                'table_count': table_count,
                'database_url': self.database_url.split('@')[-1] if '@' in self.database_url else 'local',
                'engine_status': 'active' if self.engine else 'inactive',
                'async_engine_status': 'active' if self.async_engine else 'inactive'
            })
            
            return health_status
            
        except Exception as e:
            logger.error(f"❌ Database health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'basic_connectivity': False,
                'table_count': 0
            }
    
    # ============================================================================
    # UNIFIED SERVICE ACCESS
    # ============================================================================
    
    def get_unified_service(self) -> UnifiedDatabaseService:
        """Get the unified database service instance"""
        return self.unified_service
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    async def close(self):
        """Close all database connections"""
        try:
            if self.unified_service:
                await self.unified_service.close()
            
            if self.async_engine:
                await self.async_engine.dispose()
            
            if self.engine:
                self.engine.dispose()
            
            logger.info("✅ All database connections closed")
            
        except Exception as e:
            logger.error(f"❌ Error closing database connections: {e}")
            raise
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database connection information"""
        return {
            'database_url': self.database_url.split('@')[-1] if '@' in self.database_url else self.database_url,
            'database_type': 'sqlite' if self.database_url.startswith('sqlite') else 'postgresql',
            'has_sync_engine': self.engine is not None,
            'has_async_engine': self.async_engine is not None,
            'has_unified_service': self.unified_service is not None,
            'config': self.config
        }
    
    def check_connection(self) -> bool:
        """Check if database connection is healthy"""
        try:
            if self.unified_service:
                # Use the unified service health check
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    health_result = loop.run_until_complete(self.unified_service.health_check())
                    return health_result.get('healthy', False)
                finally:
                    loop.close()
            else:
                # Basic check - if we have engines, assume healthy
                return self.engine is not None or self.async_engine is not None
        except Exception:
            return False

# ============================================================================
# BACKWARD COMPATIBILITY WRAPPERS
# ============================================================================

class DatabaseManager:
    """
    Backward compatibility wrapper for the original DatabaseManager.
    This class provides the same interface as the original but uses the unified implementation.
    """
    
    def __init__(self, database_url: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """Initialize with backward compatibility"""
        self.unified_manager = UnifiedDatabaseManager(database_url, config)
        self.database_url = self.unified_manager.database_url
        self.engine = self.unified_manager.engine
        self.SessionLocal = self.unified_manager.SessionLocal
        logger.info("🗄️ Database Manager (backward compatibility) initialized")
    
    def setup_database(self):
        """Setup database connection"""
        return self.unified_manager.setup_database()
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session"""
        return self.unified_manager.get_session()
    
    @contextmanager
    def get_session_context(self) -> Generator[Session, None, None]:
        """Get a database session (alternative method name)"""
        return self.unified_manager.get_session()
    
    def create_tables(self):
        """Create all database tables (synchronous version)"""
        # This is a synchronous wrapper around the async method
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.unified_manager.create_tables())
        finally:
            loop.close()
    
    def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the database (synchronous version)"""
        # This is a synchronous wrapper around the async method
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.unified_manager.health_check())
        finally:
            loop.close()
    
    def check_connection(self) -> bool:
        """Check if database connection is healthy"""
        try:
            health_result = self.health_check()
            return health_result.get('healthy', False)
        except Exception:
            return False
    
    def close(self):
        """Close database connections (synchronous version)"""
        # This is a synchronous wrapper around the async method
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.unified_manager.close())
        finally:
            loop.close()

# ============================================================================
# GLOBAL INSTANCE AND UTILITY FUNCTIONS
# ============================================================================

# Global database manager instance
_global_db_manager: Optional[UnifiedDatabaseManager] = None

def get_database_manager(database_url: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> UnifiedDatabaseManager:
    """Get or create the global database manager instance"""
    global _global_db_manager
    if _global_db_manager is None:
        _global_db_manager = UnifiedDatabaseManager(database_url, config)
    return _global_db_manager

def get_session_context() -> Generator[Session, None, None]:
    """Get a database session context (backward compatibility)"""
    manager = get_database_manager()
    return manager.get_session()

async def get_async_session_context() -> Generator[AsyncSession, None, None]:
    """Get an async database session context"""
    manager = get_database_manager()
    return manager.get_async_session()

# ============================================================================
# EXPORT ALL CLASSES AND FUNCTIONS
# ============================================================================

__all__ = [
    'UnifiedDatabaseManager',
    'DatabaseManager',  # Backward compatibility
    'get_database_manager',
    'get_session_context',
    'get_async_session_context'
]
