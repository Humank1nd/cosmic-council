# Phase 14 Autonomous Backlog

Objective: reduce remaining mirror drift (`MEDIUM=3`, `HIGH=6`) without breaking validated runtime/API contracts.

## Stage 1: DB Safety Tranche

1. Snapshot current runtime DB artifacts before any DB-layer merge.
2. Add a dry-run migration checker script for `unified_database_manager.py` and `unified_database_service.py`.
3. Add a schema diff assertion comparing current metadata to mirror metadata in isolation.
4. Add DB contract tests for:
   - idempotent table creation
   - session lifecycle create/read/update
   - ethical policy and perpetual session persistence
5. Run:
   - `python scripts/phase7_tests_artifacts_audit.py --run-core-suites --timeout-seconds 300`
   - `python scripts/phase11_api_runtime_probe.py --base-url http://127.0.0.1:8012 --strict`
   - `python scripts/phase13_endpoint_contract_snapshot.py --base-url http://127.0.0.1:8012 --strict`

## Stage 2: Workflow/API Reconciliation

1. Generate hunk-level diff map for:
   - `src/cosmic_council/core/workflow_engine.py`
   - `src/cosmic_council/core/api.py`
2. Classify each hunk as:
   - safe mechanical sync
   - requires compatibility adapter
   - defer (high regression likelihood)
3. Merge only safe hunks in atomic commits (max 1-2 related hunks per commit).
4. After each atomic commit, run:
   - focused integration tests for touched endpoints/workflows
   - phase11 strict runtime probe
   - phase13 strict endpoint contracts

## Stage 3: Medium Drift Closure

1. `agent_registry_36.py`: validate enum/mapping expectations then sync non-breaking metadata hunks.
2. `core/types.py`: preserve backward-compatible normalization and sync non-contract mirror improvements.
3. `database/models/base.py`: keep metadata-collision protection and sync style/documentation-only hunks.

## Stage 4: Validation Hardening

1. Keep concurrent pytest stress check for temp DB isolation:
   - run two pytest commands in parallel and assert no conftest import/setup collisions.
2. Add a single command script to run phase7 + phase11 + phase13 in sequence and emit a summary file.
3. Regenerate drift reports (`phase9`, `phase12`) and update runlog.

## Exit Criteria

1. No runtime regressions:
   - phase11 `CHECKS_OK=10/10`
   - phase13 `CHECKS_OK=10/10`, `CONTRACT_FAILURES=0`
2. Core suites stable:
   - unit/integration/e2e all green
3. Every remaining medium/high file either:
   - merged safely, or
   - explicitly locked as intentional divergence with proof command + result.
