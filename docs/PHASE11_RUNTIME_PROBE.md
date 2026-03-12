# Phase 11 Runtime Probe

Phase 11 adds a reproducible live-API probe for troubleshooting.

## Purpose

- Validate runtime health endpoints against a running API instance.
- Validate key perpetual endpoints.
- Validate all six enterprise agent-processing endpoints.
- Persist results to a JSON report for incident tracking.

## Command

```bash
python scripts/phase11_api_runtime_probe.py --base-url http://127.0.0.1:8012
```

Strict mode:

```bash
python scripts/phase11_api_runtime_probe.py --base-url http://127.0.0.1:8012 --strict
```

## Output

- Default report: `recovery/phase11_runtime_probe.json`
- Includes per-check status code, latency, and response/error payload.
