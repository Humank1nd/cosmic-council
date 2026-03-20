from __future__ import annotations

import importlib
import json
import sqlite3
from pathlib import Path


def test_resolve_purple_decision_payload_terminal_recursive():
    module = importlib.import_module("cosmic_council.api.compat_council")
    payload = {
        "loopback_context": {
            "trigger_seat": "purple",
            "trigger_outcome": "adjustments_needed",
        },
        "lessons_learned": ["prior lesson"],
    }

    resolved = module._resolve_purple_decision_payload(payload, decision_outcome="effective_solution")

    assert resolved["decision_outcome"] == "effective_solution"
    assert resolved["recommended_next_seat"] is None
    assert resolved["resolution_mode"] == "terminal_close"
    assert resolved["resolution_assessment"] == "recursive_reflection_resolved"
    assert "closed the recursively adjusted cycle" in resolved["resolution_reason"]
    assert any("closed the loop" in lesson for lesson in resolved["lessons_learned"])


def test_resolve_purple_decision_payload_loopback_recursive():
    module = importlib.import_module("cosmic_council.api.compat_council")
    payload = {
        "loopback_context": {
            "trigger_seat": "purple",
            "trigger_outcome": "adjustments_needed",
        },
        "lessons_learned": ["prior lesson"],
    }

    resolved = module._resolve_purple_decision_payload(payload, decision_outcome="adjustments_needed")

    assert resolved["decision_outcome"] == "adjustments_needed"
    assert resolved["recommended_next_seat"] == "red"
    assert resolved["resolution_mode"] == "recursive_loopback"
    assert resolved["resolution_assessment"] == "recursive_reflection_requires_adjustment"
    assert "continued the recursively adjusted cycle" in resolved["resolution_reason"]
    assert any("kept the cycle open" in lesson for lesson in resolved["lessons_learned"])


def test_bind_active_problem_archives_previous_cycle_and_clears_resolution(tmp_path, monkeypatch):
    runtime_root = tmp_path / "runtime"
    desktop_root = runtime_root / "desktop-council"
    active_canon_path = desktop_root / "active-canon.json"

    monkeypatch.setenv("DREAM_CAESAR_RUNTIME_ROOT", str(runtime_root))
    monkeypatch.setenv("DREAM_CAESAR_DESKTOP_COUNCIL_ROOT", str(desktop_root))
    monkeypatch.setenv("DREAM_CAESAR_ACTIVE_CANON_PATH", str(active_canon_path))

    module = importlib.import_module("desktop_runtime")
    module = importlib.reload(module)
    module.ensure_runtime_dirs()

    previous_state = module.load_active_canon()
    previous_state.update(
        {
            "problem_id": "problem-old",
            "problem_title": "Old closed cycle",
            "workflow_session_id": "session-old",
            "workflow_current_step": "purple_elephant_support",
            "latest_decision_outcome": "effective_solution",
            "latest_decision_next_seat": None,
            "latest_decision_terminal": True,
            "latest_resolution_assessment": "recursive_reflection_resolved",
            "latest_resolution_reason": "Purple determined that the recursively adjusted cycle addressed the prior loopback condition.",
            "last_completed_seat": "purple",
            "last_completed_step_name": "purple_elephant_support",
            "last_completed_iteration_path": "/tmp/old-iteration.json",
        }
    )
    module.write_active_canon(previous_state)

    rebound = module.bind_active_problem(
        "problem-new",
        "session-new",
        problem_title="Fresh cycle",
        workflow_session_status="active",
        workflow_current_step="red_owl_research",
        source="test",
        fractal_address="red",
        validation_stage="research_inquiry",
    )

    previous_cycle = rebound["previous_cycle"]
    assert previous_cycle["workflow_session_id"] == "session-old"
    assert previous_cycle["resolution_assessment"] == "recursive_reflection_resolved"
    assert previous_cycle["last_outcome"] == "effective_solution"
    assert rebound["latest_resolution_assessment"] is None
    assert rebound["latest_resolution_reason"] is None
    assert rebound["workflow_session_id"] == "session-new"


def test_projects_hub_surfaces_previous_cycle_and_resolution(tmp_path, monkeypatch):
    runtime_root = tmp_path / "runtime"
    desktop_root = runtime_root / "desktop-council"
    data_root = runtime_root / "data"
    active_canon_path = desktop_root / "active-canon.json"
    data_root.mkdir(parents=True, exist_ok=True)
    desktop_root.mkdir(parents=True, exist_ok=True)
    (data_root / "dream_caesar.db").touch()

    monkeypatch.setenv("DREAM_CAESAR_RUNTIME_ROOT", str(runtime_root))
    monkeypatch.setenv("DREAM_CAESAR_DB_DIR", str(data_root))
    monkeypatch.setenv("DREAM_CAESAR_DB_PATH", str(data_root / "dream_caesar.db"))
    monkeypatch.setenv("DREAM_CAESAR_ACTIVE_CANON_PATH", str(active_canon_path))

    active_canon_path.write_text(
        json.dumps(
            {
                "problem_id": "problem-now",
                "problem_title": "Current cycle",
                "workflow_session_id": "session-now",
                "workflow_current_step": "purple_elephant_support",
                "latest_fractal_address": "purple",
                "latest_validation_stage": "feedback_reflection",
                "latest_validation_shell": "purple.hexagon",
                "latest_decision_outcome": "effective_solution",
                "latest_decision_next_seat": None,
                "latest_decision_terminal": True,
                "latest_resolution_assessment": "recursive_reflection_resolved",
                "latest_resolution_reason": "Purple determined that the recursively adjusted cycle addressed the prior loopback condition.",
                "last_completed_seat": "purple",
                "last_completed_step_name": "purple_elephant_support",
                "last_completed_outcome": "effective_solution",
                "last_completed_next_seat": None,
                "last_completed_resolution_assessment": "recursive_reflection_resolved",
                "last_completed_resolution_reason": "Purple determined that the recursively adjusted cycle addressed the prior loopback condition.",
                "previous_cycle": {
                    "workflow_session_id": "session-old",
                    "resolution_assessment": "recursive_reflection_requires_adjustment",
                    "last_outcome": "adjustments_needed",
                },
            }
        ),
        encoding="utf-8",
    )

    module = importlib.import_module("cosmic_council.integrations.project_implementation_hub")
    module = importlib.reload(module)
    status = module.projects_implementation_status()

    summary = status["operator_summary"]
    binding = status["active_binding"]
    assert summary["resolution_assessment"] == "recursive_reflection_resolved"
    assert summary["previous_cycle_result"] == "recursive_reflection_requires_adjustment"
    assert summary["cycle_result"] == "recursive_reflection_resolved"
    assert binding["latest_resolution_assessment"] == "recursive_reflection_resolved"
    assert binding["previous_cycle"]["workflow_session_id"] == "session-old"


def test_alignment_alert_escalation_persists_only_for_warned_or_stuck():
    module = importlib.import_module("cosmic_council.integrations.project_implementation_hub")

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE audit_logs (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            action TEXT NOT NULL,
            resource_type TEXT,
            resource_id TEXT,
            details TEXT,
            created_at TEXT
        )
        """
    )

    active_binding = {
        "workflow_session_id": "session-test",
        "problem_id": "problem-test",
    }

    lagging_state = {
        "resource_id": "cycle-test",
        "reconciliation_status": "lagging",
        "recorded_at": "2026-03-20T19:00:00+00:00",
    }
    lagging_alert = module._alignment_alert(lagging_state)
    module._persist_alignment_alert_event(conn, active_binding, lagging_state, lagging_alert)
    lagging_count = conn.execute(
        "SELECT COUNT(*) FROM audit_logs WHERE action = 'alignment_alert_escalated'"
    ).fetchone()[0]
    assert lagging_count == 0

    warned_state = {
        "resource_id": "cycle-test",
        "reconciliation_status": "warned",
        "reconciliation_warning": {"lag_ms": 12000},
        "recorded_at": "2026-03-20T19:00:12+00:00",
    }
    warned_alert = module._alignment_alert(warned_state)
    module._persist_alignment_alert_event(conn, active_binding, warned_state, warned_alert)

    row = conn.execute(
        """
        SELECT action, resource_type, resource_id, details
        FROM audit_logs
        WHERE action = 'alignment_alert_escalated'
        ORDER BY created_at DESC
        LIMIT 1
        """
    ).fetchone()
    assert row is not None
    details = json.loads(row["details"])
    assert row["resource_type"] == "cycle_alignment_alert"
    assert row["resource_id"] == "cycle-test"
    assert details["alert_status"] == "warned"
    assert details["severity"] == "warning"
    assert details["banner"] == "amber"


def test_reconciliation_retention_keeps_latest_per_status():
    module = importlib.import_module("cosmic_council.integrations.project_implementation_hub")

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE audit_logs (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            action TEXT NOT NULL,
            resource_type TEXT,
            resource_id TEXT,
            details TEXT,
            created_at TEXT
        )
        """
    )

    active_binding = {
        "workflow_session_id": "session-test",
        "problem_id": "problem-test",
    }
    runtime_snapshot = {
        "current_seat": "orange",
        "current_step": "orange_orangutan_planning",
        "cycle_id": "cycle-test",
        "cycle_status": "active",
        "timestamp": "2026-03-20T19:00:00+00:00",
    }
    db_snapshot = {
        "current_seat": "red",
        "current_step": "red_owl_research",
        "cycle_id": "cycle-test",
        "cycle_status": "active",
        "timestamp": "2026-03-20T18:59:45+00:00",
    }

    lagging = {
        "truth_source": "runtime",
        "reconciliation_status": "lagging",
        "reconciliation_warning": None,
    }
    module._persist_reconciliation_event(conn, active_binding, lagging, runtime_snapshot, db_snapshot)
    runtime_snapshot["timestamp"] = "2026-03-20T19:00:05+00:00"
    module._persist_reconciliation_event(conn, active_binding, lagging, runtime_snapshot, db_snapshot)

    warned = {
        "truth_source": "runtime",
        "reconciliation_status": "warned",
        "reconciliation_warning": {"lag_ms": 12000},
    }
    module._persist_reconciliation_event(conn, active_binding, warned, runtime_snapshot, db_snapshot)

    rows = conn.execute(
        """
        SELECT json_extract(details, '$.reconciliation_status') AS status, COUNT(*)
        FROM audit_logs
        WHERE action = 'reconciliation_state_changed'
        GROUP BY status
        ORDER BY status
        """
    ).fetchall()

    counts = {row[0]: row[1] for row in rows}
    assert counts["lagging"] == 1
    assert counts["warned"] == 1
