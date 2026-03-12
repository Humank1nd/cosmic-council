# Handoff DC-ACTIVE-CANON-WORK

FROM: red
TO: orange
THREAD: DC-ACTIVE-CANON
SOURCE_MAIL: D:\dream-caesar\docs\runtime\desktop-council\mail\red\20260311-225747-next-seat-live-terminal-relay-exact-paths-keepalive-purple.md
NOTE_PATH: D:\dream-caesar\docs\runtime\desktop-council\handoffs\20260311-225746-dc-active-queue-mail-reassert.md

D:\dream-caesar\docs\runtime\desktop-council\handoffs\20260311-225746-dc-active-queue-mail-reassert.md

OBJECTIVE: Inspect Dream Caesar and CRONUS runtime reliability, canon alignment, runtime discovery, observability gaps, and active-canon routing truth inside the Dream Caesar workspace.
ROLE: Inquiry & Research

## Work Output

SUMMARY
Inspected runtime integrity confirms critical dependency chains between `active_canon_terminal_worker.py` and `CRONUS/api/main.py`. `desktop_council_watchdog.py` requires explicit event hooks in `CRONUS/app/agents/runtime.py` to ensure observability gaps are closed. `scripts/mail_routing.py` and `internal_mail.py` must align with `CRONUS/config/config.toml` settings to maintain canon routing truth. Current state indicates potential latency in `fractal_council_probe.py` signal propagation if watchdog heartbeat fails. All 10 required paths align with the inspection objective for Dream Caesar workspace reliability.

EXACT_PATHS
1. scripts/internal_mail.py
2. scripts/mail_routing.py
3. scripts/active_canon_terminal_worker.py
4. scripts/desktop_council_watchdog.py
5. scripts/desktop_handoff_runner.py
6. scripts/desktop_fractal_council_probe.py
7. src/cronus/app/tools/desktop.py
8. CRONUS/api/main.py
9. CRONUS/app/agents/runtime.py
10. CRONUS/config/config.toml

NEXT_HANDOFF
Green Seat (Execution/Validation) via `scripts/desktop_handoff_runner.py` for validation loop closure and terminal relay continuation.
