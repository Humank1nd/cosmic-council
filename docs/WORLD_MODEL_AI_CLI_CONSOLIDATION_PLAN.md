# World Model AI CLI Consolidation Plan

Status: draft
Scope: Dream Caesar / Cosmic Council consolidation
Updated: 2026-07-12

## Purpose

Compile the Dream Caesar, Cosmic Council, CRONUS, DreamFS, Twin Earth, and related Life Itself lineage into one World Model AI CLI platform without flattening five years of evidence into unreviewed canon.

The first deliverable is a command-line operating surface that can inventory sources, ingest classified material, route questions through the Council loop, create proposals, verify claims, and commit world-state changes only after evidence review.

## Product Definition

World Model AI CLI is the local-first command surface for:

- source inventory and provenance
- canonical world-state graph management
- Council-guided reasoning
- proposal and truth-verdict workflows
- simulation and planning loops
- durable ledger/crystal records
- optional launch hooks for DC-OS, CRONUS Console, and frontend modules

It is not a single giant model. It is a platform shell that coordinates state, adapters, models, simulations, and evidence.

## Current Working Kernel

The live kernel is the existing Dream Caesar CLI:

- entrypoint: `dream-caesar.py`
- installed command: `~/.local/bin/dream-caesar`
- pipeline: Dream Caesar -> Red -> Orange -> Yellow -> Green -> Blue -> Purple -> Crystal
- ledger: `infrastructure/ledger`
- current status: conscious, ledger-backed, and able to route queries

This behavior must remain backward-compatible while new platform commands are added.

## Platform Shape

```text
worldmodel-ai/
  cli/                 # command surface and UX contract
  canon/               # approved doctrine and glossary snapshots
  sources/             # source registry and provenance indexes
  state/               # canonical world-state graph
  adapters/            # GitHub, Drive, SQLite, filesystem, APIs, Cesium/NYC later
  council/             # ROYGBV reasoning loop
  ledger/              # sessions, proposals, truth verdicts, commits
  simulation/          # world model rollouts and planning loops
  ui-launchers/        # optional DC-OS / CRONUS / frontend launch hooks
```

The repo does not need to be physically rearranged into this tree on day one. The first slice should define the contract and wrap existing modules through adapters.

## Initial CLI Contract

```bash
dream-caesar status
dream-caesar sources
dream-caesar ingest <source-id-or-path>
dream-caesar ask "<question>"
dream-caesar propose "<change>"
dream-caesar verify <proposal-id>
dream-caesar commit-world <proposal-id>
```

Backward compatibility rule:

```bash
dream-caesar "How should Dream Caesar introduce itself?"
```

must continue to route through the existing sacred pipeline.

## Canonical World Model Loop

1. Observe reality through sources, logs, APIs, repo state, and operator input.
2. Update classified source inventory.
3. Convert accepted evidence into canonical state graph proposals.
4. Run Council deliberation and simulation/planning passes.
5. Produce a proposal object.
6. Verify the proposal against source evidence or external truth checks.
7. Commit only verified changes to the world-state ledger.
8. Crystallize the outcome for future lookup and recursion.

## Source Classification Rule

No source becomes canon by default.

Every source starts as one of:

- active kernel
- canon candidate
- governance donor
- capability donor
- interface donor
- runtime evidence
- archive donor
- external data feed
- unknown

Promotion requires an explicit classification decision and a trace back to source evidence.

## First Implementation Slice

1. Keep `dream-caesar.py` as the command entrypoint.
2. Add explicit subcommands while preserving positional-query behavior.
3. Add `sources` command that prints the source registry summary.
4. Add doc-backed source registry loading and filtering.
5. Wire `ask` to the existing `route_query` behavior.
6. Add local proposal and truth-verdict storage under `artifacts/world_model`.
7. Add local evidence packet storage and `ingest --proposal` attachment.
8. Add manual verifier decisions: approve, reject, and needs-more-evidence.
9. Add local world-state index commits for approved proposals.
10. Keep external systems untouched by `commit-world`.

## Non-Goals For Slice 1

- No repo rearrangement.
- No deletion of generated files, archives, logs, caches, or donor material.
- No bulk canon promotion.
- No GitHub, Drive, Firebase, or cloud mutation from the CLI.
- No attempt to train a model.
- No NYC/Cesium ingestion until the source registry and state contract exist.

## Primary Donor Layers

- Dream Caesar: command surface, Axis voice, routing identity.
- Cosmic Council: ROYGBV reasoning loop and reflection structure.
- CRONUS: runtime, telemetry, geometry, cadence, and console donor.
- Twin Earth: proposal / truth verdict / commit record contract.
- DreamFS: storage, handoff, and artifact lineage.
- Life Itself services: recovered service/API donor material.
- KJU / Council Core: modern Know Joke council terminology and product boundary donor.

## Acceptance Criteria

- Existing `dream-caesar --status` still works.
- Existing positional query usage still works.
- `dream-caesar status` works as an alias for `--status`.
- `dream-caesar sources` reports the known source families.
- `dream-caesar sources --json` emits the parsed registry.
- `dream-caesar sources --classification "<text>"` filters registry rows.
- `dream-caesar propose "<change>"` creates a local proposal object.
- `dream-caesar ingest <source-id-or-path>` creates a local evidence packet.
- `dream-caesar ingest <source-id-or-path> --proposal <proposal-id>` attaches evidence to a proposal.
- `dream-caesar verify <proposal-id>` writes `needs_evidence` or `evidence_attached` verdicts.
- `dream-caesar verify <proposal-id> --decision approve --note "<note>"` manually approves evidence-backed proposals.
- `dream-caesar verify <proposal-id> --decision reject --note "<note>"` rejects proposals.
- `dream-caesar verify <proposal-id> --decision needs-more-evidence --note "<note>"` records an evidence gap.
- `dream-caesar commit-world <proposal-id>` refuses unverified proposals and writes a local world-state commit for approved proposals.
- All changes are additive or backward-compatible.

## Current Local Proposal Storage

Proposal objects live under:

```text
artifacts/world_model/proposals/
```

Truth verdict objects live under:

```text
artifacts/world_model/verdicts/
```

Evidence packets live under:

```text
artifacts/world_model/evidence/
```

World-state commits live under:

```text
artifacts/world_model/commits/
```

The local world-state index lives at:

```text
artifacts/world_model/state/world_state.json
```

The first recorded proposal is:

```text
WM-P-20260712T184036Z-compile-dream-caesar-and-cosmic-council
```

The first attached evidence packet is:

```text
WM-E-20260712T184504Z-WM-D8
```

The first local world-state commit is:

```text
WM-C-20260712T184938Z-wm-p-20260712t184036z-compile-dream-caes
```

This commit records the accepted proposal in the local world-state index. It does not mutate any external system.
