"\"\"\"Memory manager for Agent Orchestrator agents.\"\"\""

import asyncio
import json
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Deque, Dict, List, Optional

import aiosqlite


@dataclass
class SessionEntry:
    agent_type: str
    summary: str
    metadata: Dict[str, Any]
    timestamp: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_type": self.agent_type,
            "summary": self.summary,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }


class ShortTermMemory:
    """In-memory short-term memory for the current problem session."""

    def __init__(self, retention_seconds: int = 600):
        self._retention = timedelta(seconds=retention_seconds)
        self._storage: Dict[str, Deque[SessionEntry]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def record(
        self,
        problem_id: str,
        agent_type: str,
        summary: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        entry = SessionEntry(
            agent_type=agent_type,
            summary=summary,
            metadata=metadata or {},
            timestamp=datetime.now(timezone.utc),
        )
        async with self._lock:
            queue = self._storage[problem_id]
            queue.append(entry)
            self._prune(queue)

    async def retrieve(self, problem_id: str) -> List[Dict[str, Any]]:
        async with self._lock:
            entries = list(self._storage.get(problem_id, []))
        return [entry.to_dict() for entry in entries]

    def _prune(self, queue: Deque[SessionEntry]) -> None:
        cutoff = datetime.now(timezone.utc) - self._retention
        while queue and queue[0].timestamp < cutoff:
            queue.popleft()


class LongTermMemory:
    """Persistent memory stored in SQLite."""

    def __init__(self, db_path: str = "data/cosmic_memory.db"):
        self._db_path = Path(db_path)
        self._lock = asyncio.Lock()
        self._initialized = False

    async def _ensure_tables(self) -> None:
        if self._initialized:
            return
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        async with self._connect() as conn:
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS long_term_learnings (
                    id INTEGER PRIMARY KEY,
                    problem_id TEXT NOT NULL,
                    agent_type TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    metadata TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS shared_knowledge (
                    id INTEGER PRIMARY KEY,
                    topic TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    tags TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            await conn.commit()
        self._initialized = True

    def _connect(self):
        """Return an async context manager for database connection."""
        return aiosqlite.connect(self._db_path)

    async def record_learning(
        self,
        problem_id: str,
        agent_type: str,
        summary: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        await self._ensure_tables()
        async with self._lock:
            async with self._connect() as conn:
                await conn.execute(
                    """
                    INSERT INTO long_term_learnings (
                        problem_id,
                        agent_type,
                        summary,
                        metadata,
                        created_at
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        problem_id,
                        agent_type,
                        summary,
                        json.dumps(metadata or {}),
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                await conn.commit()

    async def query_learnings(
        self,
        agent_type: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        await self._ensure_tables()
        clauses = []
        params: List[Any] = []
        if agent_type:
            clauses.append("agent_type = ?")
            params.append(agent_type)
        where_clause = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        query = f"""
            SELECT problem_id, agent_type, summary, metadata, created_at
            FROM long_term_learnings
            {where_clause}
            ORDER BY created_at DESC
            LIMIT ?
        """
        params.append(limit)

        async with self._lock:
            async with self._connect() as conn:
                cursor = await conn.execute(query, params)
                rows = await cursor.fetchall()

        return [
            {
                "problem_id": row[0],
                "agent_type": row[1],
                "summary": row[2],
                "metadata": json.loads(row[3] or "{}"),
                "created_at": row[4],
            }
            for row in rows
        ]

    async def record_shared_knowledge(
        self,
        topic: str,
        payload: Dict[str, Any],
        tags: Optional[List[str]] = None,
    ) -> None:
        await self._ensure_tables()
        async with self._lock:
            async with self._connect() as conn:
                await conn.execute(
                    """
                    INSERT INTO shared_knowledge (topic, payload, tags, created_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        topic,
                        json.dumps(payload),
                        json.dumps(tags or []),
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                await conn.commit()

    async def query_shared_knowledge(
        self,
        tags: Optional[List[str]] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        await self._ensure_tables()
        where_clause = ""
        params: List[Any] = []
        if tags:
            where_clause = "WHERE tags LIKE ?"
            params.append(f"%{tags[0]}%")
        query = f"""
            SELECT topic, payload, tags, created_at
            FROM shared_knowledge
            {where_clause}
            ORDER BY created_at DESC
            LIMIT ?
        """
        params.append(limit)

        async with self._lock:
            async with self._connect() as conn:
                cursor = await conn.execute(query, params)
                rows = await cursor.fetchall()

        return [
            {
                "topic": row[0],
                "payload": json.loads(row[1]),
                "tags": json.loads(row[2] or "[]"),
                "created_at": row[3],
            }
            for row in rows
        ]


class MemoryManager:
    """Unified memory manager that couples short-term and persistent stores."""

    def __init__(self, retention_seconds: int = 600, db_path: str = "data/cosmic_memory.db"):
        self.session_memory = ShortTermMemory(retention_seconds=retention_seconds)
        self.long_term_memory = LongTermMemory(db_path=db_path)

    async def record_contribution(
        self,
        problem_id: str,
        agent_type: str,
        summary: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        await self.session_memory.record(problem_id, agent_type, summary, metadata)
        await self.long_term_memory.record_learning(problem_id, agent_type, summary, metadata)

    async def get_recent_context(self, problem_id: str) -> List[Dict[str, Any]]:
        return await self.session_memory.retrieve(problem_id)

    async def add_shared_knowledge(
        self,
        topic: str,
        payload: Dict[str, Any],
        tags: Optional[List[str]] = None,
    ) -> None:
        await self.long_term_memory.record_shared_knowledge(topic, payload, tags)

    async def query_shared_knowledge(self, tags: Optional[List[str]] = None, limit: int = 3):
        return await self.long_term_memory.query_shared_knowledge(tags=tags, limit=limit)
