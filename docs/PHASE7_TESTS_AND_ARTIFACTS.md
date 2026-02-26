# Phase 7 Tests And Artifacts

Phase 7 focuses on test surface verification and artifact visibility.

## What was added

- `scripts/phase7_tests_artifacts_audit.py`
  - Audits expected Phase 7 test and artifact paths from the checklist.
  - Reports missing files/directories and discovered test counts.
  - Optionally runs core test commands:
    - `pytest tests/unit`
    - `pytest tests/integration`
    - `pytest tests/e2e`
  - Writes JSON report to `recovery/`.

## Commands

Audit only:

```bash
python scripts/phase7_tests_artifacts_audit.py
```

Audit + run core suites:

```bash
python scripts/phase7_tests_artifacts_audit.py --run-core-suites --timeout-seconds 300
```

Strict mode (fail on missing expected files/dirs):

```bash
python scripts/phase7_tests_artifacts_audit.py --strict
```

## Output

- Default report: `recovery/phase7_tests_artifacts_report.json`
- Includes:
  - expected file/dir presence
  - missing path lists
  - discovered tests in `tests/` and `tests_new/`
  - optional core suite command return codes and output tails

## Notes

- The script does not modify test files.
- Core suite runs use `--maxfail=1` to fail fast and surface first blocker.
