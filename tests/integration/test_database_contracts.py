"""
Integration contracts for the SQLite-backed database manager and service.
"""

from __future__ import annotations

import uuid
from pathlib import Path

import pytest

from src.cosmic_council.database.unified_database_manager import (
    DatabaseManager,
    UnifiedDatabaseManager,
)
from src.cosmic_council.database.unified_database_service import (
    PerpetualDatabaseService,
    UnifiedDatabaseService,
)


def _sqlite_url(db_path: Path) -> str:
    return f"sqlite+aiosqlite:///{db_path.as_posix()}"


@pytest.mark.asyncio
async def test_unified_database_manager_lifecycle(tmp_path: Path) -> None:
    db_path = tmp_path / "manager_contracts.db"
    manager = UnifiedDatabaseManager(database_url=_sqlite_url(db_path))

    await manager.create_tables()
    await manager.create_tables()

    health = await manager.health_check()
    info = manager.get_database_info()

    assert health["status"] == "healthy"
    assert health["healthy"] is True
    assert health["basic_connectivity"] is True
    assert health["table_count"] > 0
    assert manager.check_connection() is True
    assert info["database_type"] == "sqlite"
    assert info["has_sync_engine"] is True
    assert info["has_async_engine"] is True
    assert info["has_unified_service"] is True

    await manager.drop_tables()
    await manager.create_tables()
    await manager.close()


@pytest.mark.asyncio
async def test_unified_database_service_problem_and_solution_roundtrip(tmp_path: Path) -> None:
    db_path = tmp_path / "service_problem_solution.db"
    service = UnifiedDatabaseService(_sqlite_url(db_path))
    await service.create_tables()

    problem_id = await service.create_problem(
        {
            "title": "Database contract problem",
            "description": "Verify problem persistence roundtrip",
            "domain": "Testing",
            "complexity": "moderate",
        }
    )
    problem = await service.get_problem(problem_id)

    assert problem is not None
    assert problem["id"] == problem_id
    assert problem["title"] == "Database contract problem"
    assert problem["domain"] == "Testing"
    assert problem["complexity"] == "moderate"
    assert problem["status"] == "active"

    solution_id = await service.create_solution(
        {
            "problem_id": uuid.UUID(problem_id),
            "title": "Database contract solution",
            "description": "Verify solution persistence roundtrip",
            "solution_type": "primary",
        }
    )
    solution = await service.get_solution(solution_id)

    assert solution is not None
    assert solution["id"] == solution_id
    assert solution["problem_id"] == problem_id
    assert solution["title"] == "Database contract solution"
    assert solution["status"] == "draft"

    await service.close()


@pytest.mark.asyncio
async def test_perpetual_database_service_session_and_cycle_roundtrip(tmp_path: Path) -> None:
    db_path = tmp_path / "perpetual_contracts.db"
    service = PerpetualDatabaseService(_sqlite_url(db_path))
    await service.create_tables()

    session_id = await service.save_perpetual_session(
        {
            "session_id": str(uuid.uuid4()),
            "session_name": "Contract Session",
            "initial_input": "Explore a contract-safe persistence roundtrip",
            "mode": "collaborative",
            "goals": ["stability"],
            "success_criteria": ["roundtrip"],
            "custom_note": "preserve extras",
        }
    )
    session_payload = await service.get_session(session_id)

    assert session_payload is not None
    assert session_payload["id"] == session_id
    assert session_payload["session_id"] == session_id
    assert session_payload["session_name"] == "Contract Session"
    assert session_payload["session_data"]["custom_note"] == "preserve extras"

    updated = await service.update_perpetual_session(
        session_id,
        {
            "current_cycle_number": 1,
            "current_input": "Refined input",
            "status": "active",
        },
    )
    assert updated is True

    cycle_id = await service.create_perpetual_cycle(
        {
            "session_id": uuid.UUID(session_id),
            "cycle_number": 1,
            "cycle_type": "exploration",
            "input_text": "Refined input",
            "status": "running",
        }
    )
    cycle_payload = await service.get_perpetual_cycle(cycle_id)
    cycle_updated = await service.update_perpetual_cycle(
        cycle_id,
        {
            "status": "completed",
            "output_text": "Cycle complete",
            "duration": 1.25,
        },
    )
    updated_cycle_payload = await service.get_perpetual_cycle(cycle_id)
    session_cycles = await service.get_session_cycles(session_id)
    session_list = await service.get_all_sessions()

    assert cycle_payload is not None
    assert cycle_payload["id"] == cycle_id
    assert cycle_payload["session_id"] == session_id
    assert cycle_payload["cycle_number"] == 1
    assert cycle_updated is True
    assert updated_cycle_payload is not None
    assert updated_cycle_payload["status"] == "completed"
    assert updated_cycle_payload["output_text"] == "Cycle complete"
    assert len(session_cycles) == 1
    assert session_cycles[0]["cycle_id"] == cycle_id
    assert any(item["session_id"] == session_id for item in session_list)

    await service.close()


def test_database_manager_sync_wrapper_reports_healthy_connection(tmp_path: Path) -> None:
    db_path = tmp_path / "sync_wrapper_contracts.db"
    manager = DatabaseManager(database_url=_sqlite_url(db_path))
    manager.create_tables()

    health = manager.health_check()

    assert health["status"] == "healthy"
    assert health["healthy"] is True
    assert manager.check_connection() is True

    manager.close()
