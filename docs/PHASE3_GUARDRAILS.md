# Phase 3 Guardrails

These guardrails are designed to prevent accidental local database loss.

## 1) Preflight DB Guard (integrity + snapshot)

Runs integrity checks against the canonical DB and creates a timestamped backup in `recovery/`.

```bash
python scripts/preflight_db_guard.py
```

Expected output includes:
- `INTEGRITY=ok`
- `CRITICAL_COUNTS` for key tables
- `SNAPSHOT=...`
- `STATUS=ok`

## 2) Guarded Git Clean

Use this instead of raw `git clean` whenever possible.

Preview only:

```bash
python scripts/guarded_git_clean.py -fd
```

Execute if safe:

```bash
python scripts/guarded_git_clean.py -fd --yes
```

If protected DB/recovery paths are detected, cleanup is blocked unless explicitly overridden:

```bash
python scripts/guarded_git_clean.py -fdx --yes --allow-protected
```

## Protected path rules

`guarded_git_clean.py` blocks removal of:
- `*.db`, `*.sqlite`, `*.sqlite3`
- WAL/SHM/journal sidecars (`*.db-wal`, `*.db-shm`, etc.)
- `recovery/*`
- `data/*`

## Canonical DB

The canonical operational DB is:

`D:/dream-caesar/cosmic_council.db`
