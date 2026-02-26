# Phase 6 Infrastructure And DevOps

Phase 6 adds static preflight checks for deployment and CI/CD assets.

## What was added

- `scripts/phase6_infra_preflight.py`
  - Validates required infrastructure and workflow files exist.
  - Parses Docker Compose and GitHub workflow YAML.
  - Verifies expected Compose services are present.
  - Verifies Compose bind-mount source paths exist.
  - Verifies Dockerfile stages used by Compose/workflows (`development`, `production`).
  - Reports missing workflow-referenced files as warnings.
  - Optionally runs `docker compose config` validation.

## Runtime fixes included

- `Dockerfile`
  - Added explicit `development` and `production` stages.
- `docker-compose.dev.yml`
  - Updated bind mounts from non-existent `./docker/...` paths to `./infrastructure/docker/...`.
  - Updated Grafana dashboard mount to `./infrastructure/monitoring/grafana-dashboards`.

## Commands

Run preflight:

```bash
python scripts/phase6_infra_preflight.py --json-out recovery/phase6_infra_report.json
```

Run with compose validation (if Docker is installed):

```bash
python scripts/phase6_infra_preflight.py --validate-compose-with-docker
```

Strict mode (fail on errors):

```bash
python scripts/phase6_infra_preflight.py --strict
```

## Notes

- Warnings indicate infrastructure debt (for example, workflow file references to missing files).
- Errors indicate concrete preflight blockers.
