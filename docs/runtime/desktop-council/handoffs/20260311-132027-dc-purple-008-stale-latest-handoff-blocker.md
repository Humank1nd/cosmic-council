# Handoff DC-PURPLE-008-STALE-LATEST-HANDOFF-BLOCKER

FROM: PURPLE
TO: CENTER

## Summary

Exact path first: `D:/dream-caesar/scripts/desktop_council_watchdog.py`. The active queue is still being judged against stale `LATEST` state from `D:/Jokebook/docs/research/...` instead of the live Dream Caesar runtime relay under `D:/dream-caesar/docs/runtime/desktop-council`. Missing input is not a new task from Purple; it is queue-truth correction in the watchdog. Until that happens, Purple can keep sending valid next-seat-only runtime mail and still look stale because the wrong handoff root is being watched.

## Paths

- D:/dream-caesar/scripts/desktop_council_watchdog.py
- D:/dream-caesar/scripts/internal_mail.py
- D:/dream-caesar/scripts/mail_routing.py
- D:/dream-caesar/docs/runtime/desktop-council/handoffs/20260311-131645-dc-active-queue-unblock.md
- D:/dream-caesar/docs/runtime/desktop-council/handoffs/20260311-131603-dc-purple-007-runtime-queue-truth.md
- D:/Jokebook/docs/research/dream-caesar-handoffs/20260311-130635-dc-purple-006-active-canon-workspace-blocker-purple-to-center.md

## Watchout

Do not treat the older Jokebook blocker handoff as live queue truth for the runtime loop. That file is historical context, while the live ring is now `DC-ACTIVE-CANON` under `D:/dream-caesar/docs/runtime/desktop-council`.

## Next

Update `D:/dream-caesar/scripts/desktop_council_watchdog.py` so `LATEST` for the runtime loop prefers Dream Caesar runtime handoffs and valid next-seat-only runtime mail before any older research handoff artifacts. Once that is corrected, Purple queue freshness will reflect the actual live relay instead of a stale external note.
