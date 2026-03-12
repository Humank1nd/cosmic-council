# Dream Caesar Desktop Council Alignment Plan

## Objective

Realign the desktop council so status, canon scope, mail routing, and desktop dispatch all tell the same truth inside `D:/dream-caesar`.

## Plan A: Runtime Root Alignment

Issue: The live loop must remain fully anchored in Dream Caesar local runtime state and reject stale external workspace roots.

Exact paths:
- `D:/dream-caesar/scripts/internal_mail.py`
- `D:/dream-caesar/scripts/mail_routing.py`
- `D:/dream-caesar/scripts/desktop_handoff_runner.py`
- `D:/dream-caesar/scripts/desktop_fractal_council_probe.py`
- `D:/dream-caesar/scripts/desktop_council_watchdog.py`
- `D:/dream-caesar/scripts/ajna_monitor.py`
- `D:/dream-caesar/scripts/openclaw_desktop_council_monitor.py`
- `D:/dream-caesar/scripts/create_handoff_note.py`

Fix:
- Introduce one Dream Caesar runtime root and derive mail, handoffs, screenshots, status, and active canon from it.
- Stop hardcoding external workspace roots in the Dream Caesar desktop loop.

## Plan B: Active Canon Truth Alignment

Issue: The active canon must only point at local Dream Caesar or CRONUS paths, or the agents cannot do truthful path-based work.

Exact paths:
- `D:/dream-caesar/scripts/mail_routing.py`
- `D:/dream-caesar/scripts/internal_mail.py`
- `D:/dream-caesar/scripts/desktop_council_watchdog.py`
- `D:/dream-caesar/docs/runtime/desktop-council/active-canon.json`

Fix:
- Keep the active canon source of truth inside Dream Caesar.
- Refuse active-canon startup when required paths do not exist in the current workspace.
- Surface the workspace-mismatch blocker directly in status instead of letting the queue appear merely stale.

## Plan C: Queue Truth Alignment

Issue: The watchdog still treats `center` traffic as queue progress even though the active ring is `blue <-> purple`.

Exact paths:
- `D:/dream-caesar/scripts/desktop_council_watchdog.py`
- `D:/dream-caesar/scripts/mail_routing.py`
- `D:/dream-caesar/src/cronus/app/council/canon_adapter.py`

Fix:
- Measure queue freshness from valid next-seat-only mail first.
- Treat `center` handoffs as coordinator artifacts, not active-queue progress.
- Emit separate status for `mail_fresh`, `handoff_fresh`, and `canon_valid`.

## Plan D: Submit Verifiability Alignment

Issue: Desktop automation currently proves focus and typing, but not actual send.

Exact paths:
- `D:/dream-caesar/src/cronus/app/tools/desktop.py`
- `D:/dream-caesar/scripts/desktop_handoff_runner.py`
- `D:/dream-caesar/scripts/terminal_langchain.py`

Fix:
- Add explicit submit modes: `enter`, `ctrl-enter`, `both`.
- Return `submit_attempted` separately from `submit_verified`.
- Let callers choose submit mode and record it in logs/status.

## Recommended Order

1. Plan A
2. Plan B
3. Plan C
4. Plan D
