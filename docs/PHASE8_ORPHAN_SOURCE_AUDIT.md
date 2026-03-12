# Phase 8 Orphan Source Audit

Phase 8 is a non-destructive source recovery audit based on cleanup breadcrumbs.

## Purpose

- Inventory orphan/untracked Python files.
- Audit `frontend/think-tank/src` as a potential mirror of `src/`.
- Inventory `*_new` directories and `database_backup` directories.
- Produce a JSON report for merge/restore decisions.

## Command

```bash
python scripts/phase8_orphan_source_audit.py
```

Optional strict mode:

```bash
python scripts/phase8_orphan_source_audit.py --strict
```

Optional custom output:

```bash
python scripts/phase8_orphan_source_audit.py --json-out recovery/phase8_orphan_source_report.json
```

## Output

- Default report: `recovery/phase8_orphan_source_report.json`
- Console summary includes:
  - root untracked totals
  - `src` vs `frontend/think-tank/src` overlap and drift
  - `*_new` directory counts
  - `database_backup` directory counts

## Notes

- No files are moved, deleted, or merged in this phase.
- Use this report to define a targeted restore/merge plan before any cleanup.
