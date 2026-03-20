"""
Projects & Implementation Hub for Dream Caesar.

This provides a local-first operational view over the main project execution
surfaces already present in the Ubuntu runtime:
- problems
- solutions
- workflow sessions / workflow steps
- implementation tracking
- active canon binding
- council iteration events
"""

from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_RUNTIME_ROOT = Path(os.getenv("DREAM_CAESAR_RUNTIME_ROOT", "/mnt/storage/AI/apps/dream-caesar"))
DEFAULT_DB_DIR = Path(os.getenv("DREAM_CAESAR_DB_DIR", DEFAULT_RUNTIME_ROOT / "data"))
DEFAULT_DB_PATH = Path(os.getenv("DREAM_CAESAR_DB_PATH", DEFAULT_DB_DIR / "dream_caesar.db"))
DEFAULT_ACTIVE_CANON_PATH = Path(
    os.getenv("DREAM_CAESAR_ACTIVE_CANON_PATH", DEFAULT_RUNTIME_ROOT / "desktop-council" / "active-canon.json")
)
DEFAULT_WORKFLOW_ARTIFACT_ROOT = DEFAULT_RUNTIME_ROOT / "desktop-council" / "artifacts" / "workflow-steps"
DEFAULT_ITERATION_ARTIFACT_ROOT = DEFAULT_RUNTIME_ROOT / "desktop-council" / "artifacts" / "iterative-cycle-tracking"
WARN_THRESHOLD_MS = 8000
STUCK_THRESHOLD_MS = 30000
STATUS_CACHE_TTL_SECONDS = 2.0

_STATUS_CACHE_LOCK = threading.Lock()
_STATUS_CACHE: dict[str, Any] = {
    "full": {"value": None, "expires_at": 0.0},
    "fast": {"value": None, "expires_at": 0.0},
}


def db_path() -> Path:
    return DEFAULT_DB_PATH


def _connect_db(timeout_seconds: float = 5.0) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path()), timeout=timeout_seconds)
    conn.row_factory = sqlite3.Row
    conn.execute(f"PRAGMA busy_timeout = {max(1, int(timeout_seconds * 1000))}")
    return conn


def _table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    try:
        row = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
            (table_name,),
        ).fetchone()
    except sqlite3.OperationalError:
        return False
    return row is not None


def _existing_tables(conn: sqlite3.Connection) -> set[str]:
    try:
        rows = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
    except sqlite3.OperationalError:
        return set()
    return {str(row["name"]) for row in rows}


def _count_if_exists(conn: sqlite3.Connection, table_name: str, existing_tables: set[str] | None = None) -> int | None:
    if existing_tables is None:
        exists = _table_exists(conn, table_name)
    else:
        exists = table_name in existing_tables
    if not exists:
        return None
    try:
        row = conn.execute(f"SELECT COUNT(*) AS count FROM {table_name}").fetchone()
    except sqlite3.OperationalError:
        return None
    return int(row["count"]) if row is not None else 0


def _normalize_runtime_artifact_path(raw_path: str | None) -> str | None:
    text = str(raw_path or "").strip()
    if not text:
        return None

    legacy_root = Path("/home/humank1nd/dream-caesar/docs/runtime/desktop-council")
    candidate = Path(text)
    if str(candidate).startswith(str(legacy_root)):
        relative = candidate.relative_to(legacy_root)
        return str((DEFAULT_RUNTIME_ROOT / "desktop-council" / relative).resolve())
    return text


def _load_active_canon() -> dict[str, Any]:
    if not DEFAULT_ACTIVE_CANON_PATH.exists():
        return {}
    try:
        data = json.loads(DEFAULT_ACTIVE_CANON_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict):
        return {}

    latest_step_path = _normalize_runtime_artifact_path(data.get("latest_workflow_step_artifact_path"))
    if latest_step_path:
        data["latest_workflow_step_artifact_path"] = latest_step_path

    latest_iteration_path = _normalize_runtime_artifact_path(data.get("latest_iteration_event_path"))
    if latest_iteration_path:
        data["latest_iteration_event_path"] = latest_iteration_path

    summary_path = _normalize_runtime_artifact_path(data.get("iteration_tracking_summary_path"))
    if summary_path:
        data["iteration_tracking_summary_path"] = summary_path

    return data


def _load_json_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _parse_json_field(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return {}


def _parse_iso_timestamp(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        normalized = text.replace("Z", "+00:00")
        dt = datetime.fromisoformat(normalized)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def _lookup_current_cycle_id(conn: sqlite3.Connection, problem_id: str | None) -> str | None:
    problem_text = str(problem_id or "").replace("-", "").strip()
    if not problem_text or not _table_exists(conn, "cycles"):
        return None
    try:
        row = conn.execute(
            """
            SELECT id
            FROM cycles
            WHERE problem_id = ? OR REPLACE(problem_id, '-', '') = ?
            ORDER BY started_at DESC
            LIMIT 1
            """,
            (problem_id, problem_text),
        ).fetchone()
    except sqlite3.OperationalError:
        return None
    return str(row["id"]) if row is not None else None


def reconcile_cycle_truth(
    runtime_snapshot: dict[str, Any],
    db_snapshot: dict[str, Any],
) -> dict[str, Any]:
    runtime_cycle_id = runtime_snapshot.get("cycle_id")
    db_cycle_id = db_snapshot.get("cycle_id")
    cycle_id_pending = bool(runtime_snapshot.get("cycle_id_pending"))
    runtime_time = _parse_iso_timestamp(runtime_snapshot.get("timestamp"))
    db_time = _parse_iso_timestamp(db_snapshot.get("timestamp"))
    lag_ms = None
    if runtime_time and db_time:
        lag_ms = max(0, int((runtime_time - db_time).total_seconds() * 1000))

    has_runtime = any(runtime_snapshot.values())
    has_db = any(db_snapshot.values())
    if has_runtime:
        truth_source = "runtime"
    elif has_db:
        truth_source = "db_fallback"
    else:
        truth_source = "db"

    status = "synced"
    warning = None

    required_fields = ("current_seat", "current_step", "cycle_id", "cycle_status")
    mismatches = {
        field: {
            "runtime": runtime_snapshot.get(field),
            "db": db_snapshot.get(field),
        }
        for field in required_fields
        if runtime_snapshot.get(field) != db_snapshot.get(field)
    }
    mismatch = bool(mismatches)

    if cycle_id_pending and has_runtime:
        status = "lagging"
    elif mismatch:
        if runtime_cycle_id and db_cycle_id and runtime_cycle_id != db_cycle_id:
            status = "stuck"
        elif runtime_snapshot.get("cycle_status") == "active" and db_snapshot.get("cycle_status") == "completed":
            status = "stuck"
        elif lag_ms is None or lag_ms <= WARN_THRESHOLD_MS:
            status = "lagging"
        elif lag_ms <= STUCK_THRESHOLD_MS:
            status = "warned"
        else:
            status = "stuck"

    if status in {"warned", "stuck"}:
        warning = {
            "db_snapshot": db_snapshot,
            "runtime_snapshot": runtime_snapshot,
            "lag_ms": lag_ms or 0,
            "mismatches": mismatches,
            "cycle_id_pending": cycle_id_pending,
            "message": (
                f"Runtime shows {runtime_snapshot.get('current_seat')}:{runtime_snapshot.get('current_step')} "
                f"while DB shows {db_snapshot.get('current_seat')}:{db_snapshot.get('current_step')}."
            ),
        }

    return {
        "truth_source": truth_source,
        "reconciliation_status": status,
        "reconciliation_warning": warning,
    }


def _json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _persist_reconciliation_event(
    conn: sqlite3.Connection,
    active_binding: dict[str, Any],
    reconciliation: dict[str, Any],
    runtime_snapshot: dict[str, Any],
    db_snapshot: dict[str, Any],
) -> None:
    if not _table_exists(conn, "audit_logs"):
        return

    status = str(reconciliation.get("reconciliation_status") or "")
    if not status:
        return

    resource_id = (
        runtime_snapshot.get("cycle_id")
        or db_snapshot.get("cycle_id")
        or active_binding.get("problem_id")
        or active_binding.get("workflow_session_id")
    )
    if not resource_id:
        return

    details = {
        "truth_source": reconciliation.get("truth_source"),
        "reconciliation_status": status,
        "reconciliation_warning": reconciliation.get("reconciliation_warning"),
        "runtime_snapshot": runtime_snapshot,
        "db_snapshot": db_snapshot,
        "workflow_session_id": active_binding.get("workflow_session_id"),
        "problem_id": active_binding.get("problem_id"),
        "system_alignment_objective": True,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    details_text = _json_dumps(details)

    try:
        row = conn.execute(
            """
            SELECT id, details
            FROM audit_logs
            WHERE action = 'reconciliation_state_changed'
              AND resource_type = 'cycle_alignment'
              AND resource_id = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (resource_id,),
        ).fetchone()
        if row is not None and str(row["details"] or "") == details_text:
            return

        same_status_row = conn.execute(
            """
            SELECT id
            FROM audit_logs
            WHERE action = 'reconciliation_state_changed'
              AND resource_type = 'cycle_alignment'
              AND resource_id = ?
              AND json_extract(details, '$.reconciliation_status') = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (resource_id, status),
        ).fetchone()
        if same_status_row is not None:
            conn.execute("DELETE FROM audit_logs WHERE id = ?", (str(same_status_row["id"]),))

        now = datetime.now(timezone.utc).isoformat()
        conn.execute(
            """
            INSERT INTO audit_logs (
                id, user_id, action, resource_type, resource_id, details, created_at
            ) VALUES (?, NULL, 'reconciliation_state_changed', 'cycle_alignment', ?, ?, ?)
            """,
            (str(uuid.uuid4()), resource_id, details_text, now),
        )
    except sqlite3.OperationalError:
        return


def _persist_alignment_alert_event(
    conn: sqlite3.Connection,
    active_binding: dict[str, Any],
    alignment_state: dict[str, Any],
    alignment_alert: dict[str, Any],
) -> None:
    if not _table_exists(conn, "audit_logs"):
        return
    if not alignment_state or not alignment_alert:
        return

    status = str(alignment_alert.get("status") or "")
    if status not in {"warned", "stuck"}:
        return

    resource_id = (
        alignment_state.get("resource_id")
        or active_binding.get("problem_id")
        or active_binding.get("workflow_session_id")
    )
    if not resource_id:
        return

    details = {
        "alert_status": status,
        "severity": alignment_alert.get("severity"),
        "banner": alignment_alert.get("banner"),
        "message": alignment_alert.get("message"),
        "alignment_state": alignment_state,
        "workflow_session_id": active_binding.get("workflow_session_id"),
        "problem_id": active_binding.get("problem_id"),
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    details_text = _json_dumps(details)

    try:
        row = conn.execute(
            """
            SELECT details
            FROM audit_logs
            WHERE action = 'alignment_alert_escalated'
              AND resource_type = 'cycle_alignment_alert'
              AND resource_id = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (resource_id,),
        ).fetchone()
        if row is not None and str(row["details"] or "") == details_text:
            return

        now = datetime.now(timezone.utc).isoformat()
        conn.execute(
            """
            INSERT INTO audit_logs (
                id, user_id, action, resource_type, resource_id, details, created_at
            ) VALUES (?, NULL, 'alignment_alert_escalated', 'cycle_alignment_alert', ?, ?, ?)
            """,
            (str(uuid.uuid4()), resource_id, details_text, now),
        )
    except sqlite3.OperationalError:
        return


def _latest_alignment_state(
    conn: sqlite3.Connection,
    active_binding: dict[str, Any],
    runtime_snapshot: dict[str, Any],
    db_snapshot: dict[str, Any],
) -> dict[str, Any]:
    if not _table_exists(conn, "audit_logs"):
        return {}

    resource_id = (
        runtime_snapshot.get("cycle_id")
        or db_snapshot.get("cycle_id")
        or active_binding.get("problem_id")
        or active_binding.get("workflow_session_id")
    )
    if not resource_id:
        return {}

    row = conn.execute(
        """
        SELECT id, action, resource_type, resource_id, details, created_at
        FROM audit_logs
        WHERE action = 'reconciliation_state_changed'
          AND resource_type = 'cycle_alignment'
          AND resource_id = ?
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (resource_id,),
    ).fetchone()
    if row is None:
        return {}

    details = _parse_json_field(row["details"])
    return {
        "audit_log_id": str(row["id"]),
        "resource_id": str(row["resource_id"]),
        "recorded_at": row["created_at"],
        "truth_source": details.get("truth_source"),
        "reconciliation_status": details.get("reconciliation_status"),
        "reconciliation_warning": details.get("reconciliation_warning"),
        "runtime_snapshot": details.get("runtime_snapshot"),
        "db_snapshot": details.get("db_snapshot"),
        "system_alignment_objective": bool(details.get("system_alignment_objective")),
    }


def _alignment_alert(alignment_state: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(alignment_state, dict) or not alignment_state:
        return {}

    status = str(alignment_state.get("reconciliation_status") or "")
    if not status:
        return {}

    severity_map = {
        "synced": "info",
        "lagging": "info",
        "warned": "warning",
        "stuck": "critical",
    }
    banner_map = {
        "synced": "none",
        "lagging": "none",
        "warned": "amber",
        "stuck": "red",
    }
    message_map = {
        "synced": "Runtime and DB are aligned.",
        "lagging": "Runtime leads the DB within the normal write window.",
        "warned": "Runtime and DB are diverging beyond the normal write window.",
        "stuck": "Runtime and DB are materially out of sync; alignment intervention is required.",
    }
    return {
        "status": status,
        "severity": severity_map.get(status, "info"),
        "banner": banner_map.get(status, "none"),
        "message": message_map.get(status, "Alignment state changed."),
        "recorded_at": alignment_state.get("recorded_at"),
    }


def _alignment_timeline(
    conn: sqlite3.Connection,
    active_binding: dict[str, Any],
    alignment_state: dict[str, Any],
) -> dict[str, Any]:
    if not _table_exists(conn, "audit_logs"):
        return {}

    resource_id = (
        alignment_state.get("resource_id")
        or active_binding.get("problem_id")
        or active_binding.get("workflow_session_id")
    )
    if not resource_id:
        return {}

    latest_alert_row = conn.execute(
        """
        SELECT id, details, created_at
        FROM audit_logs
        WHERE action = 'alignment_alert_escalated'
          AND resource_type = 'cycle_alignment_alert'
          AND resource_id = ?
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (resource_id,),
    ).fetchone()

    status_rows = conn.execute(
        """
        SELECT id, details, created_at
        FROM audit_logs
        WHERE action = 'reconciliation_state_changed'
          AND resource_type = 'cycle_alignment'
          AND resource_id = ?
        ORDER BY created_at DESC
        LIMIT 10
        """,
        (resource_id,),
    ).fetchall()

    previous_distinct_state: dict[str, Any] = {}
    current_status = str(alignment_state.get("reconciliation_status") or "")
    for row in status_rows:
        details = _parse_json_field(row["details"])
        status = str(details.get("reconciliation_status") or "")
        if status and status != current_status:
            previous_distinct_state = {
                "audit_log_id": str(row["id"]),
                "recorded_at": row["created_at"],
                "reconciliation_status": status,
                "truth_source": details.get("truth_source"),
            }
            break

    latest_alert: dict[str, Any] = {}
    if latest_alert_row is not None:
        details = _parse_json_field(latest_alert_row["details"])
        latest_alert = {
            "audit_log_id": str(latest_alert_row["id"]),
            "recorded_at": latest_alert_row["created_at"],
            "alert_status": details.get("alert_status"),
            "severity": details.get("severity"),
            "banner": details.get("banner"),
            "message": details.get("message"),
        }

    return {
        "resource_id": resource_id,
        "latest_state": {
            "audit_log_id": alignment_state.get("audit_log_id"),
            "recorded_at": alignment_state.get("recorded_at"),
            "reconciliation_status": alignment_state.get("reconciliation_status"),
            "truth_source": alignment_state.get("truth_source"),
        }
        if alignment_state
        else {},
        "latest_alert": latest_alert,
        "previous_distinct_state": previous_distinct_state,
    }


def _runtime_cycle_status(active_binding: dict[str, Any]) -> str:
    explicit = str(active_binding.get("workflow_session_status") or "").strip().lower()
    if explicit in {"pending", "active", "completed", "failed", "cancelled"}:
        return explicit
    if bool(active_binding.get("latest_decision_terminal")):
        return "completed"
    if str(active_binding.get("latest_workflow_step_status") or "").strip().lower() == "completed" and bool(
        active_binding.get("last_completed_terminal")
    ):
        return "completed"
    if active_binding.get("workflow_session_id"):
        return "active"
    return "idle"


def _latest_completed_iteration(session_iteration_dir: Path) -> dict[str, Any]:
    latest: dict[str, Any] = {}
    if not session_iteration_dir.exists():
        return latest

    for path in sorted(session_iteration_dir.glob("*.json")):
        if path.name == "latest-iteration.json":
            continue
        payload = _load_json_file(path)
        if not payload:
            continue
        if str(payload.get("event_type") or "") != "step_completed":
            continue
        latest = payload
    return latest


def _hydrate_active_binding_from_runtime(active_binding: dict[str, Any]) -> dict[str, Any]:
    workflow_session_id = str(active_binding.get("workflow_session_id") or "").strip()
    if not workflow_session_id:
        return active_binding

    session_step_dir = DEFAULT_WORKFLOW_ARTIFACT_ROOT / workflow_session_id
    session_iteration_dir = DEFAULT_ITERATION_ARTIFACT_ROOT / workflow_session_id
    latest_step = _load_json_file(session_step_dir / "latest-step.json")
    latest_iteration = _load_json_file(session_iteration_dir / "latest-iteration.json")
    latest_completed_iteration: dict[str, Any] = {}

    if latest_step:
        active_binding["workflow_current_step"] = latest_step.get("step_name") or active_binding.get("workflow_current_step")
        active_binding["latest_workflow_step_name"] = latest_step.get("step_name") or active_binding.get("latest_workflow_step_name")
        active_binding["latest_workflow_step_status"] = latest_step.get("status") or active_binding.get("latest_workflow_step_status")
        active_binding["latest_workflow_step_artifact_path"] = str((session_step_dir / "latest-step.json").resolve())
        latest_output = latest_step.get("output_data") or {}
        latest_input = latest_step.get("input_data") or {}
        upstream_payload = latest_input.get("upstream_payload") if isinstance(latest_input, dict) else {}
        if isinstance(latest_output, dict):
            active_binding["latest_resolution_assessment"] = latest_output.get("resolution_assessment")
            active_binding["latest_resolution_reason"] = latest_output.get("resolution_reason")
            active_binding["latest_node_identity"] = latest_output.get("node_identity") or (
                upstream_payload.get("node_identity") if isinstance(upstream_payload, dict) else None
            )
            active_binding["latest_sentry_tribunal"] = latest_output.get("sentry_tribunal") or (
                upstream_payload.get("sentry_tribunal") if isinstance(upstream_payload, dict) else None
            )
            tribunal_payload = active_binding.get("latest_sentry_tribunal") or {}
            if isinstance(tribunal_payload, dict) and tribunal_payload:
                active_binding["latest_sentry_recovery_attempt"] = tribunal_payload.get("recovery_attempt")
                repaired_payload = tribunal_payload.get("repaired_payload") or {}
                if isinstance(repaired_payload, dict) and repaired_payload:
                    active_binding["latest_sentry_recovery"] = repaired_payload.get("sentry_recovery")
        loopback_context = ((latest_step.get("input_data") or {}).get("loopback_context") or {})
        if isinstance(loopback_context, dict) and loopback_context:
            active_binding["loopback_context"] = loopback_context

    if latest_iteration:
        latest_event_type = str(latest_iteration.get("event_type") or "")
        active_binding["latest_iteration_recorded_at"] = latest_iteration.get("recorded_at")
        active_binding["latest_iteration_event_path"] = str((session_iteration_dir / "latest-iteration.json").resolve())
        active_binding["latest_iteration_event_type"] = latest_event_type
        active_binding["latest_iteration_status"] = latest_iteration.get("status")
        active_binding["latest_iteration_seat"] = latest_iteration.get("seat")
        active_binding["latest_iteration_step_name"] = latest_iteration.get("step_name")
        active_binding["latest_fractal_address"] = latest_iteration.get("fractal_address") or active_binding.get("latest_fractal_address")
        active_binding["latest_council_address_kind"] = latest_iteration.get("council_address_kind") or active_binding.get("latest_council_address_kind")
        active_binding["latest_validation_stage"] = latest_iteration.get("validation_stage") or active_binding.get("latest_validation_stage")
        active_binding["latest_validation_shell"] = latest_iteration.get("validation_shell") or active_binding.get("latest_validation_shell")
        active_binding["latest_sentry_path"] = latest_iteration.get("sentry_path") or active_binding.get("latest_sentry_path")
        active_binding["latest_sentry_shell_state"] = latest_iteration.get("sentry_shell_state") or active_binding.get("latest_sentry_shell_state")
        active_binding["latest_cronus_info"] = latest_iteration.get("cronus_info")
        active_binding["latest_coords"] = latest_iteration.get("coords")
        if latest_event_type == "step_completed":
            active_binding["latest_decision_outcome"] = latest_iteration.get("decision_outcome")
            active_binding["latest_decision_next_seat"] = latest_iteration.get("next_seat")
            active_binding["latest_decision_terminal"] = bool(latest_iteration.get("terminal"))
            latest_completed_iteration = latest_iteration
        active_binding["runtime_projection_source"] = "runtime_artifacts"

    if not latest_completed_iteration:
        has_completed_summary = bool(active_binding.get("last_completed_seat")) and bool(
            active_binding.get("last_completed_step_name")
        )
        if not has_completed_summary:
            latest_completed_iteration = _latest_completed_iteration(session_iteration_dir)

    if latest_completed_iteration:
        active_binding["last_completed_seat"] = latest_completed_iteration.get("seat")
        active_binding["last_completed_step_name"] = latest_completed_iteration.get("step_name")
        active_binding["last_completed_outcome"] = latest_completed_iteration.get("decision_outcome")
        active_binding["last_completed_next_seat"] = latest_completed_iteration.get("next_seat")
        active_binding["last_completed_loopback"] = bool(latest_completed_iteration.get("loopback"))
        active_binding["last_completed_terminal"] = bool(latest_completed_iteration.get("terminal"))
        metadata = latest_completed_iteration.get("metadata") or {}
        if isinstance(metadata, dict):
            active_binding["last_completed_resolution_assessment"] = metadata.get("resolution_assessment") or active_binding.get("last_completed_resolution_assessment")
            active_binding["last_completed_resolution_reason"] = metadata.get("resolution_reason") or active_binding.get("last_completed_resolution_reason")
            active_binding["last_completed_sentry_recovery_attempt"] = metadata.get("sentry_recovery_attempt")
            active_binding["last_completed_sentry_recovery"] = metadata.get("sentry_recovery")
        active_binding["last_completed_iteration_path"] = str(
            (
                session_iteration_dir
                / f"{int(latest_completed_iteration.get('event_index') or 0):03d}-"
                f"{str(latest_completed_iteration.get('seat') or 'seat').lower()}-"
                f"{str(latest_completed_iteration.get('step_name') or latest_completed_iteration.get('event_type') or 'event').lower().replace('_', '-')}.json"
            ).resolve()
        )

    return active_binding


def _hydrate_active_binding_from_db(conn: sqlite3.Connection, active_binding: dict[str, Any]) -> dict[str, Any]:
    workflow_session_id = str(active_binding.get("workflow_session_id") or "").strip()
    if not workflow_session_id or not _table_exists(conn, "workflow_sessions") or not _table_exists(conn, "workflow_steps"):
        return active_binding

    normalized = workflow_session_id.replace("-", "")
    try:
        workflow_row = conn.execute(
            """
            SELECT id, status, current_step
            FROM workflow_sessions
            WHERE id = ? OR REPLACE(id, '-', '') = ?
            ORDER BY started_at DESC
            LIMIT 1
            """,
            (workflow_session_id, normalized),
        ).fetchone()
    except sqlite3.OperationalError:
        return active_binding
    if workflow_row is None:
        return active_binding

    session_db_id = str(workflow_row["id"])
    active_binding["workflow_current_step"] = workflow_row["current_step"] or active_binding.get("workflow_current_step")
    active_binding["workflow_session_status"] = workflow_row["status"] or active_binding.get("workflow_session_status")
    active_binding["db_cycle_id"] = _lookup_current_cycle_id(conn, active_binding.get("problem_id"))

    try:
        active_step_row = conn.execute(
            """
            SELECT step_name, step_type, status, input_data, output_data, step_order
            FROM workflow_steps
            WHERE (session_id = ? OR REPLACE(session_id, '-', '') = ?)
              AND status = 'active'
            ORDER BY step_order ASC
            LIMIT 1
            """,
            (session_db_id, session_db_id.replace("-", "")),
        ).fetchone()
    except sqlite3.OperationalError:
        active_step_row = None
    if active_step_row is not None:
        active_binding["workflow_current_step"] = active_step_row["step_name"] or active_binding.get("workflow_current_step")
        active_binding["latest_workflow_step_name"] = active_step_row["step_name"] or active_binding.get("latest_workflow_step_name")
        active_binding["latest_workflow_step_status"] = active_step_row["status"] or active_binding.get("latest_workflow_step_status")
        active_binding["latest_fractal_address"] = active_step_row["step_type"] or active_binding.get("latest_fractal_address")
        active_binding["db_active_step_order"] = active_step_row["step_order"]
        active_input = _parse_json_field(active_step_row["input_data"])
        active_output = _parse_json_field(active_step_row["output_data"])
        upstream_payload = active_input.get("upstream_payload") if isinstance(active_input, dict) else {}
        latest_node_identity = active_output.get("node_identity") or (
            upstream_payload.get("node_identity") if isinstance(upstream_payload, dict) else None
        )
        latest_sentry_tribunal = active_output.get("sentry_tribunal") or (
            upstream_payload.get("sentry_tribunal") if isinstance(upstream_payload, dict) else None
        )
        if latest_node_identity:
            active_binding["latest_node_identity"] = latest_node_identity
        if latest_sentry_tribunal:
            active_binding["latest_sentry_tribunal"] = latest_sentry_tribunal
            active_binding["latest_sentry_recovery_attempt"] = latest_sentry_tribunal.get("recovery_attempt")
            repaired_payload = latest_sentry_tribunal.get("repaired_payload") or {}
            if isinstance(repaired_payload, dict) and repaired_payload:
                active_binding["latest_sentry_recovery"] = repaired_payload.get("sentry_recovery")
        loopback_context = active_input.get("loopback_context") if isinstance(active_input, dict) else None
        if isinstance(loopback_context, dict) and loopback_context:
            active_binding["loopback_context"] = loopback_context

    try:
        completed_step_row = conn.execute(
            """
            SELECT step_name, step_type, status, output_data, step_order, completed_at
            FROM workflow_steps
            WHERE (session_id = ? OR REPLACE(session_id, '-', '') = ?)
              AND status = 'completed'
            ORDER BY step_order DESC
            LIMIT 1
            """,
            (session_db_id, session_db_id.replace("-", "")),
        ).fetchone()
    except sqlite3.OperationalError:
        completed_step_row = None
    if completed_step_row is not None:
        completed_output = _parse_json_field(completed_step_row["output_data"])
        active_binding["last_completed_seat"] = completed_step_row["step_type"] or active_binding.get("last_completed_seat")
        active_binding["last_completed_step_name"] = completed_step_row["step_name"] or active_binding.get("last_completed_step_name")
        active_binding["last_completed_outcome"] = completed_output.get("decision_outcome") or active_binding.get("last_completed_outcome")
        active_binding["last_completed_next_seat"] = completed_output.get("recommended_next_seat") or active_binding.get("last_completed_next_seat")
        active_binding["last_completed_resolution_assessment"] = completed_output.get("resolution_assessment") or active_binding.get("last_completed_resolution_assessment")
        active_binding["last_completed_resolution_reason"] = completed_output.get("resolution_reason") or active_binding.get("last_completed_resolution_reason")
        active_binding["db_last_transition_at"] = completed_step_row["completed_at"]
        tribunal_payload = completed_output.get("sentry_tribunal") or {}
        if isinstance(tribunal_payload, dict) and tribunal_payload:
            active_binding["last_completed_sentry_recovery_attempt"] = tribunal_payload.get("recovery_attempt")
            repaired_payload = tribunal_payload.get("repaired_payload") or {}
            if isinstance(repaired_payload, dict) and repaired_payload:
                active_binding["last_completed_sentry_recovery"] = repaired_payload.get("sentry_recovery")

    return active_binding


def _recent_problems(
    conn: sqlite3.Connection, limit: int = 5, existing_tables: set[str] | None = None
) -> list[dict[str, Any]]:
    if existing_tables is None:
        exists = _table_exists(conn, "problems")
    else:
        exists = "problems" in existing_tables
    if not exists:
        return []
    try:
        rows = conn.execute(
            """
            SELECT id, title, domain, status, priority, updated_at, created_at
            FROM problems
            ORDER BY COALESCE(updated_at, created_at) DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    except sqlite3.OperationalError:
        return []
    return [dict(row) for row in rows]


def _recent_workflow_sessions(
    conn: sqlite3.Connection, limit: int = 5, existing_tables: set[str] | None = None
) -> list[dict[str, Any]]:
    if existing_tables is None:
        exists = _table_exists(conn, "workflow_sessions")
    else:
        exists = "workflow_sessions" in existing_tables
    if not exists:
        return []
    try:
        rows = conn.execute(
            """
            SELECT id, problem_id, session_type, status, current_step, started_at, completed_at
            FROM workflow_sessions
            ORDER BY COALESCE(completed_at, started_at) DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    except sqlite3.OperationalError:
        return []
    return [dict(row) for row in rows]


def _build_projects_implementation_status(
    *,
    include_heavy_reads: bool = True,
    include_alignment_history: bool = True,
) -> dict[str, Any]:
    active_canon = _load_active_canon()
    counts: dict[str, Any] = {}
    recent: dict[str, Any] = {
        "problems": [],
        "workflow_sessions": [],
    }
    conn: sqlite3.Connection | None = None
    existing_tables: set[str] = set()
    if db_path().exists():
        conn = _connect_db(timeout_seconds=0.25)
        existing_tables = _existing_tables(conn)
        if include_heavy_reads:
            counts = {
                "problems": _count_if_exists(conn, "problems", existing_tables),
                "solutions": _count_if_exists(conn, "solutions", existing_tables),
                "workflow_sessions": _count_if_exists(conn, "workflow_sessions", existing_tables),
                "workflow_steps": _count_if_exists(conn, "workflow_steps", existing_tables),
                "implementation_tracking": _count_if_exists(conn, "implementation_tracking", existing_tables),
                "planning_action_plans": _count_if_exists(conn, "planning_action_plans", existing_tables),
                "council_iteration_events": _count_if_exists(conn, "council_iteration_events", existing_tables),
            }
            recent["problems"] = _recent_problems(conn, existing_tables=existing_tables)
            recent["workflow_sessions"] = _recent_workflow_sessions(conn, existing_tables=existing_tables)

    execution_readiness = {
        "has_problem_records": bool(counts.get("problems")),
        "has_workflow_sessions": bool(counts.get("workflow_sessions")),
        "has_action_plans": bool(counts.get("planning_action_plans")),
        "has_implementation_tracking": bool(counts.get("implementation_tracking")),
        "has_iteration_events": bool(counts.get("council_iteration_events")),
    }

    active_binding = {
        "problem_id": active_canon.get("problem_id"),
        "problem_title": active_canon.get("problem_title"),
        "workflow_session_id": active_canon.get("workflow_session_id"),
        "workflow_session_status": active_canon.get("workflow_session_status"),
        "workflow_current_step": active_canon.get("workflow_current_step"),
        "latest_fractal_address": active_canon.get("latest_fractal_address"),
        "latest_council_address_kind": active_canon.get("latest_council_address_kind"),
        "latest_validation_stage": active_canon.get("latest_validation_stage"),
        "latest_validation_shell": active_canon.get("latest_validation_shell"),
        "latest_sentry_path": active_canon.get("latest_sentry_path"),
        "latest_sentry_shell_state": active_canon.get("latest_sentry_shell_state"),
        "latest_cronus_info": active_canon.get("latest_cronus_info"),
        "latest_coords": active_canon.get("latest_coords"),
        "latest_rag_tags": active_canon.get("latest_rag_tags"),
        "cycle_debt": active_canon.get("cycle_debt", {}),
        "latest_workflow_step_name": active_canon.get("latest_workflow_step_name"),
        "latest_workflow_step_status": active_canon.get("latest_workflow_step_status"),
        "latest_workflow_step_artifact_path": active_canon.get("latest_workflow_step_artifact_path"),
        "latest_decision_outcome": active_canon.get("latest_decision_outcome"),
        "latest_decision_next_seat": active_canon.get("latest_decision_next_seat"),
        "latest_decision_terminal": active_canon.get("latest_decision_terminal"),
        "latest_resolution_assessment": active_canon.get("latest_resolution_assessment"),
        "latest_resolution_reason": active_canon.get("latest_resolution_reason"),
        "last_completed_resolution_assessment": active_canon.get("last_completed_resolution_assessment"),
        "last_completed_resolution_reason": active_canon.get("last_completed_resolution_reason"),
        "previous_cycle": active_canon.get("previous_cycle", {}),
        "metadata": active_canon.get("metadata", {}),
    }
    active_binding = _hydrate_active_binding_from_runtime(active_binding)
    runtime_snapshot = {
        "current_seat": active_binding.get("latest_fractal_address"),
        "current_step": active_binding.get("workflow_current_step"),
        "cycle_id": None,
        "cycle_id_pending": False,
        "cycle_status": _runtime_cycle_status(active_binding),
        "timestamp": active_binding.get("latest_iteration_recorded_at"),
    }
    if conn is not None:
        active_binding = _hydrate_active_binding_from_db(conn, active_binding)
        runtime_snapshot["cycle_id"] = _lookup_current_cycle_id(conn, active_binding.get("problem_id"))
        runtime_snapshot["cycle_id_pending"] = (
            bool(active_binding.get("problem_id"))
            and bool(active_binding.get("workflow_session_id"))
            and not bool(runtime_snapshot["cycle_id"])
        )
    previous_cycle = active_binding.get("previous_cycle") or {}
    meaningful_previous_cycle = (
        previous_cycle
        if isinstance(previous_cycle, dict)
        and (previous_cycle.get("terminal") or previous_cycle.get("resolution_assessment"))
        else {}
    )
    active_binding["previous_cycle"] = meaningful_previous_cycle
    db_snapshot = {
        "current_seat": active_binding.get("latest_fractal_address"),
        "current_step": active_binding.get("workflow_current_step"),
        "cycle_id": active_binding.get("db_cycle_id"),
        "cycle_status": active_binding.get("workflow_session_status") or ("active" if active_binding.get("workflow_session_id") else "idle"),
        "timestamp": active_binding.get("db_last_transition_at"),
    }
    reconciliation = reconcile_cycle_truth(runtime_snapshot, db_snapshot)
    if runtime_snapshot.get("current_step"):
        active_binding["workflow_current_step"] = runtime_snapshot.get("current_step")
    if runtime_snapshot.get("current_seat"):
        active_binding["latest_fractal_address"] = runtime_snapshot.get("current_seat")
    alignment_state: dict[str, Any] = {}
    alignment_timeline: dict[str, Any] = {}
    if conn is not None and include_alignment_history:
        try:
            _persist_reconciliation_event(conn, active_binding, reconciliation, runtime_snapshot, db_snapshot)
            alignment_state = _latest_alignment_state(conn, active_binding, runtime_snapshot, db_snapshot)
            alignment_alert = _alignment_alert(alignment_state)
            _persist_alignment_alert_event(conn, active_binding, alignment_state, alignment_alert)
            try:
                conn.commit()
            except sqlite3.OperationalError:
                pass
            alignment_timeline = _alignment_timeline(conn, active_binding, alignment_state)
        finally:
            conn.close()
    else:
        if conn is not None:
            conn.close()
        cycle_resource_id = (
            runtime_snapshot.get("cycle_id")
            or db_snapshot.get("cycle_id")
            or active_binding.get("problem_id")
            or active_binding.get("workflow_session_id")
        )
        alignment_state = {
            "audit_log_id": None,
            "resource_id": cycle_resource_id,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "truth_source": reconciliation.get("truth_source"),
            "reconciliation_status": reconciliation.get("reconciliation_status"),
            "reconciliation_warning": reconciliation.get("reconciliation_warning"),
            "runtime_snapshot": runtime_snapshot,
            "db_snapshot": db_snapshot,
            "system_alignment_objective": True,
        }
        alignment_alert = _alignment_alert(alignment_state)
    active_binding.update(reconciliation)
    active_binding["alignment_state"] = alignment_state
    active_binding["alignment_alert"] = alignment_alert
    active_binding["alignment_timeline"] = alignment_timeline

    operator_current_seat = runtime_snapshot.get("current_seat") or active_binding.get("latest_fractal_address")
    operator_current_step = runtime_snapshot.get("current_step") or active_binding.get("workflow_current_step")
    operator_cycle_state = (
        "closed"
        if runtime_snapshot.get("cycle_status") == "completed"
        else "looped"
        if active_binding.get("last_completed_loopback")
        else "active"
        if active_binding["workflow_session_id"]
        else "idle"
    )

    operator_summary = {
        "cycle_state": operator_cycle_state,
        "current_seat": operator_current_seat,
        "current_step": operator_current_step,
        "last_completed_step": active_binding["latest_workflow_step_name"],
        "last_step_status": active_binding["latest_workflow_step_status"],
        "last_outcome": active_binding["latest_decision_outcome"],
        "last_completed_seat": active_binding.get("last_completed_seat"),
        "last_completed_step_name": active_binding.get("last_completed_step_name"),
        "last_completed_outcome": active_binding.get("last_completed_outcome"),
        "last_completed_next_seat": active_binding.get("last_completed_next_seat"),
        "resolution_assessment": active_binding.get("latest_resolution_assessment"),
        "resolution_reason": active_binding.get("latest_resolution_reason"),
        "last_completed_resolution_assessment": active_binding.get("last_completed_resolution_assessment"),
        "last_completed_resolution_reason": active_binding.get("last_completed_resolution_reason"),
        "cycle_result": active_binding.get("latest_resolution_assessment") or active_binding.get("latest_decision_outcome"),
        "resolved_by": active_binding.get("last_completed_seat"),
        "resolved_reason": active_binding.get("latest_resolution_reason"),
        "previous_cycle_result": meaningful_previous_cycle.get("resolution_assessment")
        or meaningful_previous_cycle.get("last_outcome"),
        "loopback_reason": (active_binding.get("loopback_context") or {}).get("reason"),
        "loopback_trigger_seat": (active_binding.get("loopback_context") or {}).get("trigger_seat"),
        "loopback_trigger_outcome": (active_binding.get("loopback_context") or {}).get("trigger_outcome"),
        "next_seat": active_binding["latest_decision_next_seat"],
        "validation_stage": active_binding["latest_validation_stage"],
        "validation_shell": active_binding["latest_validation_shell"],
        "workflow_session_id": active_binding["workflow_session_id"],
        "problem_title": active_binding["problem_title"],
        "truth_source": active_binding.get("truth_source"),
        "reconciliation_status": active_binding.get("reconciliation_status"),
    }
    latest_node_identity = active_binding.get("latest_node_identity") or {}
    if isinstance(latest_node_identity, dict) and latest_node_identity:
        operator_summary["current_node_address"] = latest_node_identity.get("node_address")
        operator_summary["current_node_kind"] = latest_node_identity.get("node_kind")
    latest_sentry_tribunal = active_binding.get("latest_sentry_tribunal") or {}
    if isinstance(latest_sentry_tribunal, dict) and latest_sentry_tribunal:
        operator_summary["latest_sentry_verdict"] = latest_sentry_tribunal.get("overall_verdict")
        operator_summary["latest_sentry_redirect"] = latest_sentry_tribunal.get("redirect_address")
    latest_sentry_recovery_attempt = active_binding.get("latest_sentry_recovery_attempt") or {}
    if isinstance(latest_sentry_recovery_attempt, dict) and latest_sentry_recovery_attempt:
        operator_summary["latest_sentry_auto_recovered"] = bool(latest_sentry_recovery_attempt.get("triggered"))
        operator_summary["latest_sentry_recovery_owner"] = latest_sentry_recovery_attempt.get("owner")
        operator_summary["latest_sentry_recovery_mode"] = latest_sentry_recovery_attempt.get("mode")
        operator_summary["latest_sentry_recovery_result"] = latest_sentry_recovery_attempt.get("result")
    last_completed_sentry_recovery_attempt = active_binding.get("last_completed_sentry_recovery_attempt") or {}
    if isinstance(last_completed_sentry_recovery_attempt, dict) and last_completed_sentry_recovery_attempt:
        operator_summary["last_completed_sentry_recovery_mode"] = last_completed_sentry_recovery_attempt.get("mode")
        operator_summary["last_completed_sentry_recovery_result"] = last_completed_sentry_recovery_attempt.get("result")

    return {
        "summary": "Project execution hub across problems, workflows, implementation tracking, and active council runtime state.",
        "db_path": str(db_path()),
        "truth_source": active_binding.get("truth_source"),
        "reconciliation_status": active_binding.get("reconciliation_status"),
        "reconciliation_warning": active_binding.get("reconciliation_warning"),
        "alignment_state": alignment_state,
        "alignment_alert": alignment_alert,
        "alignment_timeline": alignment_timeline,
        "operator_summary": operator_summary,
        "active_binding": active_binding,
        "counts": counts,
        "execution_readiness": execution_readiness,
        "recent": recent,
    }


def projects_implementation_status() -> dict[str, Any]:
    return projects_implementation_status_fast(include_heavy_reads=True)


def projects_implementation_status_fast(
    *,
    include_heavy_reads: bool = False,
    include_alignment_history: bool = False,
) -> dict[str, Any]:
    now = time.monotonic()
    cache_key = "full" if include_heavy_reads else "fast"
    with _STATUS_CACHE_LOCK:
        cache_entry = _STATUS_CACHE.get(cache_key, {})
        cached_value = cache_entry.get("value")
        expires_at = float(cache_entry.get("expires_at") or 0.0)
        if cached_value is not None and now < expires_at:
            return cached_value

        status = _build_projects_implementation_status(
            include_heavy_reads=include_heavy_reads,
            include_alignment_history=include_alignment_history,
        )
        _STATUS_CACHE[cache_key] = {
            "value": status,
            "expires_at": now + STATUS_CACHE_TTL_SECONDS,
        }
        return status


def list_project_execution_gaps() -> list[dict[str, str]]:
    status = projects_implementation_status()
    counts = status.get("counts", {})
    gaps: list[dict[str, str]] = []

    if not counts.get("workflow_sessions"):
        gaps.append(
            {
                "gap": "workflow_sessions_empty",
                "impact": "No persisted project workflows are driving the council runtime.",
            }
        )
    if not counts.get("planning_action_plans"):
        gaps.append(
            {
                "gap": "planning_action_plans_empty",
                "impact": "Plans are not yet materialized as durable execution records.",
            }
        )
    if not counts.get("implementation_tracking"):
        gaps.append(
            {
                "gap": "implementation_tracking_empty",
                "impact": "Implementation progress is not yet tracked in the DB.",
            }
        )
    if status.get("active_binding", {}).get("latest_workflow_step_artifact_path"):
        artifact_path = str(status["active_binding"]["latest_workflow_step_artifact_path"])
        if artifact_path.startswith("/home/humank1nd/dream-caesar/docs/runtime"):
            gaps.append(
                {
                    "gap": "runtime_artifact_path_drift",
                    "impact": "Active canon still points at an old repo-side workflow artifact path instead of the storage-backed runtime.",
                }
            )
    return gaps
