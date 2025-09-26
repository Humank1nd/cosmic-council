# Guardrail Gateway — Skeleton

Policy-enforced, auditable trust spine for agentic multi-enterprise systems. Ships with:
- FastAPI service exposing `/v1/evaluate`, `/v1/simulate`, `/v1/policies`
- Postgres schema for agents, policies, decisions, incidents
- OPA/Rego policy bundle (access, brand, budget)
- Docker Compose (Postgres, OPA, Gateway)
- K8s/Istio manifests for sidecar authz
- Sync worker stub for Kafka→Airtable

## Quickstart (Docker)
```bash
cp .env.example .env
make up        # docker compose up -d
make migrate   # apply SQL migrations
make seed      # optional demo data
make curl      # send a sample /evaluate request
```

## Endpoints
- `POST /v1/evaluate` — run policy decision
- `POST /v1/simulate` — what-if decision (hypothetical inputs/policies)
- `GET  /v1/policies`  — list active policies
- `POST /v1/policies`  — create/update policy (unsafe in prod; wire to CI bundle)

## Dev Notes
- OPA runs as a sidecar or standalone for local; policies mounted from `policies/bundles/guard`
- In prod, use bundle server + signed policy packages
- Audit stream topic names are placeholders; connect to Kafka/NATS during integration
