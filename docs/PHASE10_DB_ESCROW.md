# Phase 10 DB Escrow

Phase 10 creates a full database escrow bundle under `recovery/`.

## Purpose

- Preserve a full point-in-time copy of the operational SQLite database.
- Export schema and full SQL dump for portable restore.
- Capture checksums and row counts in a manifest.

## Command

```bash
python scripts/phase10_db_escrow_snapshot.py
```

Optional (faster, no full SQL dump):

```bash
python scripts/phase10_db_escrow_snapshot.py --skip-dump
```

## Output

Bundle path:

`recovery/phase10_db_escrow_<UTC timestamp>/`

Includes:

- `cosmic_council.db` (and sidecars if present)
- `cosmic_council.schema.sql`
- `cosmic_council.dump.sql` (unless `--skip-dump`)
- `cosmic_council.table_counts.tsv`
- `manifest.json` with `sha256` for each output file

## Notes

- Non-destructive: does not mutate table data.
- Intended as an additional safety net after DB recovery.
- If Python `iterdump()` fails due FK metadata issues, the script falls back
  to a best-effort dump path and still emits `cosmic_council.dump.sql`.
