#!/usr/bin/env python3
"""
Dream Caesar — CLI Entry Point

The prism where signal enters and exits. Routes queries through
the Sacred Pipeline: Dream Caesar → Red → Orange → Yellow → Green → Blue → Purple → Crystal.

Usage:
    python dream-caesar.py "your question"
    python dream-caesar.py --setup
    python dream-caesar.py --status
    python dream-caesar.py --pipeline "your question"
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure infrastructure modules are importable
REPO_ROOT = Path(__file__).resolve().parent
INFRA = REPO_ROOT / "infrastructure"
sys.path.insert(0, str(INFRA))
sys.path.insert(0, str(INFRA / "ledger"))
sys.path.insert(0, str(INFRA / "auth"))

PLATFORM_COMMANDS = {
    "status",
    "sources",
    "ingest",
    "evidence",
    "inspect-evidence",
    "add-claim",
    "ask",
    "propose",
    "verify",
    "commit-world",
}

SOURCE_REGISTRY_DOC = REPO_ROOT / "docs" / "WORLD_MODEL_SOURCE_REGISTRY.md"
WORLD_MODEL_DIR = REPO_ROOT / "artifacts" / "world_model"
PROPOSALS_DIR = WORLD_MODEL_DIR / "proposals"
VERDICTS_DIR = WORLD_MODEL_DIR / "verdicts"
EVIDENCE_DIR = WORLD_MODEL_DIR / "evidence"
COMMITS_DIR = WORLD_MODEL_DIR / "commits"
STATE_DIR = WORLD_MODEL_DIR / "state"
WORLD_STATE_PATH = STATE_DIR / "world_state.json"


def run_consciousness_check(verbose=False):
    """Run the consciousness check and display results."""
    from consciousness import consciousness_check, format_consciousness_report

    result = consciousness_check()
    if verbose:
        print(format_consciousness_report(result))
    else:
        status = result["status"]
        icon = "+" if status == "conscious" else "!"
        print(f"[{icon}] Consciousness: {status} — {result['recommendation']}")

    return result


def check_first_run(user_config):
    """Return True if the setup wizard should run."""
    return user_config.is_first_run()


def run_setup(user_config):
    """Launch the first-run setup wizard."""
    import sys as _sys
    # Skip interactive setup if no TTY (e.g., piped input, CI/CD)
    if not _sys.stdin.isatty():
        print("Non-interactive mode detected. Skipping setup wizard.")
        print("Run 'python dream-caesar.py --setup' manually to configure.")
        user_config.set('setup_complete', True)
        return
    user_config.first_run_setup()


def show_status():
    """Display full system status."""
    from consciousness import consciousness_check, format_consciousness_report
    from ledger import get_stats
    from user_config import user_config

    print(format_consciousness_report(consciousness_check()))
    print()

    try:
        stats = get_stats()
        print("LEDGER:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"LEDGER: unavailable ({e})")

    print()
    print("CONFIGURATION:")
    print(f"  first_run: {user_config.is_first_run()}")
    print(f"  google_connected: {user_config.is_google_connected()}")
    print(f"  user_email: {user_config.get('user_email', 'Not set')}")
    print(f"  auto_pipeline: {user_config.get('auto_pipeline', True)}")
    print(f"  verbose: {user_config.get('verbose', False)}")


def strip_markdown_cell(value):
    """Normalize a Markdown table cell into display text."""
    value = value.strip()
    if value.startswith("`") and value.endswith("`"):
        value = value[1:-1]
    return value.replace("\\|", "|").strip()


def is_table_separator(cells):
    """Return True for Markdown table separator rows."""
    return all(set(cell.strip()) <= {"-", ":", " "} for cell in cells)


def parse_markdown_row(line):
    """Parse a simple Markdown table row."""
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return None
    return [strip_markdown_cell(cell) for cell in stripped.strip("|").split("|")]


def normalize_source_row(headers, cells):
    """Normalize registry rows from section-specific tables."""
    row = dict(zip(headers, cells))
    source_id = row.get("Source ID", "")
    if not source_id:
        return None

    name = (
        row.get("Title / Path")
        or row.get("Repository")
        or row.get("Drive path")
        or source_id
    )
    location = row.get("Location") or row.get("Repository") or row.get("Drive path") or name
    classification = row.get("Classification") or row.get("Type") or "unknown"

    return {
        "id": source_id,
        "name": name,
        "location": location,
        "type": row.get("Type", ""),
        "classification": classification,
        "platform_relevance": row.get("Platform relevance", ""),
        "next_action": row.get("Next action", ""),
    }


def load_source_registry():
    """Load source registry rows from the durable Markdown registry."""
    if not SOURCE_REGISTRY_DOC.exists():
        return []

    sources = []
    headers = None
    for line in SOURCE_REGISTRY_DOC.read_text(encoding="utf-8").splitlines():
        cells = parse_markdown_row(line)
        if not cells:
            headers = None
            continue

        if is_table_separator(cells):
            continue

        if "Source ID" in cells:
            headers = cells
            continue

        if not headers or len(cells) != len(headers):
            continue

        source = normalize_source_row(headers, cells)
        if source:
            sources.append(source)

    return sources


def filter_sources(sources, source_filter=None, classification_filter=None):
    """Filter registry rows by text and/or classification."""
    filtered = sources
    if classification_filter:
        needle = classification_filter.lower()
        filtered = [
            source for source in filtered
            if needle in source.get("classification", "").lower()
        ]

    if source_filter:
        needle = source_filter.lower()
        filtered = [
            source for source in filtered
            if any(
                needle in str(source.get(key, "")).lower()
                for key in ("id", "name", "location", "type", "classification")
            )
        ]

    return filtered


def show_sources(json_output=False, source_filter=None, classification_filter=None):
    """Display the World Model source registry."""
    sources = load_source_registry()
    sources = filter_sources(
        sources,
        source_filter=source_filter,
        classification_filter=classification_filter,
    )
    payload = {
        "registry_doc": str(SOURCE_REGISTRY_DOC),
        "count": len(sources),
        "sources": sources,
        "rule": "Sources are evidence first. Promotion to canon requires classification.",
    }

    if json_output:
        print(json.dumps(payload, indent=2))
        return

    print("WORLD MODEL SOURCE REGISTRY")
    print("=" * 60)
    print(f"Registry doc: {payload['registry_doc']}")
    print(f"Sources: {payload['count']}")
    print(payload["rule"])
    print()
    for source in sources:
        print(f"{source['id']}: {source['name']}")
        print(f"  location: {source['location']}")
        print(f"  classification: {source['classification']}")
        if source.get("platform_relevance"):
            print(f"  relevance: {source['platform_relevance']}")
        if source.get("next_action"):
            print(f"  next: {source['next_action']}")


def show_command_contract(command, subject=None):
    """Print a non-mutating contract for World Model commands not wired yet."""
    contracts = {
        "ingest": (
            "ingest <source-id-or-path>",
            "Classify a source and prepare an evidence packet. "
            "Current scaffold does not import, copy, or promote material.",
        ),
    }
    usage, description = contracts[command]
    print(f"Command: dream-caesar {usage}")
    print(description)
    if subject:
        print(f"Received: {subject}")


def utc_now():
    """Return an ISO UTC timestamp."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def safe_id_fragment(text):
    """Create a readable ID fragment from operator text."""
    chars = []
    for char in text.lower():
        if char.isalnum():
            chars.append(char)
        elif chars and chars[-1] != "-":
            chars.append("-")
        if len(chars) >= 40:
            break
    fragment = "".join(chars).strip("-")
    return fragment or "proposal"


def ensure_world_model_dirs():
    """Create local proposal/verdict storage directories."""
    PROPOSALS_DIR.mkdir(parents=True, exist_ok=True)
    VERDICTS_DIR.mkdir(parents=True, exist_ok=True)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    COMMITS_DIR.mkdir(parents=True, exist_ok=True)
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def proposal_path(proposal_id):
    """Return a proposal path for a proposal id."""
    return PROPOSALS_DIR / f"{proposal_id}.json"


def verdict_path(proposal_id):
    """Return a verdict path for a proposal id."""
    return VERDICTS_DIR / f"{proposal_id}.verdict.json"


def evidence_path(evidence_id):
    """Return an evidence path for an evidence id."""
    return EVIDENCE_DIR / f"{evidence_id}.json"


def world_commit_path(commit_id):
    """Return a world-state commit path for a commit id."""
    return COMMITS_DIR / f"{commit_id}.json"


def load_json_file(path):
    """Load a JSON file."""
    return json.loads(path.read_text(encoding="utf-8"))


def write_json_file(path, payload):
    """Write pretty JSON with stable ordering."""
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_world_state():
    """Load or initialize the local world-state index."""
    if WORLD_STATE_PATH.exists():
        return load_json_file(WORLD_STATE_PATH)

    return {
        "created_at": utc_now(),
        "updated_at": None,
        "version": 0,
        "commits": [],
        "proposals": {},
    }


def find_source(source_ref):
    """Find a source by id or text in the registry."""
    if not source_ref:
        return None

    sources = load_source_registry()
    exact = [source for source in sources if source.get("id", "").lower() == source_ref.lower()]
    if exact:
        return exact[0]

    matches = filter_sources(sources, source_filter=source_ref)
    if len(matches) == 1:
        return matches[0]

    return None


def make_source_from_path(source_ref):
    """Create an ad hoc source record for a local path that is not in the registry."""
    path = Path(source_ref).expanduser()
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()

    if not path.exists():
        return None

    return {
        "id": f"WM-LOCAL-{safe_id_fragment(str(path.name)).upper()}",
        "name": str(path),
        "location": str(path),
        "type": "local path",
        "classification": "unclassified local evidence",
        "platform_relevance": "Ad hoc local source captured by ingest.",
        "next_action": "Classify before canon promotion.",
    }


def attach_evidence_to_proposal(proposal_id, evidence_id):
    """Attach evidence to a local proposal."""
    path = proposal_path(proposal_id)
    if not path.exists():
        print(f"Error: proposal not found: {proposal_id}")
        print(f"Expected: {path}")
        return None

    proposal = load_json_file(path)
    evidence = proposal.setdefault("source_evidence", [])
    if evidence_id not in evidence:
        evidence.append(evidence_id)
    proposal["updated_at"] = utc_now()
    write_json_file(path, proposal)
    return proposal


def ingest_source(source_ref, proposal_id=None, json_output=False):
    """Create a local evidence packet from a registry source or local path."""
    if not source_ref:
        print("Error: ingest requires a source id or local path.")
        return 1

    ensure_world_model_dirs()
    source = find_source(source_ref) or make_source_from_path(source_ref)
    if not source:
        print(f"Error: source not found: {source_ref}")
        print("Use: dream-caesar sources")
        return 1

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    evidence_id = f"WM-E-{timestamp}-{source['id']}"
    packet = {
        "id": evidence_id,
        "created_at": utc_now(),
        "source": source,
        "classification": source.get("classification", "unknown"),
        "capture_mode": "registry-metadata",
        "claims": [],
        "notes": [
            "Evidence packet captures source metadata only.",
            "No Drive/GitHub/cloud content was copied by this command.",
            "Canon promotion requires later review.",
        ],
    }
    write_json_file(evidence_path(evidence_id), packet)

    proposal = None
    if proposal_id:
        proposal = attach_evidence_to_proposal(proposal_id, evidence_id)
        if proposal is None:
            return 1

    if json_output:
        print(json.dumps({
            "evidence": packet,
            "path": str(evidence_path(evidence_id)),
            "proposal": proposal,
        }, indent=2, sort_keys=True))
    else:
        print(f"Evidence: {evidence_id}")
        print(f"Source: {source['id']} — {source['name']}")
        print(f"Path: {evidence_path(evidence_id)}")
        if proposal_id:
            print(f"Attached to proposal: {proposal_id}")
        print("Capture mode: registry-metadata")
    return 0


def load_evidence(evidence_id):
    """Load an evidence packet by id."""
    path = evidence_path(evidence_id)
    if not path.exists():
        return None, path
    return load_json_file(path), path


def inspect_evidence(evidence_id, json_output=False):
    """Display one evidence packet."""
    if not evidence_id:
        print("Error: inspect-evidence requires an evidence id.")
        return 1

    evidence, path = load_evidence(evidence_id)
    if evidence is None:
        print(f"Error: evidence not found: {evidence_id}")
        print(f"Expected: {path}")
        return 1

    if json_output:
        print(json.dumps({"evidence": evidence, "path": str(path)}, indent=2, sort_keys=True))
        return 0

    print(f"Evidence: {evidence['id']}")
    print(f"Path: {path}")
    source = evidence.get("source", {})
    print(f"Source: {source.get('id', 'unknown')} — {source.get('name', 'unknown')}")
    print(f"Classification: {evidence.get('classification', 'unknown')}")
    claims = evidence.get("claims", [])
    print(f"Claims: {len(claims)}")
    for claim in claims:
        print(f"  {claim.get('id')}: {claim.get('text')}")
        if claim.get("claim_type"):
            print(f"    type: {claim['claim_type']}")
    return 0


def add_claim(evidence_id, claim_text, claim_type=None, json_output=False):
    """Attach a manual claim to an evidence packet."""
    if not evidence_id or not claim_text:
        print('Error: add-claim requires an evidence id and claim text.')
        print('Example: dream-caesar add-claim WM-E-... "World models need symbolic state."')
        return 1

    evidence, path = load_evidence(evidence_id)
    if evidence is None:
        print(f"Error: evidence not found: {evidence_id}")
        print(f"Expected: {path}")
        return 1

    claims = evidence.setdefault("claims", [])
    claim_id = f"{evidence_id}-C{len(claims) + 1:03d}"
    claim = {
        "id": claim_id,
        "created_at": utc_now(),
        "text": claim_text,
        "claim_type": claim_type or "manual",
        "status": "operator-extracted",
    }
    claims.append(claim)
    evidence["updated_at"] = utc_now()
    write_json_file(path, evidence)

    if json_output:
        print(json.dumps({"claim": claim, "evidence": evidence, "path": str(path)}, indent=2, sort_keys=True))
    else:
        print(f"Claim: {claim_id}")
        print(f"Evidence: {evidence_id}")
        print(f"Text: {claim_text}")
        print(f"Path: {path}")
    return 0


def show_proposal_evidence(proposal_id, json_output=False):
    """List evidence packets attached to a proposal."""
    if not proposal_id:
        print("Error: evidence requires a proposal id.")
        return 1

    path = proposal_path(proposal_id)
    if not path.exists():
        print(f"Error: proposal not found: {proposal_id}")
        print(f"Expected: {path}")
        return 1

    proposal = load_json_file(path)
    evidence_packets = []
    missing = []
    for evidence_id in proposal.get("source_evidence", []):
        packet, packet_path = load_evidence(evidence_id)
        if packet:
            evidence_packets.append({"evidence": packet, "path": str(packet_path)})
        else:
            missing.append(evidence_id)

    payload = {
        "proposal_id": proposal_id,
        "evidence_count": len(evidence_packets),
        "evidence": evidence_packets,
        "missing": missing,
    }

    if json_output:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    print(f"Proposal: {proposal_id}")
    print(f"Evidence: {len(evidence_packets)}")
    for item in evidence_packets:
        packet = item["evidence"]
        source = packet.get("source", {})
        print(f"{packet['id']}: {source.get('id', 'unknown')} — {source.get('name', 'unknown')}")
        print(f"  claims: {len(packet.get('claims', []))}")
        print(f"  path: {item['path']}")
    if missing:
        print("Missing evidence:")
        for evidence_id in missing:
            print(f"  {evidence_id}")
    return 0


def create_proposal(change, json_output=False):
    """Create a local world-state proposal object."""
    if not change:
        print('Error: propose requires a change. Example: dream-caesar propose "Add source registry"')
        return 1

    ensure_world_model_dirs()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    proposal_id = f"WM-P-{timestamp}-{safe_id_fragment(change)}"
    path = proposal_path(proposal_id)
    proposal = {
        "id": proposal_id,
        "created_at": utc_now(),
        "status": "proposed",
        "change": change,
        "source_evidence": [],
        "truth_verdict": "pending",
        "world_state_commit": None,
        "notes": [
            "Proposal is local only.",
            "Verification must attach evidence before commit-world can proceed.",
        ],
    }
    write_json_file(path, proposal)

    if json_output:
        print(json.dumps({"proposal": proposal, "path": str(path)}, indent=2, sort_keys=True))
    else:
        print(f"Proposal: {proposal_id}")
        print(f"Path: {path}")
        print("Status: proposed")
        print("Next: dream-caesar verify " + proposal_id)
    return 0


def normalize_decision(decision):
    """Normalize verifier decisions."""
    if not decision:
        return None
    decision = decision.lower().strip().replace("_", "-")
    aliases = {
        "approve": "approve",
        "approved": "approve",
        "reject": "reject",
        "rejected": "reject",
        "needs-more-evidence": "needs-more-evidence",
        "more-evidence": "needs-more-evidence",
        "needs-evidence": "needs-more-evidence",
    }
    return aliases.get(decision)


def verify_proposal(proposal_id, json_output=False, decision=None, note=None):
    """Create or display a local truth-verdict for a proposal."""
    if not proposal_id:
        print("Error: verify requires a proposal id.")
        return 1

    path = proposal_path(proposal_id)
    if not path.exists():
        print(f"Error: proposal not found: {proposal_id}")
        print(f"Expected: {path}")
        return 1

    ensure_world_model_dirs()
    proposal = load_json_file(path)
    existing_verdict = None
    if verdict_path(proposal_id).exists():
        existing_verdict = load_json_file(verdict_path(proposal_id))

    normalized_decision = normalize_decision(decision)
    if decision and not normalized_decision:
        print("Error: --decision must be approve, reject, or needs-more-evidence.")
        return 1

    if not normalized_decision and existing_verdict:
        preserved_statuses = {"approved", "rejected", "needs_more_evidence"}
        if existing_verdict.get("status") in preserved_statuses:
            if json_output:
                print(json.dumps(
                    {"proposal": proposal, "verdict": existing_verdict},
                    indent=2,
                    sort_keys=True,
                ))
            else:
                print(f"Proposal: {proposal_id}")
                print(f"Verdict: {existing_verdict.get('status')}")
                print(f"Verified: {existing_verdict.get('verified')}")
                print(existing_verdict.get("decision", ""))
                print(f"Verdict path: {verdict_path(proposal_id)}")
            return 0

    evidence_ids = proposal.get("source_evidence", [])
    evidence_checked = []
    missing_evidence = []
    for evidence_id in evidence_ids:
        path_for_evidence = evidence_path(evidence_id)
        if path_for_evidence.exists():
            evidence_checked.append(load_json_file(path_for_evidence))
        else:
            missing_evidence.append(evidence_id)

    if normalized_decision == "approve" and not evidence_checked:
        print("Error: refusing approval without attached evidence.")
        print("Run: dream-caesar ingest <source-id-or-path> --proposal " + proposal_id)
        return 1

    verified = normalized_decision == "approve"
    if normalized_decision == "approve":
        status = "approved"
        decision_text = "Manual verifier approved this proposal for world-state commit."
        required_next_step = "Run commit-world to materialize a local world-state commit."
    elif normalized_decision == "reject":
        status = "rejected"
        decision_text = "Manual verifier rejected this proposal."
        required_next_step = "Revise or create a new proposal."
    elif normalized_decision == "needs-more-evidence":
        status = "needs_more_evidence"
        decision_text = "Manual verifier requested more evidence."
        required_next_step = "Attach additional evidence and verify again."
    elif evidence_checked:
        status = "evidence_attached"
        decision_text = "No world-state commit allowed yet."
        required_next_step = "Run a real verifier over attached evidence."
    else:
        status = "needs_evidence"
        decision_text = "No world-state commit allowed yet."
        required_next_step = "Attach source evidence and run a real verifier."

    verdict = {
        "proposal_id": proposal_id,
        "created_at": utc_now(),
        "status": status,
        "verified": verified,
        "manual_decision": normalized_decision,
        "manual_note": note,
        "evidence_checked": evidence_checked,
        "missing_evidence": missing_evidence,
        "decision": decision_text,
        "required_next_step": required_next_step,
    }
    write_json_file(verdict_path(proposal_id), verdict)

    if normalized_decision:
        proposal["truth_verdict"] = status
        proposal["updated_at"] = utc_now()
        write_json_file(path, proposal)

    if json_output:
        print(json.dumps({"proposal": proposal, "verdict": verdict}, indent=2, sort_keys=True))
    else:
        print(f"Proposal: {proposal_id}")
        print(f"Verdict: {verdict['status']}")
        print(f"Verified: {verdict['verified']}")
        print(verdict["decision"])
        print(f"Verdict path: {verdict_path(proposal_id)}")
    return 0


def commit_world(proposal_id, json_output=False):
    """Create a local world-state commit for a verified proposal."""
    if not proposal_id:
        print("Error: commit-world requires a proposal id.")
        return 1

    path = proposal_path(proposal_id)
    verdict = verdict_path(proposal_id)
    if not path.exists():
        print(f"Error: proposal not found: {proposal_id}")
        return 1
    if not verdict.exists():
        print(f"Refusing commit: no verdict exists for {proposal_id}.")
        print(f"Run: dream-caesar verify {proposal_id}")
        return 1

    verdict_payload = load_json_file(verdict)
    if not verdict_payload.get("verified"):
        print(f"Refusing commit: proposal {proposal_id} is not verified.")
        print(f"Verdict: {verdict_payload.get('status', 'unknown')}")
        print("World-state commits require verified=true.")
        if json_output:
            print(json.dumps({"committed": False, "verdict": verdict_payload}, indent=2, sort_keys=True))
        return 1

    proposal = load_json_file(path)
    ensure_world_model_dirs()
    world_state = load_world_state()

    if proposal_id in world_state.get("proposals", {}):
        existing_commit = world_state["proposals"][proposal_id].get("commit_id")
        print(f"Proposal already committed: {proposal_id}")
        print(f"Commit: {existing_commit}")
        return 0

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    commit_id = f"WM-C-{timestamp}-{safe_id_fragment(proposal_id)}"
    commit = {
        "id": commit_id,
        "created_at": utc_now(),
        "proposal_id": proposal_id,
        "proposal_change": proposal.get("change"),
        "verdict_path": str(verdict),
        "proposal_path": str(path),
        "evidence": proposal.get("source_evidence", []),
        "state_effect": "recorded_proposal_commit",
        "notes": [
            "This is a local world-state index commit.",
            "It records the accepted proposal; it does not mutate external systems.",
        ],
    }
    write_json_file(world_commit_path(commit_id), commit)

    world_state.setdefault("commits", []).append(commit_id)
    world_state.setdefault("proposals", {})[proposal_id] = {
        "commit_id": commit_id,
        "change": proposal.get("change"),
        "committed_at": commit["created_at"],
        "evidence": proposal.get("source_evidence", []),
    }
    world_state["version"] = int(world_state.get("version", 0)) + 1
    world_state["updated_at"] = utc_now()
    write_json_file(WORLD_STATE_PATH, world_state)

    proposal["status"] = "committed"
    proposal["world_state_commit"] = commit_id
    proposal["updated_at"] = utc_now()
    write_json_file(path, proposal)

    if json_output:
        print(json.dumps({"committed": True, "commit": commit, "world_state": world_state}, indent=2, sort_keys=True))
    else:
        print(f"Committed: {commit_id}")
        print(f"Proposal: {proposal_id}")
        print(f"World state: {WORLD_STATE_PATH}")
        print(f"Commit path: {world_commit_path(commit_id)}")
    return 0


def route_query(query, session_id=None, verbose=False, manual=False):
    """
    Route a query through the system.

    1. Router checks for past solutions.
    2. If solved, display the past solution.
    3. If not solved, create a session and run the pipeline.
    4. When Purple says "solved", crystallize.

    Args:
        query: The user's problem statement.
        session_id: Existing session to continue (for --pipeline mode).
        verbose: Print detailed output.
        manual: If True, pause at each pipeline stage (--pipeline mode).

    Returns:
        dict with outcome and session_id.
    """
    from router import router_lookup, format_router_response
    from pipeline_enforcer import PipelineEnforcer, PipelineStage
    from ledger import create_session, update_session
    from crystallize import crystallize

    # --- Router lookup ---
    router_result = router_lookup(query)
    if verbose:
        print(format_router_response(router_result))
        print()

    # --- Previously solved: display and exit ---
    if router_result["found"]:
        attempts = router_result["attempts"]
        solved = [a for a in attempts if a["outcome"] == "solved"]
        not_solved = [a for a in attempts if a["outcome"] == "not_solved"]

        if solved:
            latest = solved[0]
            print("=== PREVIOUSLY SOLVED ===")
            print(f"Session: {latest['session_id']}")
            print(f"Solution: {latest.get('solution', 'N/A')}")
            print()
            print("Run with --pipeline to force re-processing if needed.")
            return {"outcome": "displayed", "session_id": latest["session_id"]}

        if not_solved:
            latest = not_solved[0]
            print("=== PREVIOUS ATTEMPT FAILED ===")
            print(f"Session: {latest['session_id']}")
            print(f"Feedback: {latest.get('feedback', 'None')}")
            print("Triggering recursion with new feedback context...")
            print()
            # Fall through to pipeline with recursion context

    # --- Create or resume session ---
    if not session_id:
        session_id = create_session(query, outcome="in_progress")
        print(f"Session: {session_id}")

    # --- Initialize pipeline ---
    enforcer = PipelineEnforcer(session_id)
    enforcer.start()

    if verbose:
        print(f"Pipeline started: {enforcer.current_stage.value}")

    # --- Determine recursion context ---
    recursion_feedback = None
    if router_result["found"] and router_result.get("previous_feedback"):
        recursion_feedback = router_result["previous_feedback"]
        if verbose:
            print(f"Recursion feedback loaded: {recursion_feedback}")

    # --- Walk the pipeline ---
    pipeline_stages = [
        PipelineStage.RED,
        PipelineStage.ORANGE,
        PipelineStage.YELLOW,
        PipelineStage.GREEN,
        PipelineStage.BLUE,
        PipelineStage.PURPLE,
    ]

    for stage in pipeline_stages:
        stage_name = stage.value.upper()

        if manual:
            # --pipeline mode: pause and wait for user input at each stage
            print(f"\n--- {stage_name} ---")
            if sys.stdin.isatty():
                stage_input = input(f"Enter {stage_name} output (or press Enter to skip): ").strip()
            else:
                # Non-interactive: use default
                stage_input = ""
                print(f"[non-interactive] Skipping {stage_name} input")
            if stage_input:
                result = enforcer.advance(stage, {"input": stage_input})
            else:
                result = enforcer.advance(stage, {"input": "skipped"})
        else:
            # Auto mode: log the transition, LLM handles reasoning via SKILL.md
            stage_context = {
                "query": query,
                "recursion_feedback": recursion_feedback,
                "session_id": session_id,
            }
            result = enforcer.advance(stage, stage_context)

        if verbose:
            print(f"  [{stage_name}] {result.get('message', '')}")

        if result["status"] == "violation":
            print(f"Pipeline violation at {stage_name}: {result['message']}")
            break

    # --- Purple reflection: decide crystallize or recurse ---
    print()
    print("--- PURPLE REFLECTION ---")
    if manual and sys.stdin.isatty():
        outcome_input = input("Outcome (solved / not_solved): ").strip().lower()
        solution_input = input("Solution summary: ").strip() if outcome_input == "solved" else None
        feedback_input = input("Feedback for recursion: ").strip() if outcome_input == "not_solved" else None
    else:
        # Auto mode or non-interactive: mark as solved (LLM will refine via SKILL.md in practice)
        outcome_input = "solved"
        solution_input = f"Pipeline completed for: {query[:80]}"
        feedback_input = None

    if outcome_input == "solved" and solution_input:
        # Crystallize
        print("Crystallizing solution...")
        update_session(session_id, solution=solution_input, outcome="solved")
        crystal = crystallize(session_id, solution_input)
        print(f"Crystal: {crystal.get('crystal_id', 'unknown')}")
        print(f"Git: {crystal.get('git_commit_hash', 'N/A')}")
        enforcer.advance(PipelineStage.CRYSTAL)
        return {"outcome": "crystallized", "session_id": session_id, "crystal": crystal}

    if outcome_input == "not_solved":
        # Recursion
        update_session(
            session_id,
            outcome="not_solved",
            feedback=feedback_input or "Recursion triggered",
        )
        print(f"Recursion: looping back to Red with feedback: {feedback_input}")
        enforcer.advance(PipelineStage.RED, {"recursion": True, "feedback": feedback_input})
        return {"outcome": "not_solved", "session_id": session_id, "feedback": feedback_input}

    # Default: treat as solved without crystal
    update_session(session_id, solution="Pipeline completed", outcome="solved")
    return {"outcome": "completed", "session_id": session_id}


def build_parser():
    """Build the argparse CLI."""
    parser = argparse.ArgumentParser(
        prog="dream-caesar",
        description="Dream Caesar — the prism where signal enters and exits.",
        epilog="Example: python dream-caesar.py 'How should Dream Caesar introduce itself?'",
    )

    parser.add_argument(
        "query",
        nargs="?",
        default=None,
        help=(
            "A platform command or a problem/question to process through "
            "the Sacred Pipeline."
        ),
    )
    parser.add_argument(
        "command_args",
        nargs="*",
        help="Arguments for platform commands.",
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Run the first-run setup wizard.",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show full system status (consciousness, ledger, config).",
    )
    parser.add_argument(
        "--pipeline",
        action="store_true",
        help="Manually step through the Sacred Pipeline stage by stage.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed output at each step.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON.",
    )
    parser.add_argument(
        "--classification",
        default=None,
        help="Filter source registry rows by classification text.",
    )
    parser.add_argument(
        "--proposal",
        default=None,
        help="Attach an ingested source evidence packet to a proposal id.",
    )
    parser.add_argument(
        "--decision",
        default=None,
        help="Manual verifier decision: approve, reject, or needs-more-evidence.",
    )
    parser.add_argument(
        "--note",
        default=None,
        help="Manual verifier note recorded with --decision.",
    )
    parser.add_argument(
        "--claim-type",
        default=None,
        help="Optional claim type for add-claim.",
    )

    return parser


def normalize_subject(args):
    """Join command arguments into a subject string."""
    return " ".join(args.command_args).strip() if args.command_args else None


def main():
    parser = build_parser()
    args = parser.parse_args()

    from user_config import user_config

    # --- --setup flag ---
    if args.setup:
        run_setup(user_config)
        return 0

    command = args.query if args.query in PLATFORM_COMMANDS else None
    subject = normalize_subject(args)

    # --- --status flag / status command ---
    if args.status or command == "status":
        show_status()
        return 0

    # --- World Model platform commands ---
    if command == "sources":
        show_sources(
            json_output=args.json_output,
            source_filter=subject,
            classification_filter=args.classification,
        )
        return 0

    if command == "ask":
        if not subject:
            print('Error: ask requires a question. Example: dream-caesar ask "What changed?"')
            return 1
        args.query = subject

    if command == "propose":
        return create_proposal(subject, json_output=args.json_output)

    if command == "verify":
        return verify_proposal(
            subject,
            json_output=args.json_output,
            decision=args.decision,
            note=args.note,
        )

    if command == "commit-world":
        return commit_world(subject, json_output=args.json_output)

    if command == "ingest":
        return ingest_source(subject, proposal_id=args.proposal, json_output=args.json_output)

    if command == "evidence":
        return show_proposal_evidence(subject, json_output=args.json_output)

    if command == "inspect-evidence":
        return inspect_evidence(subject, json_output=args.json_output)

    if command == "add-claim":
        if not args.command_args:
            print('Error: add-claim requires an evidence id and claim text.')
            return 1
        evidence_id = args.command_args[0]
        claim_text = " ".join(args.command_args[1:]).strip()
        return add_claim(
            evidence_id,
            claim_text,
            claim_type=args.claim_type,
            json_output=args.json_output,
        )

    # --- Query required for pipeline modes ---
    if not args.query and not args.pipeline:
        parser.print_help()
        return 1

    if args.pipeline and not args.query:
        print("Error: --pipeline requires a query argument.")
        print("Usage: python dream-caesar.py --pipeline 'your question'")
        return 1

    # --- Consciousness check on startup ---
    consciousness = run_consciousness_check(verbose=args.verbose)

    if consciousness["status"] == "degraded":
        warnings = [w for w in consciousness["warnings"] if w["status"] == "fail"]
        if warnings:
            print(f"\nCritical issue: {warnings[0]['message']}")
            print("Run with --status for details.")
            return 1

    # --- Check first run ---
    if check_first_run(user_config):
        print("First run detected. Running setup wizard...\n")
        run_setup(user_config)
        print()

    # --- Route the query ---
    print(f"Query: {args.query}\n")

    result = route_query(
        args.query,
        verbose=args.verbose,
        manual=args.pipeline,
    )

    if args.json_output:
        print(json.dumps(result, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
