# Phase 4 Runtime Hardening

Phase 4 focuses on safe startup and runtime verification after database recovery.

## What was added

- `scripts/launch_api_guarded.py`
  - Enforces canonical SQLite target (`D:/dream-caesar/cosmic_council.db`) unless explicitly overridden.
  - Runs `scripts/preflight_db_guard.py` before startup by default.
  - Supports smoke mode (`--smoke`) that launches API, waits for `/health`, then shuts down.
- `src/cosmic_council/database/unified_database_manager.py`
  - Fixed SQLite URL parsing bugs for `sqlite:///...` inputs.
  - Anchors relative SQLite paths to repo root to prevent cwd-based DB drift.

## Recommended commands

Run guarded smoke check:

```bash
python scripts/launch_api_guarded.py --smoke --port 8011
```

Use a free port for smoke mode. The script now fails fast if the target health endpoint is already live before launch.

Run full guarded startup:

```bash
python scripts/launch_api_guarded.py
```

If you intentionally need a non-canonical DB path:

```bash
python scripts/launch_api_guarded.py --allow-db-mismatch
```
