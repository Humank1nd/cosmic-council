# Phase 9 Mirror Restore Plan

Phase 9 creates a concrete restore plan for `src/` vs `frontend/think-tank/src/`.

## Purpose

- Identify files only present in mirror (`add_from_mirror` candidates).
- Identify files with same relative path but different content (`merge_review_required`).
- Optionally emit unified diff patches for every differing file.

## Commands

Generate plan:

```bash
python scripts/phase9_mirror_restore_plan.py
```

Generate plan + diffs:

```bash
python scripts/phase9_mirror_restore_plan.py --emit-diffs-dir recovery/phase9_mirror_diffs
```

Strict mode (fails if mirror root is missing):

```bash
python scripts/phase9_mirror_restore_plan.py --strict
```

## Output

- Default JSON: `recovery/phase9_mirror_restore_plan.json`
- Optional patch files: `recovery/phase9_mirror_diffs/*.patch`

## Notes

- This phase does not apply merges or copy files into `src/`.
- Use the generated plan/diffs to choose a targeted merge batch.
