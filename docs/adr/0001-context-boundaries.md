---
title: Define bounded contexts and import-layer enforcement
status: Accepted
date: 2025-10-05
deciders: Core Team
consulted: Security, Ops
informed: All contributors
---

## Context

We have duplicated trees (`*_new`) and unclear boundaries causing cross-imports and drift.

## Decision

- Establish contexts: `agents`, `governance`, `refinement`, `gateway` (API), `core`, `database`.
- Enforce with `.importlinter` contracts and CI.
- Contracts: gateway cannot import agents/refinement; core cannot import database adapters; agents depend on core via ports.

## Consequences

- Clear ownership and safer refactors.
- Initial CI breakage may require shims; short-term friction, long-term stability.

## Rollout Plan

1. Add contracts in CI (fail-on-new).
2. Produce dependency graph; create issues for violations.
3. Fix violations per module; merge when green.

## Links

- `.importlinter`
- `.github/workflows/ci.yml`

