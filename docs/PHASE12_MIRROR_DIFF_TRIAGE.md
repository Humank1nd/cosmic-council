# Phase 12 Mirror Diff Triage

Phase 12 ranks `src/` vs `frontend/think-tank/src/` merge candidates by risk.

## Purpose

- Analyze remaining mirror diff files from Phase 9.
- Classify each file as `low`, `medium`, or `high` risk.
- Surface low-risk merge candidates first.

## Command

```bash
python scripts/phase12_mirror_diff_triage.py
```

## Output

- Default report: `recovery/phase12_mirror_diff_triage.json`
- Contains:
  - risk counts
  - low/medium candidate lists
  - per-file triage metadata (signature/import changes, branding-only, etc.)
