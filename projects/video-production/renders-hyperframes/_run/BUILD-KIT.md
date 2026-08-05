# BUILD-KIT — read this, then your script. Nothing else.

Generated per run by `scripts/batch-prepare.sh`. Never edit by hand; never
commit. If this contradicts `.claude/rules/video-production.md` or the
render-lessons SKILL, THEY WIN — report the contradiction rather than
following this file. Where a gate and any prose disagree, the gate is right.

## Your job

Turn ONE refined script into a gate-clean HyperFrames workspace. You author
the HTML yourself — there are no templates and no compiler (the template lane
retired 2026-08-05). You do not render. You do not publish. You stop when the
gates are green, and you report five fields.

## Start from the scaffold — do NOT run `hyperframes init`

The workspace is named `<title>_<program>` — the script's name with any date
suffix stripped. No date. `render-qa/src/stem.py` owns that; never hand-slice a
suffix. (Dates live on the delivered MP4 only.)

**`build-claim.sh` starts every build — there is no other way in.** It takes
the atomic `mkdir` lock (exactly one of N concurrent subagents wins), arms the
write fence, opens the build journal, and regenerates `PIPELINE-STATUS.md`:

```bash
bash scripts/build-claim.sh <base> <program-slug>   # exits non-zero if claimed
cd projects/video-production/renders-hyperframes/<base>
cp -a ../_run/scaffold/. .     # note the /. — copies CONTENTS into the claimed dir
```

The trailing `/.` is load-bearing: without it the scaffold nests *inside* your
workspace and every gate then reads stale files.

If the claim fails, STOP and report it. Do not delete the other directory, do
not pick a different name, do not build into it.

The scaffold has `tokens.yml` (palette, type floors, pinned voice, program
display names — the gates read the workspace copy), the vendored Proxima
woff2 set and the brand SVGs under `assets/`, and the pinned toolchain.

## What to read, in order

1. **This file.**
2. **`tokens.yml`** (in your workspace) — every normative number and name.
3. **Your refined script.** Verbatim source for every beat's narration.

Do not read other builds' `index.html`, archived templates, or other skills.

     these two markers verbatim into _run/BUILD-KIT.md for cold build
     subagents. Keep ONLY builder-facing content here: no orchestrator
     phases, no ship/publish steps, and never any quotable example copy
     (a builder once pasted a cautionary example's heading into a video). -->

**The HTML is the authored artifact.** No templates, no scenes.json, no
compiler — you author `index.html` + `compositions/*.html` directly against
computed timings. Reference build (visual bar + working example of every
artifact): `projects/video-production/experiments/m1-mini-syllabus-freeform-trial/`
(the owner-approved 2026-08-05 cut) — read its `design.md`, never copy its
compositions. Build order is narration-first (a late visual fix then costs an
HTML edit, never a re-synthesis):

1. **`design.md`** — brand truth for THIS video plus the one thing no checker
   can grade: the **concept angle**, one sentence naming the single carrying
   visual idea (the reference's: "four transitions are four positions on ONE
   map, built once, never left") **and the beat range it persists across —
   this must cover ≥60% of the runtime.** ("Laid down, read twice, then hands
   off" is a rejected cut's own honest description of itself and is not a
   concept angle; see `decisions/log.md` 2026-08-04 "Owner verdict".) State the
   rule out loud and hold to it: *if an element cannot be justified as
   another way of reading the same object, it does not exist.* Palette and
   face come from `tokens.yml` / `brand/visual-identity.md`; hierarchy by
   weight/size/color, headings Title Case without terminal periods.
2. **`audio_request.json`** — the beat manifest: `lines: [{id, text}]`, the
   ready script **verbatim** (TTS normalizations only), split into
   narration beats. **Pace target: ~10 beats per minute** — a ~150s lesson is
   ~25 beats, not ~17; a beat manifest that undershoots this by a wide margin
   is what the owner rejected as "SO boring" (`decisions/log.md` 2026-08-04
   "Owner verdict"; the numbers are gated by `render-qa/src/check_pace.py`).
   This file is the gates' narration source (`preflight --static` diffs it
   against the approved script — run it now, it is free).
3. **Synthesize** via the HyperFrames audio engine (`audio.mjs` from the
   `hyperframes-media` skill), pinned voice from `tokens.yml`, through
   `scripts/with-secrets.sh` — never a bare env. Output: `audio_meta.json`
   + one wav per beat.
4. **`timing.json`** — `{total, rows:[{id, audio_start, audio_dur, vis_start,
   vis_dur}]}` COMPUTED from `audio_meta.json` durations (a script computes
   it; never hand-tune a number). The tail after the last word ≥ **1.8s**
   (`FINAL_HOLD` — the gate floor is 1.5s and the owner rejected 1.1s twice).
   **Run `python3 projects/video-production/render-qa/src/check_pace.py
   projects/video-production/renders-hyperframes/<stem> --static` here** —
   this is the step where a pace fix is still free (re-splitting
   `audio_request.json` and re-synthesizing), not after HTML is authored
   against these timings. `beat-pace` / `long-beat-share` are BLOCKING in the
   real gate (`preflight --static`); catch them here first, where the fix
   costs nothing.
5. **Author** `index.html` + `compositions/*.html` against the frozen
   timings, word-timestamp-driven reveals. The freeform contract the gates
   read: on-frame copy lives in **markup, never JS strings**; headings carry
   **`data-role="heading"`** (or are `<h1>`–`<h3>`); the program display name
   and the lesson title appear on the title card in markup; deliberate
   exceptions are declared where they live (`/* motion-allow: … */`,
   `/* brand-allow: … */`). Colors are `tokens.yml colors:` at any alpha;
   every `font-family` leads with the brand face; body text ≥ 40px.
6. **Snapshot every beat midpoint** with the pinned CLI:
   `npx hyperframes@<pin> snapshot . --at <beat midpoints from timing.json>
   --no-end -o snapshots` — this grid is not ink-only: the pixel bounds gate
   (`check_ink`) grades it, and so does `check_pace.py --stills`
   (`carrier-drift` + `twin-share`, run automatically inside the full
   `preflight.py`). Fewer stills than beats is a preflight FAIL either way.
   Review them yourself before presenting the gate.
7. **Gates:** `bash scripts/build-gate.sh <stem>` (runs `preflight.py`:
   timing contract, script-vs-beats, copy, continuity, forms, brand, text,
   title, ink, motion, pace, per-beat layout) exit 0, then `npm run check`.
   **Stop here. No render in this phase.**

Standing landmines:

- **Headings are Title Case, no terminal period** (gate:
  `render-qa/src/check_copy.py`). Body copy stays sentence case.
- **Never a one-item list, never a one-card comparison** (gate:
  `render-qa/src/check_forms.py` on element structure) — a list with one
  entry draws the bullet/pill illustration around a single fact; give it ≥2
  items or state the idea in a form that is not a list.
- **Vary the form.** The variety thresholds (max 2 consecutive scenes on one
  visual family, ≥6 distinct content forms, no form above 40%) are
  Conventions since 2026-08-05 — their checker retired with the template
  lane and the owner call on freeform variety is pending — but the taste
  they encode is unchanged: rotate the connective device (an arrow between
  two statements, a comparison scale, a split frame), not a fourth pill row.
- **Settled content never re-animates in place** (gate:
  `render-qa/src/check_motion.py`) — idle pulses are banned; deliberate
  exceptions are declared inline with `/* motion-allow: <reason> */`.
- Idle drift on decoration: translate-only (the y-nudge pattern). Animating
  `scale` + SVG `opacity` together ghosts in the streaming encode.
- Never qualify a bespoke sub-comp root by its own class/attribute (e.g. a
  `#root.navy` selector): it renders unstyled under composition scoping even
  though it passes every static check. Style bespoke roots with a plain
  `#root` block or a child wrapper. (Promoted 2026-07-14; landed 2026-07-15.)

**There is no fallback voice.** The narration voice is pinned
(`.claude/rules/video-production.md`) and kokoro is not provisioned here. If
HeyGen fails: STOP, capture the exact command + full error output, and report
— never switch providers, never `pip install` a TTS, never work around a
credential failure (a 2026-07-28 builder did all three; the actual fault was a
broken flag in `with-secrets.sh`, which only the orchestrator could see).

Edited a beat's narration or re-split the manifest? Re-synthesize (the audio
engine re-does only changed clips), recompute `timing.json`, re-snapshot, and
re-run the gates — a stale manifest fails loudly instead of misaligning.

## RULES THAT NO OTHER DOC WILL TEACH YOU

Discovered by real pilot builds that passed every static check and still
produced broken videos. None are optional.

### 1. On-screen copy must trace to the narration

Headings, labels and points may compress or excerpt the beat's own narration
— they must never introduce facts, counts, or sequence claims the narration
does not say ("two more ways", "step 3 of 5", a stat). When unsure, use the
narration's own words. Never reuse wording from THIS document: these are
instructions to you, not lesson content.

### 2. Title card is DERIVED — never invent it

The eyebrow is the program display name from tokens.yml's `programs:` map;
the title is the stem's title segment, hyphens to spaces — never the opening
narration sentence, never a paraphrase. Both must appear in on-frame MARKUP
text (chrome built in JS is invisible to every gate). `preflight.py` fails
both.

### 3. Headings stand alone — never a fragment completed by later copy

A heading must read as a complete phrase by itself ("Where people look for
the answer"), never a fragment that later items finish ("The right" + "The
right job / The right major" — a real pilot defect that read as truncated
text on screen). If a beat would show a title plus a large empty area at its
midpoint, give it a sub-line or tighten the beat.

### 4. The freeform contract the gates read

On-frame copy lives in **markup, never JS strings**; headings carry
`data-role="heading"` (or are `<h1>`–`<h3>`); declared lists that are not
`<ul>`/`<ol>` carry `data-role="list"`, comparisons `data-role="compare"`.
Deliberate exceptions are declared where they live (`/* motion-allow: … */`,
`/* brand-allow: … */`, `/* text-floor-exempt: … */`). Colors are
`tokens.yml colors:` at any alpha; every `font-family` leads with the brand
face; body text ≥ 40px.

## Report exactly these five fields, no prose

```
workspace: <path>
beats:     <n>
concept:   <the design.md concept angle, one line>
gates:     static=<exit> synth=<exit> pace=<exit> preflight=<exit> check=<exit>
status:    <one line>
```

## Hard rules

- **Never hand-tune a timing number.** timing.json is COMPUTED from
  audio_meta.json durations.
- **Never fabricate SCLA content.** Work only from the refined script.
- **No FERPA/PII** in any prompt sent to an AI tool.
- Never synthesize bare — only via `scripts/with-secrets.sh`
  (the ambient `HEYGEN_API_KEY` is stale and returns 403).
- Do **not** run `npm run render`. The orchestrator ships.
