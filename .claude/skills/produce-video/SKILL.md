---
name: produce-video
description: SCLA's one-call illustrated-lesson pipeline — THE workflow for any SCLA lesson/program video, from raw script text, a `.txt`, or a `lesson-scripts/` stem. Drafts/refines and fact-checks the script, then after one human approval builds, renders, verifies, and files the MP4 in a single unattended run, stopping only at the final human QA gate. Always use this for SCLA lesson videos — never route them into generic hyperframes workflow skills (faceless-explainer, general-video, etc.).
---

# produce-video — the SCLA illustrated-video pipeline

**This file owns the build sequence and every command.** Design decisions live
elsewhere and are not restated here: `projects/video-production/design-system/frame.md`
is the design contract (tokens, animacy rules, anchor/timing contract, templates,
style packages, motion rotation) — read it while assembling;
`design-system/CLAUDE.md` covers only what's in that folder and the voice decision.

**Two human gates, nothing else stops the run:**
1. **SCRIPT GATE** — the human approves the narration text (Step 1).
2. **QA GATE** — the human reviews the rendered MP4 (Step 6).

Everything between the gates is machine work: build → compile → preflight →
check → render → verify. Never self-approve a gate. Never fabricate SCLA
content — draft only from provided source material; no FERPA/PII in any prompt.
No source material for a script that needs drafting → stop and say so.

## Step 0 — Preflight (~1 min)

```bash
date +%Y-%m-%d                                       # today's date for the stem
pkill -f "hyperframes[ ]preview" 2>/dev/null || true # stale previews contaminate renders
grep /dev/shm /proc/mounts                           # need >=256M for headless Chrome
```

- **Keep the bracket in the pkill pattern.** The unbracketed form matches its own
  shell and kills it (exit 144) before anything after it runs.
- `/dev/shm` under ~256M → `sudo mount -o remount,size=512M /dev/shm` (the
  devcontainer remount can fail silently; 64M hangs Chrome mid-render).
- CLI pin: `design-system/package.json` pins hyperframes **0.7.45+** — never
  older (<=0.7.44 silently renders template defaults, upstream #2064). If a
  rendered frame ever shows template-default content, fix the pin, don't hand-bake.
- If `npx hyperframes tts` fails on a missing `kokoro_onnx`, it resolved the
  wrong Python — set `HYPERFRAMES_PYTHON` to an interpreter that has it
  (`findPython()` respects it).
- Read the **Known snags** list at the top of
  `projects/video-production/render-qa/snag-log.md` and avoid re-hitting them.

Then announce the plan: which video(s), and that you'll pause at the two gates.

## Step 1 — Script → SCRIPT GATE

**Fast path:** if the request names a script tracked in
`projects/video-production/lesson-scripts/refinement-log.md`, that row decides:

- **Refined filled, Rendered empty** → pre-approved. Skip the gate, go to Step 2
  with the file as it sits; tell the user you're doing so and why.
- **Rendered filled** → already produced; flag instead of re-rendering.
- **Refined blank** → run the refinement pass below first.
- **Not in the log** → ask which case applies (draft / verbatim / refine), or
  infer it from what was handed over.

**Drafting/refining rules** (full prompt templates in `script-templates/`):
- Strip capture noise hard (`LESSON CAPTURE` headers, `[IMAGE]`/`[VIDEO]`
  markers, duplicated paragraphs, inserted stat tangents) — but **never cut a
  callback to what the viewer already built or named** (a named tool, "Module N",
  their purpose statement), and keep enumerated source lists complete.
- The `.txt` is plain spoken lines only — no cues, headings, or shot lists.
- Spoken enumerations should resolve (end on a question or closing item), so
  scenes can cut cleanly.

**Facts check (here, not per render).** Facts are a property of the script:
if you drafted or refined it, verify every claim, name, list, and framework
against the source material before showing it to the human — spawn the
`qa-facts` agent for an independent pass when the script was drafted from
source docs. A verbatim user-provided script skips this (the human owns it).
Re-renders never re-check facts.

Save as `<section>_<program-slug>_<YYYY-MM-DD>.txt` under
`lesson-scripts/<program-slug>/` (naming: `lesson-scripts/README.md`), update the
refinement-log row, then **→ SCRIPT GATE**: show the script, stop, resume on
approval. After approval, copy the approved text back over the repo `.txt` —
production renders what was approved.

## Steps 2–5 — Build (no stops)

**Workspace + narration** (voice is pinned in `frame.md` → `voice:`):

```bash
cd projects/video-production/renders-hyperframes
HYPERFRAMES_SKIP_SKILLS=1 npx hyperframes init <stem> --example=blank --non-interactive
# copy frame.md, compositions/, assets/ in from ../design-system/
cd <stem>
# init generates a CLAUDE.md routing to generic skills this repo deleted — replace it:
printf '# Build workspace. Sequence + commands: /produce-video. Design contract: ../../design-system/frame.md\n' > CLAUDE.md
npx hyperframes tts "$(cat ../../lesson-scripts/<program-slug>/<stem>.txt)" \
  --voice af_heart --speed 0.95 -o assets/voice/narration.wav
npx hyperframes transcribe assets/voice/narration.wav --model small.en
```

**Assemble `index.html`** — one scene slot per beat from the nine templates
(copy the demo-reel pattern from `../design-system/index.html`), `<audio>` at
the host root. Read `frame.md` and follow its animacy + illustration rules; the
two mechanics that most often go wrong:

- **Never type a timing number.** Set `data-anchor-end="<last spoken phrase>"`
  on every scene slot and `data-cue-anchors='{"chipCues":[…],…}'` with verbatim
  transcript phrases; placeholder numbers are fine — the compiler owns them all.
- **One style package per video** (`theme` on every scene). Use the user's pick;
  otherwise rotate summit → horizon → cadence by the program's **started-build**
  count — rule + count definition in `frame.md` → "Style packages" — and say
  which you picked.

**Compile + gate** (from the workspace):

```bash
python3 ../../render-qa/compile_timeline.py . --apply  # boundaries, cues, padding — all from the transcript
python3 ../../render-qa/preflight.py .                 # deterministic gate — exit 0 or fix
npm run check                                          # lint + validate + inspect
```

If the compiler can't resolve an anchor it names the scene and transcript
window — fix the phrase, never the numbers. Loop until all three are green,
then render. **There is no human stop here.**

## Step 6 — Render + verify → QA GATE

```bash
pkill -f "hyperframes[ ]preview" 2>/dev/null || true   # again (keep the bracket)
npm run render
python3 ../../render-qa/verify_render.py .             # container truth + presence v2 + frame dump → qa/frames/ — must exit 0
```

**Self-review before the gate:** look at the dumped frames in `qa/frames/`
(3 per scene) against the transcript — reveals land on the right words, every
frame depicts its sentence, nothing clipped or off-brand. Fix + re-render until
you'd ship it. This replaces the old four-agent gauntlet as the default check;
the deterministic gates catch timing/coverage/presence, your eyeball catches
judgment. **Escalation only:** if the human rejects a cut and the cause isn't
obvious, or they ask to "try to break it", run `/adversarial-qa`.

**→ QA GATE.** Present: the MP4 path, a few key frames, the preflight/verify
summaries, and `script-templates/qa-checklist.md` (illustrated section). Stop;
resume on sign-off.

**File it:** rename to `<section>_<program>_<render-date>` and move to
`../renders-mp4/<program-slug>/`; upload to Wistia (title = stem; the `.mp4` is
never committed); fill the refinement-log row's Rendered date + location.

## Producing several videos in one session (batch)

The refinement-log fast path makes batch runs natural: every script whose row
shows Refined-filled / Rendered-empty is pre-approved, so Steps 2-6 loop per
script with no human stop until each cut's QA gate. Run them sequentially
(renders are ~7 min each and share the toolchain); present each finished MP4 at
its own QA gate as it lands rather than holding all of them to the end. Budget:
one build costs roughly 150-300 tool calls and the session cap is 500
(`hooks/pre-tool.sh`) — for more than 2 videos, split sessions or raise the cap
via `~/.claude/budget.json` and say so in the close-out report.

## Step 7 — Close out

```bash
cd <repo-root> && bash scripts/archive-lesson.sh <stem>   # workspace → _archive (gitignored)
```

Report per video: stem, style package, gate outcomes, Wistia URL (or pending).
Commit drafted/approved scripts per the repo flow. If the run hit a snag worth
remembering, append one line to the **Known snags** list in
`render-qa/snag-log.md` (and a dated session note below it); file any new
HyperFrames bug upstream before ending (hyperframes#2064 is the model repro).
