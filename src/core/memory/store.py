"""
Graph Store Abstraction
=======================

Pluggable storage backends for the knowledge graph.

Supported backends:
- SQLite: Default, file-based, suitable for development and single-node
- PostgreSQL: Production-grade, supports concurrent access
- Neo4j: Optional, native graph database for complex traversals
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type

from .schemas import (
    MemoryEntity,
    Relation,
    MemoryFact,
    MemoryQuery,
    MemoryResult,
    EntityType,
    RelationType,
    MemoryLayer,
    AccessLevel,
    MemoryScope,
    Provenance,
    ConfidenceLevel,
)

logger = logging.getLogger(__name__)


class GraphStore(ABC):
    """Abstract base class for graph storage backends."""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the store (create tables, indexes, etc.)."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close connections and cleanup."""
        pass

    # Entity operations
    @abstractmethod
    async def save_entity(self, entity: MemoryEntity) -> str:
        """Save an entity, returns entity ID."""
        pass

    @abstractmethod
    async def get_entity(self, entity_id: str) -> Optional[MemoryEntity]:
        """Get entity by ID."""
        pass

    @abstractmethod
    async def update_entity(self, entity: MemoryEntity) -> bool:
        """Update an existing entity."""
        pass

    @abstractmethod
    async def delete_entity(self, entity_id: str, hard_delete: bool = False) -> bool:
        """Delete or archive an entity."""
        pass

    @abstractmethod
    async def query_entities(self, query: MemoryQuery) -> List[MemoryEntity]:
        """Query entities with filters."""
        pass

    # Relation operations
    @abstractmethod
    async def save_relation(self, relation: Relation) -> str:
        """Save a relation, returns relation ID."""
        pass

    @abstractmethod
    async def get_relation(self, relation_id: str) -> Optional[Relation]:
        """Get relation by ID."""
        pass

    @abstractmethod
    async def get_relations(
        self,
        entity_id: str,
        direction: str = "both",  # "outgoing", "incoming", "both"
        relation_types: Optional[List[RelationType]] = None,
    ) -> List[Relation]:
        """Get relations for an entity."""
        pass

    @abstractmethod
    async def delete_relation(self, relation_id: str) -> bool:
        """Delete a relation."""
        pass

    # Fact operations
    @abstractmethod
    async def save_fact(self, fact: MemoryFact) -> str:
        """Save a memory fact."""
        pass

    @abstractmethod
    async def query_facts(self, query: MemoryQuery) -> List[MemoryFact]:
        """Query facts with filters."""
        pass

    # Graph traversal
    @abstractmethod
    async def traverse(
        self,
        start_id: str,
        relation_types: Optional[List[RelationType]] = None,
        max_depth: int = 3,
        direction: str = "outgoing",
    ) -> Dict[str, Any]:
        """Traverse graph from starting entity."""
        pass

    # Bulk operations
    @abstractmethod
    async def bulk_save_entities(self, entities: List[MemoryEntity]) -> List[str]:
        """Bulk save entities."""
        pass

    @abstractmethod
    async def bulk_save_relations(self, relations: List[Relation]) -> List[str]:
        """Bulk save relations."""
        pass

    # Statistics
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        pass


class SQLiteGraphStore(GraphStore):
    """SQLite-based graph store for development and single-node deployments."""

    def __init__(self, db_path: str = "data/memory_graph.db"):
        self._db_path = Path(db_path)
        self._lock = asyncio.Lock()
        self._initialized = False
        self._conn = None

    async def initialize(self) -> None:
        """Initialize SQLite database with schema."""
        if self._initialized:
            return

        import aiosqlite

        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = await aiosqlite.connect(self._db_path)

        # Enable foreign keys
        await self._conn.execute("PRAGMA foreign_keys = ON")

        # Create entities table
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                layer TEXT NOT NULL,
                confidence REAL NOT NULL,
                provenance TEXT NOT NULL,
                scope TEXT NOT NULL,
                properties TEXT,
                tags TEXT,
                ttl_days INTEGER,
                is_archived INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT
            )
        """)

        # Create relations table
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS relations (
                id TEXT PRIMARY KEY,
                relation_type TEXT NOT NULL,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                confidence REAL NOT NULL,
                provenance TEXT NOT NULL,
                properties TEXT,
                is_bidirectional INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (source_id) REFERENCES entities(id) ON DELETE CASCADE,
                FOREIGN KEY (target_id) REFERENCES entities(id) ON DELETE CASCADE
            )
        """)

        # Create facts table
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS facts (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                summary TEXT NOT NULL,
                layer TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                confidence REAL NOT NULL,
                provenance TEXT NOT NULL,
                scope TEXT NOT NULL,
                embedding BLOB,
                metadata TEXT,
                related_entity_ids TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # Create indexes
        await self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type)"
        )
        await self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_entities_layer ON entities(layer)"
        )
        await self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_entities_archived ON entities(is_archived)"
        )
        await self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_relations_source ON relations(source_id)"
        )
        await self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_relations_target ON relations(target_id)"
        )
        await self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_relations_type ON relations(relation_type)"
        )
        await self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_facts_layer ON facts(layer)"
        )
        await self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_facts_type ON facts(entity_type)"
        )

        await self._conn.commit()
        self._initialized = True
        logger.info(f"SQLite graph store initialized at {self._db_path}")

    async def close(self) -> None:
        """Close database connection."""
        if self._conn:
            await self._conn.close()
            self._conn = None
            self._initialized = False

    async def save_entity(self, entity: MemoryEntity) -> str:
        """Save an entity to the database."""
        async with self._lock:
            await self._conn.execute(
                """
                INSERT OR REPLACE INTO entities (
                    id, entity_type, name, description, layer, confidence,
                    provenance, scope, properties, tags, ttl_days, is_archived,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entity.id,
                    entity.entity_type.value,
                    entity.name,
                    entity.description,
                    entity.layer.value,
                    entity.confidence,
                    json.dumps(entity.provenance.to_dict()),
                    json.dumps({
                        "access_level": entity.scope.access_level.value,
                        "tenant_id": entity.scope.tenant_id,
                        "allowed_roles": list(entity.scope.allowed_roles) if entity.scope.allowed_roles else None,
                        "allowed_agents": list(entity.scope.allowed_agents) if entity.scope.allowed_agents else None,
                    }),
                    json.dumps(entity.properties),
                    json.dumps(entity.tags),
                    entity.ttl_days,
                    1 if entity.is_archived else 0,
                    entity.provenance.created_at.isoformat(),
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            await self._conn.commit()
        return entity.id

    async def get_entity(self, entity_id: str) -> Optional[MemoryEntity]:
        """Get entity by ID."""
        async with self._lock:
            cursor = await self._conn.execute(
                "SELECT * FROM entities WHERE id = ?", (entity_id,)
            )
            row = await cursor.fetchone()

        if not row:
            return None

        return self._row_to_entity(row)

    def _row_to_entity(self, row: Tuple) -> MemoryEntity:
        """Convert database row to MemoryEntity."""
        scope_data = json.loads(row[7])
        return MemoryEntity(
            id=row[0],
            entity_type=EntityType(row[1]),
            name=row[2],
            description=row[3],
            layer=MemoryLayer(row[4]),
            confidence=row[5],
            provenance=Provenance.from_dict(json.loads(row[6])),
            scope=MemoryScope(
                access_level=AccessLevel(scope_data.get("access_level", "global")),
                tenant_id=scope_data.get("tenant_id"),
                allowed_roles=set(scope_data["allowed_roles"]) if scope_data.get("allowed_roles") else None,
                allowed_agents=set(scope_data["allowed_agents"]) if scope_data.get("allowed_agents") else None,
            ),
            properties=json.loads(row[8]) if row[8] else {},
            tags=json.loads(row[9]) if row[9] else [],
            ttl_days=row[10],
            is_archived=bool(row[11]),
        )

    async def update_entity(self, entity: MemoryEntity) -> bool:
        """Update an existing entity."""
        async with self._lock:
            cursor = await self._conn.execute(
                """
                UPDATE entities SET
                    name = ?, description = ?, layer = ?, confidence = ?,
                    provenance = ?, scope = ?, properties = ?, tags = ?,
                    ttl_days = ?, is_archived = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    entity.name,
                    entity.description,
                    entity.layer.value,
                    entity.confidence,
                    json.dumps(entity.provenance.to_dict()),
                    json.dumps({
                        "access_level": entity.scope.access_level.value,
                        "tenant_id": entity.scope.tenant_id,
                    }),
                    json.dumps(entity.properties),
                    json.dumps(entity.tags),
                    entity.ttl_days,
                    1 if entity.is_archived else 0,
                    datetime.now(timezone.utc).isoformat(),
                    entity.id,
                ),
            )
            await self._conn.commit()
            return cursor.rowcount > 0

    async def delete_entity(self, entity_id: str, hard_delete: bool = False) -> bool:
        """Delete or archive an entity."""
        async with self._lock:
            if hard_delete:
                cursor = await self._conn.execute(
                    "DELETE FROM entities WHERE id = ?", (entity_id,)
                )
            else:
                cursor = await self._conn.execute(
                    "UPDATE entities SET is_archived = 1, updated_at = ? WHERE id = ?",
                    (datetime.now(timezone.utc).isoformat(), entity_id),
                )
            await self._conn.commit()
            return cursor.rowcount > 0

    async def query_entities(self, query: MemoryQuery) -> List[MemoryEntity]:
        """Query entities with filters."""
        conditions = []
        params = []

        if not query.include_archived:
            conditions.append("is_archived = 0")

        if query.entity_types:
            placeholders = ",".join("?" * len(query.entity_types))
            conditions.append(f"entity_type IN ({placeholders})")
            params.extend([t.value for t in query.entity_types])

        if query.layers:
            placeholders = ",".join("?" * len(query.layers))
            conditions.append(f"layer IN ({placeholders})")
            params.extend([l.value for l in query.layers])

        if query.min_confidence > 0:
            conditions.append("confidence >= ?")
            params.append(query.min_confidence)

        if query.tags:
            # Simple tag search using LIKE
            tag_conditions = []
            for tag in query.tags:
                tag_conditions.append("tags LIKE ?")
                params.append(f"%{tag}%")
            conditions.append(f"({' OR '.join(tag_conditions)})")

        if query.query_text:
            conditions.append("(name LIKE ? OR description LIKE ?)")
            params.extend([f"%{query.query_text}%", f"%{query.query_text}%"])

        if query.time_range_start:
            conditions.append("created_at >= ?")
            params.append(query.time_range_start.isoformat())

        if query.time_range_end:
            conditions.append("created_at <= ?")
            params.append(query.time_range_end.isoformat())

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        sql = f"""
            SELECT * FROM entities
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        params.extend([query.limit, query.offset])

        async with self._lock:
            cursor = await self._conn.execute(sql, params)
            rows = await cursor.fetchall()

        entities = [self._row_to_entity(row) for row in rows]

        # Apply access control filtering
        if query.requester_agent or query.requester_role:
            entities = [
                e for e in entities
                if e.scope.can_access(
                    query.requester_agent or "",
                    query.requester_role or "",
                    query.requester_tenant,
                )
            ]

        return entities

    async def save_relation(self, relation: Relation) -> str:
        """Save a relation."""
        async with self._lock:
            await self._conn.execute(
                """
                INSERT OR REPLACE INTO relations (
                    id, relation_type, source_id, target_id, confidence,
                    provenance, properties, is_bidirectional, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    relation.id,
                    relation.relation_type.value,
                    relation.source_id,
                    relation.target_id,
                    relation.confidence,
                    json.dumps(relation.provenance.to_dict()),
                    json.dumps(relation.properties),
                    1 if relation.is_bidirectional else 0,
                    relation.provenance.created_at.isoformat(),
                ),
            )
            await self._conn.commit()
        return relation.id

    async def get_relation(self, relation_id: str) -> Optional[Relation]:
        """Get relation by ID."""
        async with self._lock:
            cursor = await self._conn.execute(
                "SELECT * FROM relations WHERE id = ?", (relation_id,)
            )
            row = await cursor.fetchone()

        if not row:
            return None

        return self._row_to_relation(row)

    def _row_to_relation(self, row: Tuple) -> Relation:
        """Convert database row to Relation."""
        return Relation(
            id=row[0],
            relation_type=RelationType(row[1]),
            source_id=row[2],
            target_id=row[3],
            confidence=row[4],
            provenance=Provenance.from_dict(json.loads(row[5])),
            properties=json.loads(row[6]) if row[6] else {},
            is_bidirectional=bool(row[7]),
        )

    async def get_relations(
        self,
        entity_id: str,
        direction: str = "both",
        relation_types: Optional[List[RelationType]] = None,
    ) -> List[Relation]:
        """Get relations for an entity."""
        conditions = []
        params = []

        if direction == "outgoing":
            conditions.append("source_id = ?")
            params.append(entity_id)
        elif direction == "incoming":
            conditions.append("target_id = ?")
            params.append(entity_id)
        else:  # both
            conditions.append("(source_id = ? OR target_id = ?)")
            params.extend([entity_id, entity_id])

        if relation_types:
            placeholders = ",".join("?" * len(relation_types))
            conditions.append(f"relation_type IN ({placeholders})")
            params.extend([rt.value for rt in relation_types])

        where_clause = " AND ".join(conditions)
        sql = f"SELECT * FROM relations WHERE {where_clause}"

        async with self._lock:
            cursor = await self._conn.execute(sql, params)
            rows = await cursor.fetchall()

        return [self._row_to_relation(row) for row in rows]

    async def delete_relation(self, relation_id: str) -> bool:
        """Delete a relation."""
        async with self._lock:
            cursor = await self._conn.execute(
                "DELETE FROM relations WHERE id = ?", (relation_id,)
            )
            await self._conn.commit()
            return cursor.rowcount > 0

    async def save_fact(self, fact: MemoryFact) -> str:
        """Save a memory fact."""
        embedding_blob = None
        if fact.embedding:
            import struct
            embedding_blob = struct.pack(f"{len(fact.embedding)}f", *fact.embedding)

        async with self._lock:
            await self._conn.execute(
                """
                INSERT OR REPLACE INTO facts (
                    id, content, summary, layer, entity_type, confidence,
                    provenance, scope, embedding, metadata, related_entity_ids,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    fact.id,
                    fact.content,
                    fact.summary,
                    fact.layer.value,
                    fact.entity_type.value,
                    fact.confidence,
                    json.dumps(fact.provenance.to_dict()),
                    json.dumps({
                        "access_level": fact.scope.access_level.value,
                        "tenant_id": fact.scope.tenant_id,
                    }),
                    embedding_blob,
                    json.dumps(fact.metadata),
                    json.dumps(fact.related_entity_ids),
                    fact.provenance.created_at.isoformat(),
                ),
            )
            await self._conn.commit()
        return fact.id

    async def query_facts(self, query: MemoryQuery) -> List[MemoryFact]:
        """Query facts with filters."""
        conditions = []
        params = []

        if query.entity_types:
            placeholders = ",".join("?" * len(query.entity_types))
            conditions.append(f"entity_type IN ({placeholders})")
            params.extend([t.value for t in query.entity_types])

        if query.layers:
            placeholders = ",".join("?" * len(query.layers))
            conditions.append(f"layer IN ({placeholders})")
            params.extend([l.value for l in query.layers])

        if query.min_confidence > 0:
            conditions.append("confidence >= ?")
            params.append(query.min_confidence)

        if query.query_text:
            conditions.append("(content LIKE ? OR summary LIKE ?)")
            params.extend([f"%{query.query_text}%", f"%{query.query_text}%"])

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        sql = f"""
            SELECT * FROM facts
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        params.extend([query.limit, query.offset])

        async with self._lock:
            cursor = await self._conn.execute(sql, params)
            rows = await cursor.fetchall()

        facts = []
        for row in rows:
            embedding = None
            if row[8]:
                import struct
                embedding_blob = row[8]
                count = len(embedding_blob) // 4
                embedding = list(struct.unpack(f"{count}f", embedding_blob))

            scope_data = json.loads(row[7])
            facts.append(MemoryFact(
                id=row[0],
                content=row[1],
                summary=row[2],
                layer=MemoryLayer(row[3]),
                entity_type=EntityType(row[4]),
                confidence=row[5],
                provenance=Provenance.from_dict(json.loads(row[6])),
                scope=MemoryScope(
                    access_level=AccessLevel(scope_data.get("access_level", "global")),
                    tenant_id=scope_data.get("tenant_id"),
                ),
                embedding=embedding,
                metadata=json.loads(row[9]) if row[9] else {},
                related_entity_ids=json.loads(row[10]) if row[10] else [],
            ))

        return facts

    async def traverse(
        self,
        start_id: str,
        relation_types: Optional[List[RelationType]] = None,
        max_depth: int = 3,
        direction: str = "outgoing",
    ) -> Dict[str, Any]:
        """Traverse graph from starting entity."""
        visited = set()
        result = {
            "start_id": start_id,
            "nodes": [],
            "edges": [],
            "depth_reached": 0,
        }

        async def _traverse_level(entity_ids: List[str], depth: int):
            if depth > max_depth or not entity_ids:
                return

            result["depth_reached"] = max(result["depth_reached"], depth)

            for entity_id in entity_ids:
                if entity_id in visited:
                    continue
                visited.add(entity_id)

                entity = await self.get_entity(entity_id)
                if entity:
                    result["nodes"].append(entity.to_dict())

                relations = await self.get_relations(
                    entity_id, direction, relation_types
                )

                next_ids = []
                for rel in relations:
                    result["edges"].append(rel.to_dict())
                    next_id = rel.target_id if direction == "outgoing" else rel.source_id
                    if next_id not in visited:
                        next_ids.append(next_id)

                await _traverse_level(next_ids, depth + 1)

        await _traverse_level([start_id], 1)
        return result

    async def bulk_save_entities(self, entities: List[MemoryEntity]) -> List[str]:
        """Bulk save entities."""
        ids = []
        for entity in entities:
            entity_id = await self.save_entity(entity)
            ids.append(entity_id)
        return ids

    async def bulk_save_relations(self, relations: List[Relation]) -> List[str]:
        """Bulk save relations."""
        ids = []
        for relation in relations:
            rel_id = await self.save_relation(relation)
            ids.append(rel_id)
        return ids

    async def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        async with self._lock:
            entity_count = await self._conn.execute(
                "SELECT COUNT(*) FROM entities WHERE is_archived = 0"
            )
            entity_row = await entity_count.fetchone()

            relation_count = await self._conn.execute("SELECT COUNT(*) FROM relations")
            relation_row = await relation_count.fetchone()

            fact_count = await self._conn.execute("SELECT COUNT(*) FROM facts")
            fact_row = await fact_count.fetchone()

            # Count by type
            type_counts = {}
            cursor = await self._conn.execute(
                "SELECT entity_type, COUNT(*) FROM entities WHERE is_archived = 0 GROUP BY entity_type"
            )
            for row in await cursor.fetchall():
                type_counts[row[0]] = row[1]

        return {
            "total_entities": entity_row[0],
            "total_relations": relation_row[0],
            "total_facts": fact_row[0],
            "entities_by_type": type_counts,
            "backend": "sqlite",
            "db_path": str(self._db_path),
        }


class PostgresGraphStore(GraphStore):
    """PostgreSQL-based graph store for production deployments."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "memory_graph",
        user: str = "postgres",
        password: str = "",
        pool_size: int = 10,
    ):
        self._host = host
        self._port = port
        self._database = database
        self._user = user
        self._password = password
        self._pool_size = pool_size
        self._pool = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize PostgreSQL connection pool and schema."""
        if self._initialized:
            return

        try:
            import asyncpg
        except ImportError:
            raise ImportError("asyncpg is required for PostgreSQL backend: pip install asyncpg")

        self._pool = await asyncpg.create_pool(
            host=self._host,
            port=self._port,
            database=self._database,
            user=self._user,
            password=self._password,
            min_size=2,
            max_size=self._pool_size,
        )

        async with self._pool.acquire() as conn:
            # Create entities table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS entities (
                    id TEXT PRIMARY KEY,
                    entity_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    layer TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    provenance JSONB NOT NULL,
                    scope JSONB NOT NULL,
                    properties JSONB,
                    tags JSONB,
                    ttl_days INTEGER,
                    is_archived BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMPTZ NOT NULL,
                    updated_at TIMESTAMPTZ
                )
            """)

            # Create relations table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS relations (
                    id TEXT PRIMARY KEY,
                    relation_type TEXT NOT NULL,
                    source_id TEXT NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
                    target_id TEXT NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
                    confidence REAL NOT NULL,
                    provenance JSONB NOT NULL,
                    properties JSONB,
                    is_bidirectional BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMPTZ NOT NULL
                )
            """)

            # Create facts table with vector support (if pgvector is available)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS facts (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    layer TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    provenance JSONB NOT NULL,
                    scope JSONB NOT NULL,
                    embedding BYTEA,
                    metadata JSONB,
                    related_entity_ids JSONB,
                    created_at TIMESTAMPTZ NOT NULL
                )
            """)

            # Create indexes
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type)"
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_entities_layer ON entities(layer)"
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_entities_tags ON entities USING GIN(tags)"
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_relations_source ON relations(source_id)"
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_relations_target ON relations(target_id)"
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_facts_content ON facts USING GIN(to_tsvector('english', content))"
            )

        self._initialized = True
        logger.info(f"PostgreSQL graph store initialized: {self._host}:{self._port}/{self._database}")

    async def close(self) -> None:
        """Close connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None
            self._initialized = False

    async def save_entity(self, entity: MemoryEntity) -> str:
        """Save an entity."""
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO entities (
                    id, entity_type, name, description, layer, confidence,
                    provenance, scope, properties, tags, ttl_days, is_archived,
                    created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    description = EXCLUDED.description,
                    layer = EXCLUDED.layer,
                    confidence = EXCLUDED.confidence,
                    provenance = EXCLUDED.provenance,
                    scope = EXCLUDED.scope,
                    properties = EXCLUDED.properties,
                    tags = EXCLUDED.tags,
                    ttl_days = EXCLUDED.ttl_days,
                    is_archived = EXCLUDED.is_archived,
                    updated_at = EXCLUDED.updated_at
                """,
                entity.id,
                entity.entity_type.value,
                entity.name,
                entity.description,
                entity.layer.value,
                entity.confidence,
                json.dumps(entity.provenance.to_dict()),
                json.dumps({
                    "access_level": entity.scope.access_level.value,
                    "tenant_id": entity.scope.tenant_id,
                }),
                json.dumps(entity.properties),
                json.dumps(entity.tags),
                entity.ttl_days,
                entity.is_archived,
                entity.provenance.created_at,
                datetime.now(timezone.utc),
            )
        return entity.id

    async def get_entity(self, entity_id: str) -> Optional[MemoryEntity]:
        """Get entity by ID."""
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM entities WHERE id = $1", entity_id
            )

        if not row:
            return None

        return self._row_to_entity(row)

    def _row_to_entity(self, row) -> MemoryEntity:
        """Convert database row to MemoryEntity."""
        scope_data = row["scope"] if isinstance(row["scope"], dict) else json.loads(row["scope"])
        provenance_data = row["provenance"] if isinstance(row["provenance"], dict) else json.loads(row["provenance"])

        return MemoryEntity(
            id=row["id"],
            entity_type=EntityType(row["entity_type"]),
            name=row["name"],
            description=row["description"],
            layer=MemoryLayer(row["layer"]),
            confidence=row["confidence"],
            provenance=Provenance.from_dict(provenance_data),
            scope=MemoryScope(
                access_level=AccessLevel(scope_data.get("access_level", "global")),
                tenant_id=scope_data.get("tenant_id"),
            ),
            properties=row["properties"] if isinstance(row["properties"], dict) else json.loads(row["properties"] or "{}"),
            tags=row["tags"] if isinstance(row["tags"], list) else json.loads(row["tags"] or "[]"),
            ttl_days=row["ttl_days"],
            is_archived=row["is_archived"],
        )

    async def update_entity(self, entity: MemoryEntity) -> bool:
        """Update an existing entity."""
        async with self._pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE entities SET
                    name = $1, description = $2, layer = $3, confidence = $4,
                    provenance = $5, scope = $6, properties = $7, tags = $8,
                    ttl_days = $9, is_archived = $10, updated_at = $11
                WHERE id = $12
                """,
                entity.name,
                entity.description,
                entity.layer.value,
                entity.confidence,
                json.dumps(entity.provenance.to_dict()),
                json.dumps({
                    "access_level": entity.scope.access_level.value,
                    "tenant_id": entity.scope.tenant_id,
                }),
                json.dumps(entity.properties),
                json.dumps(entity.tags),
                entity.ttl_days,
                entity.is_archived,
                datetime.now(timezone.utc),
                entity.id,
            )
            return "UPDATE 1" in result

    async def delete_entity(self, entity_id: str, hard_delete: bool = False) -> bool:
        """Delete or archive an entity."""
        async with self._pool.acquire() as conn:
            if hard_delete:
                result = await conn.execute(
                    "DELETE FROM entities WHERE id = $1", entity_id
                )
                return "DELETE 1" in result
            else:
                result = await conn.execute(
                    "UPDATE entities SET is_archived = TRUE, updated_at = $1 WHERE id = $2",
                    datetime.now(timezone.utc),
                    entity_id,
                )
                return "UPDATE 1" in result

    async def query_entities(self, query: MemoryQuery) -> List[MemoryEntity]:
        """Query entities with filters."""
        conditions = ["is_archived = FALSE"] if not query.include_archived else []
        params = []
        param_idx = 1

        if query.entity_types:
            placeholders = ", ".join(f"${param_idx + i}" for i in range(len(query.entity_types)))
            conditions.append(f"entity_type IN ({placeholders})")
            params.extend([t.value for t in query.entity_types])
            param_idx += len(query.entity_types)

        if query.layers:
            placeholders = ", ".join(f"${param_idx + i}" for i in range(len(query.layers)))
            conditions.append(f"layer IN ({placeholders})")
            params.extend([l.value for l in query.layers])
            param_idx += len(query.layers)

        if query.min_confidence > 0:
            conditions.append(f"confidence >= ${param_idx}")
            params.append(query.min_confidence)
            param_idx += 1

        if query.query_text:
            conditions.append(f"(name ILIKE ${param_idx} OR description ILIKE ${param_idx})")
            params.append(f"%{query.query_text}%")
            param_idx += 1

        where_clause = " AND ".join(conditions) if conditions else "TRUE"
        sql = f"""
            SELECT * FROM entities
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ${param_idx} OFFSET ${param_idx + 1}
        """
        params.extend([query.limit, query.offset])

        async with self._pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)

        return [self._row_to_entity(row) for row in rows]

    async def save_relation(self, relation: Relation) -> str:
        """Save a relation."""
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO relations (
                    id, relation_type, source_id, target_id, confidence,
                    provenance, properties, is_bidirectional, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (id) DO UPDATE SET
                    confidence = EXCLUDED.confidence,
                    provenance = EXCLUDED.provenance,
                    properties = EXCLUDED.properties
                """,
                relation.id,
                relation.relation_type.value,
                relation.source_id,
                relation.target_id,
                relation.confidence,
                json.dumps(relation.provenance.to_dict()),
                json.dumps(relation.properties),
                relation.is_bidirectional,
                relation.provenance.created_at,
            )
        return relation.id

    async def get_relation(self, relation_id: str) -> Optional[Relation]:
        """Get relation by ID."""
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM relations WHERE id = $1", relation_id
            )

        if not row:
            return None

        return self._row_to_relation(row)

    def _row_to_relation(self, row) -> Relation:
        """Convert database row to Relation."""
        provenance_data = row["provenance"] if isinstance(row["provenance"], dict) else json.loads(row["provenance"])
        return Relation(
            id=row["id"],
            relation_type=RelationType(row["relation_type"]),
            source_id=row["source_id"],
            target_id=row["target_id"],
            confidence=row["confidence"],
            provenance=Provenance.from_dict(provenance_data),
            properties=row["properties"] if isinstance(row["properties"], dict) else json.loads(row["properties"] or "{}"),
            is_bidirectional=row["is_bidirectional"],
        )

    async def get_relations(
        self,
        entity_id: str,
        direction: str = "both",
        relation_types: Optional[List[RelationType]] = None,
    ) -> List[Relation]:
        """Get relations for an entity."""
        conditions = []
        params = [entity_id]
        param_idx = 2

        if direction == "outgoing":
            conditions.append("source_id = $1")
        elif direction == "incoming":
            conditions.append("target_id = $1")
        else:
            conditions.append("(source_id = $1 OR target_id = $1)")

        if relation_types:
            placeholders = ", ".join(f"${param_idx + i}" for i in range(len(relation_types)))
            conditions.append(f"relation_type IN ({placeholders})")
            params.extend([rt.value for rt in relation_types])

        where_clause = " AND ".join(conditions)
        sql = f"SELECT * FROM relations WHERE {where_clause}"

        async with self._pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)

        return [self._row_to_relation(row) for row in rows]

    async def delete_relation(self, relation_id: str) -> bool:
        """Delete a relation."""
        async with self._pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM relations WHERE id = $1", relation_id
            )
            return "DELETE 1" in result

    async def save_fact(self, fact: MemoryFact) -> str:
        """Save a memory fact."""
        embedding_blob = None
        if fact.embedding:
            import struct
            embedding_blob = struct.pack(f"{len(fact.embedding)}f", *fact.embedding)

        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO facts (
                    id, content, summary, layer, entity_type, confidence,
                    provenance, scope, embedding, metadata, related_entity_ids,
                    created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                ON CONFLICT (id) DO UPDATE SET
                    content = EXCLUDED.content,
                    summary = EXCLUDED.summary,
                    confidence = EXCLUDED.confidence,
                    embedding = EXCLUDED.embedding,
                    metadata = EXCLUDED.metadata
                """,
                fact.id,
                fact.content,
                fact.summary,
                fact.layer.value,
                fact.entity_type.value,
                fact.confidence,
                json.dumps(fact.provenance.to_dict()),
                json.dumps({
                    "access_level": fact.scope.access_level.value,
                    "tenant_id": fact.scope.tenant_id,
                }),
                embedding_blob,
                json.dumps(fact.metadata),
                json.dumps(fact.related_entity_ids),
                fact.provenance.created_at,
            )
        return fact.id

    async def query_facts(self, query: MemoryQuery) -> List[MemoryFact]:
        """Query facts with filters."""
        conditions = []
        params = []
        param_idx = 1

        if query.entity_types:
            placeholders = ", ".join(f"${param_idx + i}" for i in range(len(query.entity_types)))
            conditions.append(f"entity_type IN ({placeholders})")
            params.extend([t.value for t in query.entity_types])
            param_idx += len(query.entity_types)

        if query.layers:
            placeholders = ", ".join(f"${param_idx + i}" for i in range(len(query.layers)))
            conditions.append(f"layer IN ({placeholders})")
            params.extend([l.value for l in query.layers])
            param_idx += len(query.layers)

        if query.min_confidence > 0:
            conditions.append(f"confidence >= ${param_idx}")
            params.append(query.min_confidence)
            param_idx += 1

        if query.query_text:
            conditions.append(f"to_tsvector('english', content) @@ plainto_tsquery('english', ${param_idx})")
            params.append(query.query_text)
            param_idx += 1

        where_clause = " AND ".join(conditions) if conditions else "TRUE"
        sql = f"""
            SELECT * FROM facts
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ${param_idx} OFFSET ${param_idx + 1}
        """
        params.extend([query.limit, query.offset])

        async with self._pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)

        facts = []
        for row in rows:
            embedding = None
            if row["embedding"]:
                import struct
                embedding_blob = row["embedding"]
                count = len(embedding_blob) // 4
                embedding = list(struct.unpack(f"{count}f", embedding_blob))

            scope_data = row["scope"] if isinstance(row["scope"], dict) else json.loads(row["scope"])
            provenance_data = row["provenance"] if isinstance(row["provenance"], dict) else json.loads(row["provenance"])

            facts.append(MemoryFact(
                id=row["id"],
                content=row["content"],
                summary=row["summary"],
                layer=MemoryLayer(row["layer"]),
                entity_type=EntityType(row["entity_type"]),
                confidence=row["confidence"],
                provenance=Provenance.from_dict(provenance_data),
                scope=MemoryScope(
                    access_level=AccessLevel(scope_data.get("access_level", "global")),
                    tenant_id=scope_data.get("tenant_id"),
                ),
                embedding=embedding,
                metadata=row["metadata"] if isinstance(row["metadata"], dict) else json.loads(row["metadata"] or "{}"),
                related_entity_ids=row["related_entity_ids"] if isinstance(row["related_entity_ids"], list) else json.loads(row["related_entity_ids"] or "[]"),
            ))

        return facts

    async def traverse(
        self,
        start_id: str,
        relation_types: Optional[List[RelationType]] = None,
        max_depth: int = 3,
        direction: str = "outgoing",
    ) -> Dict[str, Any]:
        """Traverse graph using recursive CTE."""
        type_filter = ""
        if relation_types:
            types_str = ", ".join(f"'{rt.value}'" for rt in relation_types)
            type_filter = f"AND r.relation_type IN ({types_str})"

        direction_clause = "r.source_id = t.entity_id" if direction == "outgoing" else "r.target_id = t.entity_id"
        next_id = "r.target_id" if direction == "outgoing" else "r.source_id"

        sql = f"""
            WITH RECURSIVE traverse AS (
                SELECT $1::text as entity_id, 0 as depth
                UNION ALL
                SELECT {next_id}, t.depth + 1
                FROM traverse t
                JOIN relations r ON {direction_clause} {type_filter}
                WHERE t.depth < $2
            )
            SELECT DISTINCT entity_id, depth FROM traverse
        """

        async with self._pool.acquire() as conn:
            rows = await conn.fetch(sql, start_id, max_depth)

        entity_ids = [row["entity_id"] for row in rows]
        max_depth_reached = max(row["depth"] for row in rows) if rows else 0

        # Fetch all entities and relations
        nodes = []
        edges = []

        for entity_id in entity_ids:
            entity = await self.get_entity(entity_id)
            if entity:
                nodes.append(entity.to_dict())
            relations = await self.get_relations(entity_id, direction, relation_types)
            edges.extend([r.to_dict() for r in relations])

        return {
            "start_id": start_id,
            "nodes": nodes,
            "edges": edges,
            "depth_reached": max_depth_reached,
        }

    async def bulk_save_entities(self, entities: List[MemoryEntity]) -> List[str]:
        """Bulk save entities using COPY."""
        ids = []
        for entity in entities:
            entity_id = await self.save_entity(entity)
            ids.append(entity_id)
        return ids

    async def bulk_save_relations(self, relations: List[Relation]) -> List[str]:
        """Bulk save relations."""
        ids = []
        for relation in relations:
            rel_id = await self.save_relation(relation)
            ids.append(rel_id)
        return ids

    async def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        async with self._pool.acquire() as conn:
            entity_count = await conn.fetchval(
                "SELECT COUNT(*) FROM entities WHERE is_archived = FALSE"
            )
            relation_count = await conn.fetchval("SELECT COUNT(*) FROM relations")
            fact_count = await conn.fetchval("SELECT COUNT(*) FROM facts")

            type_counts = {}
            rows = await conn.fetch(
                "SELECT entity_type, COUNT(*) as cnt FROM entities WHERE is_archived = FALSE GROUP BY entity_type"
            )
            for row in rows:
                type_counts[row["entity_type"]] = row["cnt"]

        return {
            "total_entities": entity_count,
            "total_relations": relation_count,
            "total_facts": fact_count,
            "entities_by_type": type_counts,
            "backend": "postgresql",
            "host": self._host,
            "database": self._database,
        }


def get_graph_store(backend: str = "sqlite", **kwargs) -> GraphStore:
    """Factory function to get the appropriate graph store."""
    if backend == "sqlite":
        return SQLiteGraphStore(db_path=kwargs.get("db_path", "data/memory_graph.db"))
    elif backend == "postgresql":
        return PostgresGraphStore(
            host=kwargs.get("host", "localhost"),
            port=kwargs.get("port", 5432),
            database=kwargs.get("database", "memory_graph"),
            user=kwargs.get("user", "postgres"),
            password=kwargs.get("password", ""),
            pool_size=kwargs.get("pool_size", 10),
        )
    else:
        raise ValueError(f"Unknown backend: {backend}")
