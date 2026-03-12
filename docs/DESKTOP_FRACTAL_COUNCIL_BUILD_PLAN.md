# Desktop Fractal Council Build Plan

Purpose: turn Dream Caesar into the desktop orchestrator for a live human-arranged Cosmic Council made of Codex, Claude, and Gemini windows.

Audience: one very capable operator who benefits from extremely explicit sequencing, low ambiguity, and visible stop points.

Rule set:
- Do one line at a time.
- Do not skip validation steps.
- If a step fails, stop and fix that exact step before continuing.
- Do not open extra threads of work unless the current step explicitly says to.

## Outcome

Dream Caesar sits in the middle of the hexaclock, sees the desktop, identifies each council member window, sends atomic handoff prompts with mouse/keyboard control, waits for local completion signals, then reports completed work back into the center and requests the next task.

## Phase 0: Non-negotiable constraints

- Dream Caesar must be able to capture the desktop.
- Dream Caesar must be able to list and focus windows by title.
- Dream Caesar must be able to move the mouse, click, type text, and send hotkeys.
- Every automation action must support a dry run or an explicit confirmation flag.
- Every handoff must leave a written artifact or log line.

Definition of done:
- A single command can identify the visible operator windows.
- A single command can focus one target window.
- A single command can type and send a handoff message.
- A single command can return to the central Dream Caesar window.

## Phase 1: Foundation

1. Confirm Dream Caesar vision works on the current desktop.
Done when: a screenshot file exists and can be inspected.

2. Confirm the desktop-control toolchain can enumerate visible windows.
Done when: titles, positions, and sizes are returned in structured JSON.

3. Confirm Dream Caesar can focus a specific window.
Done when: the target window becomes foreground reliably.

4. Confirm Dream Caesar can type a short test string into a known text box.
Done when: the typed text visibly appears in the target window.

5. Confirm Dream Caesar can send Enter or a hotkey without breaking focus.
Done when: a test message is submitted successfully.

## Phase 2: Hexaclock mapping

1. Capture the full desktop.
2. Identify the center window.
3. Identify all visible LLM operator windows around it.
4. Assign each visible window a council seat.
5. Persist that mapping to disk.

Suggested seat file:
- center
- red
- orange
- yellow
- green
- blue
- purple

Definition of done:
- A machine-readable file exists with seat name, window title, coordinates, and activation strategy.

## Phase 3: Handoff protocol

Each handoff message must have exactly five parts:
- Council seat
- Task ID
- Exact task
- Exact output format
- Return instruction

Template:

```text
[Seat: RED]
Task ID: JB-0001
Task: Analyze the attached code path and identify the single highest-value issue.
Output format: 3 bullets max, each with file path and fix.
Return: Reply with DONE JB-0001 followed by your findings.
```

Completion protocol:
- Worker window replies with `DONE <TASK_ID>`.
- Dream Caesar captures the result.
- Dream Caesar writes the result into a local artifact.
- Dream Caesar routes the next task.

## Phase 4: Codex delegation loop

Codex is the implementation executor.

Loop:
1. Dream Caesar analyzes the current Jokebook objective.
2. Dream Caesar delegates one atomic implementation task to Codex.
3. Codex completes the task in the repo.
4. Codex sends a completion report back to Dream Caesar.
5. Dream Caesar verifies the report and requests the next task.

Codex completion report format:

```text
DONE JB-0007
Completed:
- what changed
- what was verified
Needs:
- next highest-value task
```

Definition of done:
- One full delegation cycle completes without manual copy/paste outside the desktop-control loop.

## Phase 5: Crystallization and future-RAG tagging

For every completed task:
- Save the prompt sent.
- Save the raw reply received.
- Save the repo artifact changed.
- Save verification status.
- Save semantic tags.

Required tags:
- route
- feature
- role
- council-seat
- confidence
- launch-critical
- follow-up-needed

Definition of done:
- Every cycle creates one structured record that can be searched later.

## Phase 6: Overnight operation mode

Run mode:
- Dream Caesar remains the conductor.
- Human only intervenes for ambiguity, auth, or broken focus.
- All completed cycles append to one rolling summary file.

Stop conditions:
- desktop focus mapping becomes stale
- a target window title changes and cannot be re-identified
- automation types into the wrong window
- payment/auth flow requires human approval

## Atomic microtask queue

### Track A: Desktop control

- A1. Add window enumeration tool.
- A2. Add window focus tool.
- A3. Add mouse move tool.
- A4. Add click tool.
- A5. Add text typing tool.
- A6. Add key press and hotkey tool.
- A7. Register tools in CRONUS.
- A8. Expose tools through API.
- A9. Smoke test each tool independently.

### Track B: Vision and mapping

- B1. Save a desktop screenshot to disk.
- B2. Inspect the screenshot.
- B3. Correlate screenshot regions with enumerated windows.
- B4. Write the seat map file.
- B5. Validate the seat map by focusing each seat once.

### Track C: Council orchestration

- C1. Define handoff message schema.
- C2. Define completion message schema.
- C3. Define task artifact schema.
- C4. Implement a send-message helper.
- C5. Implement a collect-response helper.
- C6. Implement a central cycle log.

### Track D: Jokebook execution loop

- D1. Dream Caesar chooses one Jokebook task.
- D2. Dream Caesar sends one Codex handoff.
- D3. Codex implements.
- D4. Codex reports completion.
- D5. Dream Caesar verifies and chooses next task.

## Tonight’s minimum viable slice

Required tonight:
- desktop screenshot works
- windows list works
- focus works
- type and send works
- one Codex handoff round trip works

Not required tonight:
- perfect autonomous OCR
- multi-monitor perfection
- generalized agent arbitration
- full future-RAG intelligence

## Execution notes

- Prefer reliable window titles over visual guessing whenever possible.
- Prefer focusing a window before typing, always.
- Prefer short, structured prompts over long natural-language paragraphs.
- Prefer one task per seat at a time.
- Prefer writing artifacts after every cycle, not batching later.
