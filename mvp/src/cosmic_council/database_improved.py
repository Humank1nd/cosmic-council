"""
Cosmic Council Production Database Layer
Production-grade database with connection pooling, transactions, and proper error handling.
"""

import sqlite3
import json
import logging
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any, ContextManager
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
import aiosqlite
import asyncio

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """Database configuration."""
    db_path: str = "cosmic_council_production.db"
    pool_size: int = 10
    timeout: float = 30.0
    check_same_thread: bool = False
    enable_wal_mode: bool = True
    enable_foreign_keys: bool = True


class DatabaseConnectionPool:
    """Thread-safe database connection pool."""
    
    def __init__(self, config: DatabaseConfig):
        """Initialize the connection pool."""
        self.config = config
        self._pool = []
        self._lock = threading.Lock()
        self._initialized = False
        
        logger.info(f"🗄️ Database pool initialized: {config.db_path}")
    
    def _initialize_pool(self):
        """Initialize the connection pool."""
        if self._initialized:
            return
        
        with self._lock:
            if self._initialized:
                return
            
            # Create database directory if it doesn't exist
            db_path = Path(self.config.db_path)
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Initialize pool with connections
            for _ in range(self.config.pool_size):
                conn = self._create_connection()
                self._pool.append(conn)
            
            self._initialized = True
            logger.info(f"✅ Database pool initialized with {self.config.pool_size} connections")
    
    def _create_connection(self) -> sqlite3.Connection:
        """Create a new database connection."""
        conn = sqlite3.connect(
            self.config.db_path,
            timeout=self.config.timeout,
            check_same_thread=self.config.check_same_thread
        )
        
        # Enable WAL mode for better concurrency
        if self.config.enable_wal_mode:
            conn.execute("PRAGMA journal_mode=WAL")
        
        # Enable foreign keys
        if self.config.enable_foreign_keys:
            conn.execute("PRAGMA foreign_keys=ON")
        
        # Set other performance optimizations
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=10000")
        conn.execute("PRAGMA temp_store=MEMORY")
        
        return conn
    
    @contextmanager
    def get_connection(self) -> ContextManager[sqlite3.Connection]:
        """Get a connection from the pool."""
        self._initialize_pool()
        
        conn = None
        try:
            with self._lock:
                if self._pool:
                    conn = self._pool.pop()
                else:
                    # Pool exhausted, create new connection
                    conn = self._create_connection()
            
            yield conn
            
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database operation failed: {e}")
            raise
        finally:
            if conn:
                try:
                    conn.commit()
                    with self._lock:
                        if len(self._pool) < self.config.pool_size:
                            self._pool.append(conn)
                        else:
                            conn.close()
                except Exception as e:
                    logger.error(f"Error returning connection to pool: {e}")
                    conn.close()
    
    def close_all(self):
        """Close all connections in the pool."""
        with self._lock:
            for conn in self._pool:
                try:
                    conn.close()
                except Exception as e:
                    logger.error(f"Error closing connection: {e}")
            self._pool.clear()
            self._initialized = False


class ProductionDatabase:
    """Production-grade database with proper error handling and transactions."""
    
    def __init__(self, config: DatabaseConfig = None):
        """Initialize the production database."""
        self.config = config or DatabaseConfig()
        self.pool = DatabaseConnectionPool(self.config)
        self._initialize_schema()
        
        logger.info("🏗️ Production database initialized")
    
    def _initialize_schema(self):
        """Initialize the database schema with proper indexes and constraints."""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Problems table with proper constraints
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS problems (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    problem_text TEXT NOT NULL CHECK(length(problem_text) > 0),
                    problem_hash TEXT UNIQUE NOT NULL,
                    complexity_level TEXT DEFAULT 'medium' CHECK(complexity_level IN ('low', 'medium', 'high')),
                    domain TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'processing', 'completed', 'failed')),
                    metadata TEXT DEFAULT '{}'
                )
            ''')
            
            # Solutions table with foreign key constraints
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS solutions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    problem_id INTEGER NOT NULL,
                    enterprise_name TEXT NOT NULL CHECK(length(enterprise_name) > 0),
                    solution_text TEXT NOT NULL CHECK(length(solution_text) > 0),
                    confidence_score REAL DEFAULT 0.0 CHECK(confidence_score >= 0.0 AND confidence_score <= 1.0),
                    processing_time REAL DEFAULT 0.0,
                    tokens_used INTEGER DEFAULT 0,
                    cost REAL DEFAULT 0.0,
                    sources TEXT DEFAULT '[]',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (problem_id) REFERENCES problems (id) ON DELETE CASCADE
                )
            ''')
            
            # Problem sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS problem_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    problem_id INTEGER NOT NULL,
                    session_hash TEXT UNIQUE NOT NULL,
                    all_solutions TEXT NOT NULL,
                    total_confidence REAL DEFAULT 0.0,
                    total_processing_time REAL DEFAULT 0.0,
                    total_tokens_used INTEGER DEFAULT 0,
                    total_cost REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (problem_id) REFERENCES problems (id) ON DELETE CASCADE
                )
            ''')
            
            # Performance metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    metric_unit TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT DEFAULT '{}'
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_problems_hash ON problems(problem_hash)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_problems_status ON problems(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_problems_created ON problems(created_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_solutions_problem_id ON solutions(problem_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_solutions_enterprise ON solutions(enterprise_name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_problem_id ON problem_sessions(problem_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_name ON performance_metrics(metric_name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON performance_metrics(timestamp)')
            
            # Create triggers for updated_at timestamps
            cursor.execute('''
                CREATE TRIGGER IF NOT EXISTS update_problems_timestamp 
                AFTER UPDATE ON problems
                BEGIN
                    UPDATE problems SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
                END
            ''')
            
            conn.commit()
            logger.info("✅ Database schema initialized with indexes and constraints")
    
    def save_problem(self, problem: str, domain: str = None, complexity: str = "medium") -> int:
        """Save a problem with proper validation and return its ID."""
        if not problem or not problem.strip():
            raise ValueError("Problem text cannot be empty")
        
        problem_hash = self._generate_hash(problem)
        
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if problem already exists
            cursor.execute("SELECT id FROM problems WHERE problem_hash = ?", (problem_hash,))
            existing = cursor.fetchone()
            
            if existing:
                logger.info(f"Problem already exists with ID: {existing[0]}")
                return existing[0]
            
            # Insert new problem
            cursor.execute('''
                INSERT INTO problems (problem_text, problem_hash, domain, complexity_level, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (problem.strip(), problem_hash, domain, complexity, json.dumps({"source": "api"})))
            
            problem_id = cursor.lastrowid
            logger.info(f"💾 Problem saved with ID: {problem_id}")
            return problem_id
    
    def save_solution(self, problem_id: int, enterprise_name: str, solution: str, 
                     confidence: float = 0.0, processing_time: float = 0.0, 
                     tokens_used: int = 0, cost: float = 0.0, sources: List[str] = None) -> int:
        """Save a solution with comprehensive metadata."""
        if not solution or not solution.strip():
            raise ValueError("Solution text cannot be empty")
        
        sources_json = json.dumps(sources or [])
        
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO solutions (problem_id, enterprise_name, solution_text, 
                                    confidence_score, processing_time, tokens_used, cost, sources)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (problem_id, enterprise_name, solution.strip(), confidence, 
                  processing_time, tokens_used, cost, sources_json))
            
            solution_id = cursor.lastrowid
            logger.info(f"💾 Solution saved for {enterprise_name} (ID: {solution_id})")
            return solution_id
    
    def save_problem_session(self, problem_id: int, all_solutions: Dict[str, str], 
                           session_metrics: Dict[str, Any] = None) -> int:
        """Save a complete problem-solving session with metrics."""
        session_hash = self._generate_hash(f"{problem_id}_{datetime.now().isoformat()}")
        solutions_json = json.dumps(all_solutions)
        
        # Calculate session metrics
        total_confidence = session_metrics.get('total_confidence', 0.0)
        total_processing_time = session_metrics.get('total_processing_time', 0.0)
        total_tokens_used = session_metrics.get('total_tokens_used', 0)
        total_cost = session_metrics.get('total_cost', 0.0)
        
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO problem_sessions (problem_id, session_hash, all_solutions,
                                            total_confidence, total_processing_time, 
                                            total_tokens_used, total_cost)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (problem_id, session_hash, solutions_json, total_confidence,
                  total_processing_time, total_tokens_used, total_cost))
            
            session_id = cursor.lastrowid
            logger.info(f"💾 Problem session saved with ID: {session_id}")
            return session_id
    
    def get_problem(self, problem_id: int) -> Optional[Dict[str, Any]]:
        """Get a problem by ID with full details."""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, problem_text, problem_hash, complexity_level, domain, 
                       created_at, updated_at, status, metadata
                FROM problems WHERE id = ?
            ''', (problem_id,))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    "id": row[0],
                    "problem_text": row[1],
                    "problem_hash": row[2],
                    "complexity_level": row[3],
                    "domain": row[4],
                    "created_at": row[5],
                    "updated_at": row[6],
                    "status": row[7],
                    "metadata": json.loads(row[8]) if row[8] else {}
                }
            return None
    
    def get_solutions_for_problem(self, problem_id: int) -> List[Dict[str, Any]]:
        """Get all solutions for a problem with full metadata."""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT enterprise_name, solution_text, confidence_score, 
                       processing_time, tokens_used, cost, sources, created_at
                FROM solutions WHERE problem_id = ? ORDER BY created_at
            ''', (problem_id,))
            
            rows = cursor.fetchall()
            
            return [
                {
                    "enterprise_name": row[0],
                    "solution_text": row[1],
                    "confidence_score": row[2],
                    "processing_time": row[3],
                    "tokens_used": row[4],
                    "cost": row[5],
                    "sources": json.loads(row[6]) if row[6] else [],
                    "created_at": row[7]
                }
                for row in rows
            ]
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics."""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Basic counts
            cursor.execute("SELECT COUNT(*) FROM problems")
            problem_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM solutions")
            solution_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM problem_sessions")
            session_count = cursor.fetchone()[0]
            
            # Performance metrics
            cursor.execute("SELECT AVG(confidence_score) FROM solutions WHERE confidence_score > 0")
            avg_confidence = cursor.fetchone()[0] or 0.0
            
            cursor.execute("SELECT SUM(total_cost) FROM problem_sessions")
            total_cost = cursor.fetchone()[0] or 0.0
            
            cursor.execute("SELECT SUM(total_tokens_used) FROM problem_sessions")
            total_tokens = cursor.fetchone()[0] or 0
            
            return {
                "problems": problem_count,
                "solutions": solution_count,
                "sessions": session_count,
                "average_confidence": round(avg_confidence, 3),
                "total_cost": round(total_cost, 4),
                "total_tokens": total_tokens,
                "pool_size": self.config.pool_size,
                "database_path": self.config.db_path
            }
    
    def record_performance_metric(self, metric_name: str, metric_value: float, 
                                metric_unit: str = None, metadata: Dict[str, Any] = None):
        """Record a performance metric."""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_metrics (metric_name, metric_value, metric_unit, metadata)
                VALUES (?, ?, ?, ?)
            ''', (metric_name, metric_value, metric_unit, json.dumps(metadata or {})))
            
            logger.debug(f"📊 Performance metric recorded: {metric_name} = {metric_value}")
    
    def _generate_hash(self, text: str) -> str:
        """Generate a hash for the given text."""
        import hashlib
        return hashlib.sha256(text.encode()).hexdigest()[:16]
    
    def close(self):
        """Close the database and all connections."""
        self.pool.close_all()
        logger.info("🔒 Database connections closed")
