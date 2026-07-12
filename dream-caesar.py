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
    "ask",
    "propose",
    "verify",
    "commit-world",
}

SOURCE_REGISTRY = [
    {
        "id": "WM-S1",
        "name": "Dream Caesar CLI",
        "location": "dream-caesar.py",
        "classification": "active kernel",
    },
    {
        "id": "WM-S2",
        "name": "Ledger / Router / Crystallization",
        "location": "infrastructure/ledger",
        "classification": "active kernel",
    },
    {
        "id": "WM-S3",
        "name": "Cosmic Council Python package",
        "location": "src/cosmic_council",
        "classification": "active donor/kernel",
    },
    {
        "id": "WM-S4",
        "name": "CRONUS runtime and console",
        "location": "CRONUS",
        "classification": "runtime donor",
    },
    {
        "id": "WM-S5",
        "name": "Dream Caesar frontend",
        "location": "frontend",
        "classification": "UI donor",
    },
    {
        "id": "WM-D1",
        "name": "Dream Caesar Google Drive backup",
        "location": "gdrive:Dream Caesar Backups/2026-07-12/",
        "classification": "verified backup",
    },
    {
        "id": "WM-D8",
        "name": "World Model AI planning note",
        "location": "gdrive:F_Backup/Downloads/Walk me through the process of building a world model ai.md",
        "classification": "world-model planning note",
    },
]


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


def show_sources(json_output=False):
    """Display the first-pass World Model source registry."""
    payload = {
        "registry_doc": str(REPO_ROOT / "docs" / "WORLD_MODEL_SOURCE_REGISTRY.md"),
        "sources": SOURCE_REGISTRY,
        "rule": "Sources are evidence first. Promotion to canon requires classification.",
    }

    if json_output:
        print(json.dumps(payload, indent=2))
        return

    print("WORLD MODEL SOURCE REGISTRY")
    print("=" * 60)
    print(f"Registry doc: {payload['registry_doc']}")
    print(payload["rule"])
    print()
    for source in SOURCE_REGISTRY:
        print(f"{source['id']}: {source['name']}")
        print(f"  location: {source['location']}")
        print(f"  classification: {source['classification']}")


def show_command_contract(command, subject=None):
    """Print a non-mutating contract for World Model commands not wired yet."""
    contracts = {
        "ingest": (
            "ingest <source-id-or-path>",
            "Classify a source and prepare an evidence packet. "
            "Current scaffold does not import, copy, or promote material.",
        ),
        "propose": (
            'propose "<change>"',
            "Create a proposal object for a world-state change. "
            "Storage is not wired yet, so no proposal is committed.",
        ),
        "verify": (
            "verify <proposal-id>",
            "Check a proposal against source evidence and truth-verdict rules. "
            "Verification storage is not wired yet.",
        ),
        "commit-world": (
            "commit-world <proposal-id>",
            "Commit a verified proposal into the world-state ledger. "
            "This command is intentionally disabled until proposal verification exists.",
        ),
    }
    usage, description = contracts[command]
    print(f"Command: dream-caesar {usage}")
    print(description)
    if subject:
        print(f"Received: {subject}")


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
        show_sources(json_output=args.json_output)
        return 0

    if command == "ask":
        if not subject:
            print('Error: ask requires a question. Example: dream-caesar ask "What changed?"')
            return 1
        args.query = subject

    if command in {"ingest", "propose", "verify", "commit-world"}:
        show_command_contract(command, subject=subject)
        return 0

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
