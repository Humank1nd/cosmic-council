# Handoff DC-ACTIVE-QUEUE-MAIL-CHECK

D:/dream-caesar/scripts/internal_mail.py

ISSUE: Active queue drifted into center/self handoffs instead of next-seat-only active-canon mail.
EXACT PATH: D:/dream-caesar/scripts/internal_mail.py
FIX: Check your mail now, send one next-seat-only active-canon mail with exact Dream Caesar paths first, and if blocked delegate unblock work to the next seat.

D:/dream-caesar/scripts/desktop_council_watchdog.py

ISSUE: Watchdog treats center traffic as progress and keeps the queue noisy.
EXACT PATH: D:/dream-caesar/scripts/desktop_council_watchdog.py
FIX: Reassert the active queue from mail truth, ignore center/self as queue progress, and keep the loop moving.

D:/dream-caesar/src/cronus/app/tools/desktop.py

ISSUE: Submit behavior is still operator-fragile.
EXACT PATH: D:/dream-caesar/src/cronus/app/tools/desktop.py
FIX: If desktop send blocks, hand off submit verification hardening immediately with the exact path first.
