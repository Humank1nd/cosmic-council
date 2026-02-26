"""
Strategy Persistence Store
==========================

Persistent storage for strategy profiles, versions, and outcomes.

Backends:
- SQLite: Default, file-based
- PostgreSQL: Production-grade
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .registry import (
    AgentRole,
    StrategyProfile,
    StrategyVersion,
)
from .outcomes import CycleOutcome, OutcomeType
from .optimizer import StrategyUpdate

logger = logging.getLogger(__name__)


class StrategyStore(ABC):
    """Abstract base class for strategy storage."""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the store."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the store."""
        pass

    # Profile operations
    @abstractmethod
    async def save_profile(self, profile: StrategyProfile) -> None:
        """Save a strategy profile."""
        pass

    @abstractmethod
    async def get_profile(self, role: AgentRole) -> Optional[StrategyProfile]:
        """Get current profile for a role."""
        pass

    @abstractmethod
    async def get_all_profiles(self) -> Dict[AgentRole, StrategyProfile]:
        """Get all current profiles."""
        pass

    # Version operations
    @abstractmethod
    async def save_version(self, version: StrategyVersion) -> None:
        """Save a strategy version."""
        pass

    @abstractmethod
    async def get_version(self, role: AgentRole, version: int) -> Optional[StrategyVersion]:
        """Get a specific version."""
        pass

    @abstractmethod
    async def get_version_history(
        self,
        role: AgentRole,
        limit: int = 10,
    ) -> List[StrategyVersion]:
        """Get version history for a role."""
        pass

    # Outcome operations
    @abstractmethod
    async def save_outcome(self, outcome: CycleOutcome) -> None:
        """Save a cycle outcome."""
        pass

    @abstractmethod
    async def get_outcomes(
        self,
        role: AgentRole,
        since: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[CycleOutcome]:
        """Get outcomes for a role."""
        pass

    # Update operations
    @abstractmethod
    async def save_update(self, update: StrategyUpdate) -> None:
        """Save a strategy update record."""
        pass

    @abstractmethod
    async def get_updates(
        self,
        role: Optional[AgentRole] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> List[StrategyUpdate]:
        """Get update records."""
        pass


class SQLiteStrategyStore(StrategyStore):
    """SQLite-based strategy store."""

    def __init__(self, db_path: str = "data/strategy_store.db"):
        self._db_path = Path(db_path)
        self._lock = asyncio.Lock()
        self._conn = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize SQLite database."""
        if self._initialized:
            return

        import aiosqlite

        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = await aiosqlite.connect(self._db_path)

        # Create tables
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                role TEXT PRIMARY KEY,
                version INTEGER NOT NULL,
                profile_data TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                version INTEGER NOT NULL,
                profile_data TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                created_by TEXT NOT NULL,
                update_reason TEXT,
                parent_version INTEGER,
                success_rate REAL,
                avg_score REAL,
                sample_size INTEGER DEFAULT 0,
                UNIQUE(role, version)
            )
        """)

        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS outcomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cycle_id TEXT NOT NULL,
                problem_id TEXT NOT NULL,
                role TEXT NOT NULL,
                outcome_type TEXT NOT NULL,
                started_at TEXT NOT NULL,
                completed_at TEXT NOT NULL,
                duration_ms REAL NOT NULL,
                success INTEGER NOT NULL,
                confidence_reported REAL NOT NULL,
                confidence_actual REAL,
                iteration_count INTEGER DEFAULT 1,
                rework_count INTEGER DEFAULT 0,
                human_intervention INTEGER DEFAULT 0,
                intervention_type TEXT,
                user_rating REAL,
                user_feedback TEXT,
                outcome_data TEXT NOT NULL
            )
        """)

        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS updates (
                id TEXT PRIMARY KEY,
                role TEXT NOT NULL,
                update_type TEXT NOT NULL,
                risk TEXT NOT NULL,
                field_name TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                delta REAL DEFAULT 0,
                triggered_by TEXT NOT NULL,
                reason TEXT,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                applied_at TEXT,
                approved_by TEXT,
                metrics_snapshot TEXT,
                scorecard_snapshot TEXT
            )
        """)

        # Create indexes
        await self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_versions_role ON versions(role, version DESC)"
        )
        await self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_outcomes_role ON outcomes(role, completed_at DESC)"
        )
        await self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_updates_role ON updates(role, created_at DESC)"
        )
        await self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_updates_status ON updates(status)"
        )

        await self._conn.commit()
        self._initialized = True
        logger.info(f"SQLite strategy store initialized at {self._db_path}")

    async def close(self) -> None:
        """Close database connection."""
        if self._conn:
            await self._conn.close()
            self._conn = None
            self._initialized = False

    async def save_profile(self, profile: StrategyProfile) -> None:
        """Save a strategy profile."""
        async with self._lock:
            await self._conn.execute(
                """
                INSERT OR REPLACE INTO profiles (role, version, profile_data, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    profile.role.value,
                    profile.version,
                    json.dumps(profile.to_dict()),
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            await self._conn.commit()

    async def get_profile(self, role: AgentRole) -> Optional[StrategyProfile]:
        """Get current profile for a role."""
        async with self._lock:
            cursor = await self._conn.execute(
                "SELECT profile_data FROM profiles WHERE role = ?",
                (role.value,),
            )
            row = await cursor.fetchone()

        if not row:
            return None

        return StrategyProfile.from_dict(json.loads(row[0]))

    async def get_all_profiles(self) -> Dict[AgentRole, StrategyProfile]:
        """Get all current profiles."""
        async with self._lock:
            cursor = await self._conn.execute("SELECT role, profile_data FROM profiles")
            rows = await cursor.fetchall()

        profiles = {}
        for row in rows:
            role = AgentRole(row[0])
            profiles[role] = StrategyProfile.from_dict(json.loads(row[1]))

        return profiles

    async def save_version(self, version: StrategyVersion) -> None:
        """Save a strategy version."""
        async with self._lock:
            await self._conn.execute(
                """
                INSERT OR REPLACE INTO versions (
                    role, version, profile_data, content_hash, created_at,
                    created_by, update_reason, parent_version, success_rate,
                    avg_score, sample_size
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    version.role.value,
                    version.version,
                    json.dumps(version.profile.to_dict()),
                    version.content_hash,
                    version.created_at.isoformat(),
                    version.created_by,
                    version.update_reason,
                    version.parent_version,
                    version.success_rate,
                    version.avg_score,
                    version.sample_size,
                ),
            )
            await self._conn.commit()

    async def get_version(self, role: AgentRole, version: int) -> Optional[StrategyVersion]:
        """Get a specific version."""
        async with self._lock:
            cursor = await self._conn.execute(
                "SELECT * FROM versions WHERE role = ? AND version = ?",
                (role.value, version),
            )
            row = await cursor.fetchone()

        if not row:
            return None

        return self._row_to_version(row)

    def _row_to_version(self, row) -> StrategyVersion:
        """Convert database row to StrategyVersion."""
        return StrategyVersion(
            role=AgentRole(row[1]),
            version=row[2],
            profile=StrategyProfile.from_dict(json.loads(row[3])),
            content_hash=row[4],
            created_at=datetime.fromisoformat(row[5]),
            created_by=row[6],
            update_reason=row[7] or "",
            parent_version=row[8],
            success_rate=row[9],
            avg_score=row[10],
            sample_size=row[11] or 0,
        )

    async def get_version_history(
        self,
        role: AgentRole,
        limit: int = 10,
    ) -> List[StrategyVersion]:
        """Get version history for a role."""
        async with self._lock:
            cursor = await self._conn.execute(
                """
                SELECT * FROM versions
                WHERE role = ?
                ORDER BY version DESC
                LIMIT ?
                """,
                (role.value, limit),
            )
            rows = await cursor.fetchall()

        return [self._row_to_version(row) for row in rows]

    async def save_outcome(self, outcome: CycleOutcome) -> None:
        """Save a cycle outcome."""
        async with self._lock:
            await self._conn.execute(
                """
                INSERT INTO outcomes (
                    cycle_id, problem_id, role, outcome_type, started_at,
                    completed_at, duration_ms, success, confidence_reported,
                    confidence_actual, iteration_count, rework_count,
                    human_intervention, intervention_type, user_rating,
                    user_feedback, outcome_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    outcome.cycle_id,
                    outcome.problem_id,
                    outcome.role.value,
                    outcome.outcome_type.value,
                    outcome.started_at.isoformat(),
                    outcome.completed_at.isoformat(),
                    outcome.duration_ms,
                    1 if outcome.success else 0,
                    outcome.confidence_reported,
                    outcome.confidence_actual,
                    outcome.iteration_count,
                    outcome.rework_count,
                    1 if outcome.human_intervention else 0,
                    outcome.intervention_type,
                    outcome.user_rating,
                    outcome.user_feedback,
                    json.dumps(outcome.to_dict()),
                ),
            )
            await self._conn.commit()

    async def get_outcomes(
        self,
        role: AgentRole,
        since: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[CycleOutcome]:
        """Get outcomes for a role."""
        conditions = ["role = ?"]
        params = [role.value]

        if since:
            conditions.append("completed_at >= ?")
            params.append(since.isoformat())

        where_clause = " AND ".join(conditions)
        sql = f"""
            SELECT outcome_data FROM outcomes
            WHERE {where_clause}
            ORDER BY completed_at DESC
            LIMIT ?
        """
        params.append(limit)

        async with self._lock:
            cursor = await self._conn.execute(sql, params)
            rows = await cursor.fetchall()

        outcomes = []
        for row in rows:
            data = json.loads(row[0])
            outcomes.append(CycleOutcome(
                cycle_id=data["cycle_id"],
                problem_id=data["problem_id"],
                role=AgentRole(data["role"]),
                outcome_type=OutcomeType(data["outcome_type"]),
                started_at=datetime.fromisoformat(data["started_at"]),
                completed_at=datetime.fromisoformat(data["completed_at"]),
                duration_ms=data["duration_ms"],
                success=data["success"],
                confidence_reported=data["confidence_reported"],
                confidence_actual=data.get("confidence_actual"),
                iteration_count=data.get("iteration_count", 1),
                rework_count=data.get("rework_count", 0),
                human_intervention=data.get("human_intervention", False),
                intervention_type=data.get("intervention_type"),
                user_rating=data.get("user_rating"),
                user_feedback=data.get("user_feedback"),
                errors=data.get("errors", []),
                warnings=data.get("warnings", []),
                tools_used=data.get("tools_used", []),
                tool_success_rates=data.get("tool_success_rates", {}),
                memory_queries=data.get("memory_queries", 0),
                memory_hit_rate=data.get("memory_hit_rate", 0.0),
            ))

        return outcomes

    async def save_update(self, update: StrategyUpdate) -> None:
        """Save a strategy update record."""
        async with self._lock:
            await self._conn.execute(
                """
                INSERT OR REPLACE INTO updates (
                    id, role, update_type, risk, field_name, old_value,
                    new_value, delta, triggered_by, reason, status,
                    created_at, applied_at, approved_by, metrics_snapshot,
                    scorecard_snapshot
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    update.id,
                    update.role.value,
                    update.update_type.value,
                    update.risk.value,
                    update.field_name,
                    json.dumps(update.old_value) if update.old_value is not None else None,
                    json.dumps(update.new_value) if update.new_value is not None else None,
                    update.delta,
                    update.triggered_by,
                    update.reason,
                    update.status,
                    update.created_at.isoformat(),
                    update.applied_at.isoformat() if update.applied_at else None,
                    update.approved_by,
                    json.dumps(update.metrics_snapshot) if update.metrics_snapshot else None,
                    json.dumps(update.scorecard_snapshot) if update.scorecard_snapshot else None,
                ),
            )
            await self._conn.commit()

    async def get_updates(
        self,
        role: Optional[AgentRole] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> List[StrategyUpdate]:
        """Get update records."""
        conditions = []
        params = []

        if role:
            conditions.append("role = ?")
            params.append(role.value)

        if status:
            conditions.append("status = ?")
            params.append(status)

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        sql = f"""
            SELECT * FROM updates
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ?
        """
        params.append(limit)

        async with self._lock:
            cursor = await self._conn.execute(sql, params)
            rows = await cursor.fetchall()

        updates = []
        for row in rows:
            from .optimizer import UpdateType, UpdateRisk

            updates.append(StrategyUpdate(
                id=row[0],
                role=AgentRole(row[1]),
                update_type=UpdateType(row[2]),
                risk=UpdateRisk(row[3]),
                field_name=row[4],
                old_value=json.loads(row[5]) if row[5] else None,
                new_value=json.loads(row[6]) if row[6] else None,
                delta=row[7] or 0,
                triggered_by=row[8],
                reason=row[9] or "",
                status=row[10],
                created_at=datetime.fromisoformat(row[11]),
                applied_at=datetime.fromisoformat(row[12]) if row[12] else None,
                approved_by=row[13],
                metrics_snapshot=json.loads(row[14]) if row[14] else None,
                scorecard_snapshot=json.loads(row[15]) if row[15] else None,
            ))

        return updates

    async def get_outcome_stats(
        self,
        role: AgentRole,
        days: int = 30,
    ) -> Dict[str, Any]:
        """Get aggregate outcome statistics for a role."""
        from datetime import timedelta
        since = datetime.now(timezone.utc) - timedelta(days=days)

        async with self._lock:
            cursor = await self._conn.execute(
                """
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successes,
                    AVG(duration_ms) as avg_duration,
                    AVG(confidence_reported) as avg_confidence,
                    AVG(user_rating) as avg_rating,
                    SUM(CASE WHEN human_intervention = 1 THEN 1 ELSE 0 END) as interventions
                FROM outcomes
                WHERE role = ? AND completed_at >= ?
                """,
                (role.value, since.isoformat()),
            )
            row = await cursor.fetchone()

        if not row or row[0] == 0:
            return {"sample_size": 0}

        return {
            "sample_size": row[0],
            "success_rate": row[1] / row[0] if row[0] > 0 else 0,
            "avg_duration_ms": row[2],
            "avg_confidence": row[3],
            "avg_rating": row[4],
            "intervention_rate": row[5] / row[0] if row[0] > 0 else 0,
        }
