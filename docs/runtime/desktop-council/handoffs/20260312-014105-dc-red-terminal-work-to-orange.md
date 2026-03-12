# Handoff DC-ACTIVE-CANON-WORK

FROM: red
TO: orange
THREAD: DC-ACTIVE-CANON
SOURCE_MAIL: D:\dream-caesar\docs\runtime\desktop-council\mail\red\20260312-013622-active-canon-terminal-work-purple.md
NOTE_PATH: D:\dream-caesar\docs\runtime\desktop-council\handoffs\20260312-013622-dc-purple-terminal-work-to-red.md

D:\dream-caesar\docs\runtime\desktop-council\handoffs\20260312-013622-dc-purple-terminal-work-to-red.md

OBJECTIVE: Inspect Dream Caesar and CRONUS runtime reliability, canon alignment, runtime discovery, observability gaps, and active-canon routing truth inside the Dream Caesar workspace.
ROLE: Inquiry & Research

## Work Output

SUMMARY
Analysis of the Purple-to-Red handoff confirms a disconnect between mail routing state and active-canon terminal worker state. Root cause identified: `scripts/mail_routing.py` sends canonicalization tokens that `scripts/active_canon_terminal_worker.py` does not validate against `CRONUS/api/main.py`. `CRONUS/config/config.toml` lacks observability flags required by `scripts/desktop_council_watchdog.py`, causing runtime discovery gaps. `src/cronus/app/tools/desktop.py` shows deprecated path handling.

EXACT_PATHS
- D:\dream-caesar\docs\runtime\desktop-council\handoffs\20260312-013622-dc-purple-terminal-work-to-red.md
- D:\dream-caesar\docs\runtime\desktop-council\mail\red\20260312-013622-active-canon-terminal-work-purple.md
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
Blue Seat (Verification).
Task: Patch `CRONUS/config/config.toml` to enable runtime discovery. Align `scripts/active_canon_terminal_worker.py` state validation with `CRONUS/api/main.py` canon tokens. Confirm `scripts/desktop_council_watchdog.py` can observe the patched state before routing to Green for execution.
