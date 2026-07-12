# Design — render-retro self-improvement loop (snag log) · 2026-07-12

Sibling to `BUILD-LOG.md`, continuing its mission: make video creation
one-shot and error-free, and **retire the adversarial-QA gauntlet lane by lane,
on evidence.** This doc specifies the closed feedback loop that turns every
render session's friction into durable, cross-session knowledge.

## Goal

Every render session records the snags it hit. Future sessions read those snags
before building. Recurring snags are tracked toward a structural fix; when a fix
kills a defect class outright, the gauntlet check that used to catch it can be
retired — auditably, not by guess.

## The four pieces

### Piece 1 — the artifact: `render-qa/snag-log.md`

One append-only file, all programs (root causes are cross-cutting). Two sections.

**A. Session entries** — one block per render session:

```
## 2026-07-12 · career-building_early-career-boost
Caught-by: qa-layout (round 1)
- [env] kokoro TTS resolved wrong python; kokoro_onnx missing → set HYPERFRAMES_PYTHON. ~15 min.
- [tooling] scene 07 anchor unresolved (duplicate word) → re-anchored to fuller phrase.
- [upstream] career-map ghost = scale+SVG-opacity capture artifact → translate-only pulse (hyperframes#2064 class).
- [authoring] mis-sized scene 04, static >2s → split. My error.
- [defect] qa-layout FAIL round 1: career-map double-draw.
```

- Every snag tagged one of: `[env] [tooling] [authoring] [upstream] [defect]`.
- Each line carries its resolution/workaround and a rough time cost.
- `Caught-by:` names any gauntlet lane(s) that FAILed this render and which round.

**B. Retirement ledger** — the table that closes the loop:

| Snag class | Occurrences | Structural fix | Retires | Status |
|---|---|---|---|---|
| dup-word anchor unresolved | 3 | compiler picks Nth occurrence from anchor context | qa-timing dup-word check | open |
| TTS python path | 2 | pin `HYPERFRAMES_PYTHON` in preflight | — | fixed |

- A snag class recurs → promote/increment its row.
- A fix structurally kills the class → note which **gauntlet lane/check** it
  retires; set status `fixed`.
- **Retirement is human-gated.** The ledger *nominates* a lane for retirement
  once its defect class has a structural fix logged and has held with **zero
  recurrences across ≥5 clean renders per template** — i.e. every one of the
  nine scene templates must have accumulated 5 defect-class-free renders since
  the fix landed, not 5 renders total. This proves the fix holds template by
  template, not just on whatever happened to render recently. The actual
  retirement is then a deliberate call recorded in `decisions/log.md`. The
  ledger makes the nomination auditable — it never fires the retirement itself.
- **Per-template tallying.** To make the 5-per-template bar countable, the
  retirement ledger tracks a per-template clean-render count for each open snag
  class that has a fix in place (a 9-cell tally, one per template). A recurrence
  of the class resets that template's count to zero.

### Piece 2 — the hook (`.claude/settings.json`, PostToolUse on Bash)

Modeled exactly on the existing render-gate hook (the `Bash` matcher already in
`PostToolUse`). Matches the render command (`npm run render` /
`npx hyperframes … render`) and injects `additionalContext`:

> "A HyperFrames render ran this session. Before you end the session — after QA —
> append a SNAG RETRO to `render-qa/snag-log.md`: every snag this session hit
> (env / tooling / authoring / upstream / defect), each tagged with its
> resolution and rough cost, plus a `Caught-by:` line for any gauntlet lane that
> FAILed. Then update the retirement ledger for any snag that now recurs."

- **On by default.** Unlike the gauntlet hook (which spawns four agents and is
  default-off), this is a cheap prompt and is the engine of the whole loop, so
  it should not default off. It uses the same `QA_*`-style env toggle convention
  for a manual off switch, but defaults enabled.
- It plants the obligation at render time; the agent discharges it at session
  close, when all snags — including post-render gauntlet FAILs — are known.

### Piece 3 — the read-back (`produce-video` skill)

The *active-input* half. Two skill edits:

- **Step 0 (Preflight)** gains a line: read the open retirement-ledger rows +
  the last few session entries, and surface "known snags to avoid on this run"
  before building.
- **Closing out** gains the retro-write step explicitly, so the retro happens
  even if the hook is ever disabled. The skill is the primary home; the hook is
  the backstop trigger.

### Piece 4 — QA-lane findings routing

The gauntlet's FAILs are the ledger's highest-value input: a lane's catch-rate
for its defect class is exactly the measurement that governs whether that lane
can be retired. The lanes do **not** write the log directly (parallel,
cold-context, partial-view, transient → races + no whole-session picture); their
findings flow **up** to the orchestrator, which folds them into the retro.

To make that folding mechanical rather than re-summarized:

- **`adversarial-qa/SKILL.md`** and the **four `qa-*` lane charters** gain a
  "report findings as N tagged lines (`lane · defect-class · severity ·
  one-line`)" instruction, so each lane returns a copy-through-ready shape.
- Session entries gain the **`Caught-by:`** field (see Piece 1A).

## How this retires the gauntlet

Lane by lane, on evidence, matching BUILD-LOG's philosophy ("retirement happens
checker by checker, not by fiat"). A lane retires only when its whole defect
class has a structural fix logged in the ledger and that fix has held with **≥5
clean renders per template** (all nine templates) since it landed. The log — and
its per-template tally — is what makes that call auditable.

## Resolved judgment calls

1. **Trigger = the render command** (same as the existing hook), not
   `verify_render.py` — so a session that renders but skips verify is still
   prompted.
2. **Retirement is human-gated** — ledger nominates, `decisions/log.md` records.
3. **One log for all programs** — root causes are cross-cutting.
4. **Spec + log live in `render-qa/`**, not a new `docs/` root — the repo's
   Approved Root Layout forbids new root dirs without a decisions-log entry +
   hook edit, and this is a direct continuation of the `render-qa/` build work.

## Files touched

- **New:** `projects/video-production/render-qa/snag-log.md` (the artifact,
  seeded with the ledger header + this session's known snags as entry 1).
- **Edit:** `.claude/settings.json` — add the retro PostToolUse hook.
- **Edit:** `.claude/skills/produce-video/SKILL.md` — Step 0 read-back +
  Closing-out retro-write step.
- **Edit:** `.claude/skills/adversarial-qa/SKILL.md` + `.claude/agents/qa-timing.md`,
  `qa-layout.md`, `qa-facts.md`, `qa-presence.md` — structured findings return.
- **Edit:** `decisions/log.md` — log this structural addition.
```
