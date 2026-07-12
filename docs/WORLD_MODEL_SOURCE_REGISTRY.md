# World Model Source Registry

Status: draft
Scope: source inventory for Dream Caesar / Cosmic Council consolidation
Updated: 2026-07-12

## Registry Rule

This registry tracks evidence. It does not promote material to canon by itself.

Each source must keep:

- source id
- title or path
- location
- source type
- current classification
- platform relevance
- next action

## Local Active Sources

| Source ID | Title / Path | Type | Classification | Platform relevance | Next action |
| --- | --- | --- | --- | --- | --- |
| WM-S1 | `/home/humank1nd/dream-caesar/dream-caesar.py` | CLI | Active kernel | Current command entrypoint and sacred-pipeline wrapper | Preserve and extend with subcommands |
| WM-S2 | `/home/humank1nd/dream-caesar/infrastructure/ledger` | SQLite/Git/Sheets ledger | Active kernel | Sessions, routing, crystals, proposal history foundation | Wrap behind CLI ledger adapter |
| WM-S3 | `/home/humank1nd/dream-caesar/src/cosmic_council` | Python package | Active donor/kernel | Council workflow, models, integrations, API surfaces | Classify stable modules before import |
| WM-S4 | `/home/humank1nd/dream-caesar/CRONUS` | Runtime and console | Runtime donor | Telemetry, geometry, console, control-plane patterns | Keep as optional module/adapter |
| WM-S5 | `/home/humank1nd/dream-caesar/frontend` | Next frontend | UI donor | DC-app and visual surfaces | Keep optional; do not make CLI depend on it |
| WM-S6 | `/home/humank1nd/dream-caesar/docs/UNIFIED_ARCHITECTURE.md` | Architecture doc | Canon candidate / donor | Defines Dream Caesar, Cosmic Council, CRONUS, E8, Twin Earth mapping | Reconcile with current plan |
| WM-S7 | `/home/humank1nd/dream-caesar/docs/DC_OS_INTEGRATION_PLAN.md` | Architecture doc | UI/module boundary donor | Separates DC-OS, DC-app, CRONUS Console, Think Tank | Preserve for UI launcher phase |

## Local Legacy Sources

| Source ID | Title / Path | Type | Classification | Platform relevance | Next action |
| --- | --- | --- | --- | --- | --- |
| WM-L1 | `/home/humank1nd/legacy-cosmic-council` | Git repo | Historical donor | Original Cosmic Council code/docs | Mine for stable ROYGBV concepts |
| WM-L2 | `/home/humank1nd/legacy-dream-caesar` | Git repo | Historical donor | Earlier Dream Caesar implementation | Mine for CLI/runtime lineage |
| WM-L3 | `/home/humank1nd/legacy-life-itself-product-dream-caesar` | Git repo | Historical donor | Product-era Dream Caesar lineage | Mine for product vocabulary only |
| WM-L4 | `/home/humank1nd/desktop-council` | Local directory | Unknown / donor | Possible desktop council runtime material | Inventory before use |
| WM-L5 | `/home/humank1nd/know-joke-master-hub` | Doctrine hub | Source map / doctrine hub | Existing Dream Caesar source inventory and integration plan | Treat as classification reference |

## GitHub Sources

| Source ID | Repository | Classification | Platform relevance | Next action |
| --- | --- | --- | --- | --- |
| WM-GH1 | `Humank1nd/dream-caesar-runtime` | Active private backup/runtime repo | Current committed branch and full release backup | Use as source-control anchor |
| WM-GH2 | `Humank1nd/dream-caesar-canon-alignment` | Canon alignment repo | Canon synchronization branch | Compare before canon promotion |
| WM-GH3 | `Humank1nd/dream-caesar-integration` | Integration repo | Integration branch and historical split | Compare adapters and integration plans |
| WM-GH4 | `Humank1nd/legacy-cosmic-council` | Legacy donor repo | Historical Council evidence | Mine selectively |
| WM-GH5 | `Humank1nd/legacy-life-itself-svc-cosmic-council` | Legacy service donor | REST/service contract donor | Inspect before API adapter work |
| WM-GH6 | `Humank1nd/legacy-life-itself-svc-cronus-api` | Legacy service donor | CRONUS API/geometry donor | Inspect before geometry adapter work |
| WM-GH7 | `Humank1nd/legacy-life-itself-svc-e8-api` | Legacy service donor | E8 geometry/resonance donor | Inspect before E8 adapter work |
| WM-GH8 | `Humank1nd/legacy-life-itself-product-twin-earth-nyc` | Product donor | World-model city simulation donor | Inspect before NYC slice |

## Google Drive Sources

| Source ID | Drive path | Classification | Platform relevance | Next action |
| --- | --- | --- | --- | --- |
| WM-D1 | `gdrive:Dream Caesar Backups/2026-07-12/` | Verified backup | Full pre-improvement restore point | Preserve |
| WM-D2 | `gdrive:Know Joke/CAOS - White/Establishing the Know Joke University/Dream Caesar Mission Scaffold and Agency Web.docx` | Canon candidate | Mission scaffold and agency web | Read/classify before promotion |
| WM-D3 | `gdrive:Know Joke/CAOS - White/The Cosmic Council Fractal Cosmology: Observer-Activated Reality.docx` | Cosmology donor | Council/worldview lineage | Classify before import |
| WM-D4 | `gdrive:Know Joke/CROS - Red/Dream Caesar Repo Mission Charter.docx` | Governance donor | Repo boundary and role rules | Preserve as governance evidence |
| WM-D5 | `gdrive:Know Joke/CAOS - White/dream-caesar/Dream Caesar: Purpose, Capabilities, and Knowledge Base.docx` | Capability donor | Dream Caesar capability vocabulary | Read/classify |
| WM-D6 | `gdrive:Know Joke/CAOS - White/dream-caesar/Dream Caesar: Appliance Architecture, Governance, and Telemetry Hardening.docx` | Architecture donor | Appliance/governance/telemetry safety | Read/classify |
| WM-D7 | `gdrive:Know Joke/CAOS - White/dream-caesar/The Cosmic Council: CRONUS Interface & Dream Configuration.docx` | Interface donor | Threshold/interface language | Translate, do not promote wholesale |
| WM-D8 | `gdrive:F_Backup/Downloads/Walk me through the process of building a world model ai.md` | World-model planning note | Defines state/action/observation, modular models, planning loop | Use as practical architecture input |

## Platform Backlog From Registry

1. Add source registry reader for local Markdown table.
2. Add `sources --json` output.
3. Add source classification schema.
4. Add Drive/GitHub adapters as read-only inventory tools.
5. Add proposal storage before any `commit-world` command mutates state.
