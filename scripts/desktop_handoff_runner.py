import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_ROOT.parent
SRC_ROOT = REPO_ROOT / "src"

src_root_str = str(SRC_ROOT)
if src_root_str not in sys.path:
    sys.path.insert(0, src_root_str)

from desktop_runtime import ARTIFACT_ROOT, HANDOFF_DIR, SEAT_MAP_PATH, ensure_runtime_dirs
from cronus.app.council.canon_adapter import (
    normalize_title,
    outer_seats,
    resolve_seat_window,
    seat_guiding_question,
    seat_guiding_thought,
    seat_key_responsibilities,
    seat_mission_pillar,
    seat_purpose,
    seat_role,
    seat_title,
    window_selector_for_seat,
)  # noqa: E402
from cronus.app.tools.desktop import handle_list_windows, handle_send_handoff  # noqa: E402


OUTPUT_DIR = ARTIFACT_ROOT
LOG_PATH = OUTPUT_DIR / "desktop-handoff-log.jsonl"
BOOTSTRAP_ORDER = outer_seats()
OUTPUT_RULE = f"OUTPUT: write handoff under {HANDOFF_DIR}. FINAL: one line with the absolute handoff path only."


def _canon_bootstrap_message(seat_name: str) -> str:
    return (
        f"TASK DC-BOOT-{seat_name.upper()} SEAT: {seat_title(seat_name).upper()} ROLE: {seat_role(seat_name)}. "
        f"FOCUS: {seat_guiding_question(seat_name)} "
        "OUTPUT: DONE plus <=3 bullets: finding | path | next step."
    )


def _canon_system_prompt(seat_name: str, output_rule: str) -> str:
    responsibilities = " | ".join(seat_key_responsibilities(seat_name))
    return (
        f"ROLE {seat_title(seat_name).upper()}. CANON ROLE: {seat_role(seat_name)}. PURPOSE: {seat_purpose(seat_name)} "
        f"MISSION: {seat_mission_pillar(seat_name)} GUIDING QUESTION: {seat_guiding_question(seat_name)} "
        f"RESPONSIBILITIES: {responsibilities}. GUIDING THOUGHT: {seat_guiding_thought(seat_name)} "
        f"RULES: no implementation unless asked; inspect only exact paths in scope; optimize for durable, efficient, canon-aligned outcomes. {output_rule}"
    )


BOOTSTRAP_MESSAGES = {seat: _canon_bootstrap_message(seat) for seat in BOOTSTRAP_ORDER}


def _path_first_task(task_id: str, paths: list[str], goal: str, write_fields: str) -> str:
    path_block = " | ".join(paths)
    return (
        f"TASK {task_id} PATHS: {path_block} GOAL: {goal} "
        f"WRITE: {write_fields}. {OUTPUT_RULE}"
    )


SYSTEM_PROMPTS = {seat: _canon_system_prompt(seat, OUTPUT_RULE) for seat in BOOTSTRAP_ORDER}
CANON_STUDY_MESSAGES = {
    "red": _path_first_task(
        "JB-CANON-RED",
        [
            "apps/web/src/app/book/page.tsx",
            "apps/web/src/app/venues/venues-client.tsx",
            "apps/web/src/app/venues/[id]/venue-detail-client.tsx",
            "apps/web/src/app/venues/[id]/book/page.tsx",
            "apps/web/src/components/features/users/user-profile.tsx",
        ],
        "find canon for route friction and booking entry; verify or replace the start files.",
        "handoff with canon | invariants | watchout",
    ),
    "orange": _path_first_task(
        "JB-CANON-ORANGE",
        [
            "apps/web/src/app/bookings/[id]/page.tsx",
            "apps/web/src/app/bookings/[id]/respond/page.tsx",
            "apps/web/src/app/bookings/[id]/respond/booking-respond-form.tsx",
            "apps/web/src/app/api/bookings/requests/[id]/respond/route.ts",
            "apps/web/src/app/notifications/page.tsx",
        ],
        "find canon for booking detail and response flow; verify or replace the start files.",
        "handoff with canon | invariants | watchout",
    ),
    "yellow": _path_first_task(
        "JB-CANON-YELLOW",
        [
            "apps/web/src/app/venues/dashboard/bookings/[id]/approve/page.tsx",
            "apps/web/src/app/venues/dashboard/bookings/[id]/approve/booking-approve-form.tsx",
            "apps/web/src/app/bookings/[id]/booking-payment-status-banner.tsx",
            "apps/web/src/app/api/bookings/[id]/approve/route.ts",
            "apps/web/src/lib/services/bookings/booking-service.ts",
        ],
        "find canon for payment lane and booking state machine; verify or replace the start files.",
        "handoff with canon | invariants | watchout",
    ),
    "green": _path_first_task(
        "JB-CANON-GREEN",
        [
            "apps/web/src/app/dashboard/page.tsx",
            "apps/web/src/app/venues/dashboard/page.tsx",
            "apps/web/src/app/venues/dashboard/bookings/page.tsx",
            "apps/web/src/components/booking/booking-requests.tsx",
            "apps/web/src/lib/navigation-ia.ts",
        ],
        "find canon for venue dashboard, inbox, and navigation IA; verify or replace the start files.",
        "handoff with canon | invariants | watchout",
    ),
    "blue": _path_first_task(
        "JB-CANON-BLUE",
        [
            "apps/web/src/app/book/page.tsx",
            "apps/web/src/app/bookings/[id]/page.tsx",
            "apps/web/src/app/venues/dashboard/bookings/[id]/approve/page.tsx",
            "apps/web/src/components/venues/booking-form.tsx",
            "apps/web/src/components/booking/venue-request-form.tsx",
        ],
        "find canon for launch-critical copy and behavior semantics; verify or replace the start files.",
        "handoff with canon | invariants | watchout",
    ),
    "purple": _path_first_task(
        "JB-CANON-PURPLE",
        [
            "apps/web/src/lib/data/firestore/bookable-comics.ts",
            "apps/web/src/lib/utils/requestable-profile.ts",
            "apps/web/src/app/api/bookings/request/route.ts",
            "apps/mobile/src/lib/services/comedians.ts",
            "apps/mobile/app/discover/index.tsx",
            "apps/mobile/app/comedians/[id].tsx",
            "apps/mobile/app/bookings/index.tsx",
        ],
        "find canon for cross-surface synthesis and next-task selection; verify or replace the start files.",
        "handoff with canon | invariants | watchout",
    ),
}


def _load_seat(seat_name: str) -> dict:
    if SEAT_MAP_PATH.exists():
        seat_map = json.loads(SEAT_MAP_PATH.read_text(encoding="utf-8"))
        seats = seat_map.get("seats", {})
        if seat_name in seats:
            seat = dict(seats[seat_name])
            seat.setdefault("title", seat_title(seat_name))
            return seat

    return {
        "title": seat_title(seat_name),
        "selector": {},
    }


def _selector_hints(seat: dict) -> dict:
    selector = dict(seat.get("selector", {}))
    bounds = seat.get("bounds", {})
    target_left = selector.get("target_left", bounds.get("left"))
    target_top = selector.get("target_top", bounds.get("top"))
    hints = {}
    if target_left is not None:
        hints["target_left"] = target_left
    if target_top is not None:
        hints["target_top"] = target_top
    return hints


def _handoff_defaults(seat: dict) -> dict:
    defaults = dict(seat.get("handoff_defaults", {}))
    normalized = {}
    for key in (
        "input_ratio_x",
        "input_offset_y",
        "input_band_min_offset_y",
        "input_band_max_offset_y",
        "input_padding_x",
        "input_x",
        "input_y",
        "focus_retries",
        "focus_delay_seconds",
        "focus_pause_seconds",
        "clear_input",
        "clear_hotkey",
        "clear_key",
        "clear_key_presses",
        "clear_pause_seconds",
        "text_entry_method",
        "paste_threshold",
    ):
        if defaults.get(key) is not None:
            normalized[key] = defaults[key]
    return normalized


def _resolve_dispatch_target(seat_name: str, seat: dict) -> tuple[dict, dict]:
    selector = dict(seat.get("selector", {}))
    hints = _selector_hints(seat)
    windows = handle_list_windows({}).get("windows", [])
    resolved_window = resolve_seat_window(
        windows,
        seat_name,
        exact_title=selector.get("exact_title") or seat.get("title"),
        target_left=hints.get("target_left"),
        target_top=hints.get("target_top"),
    )
    return window_selector_for_seat(seat_name, resolved_window), resolved_window


def _log_dispatch(seat_name: str, title: str, message: str, submit_requested: bool, dispatch_result: dict) -> None:
    ensure_runtime_dirs()
    record = {
        "timestamp": datetime.now().astimezone().isoformat(),
        "seat": seat_name,
        "title": title,
        "message": message,
        "submit_requested": submit_requested,
        "submit_attempted": bool(dispatch_result.get("submit_attempted", False)),
        "submitted": bool(dispatch_result.get("submitted", False)),
        "delivery_confidence": dispatch_result.get("delivery_confidence"),
        "click_target": dispatch_result.get("click_target"),
        "verification": dispatch_result.get("verification"),
    }
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


def send_message(seat_name: str, message: str, submit: bool, dry_run: bool = False, submit_mode: str = "enter") -> dict:
    seat = _load_seat(seat_name)
    selector, resolved_window = _resolve_dispatch_target(seat_name, seat)
    dispatch_result = handle_send_handoff(
        {
            **{
                **selector,
                "exact_title": normalize_title(resolved_window.get("title", "")),
                "target_left": resolved_window.get("left"),
                "target_top": resolved_window.get("top"),
            },
            **_handoff_defaults(seat),
            "message": message,
            "submit": submit,
            "submit_mode": submit_mode,
            "interval": 0.01,
            "confirm": not dry_run,
        }
    )
    if not dispatch_result.get("success"):
        raise RuntimeError(f"Failed to dispatch to seat {seat_name}: {dispatch_result}")

    focused_window = dispatch_result.get("window", resolved_window)
    if not dry_run:
        _log_dispatch(
            seat_name,
            focused_window.get("title", seat["title"]),
            message,
            submit,
            dispatch_result,
        )
    return dispatch_result


def build_relay_note(
    task_id: str,
    from_seat: str,
    to_seat: str,
    why: str,
    paths: list[str],
    next_action: str,
    watchout: str | None = None,
) -> str:
    path_block = " | ".join(paths)
    watchout_text = watchout or "verify the listed paths before trusting them as canon."
    return (
        f"TASK {task_id} PATHS: {path_block} FROM: {from_seat.upper()} TO: {to_seat.upper()} "
        f"WHY: {why} WATCHOUT: {watchout_text} NEXT: {next_action} "
        f"WRITE: handoff with exact paths. {OUTPUT_RULE}"
    )


def build_relay_file_message(
    task_id: str,
    from_seat: str,
    to_seat: str,
    handoff_file: str,
    alignment_note: str | None = None,
) -> str:
    alignment = alignment_note or "stay aligned to the cosmic canon role for that seat and preserve exact paths."
    return (
        f"TASK {task_id} FILE: {handoff_file} FROM: {from_seat.upper()} TO: {to_seat.upper()} "
        f"DO: open that file first. ALIGN: {alignment} "
        f"WRITE: next handoff with exact paths. {OUTPUT_RULE}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Dispatch Dream Caesar handoffs to desktop council seats.")
    parser.add_argument("--seat", choices=sorted(BOOTSTRAP_MESSAGES.keys()) + ["center"])
    parser.add_argument("--seats", nargs="+", choices=sorted(BOOTSTRAP_MESSAGES.keys()))
    parser.add_argument("--message")
    parser.add_argument("--bootstrap", action="store_true")
    parser.add_argument("--bootstrap-all", action="store_true")
    parser.add_argument("--system-prompt", action="store_true")
    parser.add_argument("--system-prompts-all", action="store_true")
    parser.add_argument("--canon-study", action="store_true")
    parser.add_argument("--canon-study-all", action="store_true")
    parser.add_argument("--relay-note", action="store_true")
    parser.add_argument("--relay-file", action="store_true")
    parser.add_argument("--from-seat", choices=sorted(BOOTSTRAP_MESSAGES.keys()) + ["center"])
    parser.add_argument("--to-seat", choices=sorted(BOOTSTRAP_MESSAGES.keys()) + ["center"])
    parser.add_argument("--task-id")
    parser.add_argument("--handoff-file")
    parser.add_argument("--alignment-note")
    parser.add_argument("--why")
    parser.add_argument("--paths", nargs="+")
    parser.add_argument("--next-action")
    parser.add_argument("--watchout")
    parser.add_argument("--no-submit", action="store_true")
    parser.add_argument("--submit-mode", choices=["enter", "ctrl-enter", "both"], default="enter")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--resolve-only", action="store_true")
    parser.add_argument("--delay-between", type=float, default=0.6)
    args = parser.parse_args()

    if args.resolve_only:
        seats_to_resolve: list[str] = []
        if args.seats:
            seats_to_resolve.extend(args.seats)
        elif args.seat:
            seats_to_resolve.append(args.seat)
        else:
            seats_to_resolve.extend(BOOTSTRAP_ORDER)

        resolved = {}
        for seat_name in seats_to_resolve:
            seat = _load_seat(seat_name)
            selector, window = _resolve_dispatch_target(seat_name, seat)
            resolved[seat_name] = {
                "selector": selector,
                "window": window,
                "handoff_defaults": _handoff_defaults(seat),
            }
        print(json.dumps({"success": True, "resolved": resolved}, indent=2))
        return 0

    if args.canon_study_all:
        results = {}
        for seat_name in BOOTSTRAP_ORDER:
            results[seat_name] = send_message(
                seat_name,
                CANON_STUDY_MESSAGES[seat_name],
                submit=not args.no_submit,
                dry_run=args.dry_run,
                submit_mode=args.submit_mode,
            )
            time.sleep(args.delay_between)
        print(
            json.dumps(
                {
                    "success": True,
                    "seats": BOOTSTRAP_ORDER,
                    "submit_requested": not args.no_submit,
                    "submit_mode": args.submit_mode,
                    "mode": "canon-study",
                    "dry_run": args.dry_run,
                    "results": results,
                }
            )
        )
        return 0

    if args.system_prompts_all:
        results = {}
        for seat_name in BOOTSTRAP_ORDER:
            results[seat_name] = send_message(
                seat_name,
                SYSTEM_PROMPTS[seat_name],
                submit=not args.no_submit,
                dry_run=args.dry_run,
                submit_mode=args.submit_mode,
            )
            time.sleep(args.delay_between)
        print(
            json.dumps(
                {
                    "success": True,
                    "seats": BOOTSTRAP_ORDER,
                    "submit_requested": not args.no_submit,
                    "submit_mode": args.submit_mode,
                    "mode": "system-prompts",
                    "dry_run": args.dry_run,
                    "results": results,
                }
            )
        )
        return 0

    if args.bootstrap_all:
        results = {}
        for seat_name in BOOTSTRAP_ORDER:
            results[seat_name] = send_message(
                seat_name,
                BOOTSTRAP_MESSAGES[seat_name],
                submit=not args.no_submit,
                dry_run=args.dry_run,
                submit_mode=args.submit_mode,
            )
            time.sleep(args.delay_between)
        print(json.dumps({"success": True, "seats": BOOTSTRAP_ORDER, "submit_requested": not args.no_submit, "submit_mode": args.submit_mode, "dry_run": args.dry_run, "results": results}))
        return 0

    if args.seats:
        results = {}
        for seat_name in args.seats:
            results[seat_name] = send_message(
                seat_name,
                BOOTSTRAP_MESSAGES[seat_name],
                submit=not args.no_submit,
                dry_run=args.dry_run,
                submit_mode=args.submit_mode,
            )
            time.sleep(args.delay_between)
        print(json.dumps({"success": True, "seats": args.seats, "submit_requested": not args.no_submit, "submit_mode": args.submit_mode, "dry_run": args.dry_run, "results": results}))
        return 0

    if args.bootstrap:
        if not args.seat:
            raise SystemExit("--seat is required with --bootstrap")
        message = BOOTSTRAP_MESSAGES.get(args.seat)
        if not message:
            raise SystemExit(f"No bootstrap message defined for seat {args.seat}")
    elif args.relay_file:
        if not args.to_seat:
            raise SystemExit("--to-seat is required with --relay-file")
        if not args.from_seat or not args.task_id or not args.handoff_file:
            raise SystemExit("--from-seat, --task-id, and --handoff-file are required with --relay-file")
        args.seat = args.to_seat
        message = build_relay_file_message(
            task_id=args.task_id,
            from_seat=args.from_seat,
            to_seat=args.to_seat,
            handoff_file=args.handoff_file,
            alignment_note=args.alignment_note,
        )
    elif args.relay_note:
        if not args.to_seat:
            raise SystemExit("--to-seat is required with --relay-note")
        if not args.from_seat or not args.task_id or not args.why or not args.paths or not args.next_action:
            raise SystemExit("--from-seat, --task-id, --why, --paths, and --next-action are required with --relay-note")
        args.seat = args.to_seat
        message = build_relay_note(
            task_id=args.task_id,
            from_seat=args.from_seat,
            to_seat=args.to_seat,
            why=args.why,
            paths=args.paths,
            next_action=args.next_action,
            watchout=args.watchout,
        )
    elif args.canon_study:
        if not args.seat:
            raise SystemExit("--seat is required with --canon-study")
        message = CANON_STUDY_MESSAGES.get(args.seat)
        if not message:
            raise SystemExit(f"No canon-study prompt defined for seat {args.seat}")
    elif args.system_prompt:
        if not args.seat:
            raise SystemExit("--seat is required with --system-prompt")
        message = SYSTEM_PROMPTS.get(args.seat)
        if not message:
            raise SystemExit(f"No system prompt defined for seat {args.seat}")
    elif args.message:
        if not args.seat:
            raise SystemExit("--seat is required with --message")
        message = args.message
    else:
        raise SystemExit("Provide --message or --bootstrap")

    result = send_message(args.seat, message, submit=not args.no_submit, dry_run=args.dry_run, submit_mode=args.submit_mode)
    print(json.dumps({"success": True, "seat": args.seat, "submit_requested": not args.no_submit, "submit_mode": args.submit_mode, "dry_run": args.dry_run, "result": result}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
