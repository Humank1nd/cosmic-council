# Phase 5 Database And Data

Phase 5 focuses on read-only visibility of database state and schema artifacts.

## Scope

- Inventory the known SQLite files and verify integrity.
- Index schema/migration/model/repository/seed artifacts.
- Export reproducible schema snapshots to `recovery/`.

## Commands

Read-only DB inventory:

```bash
python scripts/phase5_db_inventory.py --strict
```

Optional JSON report:

```bash
python scripts/phase5_db_inventory.py --strict --json-out recovery/phase5_inventory.json
```

Export schema snapshots:

```bash
python scripts/phase5_schema_snapshot.py
```

Deep integrity + row-count parity check:

```bash
python scripts/check_data_integrity.py
```

## Expected outputs

- `phase5_db_inventory.py`
  - Prints DB file presence/size/modified time.
  - Runs SQLite integrity checks (`quick_check` by default).
  - Reports counts for:
    - master schema SQL files (`database/schemas/`)
    - migrations (`src/database/migrations/`)
    - models (`src/database/models/`)
    - repositories (`src/database/repositories/`)
    - seed CSVs (`src/database/seeds/`, `database/seeds/cosmic_council_airtable_csv/`)
- `phase5_schema_snapshot.py`
  - Writes to `recovery/phase5_schema_snapshot_<timestamp>/`
  - Exports `<db>.schema.sql` and `<db>.table_counts.tsv`
  - Writes `manifest.tsv` with checksums and status per DB.

## Notes

- These scripts are read-only and do not modify row data.
- Snapshot artifacts in `recovery/` are ignored by git.
