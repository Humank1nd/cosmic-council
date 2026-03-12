# Phase 14 Remaining Divergences

This branch is no longer blocked on unknown mirror drift. The remaining diffs are intentional and defended by tests or runtime gates.

## Mirror Summary

- `phase9_mirror_restore_plan.py`: `COMMON=247`, `SAME=231`, `DIFF=16`
- `phase12_mirror_diff_triage.py`: `MEDIUM_RISK=3`, `HIGH_RISK=6`

## Medium Risk

### `src/cosmic_council/agents/agent_registry_36.py`
- Kept local mapping because mirror expects `AgentRole.TASK_DECOMPOSER`, which is not present in this branch.
- Locked by:
  - `python -m pytest tests/unit/test_phase14_intentional_divergences.py -q`

### `src/cosmic_council/core/types.py`
- Kept local normalization because current `ProblemStatement` accepts both string and enum domains and normalizes to string.
- Locked by:
  - `python -m pytest tests/unit/test_phase14_intentional_divergences.py -q`

### `src/database/models/base.py`
- Kept local `metadata` compatibility shim because it avoids SQLAlchemy declarative metadata collisions while preserving schema/API behavior.
- Locked by:
  - `python -m pytest tests/unit/test_phase14_intentional_divergences.py -q`

## High Risk

### `src/api/main.py`
- Full mirror sync regressed legacy compatibility GET routes.
- Proof:
  - `python -m pytest tests/integration/test_api_surface_contracts.py::test_web_perpetual_sessions_compat_contract tests/integration/test_api_surface_contracts.py::test_web_perpetual_status_compat_contract tests/integration/test_api_surface_contracts.py::test_web_perpetual_ai_sessions_compat_contract -q`

### `src/cosmic_council/api/agent_interactions.py`
- Local recovered-agent fallback is required because restored task-style agents still expose `process_task`, not `process_problem_enhanced`.
- Proof:
  - `python -m pytest tests/integration/test_agent_endpoint_contracts.py -q`

### `src/cosmic_council/database/unified_database_manager.py`
### `src/cosmic_council/database/unified_database_service.py`
- Mirror versions are a Firestore rewrite; this branch is validated on SQLite/SQLAlchemy contracts.
- Locked by:
  - `python -m pytest tests/integration/test_database_contracts.py -q`
  - `python scripts/phase14_db_dry_run.py`

### `src/cosmic_council/core/workflow_engine.py`
### `src/cosmic_council/core/api.py`
- Remaining hunks are mostly real logic/signature changes, not safe mechanical sync.
- Triage report:
  - `python scripts/phase14_hunk_triage.py`
- Indexed hunk inspection:
  - `python scripts/phase14_extract_hunks.py --rel-path cosmic_council/core/api.py --classification review_small_logic_change --index 1`
  - `python scripts/phase14_extract_hunks.py --rel-path cosmic_council/core/workflow_engine.py --classification review_small_logic_change --index 1`

## Standard Validation Gate

Run this after any future atomic merge:

```bash
python scripts/phase14_validation_bundle.py --base-url http://127.0.0.1:8012
```
