# Render-Retro Self-Improvement Loop — Implementation Plan

> **Execution:** This plan is executed **inline** (superpowers:executing-plans), not by per-task subagents — most edits are exact-anchor find-and-replaces in already-read files, so a cold subagent per task would re-derive context for no gain. Checkpoint after Task 2 (the only real logic). Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Every render session records its snags to a durable cross-session log that produce-video reads before building and that tracks each recurring snag toward a structural fix, so the adversarial-QA gauntlet can be retired lane by lane on evidence.

**Architecture:** One append-only markdown log (`render-qa/snag-log.md`) with session entries + a retirement ledger. A PostToolUse hook fires on any HyperFrames render command and prompts the agent to write the retro at session close. produce-video reads the log at preflight (active input) and writes the retro at closing (backstop). The four QA lanes return structured `defect-class` tags so their FAILs fold mechanically into the ledger.

**Tech Stack:** Markdown docs, `.claude/settings.json` hooks (bash + `jq` + `grep -E`), Claude Code skill/agent markdown.

## Global Constraints

- Spec: `projects/video-production/render-qa/snag-loop-design.md` — the authority for every requirement below.
- Snag tags are exactly these five: `[env] [tooling] [authoring] [upstream] [defect]`.
- Retirement bar: a lane is nomination-eligible only after its structural fix holds **≥5 clean renders per template** across all 9 templates; a recurrence resets that template's count to zero. Retirement itself is human-gated, recorded in `decisions/log.md`.
- The retro hook is **on by default**; its manual off switch is env var `VIDEO_SNAG_RETRO_HOOK_DISABLED=1`.
- The render-command regex must be reused verbatim from the existing gauntlet hook (`.claude/settings.json`): `(^|[;&|]) *([A-Z_]+=[^ ]* )*(npm run render|npx (--yes )?hyperframes(@[^ ]*)?( lambda)? render)` — it was tightened to avoid false-positives on the word "render"; do not re-derive it.
- New files live under `projects/video-production/render-qa/` — the repo's Approved Root Layout (GOVERNANCE.md) forbids a new `docs/` root.
- Commit prefixes (GOVERNANCE.md): `project:` for `projects/`, `ops:` for `.claude/settings.json` hook config, `skill:` for `.claude/skills/` + `.claude/agents/`, `docs:` for `decisions/log.md`.

---

### Task 1: Create the snag-log artifact

**Files:**
- Create: `projects/video-production/render-qa/snag-log.md`

**Interfaces:**
- Produces: the file every other task references. Section headers relied on downstream: `## Session entries` (H2), `## Retirement ledger` (H2). Ledger columns: `Snag class | Occurrences | Structural fix | Retires | Per-template clean tally (9) | Status`.

- [ ] **Step 1: Write the log file**

Create `projects/video-production/render-qa/snag-log.md` with exactly this content:

```markdown
# Snag log — render-session retros + gauntlet retirement ledger

The self-improvement loop for SCLA video production. Every render session appends
a retro here; `/produce-video` reads it at preflight to avoid known snags; each
recurring snag is tracked toward a structural fix that can retire a gauntlet lane.
Design: `snag-loop-design.md`. Sibling to `BUILD-LOG.md`.

**How to use it**
- On every render session, append a `## <date> · <stem>` block under *Session
  entries*. Tag each snag `[env] [tooling] [authoring] [upstream] [defect]`, give
  its resolution + rough time cost, and add a `Caught-by:` line for any gauntlet
  lane that FAILed (with the lane's `defect-class`).
- Promote any snag that recurs into the *Retirement ledger*. For a class with a
  structural fix in place, keep a per-template clean-render tally (9 cells). A
  recurrence resets that template's cell to 0.
- A lane is retirement-eligible only when its defect class shows **≥5 clean
  renders on every one of the 9 templates** since its fix landed. Nominate here;
  the human records the actual retirement in `decisions/log.md`.

Templates (tally order): title · chips · statement · quote · points · steps ·
compare · career-map · numeral.

---

## Session entries

## 2026-07-12 · career-building_early-career-boost (seed)
Caught-by: —
- [env] `npx hyperframes tts` resolved the wrong Python; `kokoro_onnx` was missing
  on that interpreter → set `HYPERFRAMES_PYTHON` to the env that has it. ~15 min.
  (findPython() respects `HYPERFRAMES_PYTHON`.)

_First real entry seeds the format; extend it, don't rewrite it._

---

## Retirement ledger

| Snag class | Occurrences | Structural fix | Retires | Per-template clean tally (9) | Status |
| --- | --- | --- | --- | --- | --- |
| TTS wrong python path | 1 | pin `HYPERFRAMES_PYTHON` in produce-video preflight | — (env, not a lane) | n/a | open |

_No lane is retirement-eligible yet. Add a row the first time a `[defect]` snag
recurs; start its per-template tally once a structural fix is in place._
```

- [ ] **Step 2: Verify both sections and the ledger header exist**

Run: `grep -c "^## Session entries$\|^## Retirement ledger$\|Per-template clean tally" projects/video-production/render-qa/snag-log.md`
Expected: `3`

- [ ] **Step 3: Commit**

```bash
git add projects/video-production/render-qa/snag-log.md
git commit -m "project: add snag-log for render-retro self-improvement loop"
```

---

### Task 2: Add the retro PostToolUse hook

**Files:**
- Modify: `.claude/settings.json` (add one object to the `PostToolUse` array, after the existing gauntlet-hook object)

**Interfaces:**
- Consumes: the render-command regex (Global Constraints).
- Produces: a hook that, on a render command, prints a JSON object with `hookSpecificOutput.additionalContext` containing the string `SNAG RETRO`; silent otherwise or when `VIDEO_SNAG_RETRO_HOOK_DISABLED=1`.

- [ ] **Step 1: Write the failing test**

Create `projects/video-production/render-qa/tests/test_retro_hook.sh`:

```bash
#!/usr/bin/env bash
# Extracts the SNAG RETRO hook command from settings.json and checks its behavior.
set -u
SETTINGS=".claude/settings.json"
HOOK=$(jq -r '.hooks.PostToolUse[].hooks[].command' "$SETTINGS" | grep 'SNAG RETRO' | head -1)
if [ -z "$HOOK" ]; then echo "FAIL: no SNAG RETRO hook found"; exit 1; fi

pass=0
# 1. render command → emits SNAG RETRO
out=$(printf '%s' '{"tool_input":{"command":"npm run render"}}' | bash -c "$HOOK")
printf '%s' "$out" | grep -q "SNAG RETRO" && { echo "ok: render fires"; pass=$((pass+1)); } || echo "FAIL: render did not fire"
# 2. npx hyperframes render → fires
out=$(printf '%s' '{"tool_input":{"command":"npx hyperframes render"}}' | bash -c "$HOOK")
printf '%s' "$out" | grep -q "SNAG RETRO" && { echo "ok: npx render fires"; pass=$((pass+1)); } || echo "FAIL: npx render did not fire"
# 3. word "render" in unrelated command → silent
out=$(printf '%s' '{"tool_input":{"command":"git commit -m \"render fix\""}}' | bash -c "$HOOK")
printf '%s' "$out" | grep -q "SNAG RETRO" && echo "FAIL: false positive on word render" || { echo "ok: no false positive"; pass=$((pass+1)); }
# 4. disabled → silent even on render command
out=$(printf '%s' '{"tool_input":{"command":"npm run render"}}' | VIDEO_SNAG_RETRO_HOOK_DISABLED=1 bash -c "$HOOK")
printf '%s' "$out" | grep -q "SNAG RETRO" && echo "FAIL: fired while disabled" || { echo "ok: silent when disabled"; pass=$((pass+1)); }

echo "PASS $pass/4"
[ "$pass" -eq 4 ]
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `bash projects/video-production/render-qa/tests/test_retro_hook.sh; echo "exit=$?"`
Expected: `FAIL: no SNAG RETRO hook found` and `exit=1` (hook not added yet).

- [ ] **Step 3: Add the hook to settings.json**

In `.claude/settings.json`, the `PostToolUse` array currently ends with the gauntlet-hook object followed by the array close. Replace this exact text:

```json
          }
        ]
      }
    ],
    "Stop": [
```

with:

```json
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "if [ \"${VIDEO_SNAG_RETRO_HOOK_DISABLED:-0}\" = \"1\" ]; then exit 0; fi; c=$(jq -r \".tool_input.command // \\\"\\\"\"); if printf \"%s\" \"$c\" | grep -Eq \"(^|[;&|]) *([A-Z_]+=[^ ]* )*(npm run render|npx (--yes )?hyperframes(@[^ ]*)?( lambda)? render)\"; then printf '%s' '{\"hookSpecificOutput\": {\"hookEventName\": \"PostToolUse\", \"additionalContext\": \"SNAG RETRO (automated hook): a HyperFrames render ran this session. Before you end the session \\u2014 after QA \\u2014 append a retro entry to projects/video-production/render-qa/snag-log.md: every snag this session hit, each tagged [env]/[tooling]/[authoring]/[upstream]/[defect] with its resolution and rough time cost, plus a Caught-by: line naming any gauntlet lane that FAILed and its defect-class. Then update the retirement ledger for any snag class that recurs (per-template clean tally; a lane is retirement-eligible only after its fix holds 5 clean renders on every template).\"}}'; fi",
            "timeout": 10,
            "statusMessage": "Render detected → write snag-log retro before session end (set VIDEO_SNAG_RETRO_HOOK_DISABLED=1 to silence)"
          }
        ]
      }
    ],
    "Stop": [
```

- [ ] **Step 4: Validate JSON, then run the test to verify it passes**

Run: `jq . .claude/settings.json >/dev/null && echo "json ok"`
Expected: `json ok`

Run: `bash projects/video-production/render-qa/tests/test_retro_hook.sh; echo "exit=$?"`
Expected: `PASS 4/4` and `exit=0`

- [ ] **Step 5: Commit**

```bash
git add .claude/settings.json projects/video-production/render-qa/tests/test_retro_hook.sh
git commit -m "ops: add on-by-default snag-retro PostToolUse hook on render"
```

---

### Task 3: Wire the log into produce-video (read-back + retro-write)

**Files:**
- Modify: `.claude/skills/produce-video/SKILL.md` (Step 0 preflight; Closing out)

**Interfaces:**
- Consumes: `render-qa/snag-log.md` sections from Task 1.

- [ ] **Step 1: Add the read-back to Step 0 (Preflight)**

In `.claude/skills/produce-video/SKILL.md`, replace this exact line:

```
Then announce the plan: which video(s), and that you'll pause at the two gates.
```

with:

```
Then read `projects/video-production/render-qa/snag-log.md` — scan the open
retirement-ledger rows and the last few session entries and surface the known
snags relevant to this build, so you avoid re-hitting them this run (this is the
active-input half of the self-improvement loop).

Then announce the plan: which video(s), and that you'll pause at the two gates.
```

- [ ] **Step 2: Add the retro-write step to "Closing out"**

In the same file, replace this exact paragraph:

```
Report per video: stem, style package, gate outcomes, and the Wistia URL (or that
upload is pending). Drafted/approved scripts get committed to `main` per the repo's
PR flow. If a HyperFrames bug bit this run and isn't already filed, write it up and
file it upstream before ending (heygen-com/hyperframes#2064 is the model: minimal
repro, versions probed, workaround stated).
```

with:

```
Report per video: stem, style package, gate outcomes, and the Wistia URL (or that
upload is pending). Drafted/approved scripts get committed to `main` per the repo's
PR flow. If a HyperFrames bug bit this run and isn't already filed, write it up and
file it upstream before ending (heygen-com/hyperframes#2064 is the model: minimal
repro, versions probed, workaround stated).

**Snag retro (self-improvement loop) — do this before ending.** Append this
session's retro to `projects/video-production/render-qa/snag-log.md`: every snag
the run hit, each tagged `[env]/[tooling]/[authoring]/[upstream]/[defect]` with
its resolution and rough time cost, plus a `Caught-by:` line for any gauntlet
lane that FAILed (carry its `defect-class`). Then update the retirement ledger —
increment the per-template clean-render tally for any open-with-fix snag class
this render did not re-trip, and reset to zero any class that recurred. A lane
becomes retirement-eligible only once its fix holds 5 clean renders on every one
of the 9 templates; nominate it in the ledger, but the actual retirement is a
human call logged in `decisions/log.md`. The upstream bug-filing above is the
follow-through for the `[upstream]` tag. The render hook reminds you of this
step, but it's owned here — do it even if the hook is silenced.
```

- [ ] **Step 3: Verify both edits landed**

Run: `grep -c "active-input half\|Snag retro (self-improvement loop)" .claude/skills/produce-video/SKILL.md`
Expected: `2`

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/produce-video/SKILL.md
git commit -m "skill: produce-video reads snag-log at preflight, writes retro at close"
```

---

### Task 4: Structured defect-class returns from the four QA lanes + orchestrator routing

**Files:**
- Modify: `.claude/agents/qa-timing.md`, `.claude/agents/qa-layout.md`, `.claude/agents/qa-presence.md`, `.claude/agents/qa-facts.md` (report-format table + a defect-class definition)
- Modify: `.claude/skills/adversarial-qa/SKILL.md` (orchestrator folds FAILs into the log)

**Interfaces:**
- Produces: each lane's findings table gains a `defect-class` column (2nd column) holding a short, stable kebab-case slug; the orchestrator records FAIL findings into `snag-log.md`.

- [ ] **Step 1: qa-timing — add the column and definition**

In `.claude/agents/qa-timing.md`, replace:

```
| severity | scene / t | finding | evidence |
```

with:

```
| severity | defect-class | scene / t | finding | evidence |
```

Then replace:

```
severity: BLOCKER (violates a hard rule) or NOTE (drift within tolerance worth
a look). Any BLOCKER ⇒ VERDICT: FAIL. Cite evidence as a file path or a
transcript quote with timestamps — a finding without evidence is not a finding.
```

with:

```
severity: BLOCKER (violates a hard rule) or NOTE (drift within tolerance worth
a look). Any BLOCKER ⇒ VERDICT: FAIL. Cite evidence as a file path or a
transcript quote with timestamps — a finding without evidence is not a finding.
defect-class: a short, stable kebab-case slug naming the failure class (e.g.
`dup-word-anchor`, `uncued-reveal`, `boundary-mid-word`). Reuse the same slug
across renders for the same class — the snag-log retirement ledger tallies
occurrences by it.
```

- [ ] **Step 2: qa-layout — add the column and definition**

In `.claude/agents/qa-layout.md`, replace:

```
| severity | scene / t | finding | evidence |
```

with:

```
| severity | defect-class | scene / t | finding | evidence |
```

Then replace:

```
severity: BLOCKER (clipped/unreadable/off-brand) or NOTE. Any BLOCKER ⇒
VERDICT: FAIL. Evidence = the frame file path.
```

with:

```
severity: BLOCKER (clipped/unreadable/off-brand) or NOTE. Any BLOCKER ⇒
VERDICT: FAIL. Evidence = the frame file path.
defect-class: a short, stable kebab-case slug naming the failure class (e.g.
`card-overflow`, `token-drift`, `label-collision`). Reuse the same slug across
renders for the same class — the snag-log retirement ledger tallies occurrences
by it.
```

- [ ] **Step 3: qa-presence — add the column and definition**

In `.claude/agents/qa-presence.md`, replace:

```
| severity | t / range | finding | evidence |
```

with:

```
| severity | defect-class | t / range | finding | evidence |
```

Then replace:

```
severity: BLOCKER (bare/default/dead frame, coverage hole, clipped audio) or
NOTE. Any BLOCKER ⇒ VERDICT: FAIL. Evidence = frame path or slot attributes.
```

with:

```
severity: BLOCKER (bare/default/dead frame, coverage hole, clipped audio) or
NOTE. Any BLOCKER ⇒ VERDICT: FAIL. Evidence = frame path or slot attributes.
defect-class: a short, stable kebab-case slug naming the failure class (e.g.
`blank-flash`, `dead-hold`, `template-default-frame`). Reuse the same slug
across renders for the same class — the snag-log retirement ledger tallies
occurrences by it.
```

- [ ] **Step 4: qa-facts — add the column and definition**

In `.claude/agents/qa-facts.md`, replace:

```
| severity | claim | finding | source evidence |
```

with:

```
| severity | defect-class | claim | finding | source evidence |
```

Then replace:

```
severity: BLOCKER (unsupported/contradicted claim, missing source) or NOTE.
Any BLOCKER ⇒ VERDICT: FAIL. Evidence = quoted source line (or "NO SOURCE").
```

with:

```
severity: BLOCKER (unsupported/contradicted claim, missing source) or NOTE.
Any BLOCKER ⇒ VERDICT: FAIL. Evidence = quoted source line (or "NO SOURCE").
defect-class: a short, stable kebab-case slug naming the failure class (e.g.
`fabricated-claim`, `unfiled-source`, `drifted-quote`). Reuse the same slug
across renders for the same class — the snag-log retirement ledger tallies
occurrences by it.
```

- [ ] **Step 5: adversarial-qa SKILL — fold FAILs into the log**

In `.claude/skills/adversarial-qa/SKILL.md`, replace:

```
4. Collect the verdicts. Every lane replies with `VERDICT: PASS|FAIL` plus a
   findings table (severity, scene/timestamp, description, evidence path).
5. Apply the release rule. On FAIL: fix, re-render, GOTO 1. On all-PASS: hand
   the lane reports to the human at the QA gate as supporting evidence.
```

with:

```
4. Collect the verdicts. Every lane replies with `VERDICT: PASS|FAIL` plus a
   findings table (severity, defect-class, scene/timestamp, description, evidence
   path). The `defect-class` slug is what the snag-log retirement ledger tallies.
5. Apply the release rule. On FAIL: fix, re-render, GOTO 1. On all-PASS: hand
   the lane reports to the human at the QA gate as supporting evidence.
6. Record the outcome in `projects/video-production/render-qa/snag-log.md`. On any
   FAIL, add each blocking finding to this session's entry as a `[defect]` line
   with a `Caught-by: <lane> (<defect-class>)` note, and update the retirement
   ledger (increment/reset the per-template tally per the log's own instructions).
   This is what makes gauntlet retirement evidence-driven — see `snag-loop-design.md`.
```

- [ ] **Step 6: Verify all five edits landed**

Run: `grep -l "defect-class" .claude/agents/qa-timing.md .claude/agents/qa-layout.md .claude/agents/qa-presence.md .claude/agents/qa-facts.md .claude/skills/adversarial-qa/SKILL.md | wc -l`
Expected: `5`

- [ ] **Step 7: Commit**

```bash
git add .claude/agents/qa-timing.md .claude/agents/qa-layout.md .claude/agents/qa-presence.md .claude/agents/qa-facts.md .claude/skills/adversarial-qa/SKILL.md
git commit -m "skill: QA lanes return defect-class; orchestrator folds FAILs into snag-log"
```

---

### Task 5: Log the structural change + commit the design/plan docs

**Files:**
- Modify: `decisions/log.md` (append-only)
- Add: `projects/video-production/render-qa/snag-loop-design.md`, `snag-loop-plan.md` (this file) to git

**Interfaces:**
- Consumes: nothing. Terminal task.

- [ ] **Step 1: Read the tail of the decisions log to match its format**

Run: `tail -30 decisions/log.md`
Expected: see the existing entry format (date heading + bullets) to mirror it.

- [ ] **Step 2: Append the decision entry**

Append to `decisions/log.md` an entry dated `2026-07-12` recording: the render-retro
self-improvement loop was added (`render-qa/snag-log.md` + on-by-default
`VIDEO_SNAG_RETRO_HOOK_DISABLED` PostToolUse hook + produce-video read-back/retro +
QA-lane `defect-class` returns); rationale = turn per-session friction into durable
cross-session knowledge and retire the adversarial-QA gauntlet lane by lane on
evidence; retirement rule = human-gated, requires a structural fix holding ≥5 clean
renders per template across all 9 templates; design/plan in
`projects/video-production/render-qa/snag-loop-{design,plan}.md`. Match the exact
heading/bullet style observed in Step 1.

- [ ] **Step 3: Verify the entry landed**

Run: `grep -c "render-retro self-improvement loop\|snag-log" decisions/log.md`
Expected: `≥1`

- [ ] **Step 4: Commit**

```bash
git add decisions/log.md projects/video-production/render-qa/snag-loop-design.md projects/video-production/render-qa/snag-loop-plan.md
git commit -m "docs: log render-retro self-improvement loop; add design + plan"
```

---

## Self-Review

**1. Spec coverage:**
- Piece 1 (artifact + ledger + per-template tally) → Task 1. ✓
- Piece 2 (on-by-default render hook, verbatim regex, env toggle) → Task 2. ✓
- Piece 3 (preflight read-back + closing retro-write) → Task 3. ✓
- Piece 4 (structured lane returns + Caught-by + orchestrator folding) → Task 4. ✓
- Retirement rule (5 clean/template, human-gated, decisions/log.md) → encoded in Task 1 log text, Task 3 closing step, Task 5 decision entry. ✓
- Governance (render-qa/ location, decisions log entry) → Task 5. ✓

**2. Placeholder scan:** No TBD/TODO/"handle edge cases". Task 5 Step 2 describes prose to append (a log entry) rather than fixed code — acceptable, as its content depends on the log's live format read in Step 1; the required facts are fully enumerated.

**3. Type/name consistency:** `defect-class` column name, `Caught-by:` field, five snag tags, `VIDEO_SNAG_RETRO_HOOK_DISABLED`, and the 9-template tally order are used identically across Tasks 1–5. The render regex is quoted once (Global Constraints) and reused by reference in Task 2. ✓
