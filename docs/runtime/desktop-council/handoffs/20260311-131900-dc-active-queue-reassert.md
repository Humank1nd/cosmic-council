# Handoff DC-ACTIVE-QUEUE-REASSERT

ISSUE: Active-canon desktop loop is stalling and operators are compensating manually.

EXACT PATHS:
- scripts/internal_mail.py
- scripts/mail_routing.py
- scripts/desktop_council_watchdog.py
- scripts/desktop_handoff_runner.py
- src/cronus/app/tools/desktop.py

FIX:
- Check your mail now.
- Keep mail next-seat-only and active-canon only.
- Use exact Dream Caesar paths only.
- If blocked, send unblock work to the next seat with the exact path first.
- Never stop the loop.
