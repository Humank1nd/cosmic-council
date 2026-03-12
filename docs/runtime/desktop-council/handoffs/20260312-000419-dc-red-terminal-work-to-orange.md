# Handoff DC-ACTIVE-CANON-WORK

FROM: red
TO: orange
THREAD: DC-ACTIVE-CANON
SOURCE_MAIL: D:\dream-caesar\docs\runtime\desktop-council\mail\red\20260311-235928-active-canon-terminal-work-purple.md
NOTE_PATH: D:\dream-caesar\docs\runtime\desktop-council\handoffs\20260311-235928-dc-purple-terminal-work-to-red.md

D:\dream-caesar\docs\runtime\desktop-council\handoffs\20260311-235928-dc-purple-terminal-work-to-red.md

OBJECTIVE: Inspect Dream Caesar and CRONUS runtime reliability, canon alignment, runtime discovery, observability gaps, and active-canon routing truth inside the Dream Caesar workspace.
ROLE: Inquiry & Research

## Work Output

SUMMARY
I have reviewed the handoff from Purple Terminal Work (`20260311-235928-dc-purple-terminal-work-to-red.md`). The primary inquiry focuses on **canon alignment** and **runtime reliability**. 
WHY: The core instability lies in the disconnect between `active_canon_terminal_worker.py` execution states and CRONUS `config.toml` authority. Observability gaps exist where `desktop_council_watchdog.py` does not explicitly log routing failures back to `desktop_handoff_runner.py`. 
WHY: `src/cronus/app/tools/desktop.py` must verify if it is injecting runtime probes correctly without breaking the canon ring. 
WHY: `scripts/mail_routing.py` requires validation that it prioritizes active-canon tags over general terminal dispatch.
Current State: The handoff indicates Purple completed initial routing logic. Red must verify that the CRONUS API `api/main.py` is enforcing strict canon boundaries before the `fractal_council_probe.py` executes.

EXACT_PATHS
- scripts/internal_mail.py
- scripts/mail_routing.py
- scripts/active_canon_terminal_worker.py
- scripts/desktop_council_watchdog.py
- scripts/desktop_handoff_runner.py
- scripts/desktop_fractal_council_probe.py
- src/cronus/app/tools/desktop.py
- CRONUS/api/main.py
- CRONUS/app/agents/runtime.py
- CRONUS/config/config.toml

NEXT_HANDOFF
TARGET: Blue Executor (Action)
REASON: Research findings must be translated into runtime corrections.
ACTION:
1. Patch `mail_routing.py` to validate `config.toml` canon tags before dispatch.
2. Update `desktop_council_watchdog.py` to surface `runtime.py` observability gaps.
3. Verify `active_canon_terminal_worker.py` aligns with `CRONUS/api/main.py` enforcement logic.
4. Confirm `desktop_fractal_council_probe.py` does not route outside the canon ring.
HANDOFF_DATA: Red Owl Analysis Report (attached to terminal queue).
