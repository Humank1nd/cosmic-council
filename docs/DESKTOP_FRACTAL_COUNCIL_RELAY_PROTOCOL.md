# Desktop Fractal Council Relay Protocol

Purpose: let one council seat pass the torch to the next seat using short notes with exact local Dream Caesar paths.

Default handoff folder:
- `D:\dream-caesar\docs\runtime\desktop-council\handoffs`

## Rule

Every relay note must contain exact repo paths.

No vague references like:
- "the runtime file"
- "that route"
- "the desktop thing"

Use real paths instead.

## Relay Note Format

```text
RELAY <TASK_ID>
FROM: <SEAT>
TO: <NEXT_SEAT>
WHY: <one sentence>
PATHS:
- <path>
- <path>
- <path>
WATCHOUT: <one sentence>
NEXT: <one sentence telling the next seat what to do>
```

## Good Example

```text
RELAY DC-RELAY-001
FROM: RED
TO: ORANGE
WHY: runtime dispatch still depends on stale selector assumptions.
PATHS:
- scripts/desktop_handoff_runner.py
- scripts/desktop_fractal_council_probe.py
- src/cronus/app/tools/desktop.py
WATCHOUT: do not trust submit_attempted as send truth unless the UI-level result is verified.
NEXT: verify the next durable repair step and preserve canon routing while doing it.
```

## Closeout Rule

Do not end with `DONE`.

End work by:
- writing a handoff note file,
- then outputting one final line containing only the absolute path to that file.

Example final line:

```text
D:\dream-caesar\docs\runtime\desktop-council\handoffs\20260312-010000-dc-relay-001-red-to-orange.md
```

## Helper Script

Preferred helper:
- `D:\dream-caesar\scripts\create_handoff_note.py`

Example:

```text
python D:\dream-caesar\scripts\create_handoff_note.py --task-id DC-RELAY-001 --from-seat red --to-seat orange --summary "runtime dispatch still depends on stale selector assumptions" --paths scripts/desktop_handoff_runner.py scripts/desktop_fractal_council_probe.py src/cronus/app/tools/desktop.py --watchout "do not trust submit_attempted as send truth unless the UI-level result is verified" --next "verify the next durable repair step and preserve canon routing while doing it"
```

## Seat Behavior

When a seat receives a relay note, it should:
- open the listed paths first,
- confirm whether those paths are truly canonical,
- keep or replace them with better local paths,
- write the next handoff note to disk,
- end with one final line containing only the absolute handoff path,
- leave another relay note only if Dream Caesar explicitly asks for one.

## Dream Caesar Behavior

Dream Caesar should:
- pass only 2-5 paths at a time,
- route across seat specialties,
- preserve the same `TASK_ID` or use a clear child ID,
- log every relay note in the local handoff log.
