# BUILD-KIT — read this, then design-contract.md, then your script. Nothing else.

Generated per run by `scripts/batch-prepare.sh`. Never edit by hand; never
commit. If this contradicts `design-contract.md` or the render-lessons SKILL, THEY WIN —
report the contradiction rather than following this file.

## Your job

Turn ONE refined script into a gate-clean HyperFrames workspace. You do not
render. You do not publish. You stop when compile, preflight and check are all
green, and you report five fields.

## Start from the scaffold — do NOT run `hyperframes init`

The workspace is named `<title>_<program>` — the script's name with any date
suffix stripped. No date. `render-qa/src/stem.py` owns that; never hand-slice a
suffix. (Dates live on the delivered MP4 only.)

**`mkdir` IS the lock.** Other builds may be running right now against this same
folder. `mkdir` either creates the directory or fails because someone else got
there first — that is atomic, and it is the only thing standing between you and
two agents building the same lesson on top of each other. Never `mkdir -p`, and
never test-then-create: the gap between the test and the create is the bug.

```bash
cd projects/video-production/renders-hyperframes
WS="$(python3 ../render-qa/src/stem.py base <script-stem>)"   # -> title_program
mkdir "$WS" || { echo "workspace $WS already claimed — STOP, report, do not build"; exit 1; }
cp -a _run/scaffold/. "$WS"/     # note the /. — copies CONTENTS into the dir you just claimed
cd "$WS"
```

The trailing `/.` is load-bearing: `cp -a _run/scaffold "$WS"` would nest the
scaffold *inside* your workspace and every gate would then read stale files.

If `mkdir` fails, STOP and report it. Do not delete the other directory, do not
pick a different name, do not build into it.

The scaffold already has `compositions/`, `assets/`, `design-contract.md`, `tokens.yml` and the pinned
toolchain. You never touch its `index.html` — you author `scenes.json` and
`render-qa/src/build_index.py` compiles the markup (boilerplate, progress rail,
`<audio>` host, template clones included).

## What to read, in order

1. **This file.**
2. **`design-contract.md`** (in your workspace) — the design contract, and it is
   normative. Mandatory sections: *the animacy rules*, *the pacing rules*,
   *illustration over text*, *type rules*, *scene templates*, *style packages*
   for your assigned theme, and *host-root progress rail*.
3. **Your refined script.** Verbatim source for every scene's narration.

Do not read other builds' `index.html`, the demo reel, or other skills.

     these two markers verbatim into _run/BUILD-KIT.md for cold build
     subagents. Keep ONLY builder-facing content here: no orchestrator
     phases, no ship/publish steps, and never any quotable example copy
     (a builder once pasted a cautionary example's heading into a video). -->

**Author `scenes.json` FIRST — never `index.html`.** The plan is the only
thing you write; `render-qa/src/build_index.py` compiles it into `index.html`
deterministically (host boilerplate, progress rail, `<audio>` host, per-slot
template clones and instance repointing are all compiler-owned — the generated
file's banner comment says so). One scene entry per beat: `template` (a
design-system composition), `narration` (its verbatim span of the refined
script), every slot filled or explicitly `""`, cue **anchor phrases** never
numbers. Learn the shape from any newer dated build's `scenes.json`, or
regenerate one from an existing build with `build_index.py --extract <ws>`.
**Never pattern-match the demo reel or the init-generated workspace
`CLAUDE.md`** — both are legacy. Follow `design-contract.md`'s animacy + illustration
rules when choosing templates and copy. Standing landmines:

- **Vary the form, or the gate fails you** (`design-contract.md` → "Variety contract";
  gate: `render-qa/src/check_variety.py`). The hard rules: **never a one-item
  list** (a list slot with exactly one entry draws the bullet/pill illustration
  around a single fact — give it ≥2 items or use a form that states one idea);
  **max 2 consecutive** scenes on one template family; **≥5 distinct content
  forms** for a lesson ≥90s; **no single form above 40%** of content scenes;
  **artwork on most scenes** (≥60% coverage, ≥5 distinct assets, none reused
  more than twice, never 3 bare scenes in a row); **no long single-canvas
  block** (cap on consecutive scenes/seconds on one background). Plan the whole
  scene list against these BEFORE filling copy — variety is a property of the
  plan, not of any one scene.
  Before you settle the scene list, read the template table and deliberately
  spend the less-used forms — `scla-career-map`, `scla-steps`, `scla-morph`,
  `scla-loop`, `scla-quote`, `scla-stat` exist and go untouched build after
  build. When the narration names a thing ("a tool like a career map becomes
  helpful", "First… Second… Third…"), the template that depicts that thing is
  the one to use. Rotate the connective device too: an arrow drawn between two
  statements, a comparison scale, a split frame — not a fourth pill row.
- **Headings are Title Case, no terminal period** (gate:
  `render-qa/src/check_copy.py`). Body copy stays sentence case.
- **`index.html` is a build artifact — never hand-edit it.** Every fix goes in
  `scenes.json` (or the bespoke composition file under `compositions/`, for a
  bespoke scene) and gets recompiled. The authoring loop is seconds, not
  minutes: edit `scenes.json` → `build_index.py .` → `preflight.py . --static`
  — the same checkers the hard gate runs, before any TTS or render exists. The
  guard hook fires that same suite on every `scenes.json` write.
- **Never type a timing number.** Each scene's `narration` is its verbatim
  span of the refined script (split only at sentence ends); reveals are cue
  **anchor phrases** in the plan; the compiler owns every number
  (`data-start`/`data-duration`/cue seconds are placeholders until
  `compile_timeline.py --apply`). `data-anchor-end` is legacy-only — never
  author it.
- Whisper emits em-dash compounds as ONE token (`buzzwords—just`): a CUE
  phrase can't start or end *inside* one — quote the compound verbatim from
  the transcript or pick a phrase that clears it.
- Idle pulses: translate-only (the y-nudge pattern). Animating `scale` + SVG
  `opacity` together ghosts in the streaming encode.
- Never qualify a bespoke sub-comp root by its own class/attribute (e.g. a
  `#root.navy` selector): it renders unstyled under composition scoping even
  though it passes every static check. Style bespoke roots with a plain
  `#root` block or a child wrapper. (Promoted 2026-07-14; landed 2026-07-15.)

**Synthesize per scene, then compile + gates** (from the workspace — loop
until all green). `synth_narration.py` verifies data-narration against the
refined script BEFORE any TTS, synthesizes one clip per scene (cached —
edits only re-synthesize changed scenes), and concatenates with REAL boundary
silence; never hand-run single-take `hyperframes tts` for a lesson (the
old insert-silence flow spliced words — decisions/log.md 2026-07-14). Default
provider is **HeyGen starfish** (2026-07-22 — needs a live `HEYGEN_API_KEY`,
which **only `scripts/with-secrets.sh` supplies**; the ambient shell
`HEYGEN_API_KEY` is stale and fails, so never call `synth_narration.py` bare) —
it returns native word
timestamps with the synthesis, so the Whisper transcribe step is **skipped**:

```bash
python3 ../../render-qa/src/build_index.py .               # scenes.json -> index.html; compiler-owned, never hand-edited
python3 ../../render-qa/src/preflight.py . --static        # plan-stage gates (variety, copy, slots, text, stem) — exit 0 BEFORE any TTS is spent
../../../../scripts/with-secrets.sh python3 ../../render-qa/src/synth_narration.py .   # per-scene HeyGen TTS -> narration.wav + scene-times.json + narration.words.json
python3 ../../render-qa/src/compile_timeline.py . --apply  # owns ALL numbers (boundaries + cues from the manifest + HeyGen words)
python3 ../../render-qa/src/preflight.py .                 # full gate incl. script-vs-transcript diff — exit 0 or fix
npm run check                                          # lint + validate + inspect
```

The first two commands are the cheap loop — iterate on `scenes.json` until
`--static` exits 0 (a variety or copy failure discovered here costs seconds; the
same failure after TTS costs a re-synth, and after a render costs 7 minutes).
Only then spend TTS.

**There is no fallback voice.** The narration voice is pinned
(`.claude/rules/video-production.md`) and kokoro is not provisioned here. If
HeyGen fails: STOP, capture the exact command + full error output, and report
— never switch providers, never `pip install` a TTS, never work around a
credential failure (a 2026-07-28 builder did all three; the actual fault was a
broken flag in `with-secrets.sh`, which only the orchestrator could see).

Edited a scene's narration or reordered scenes? Re-run the same four commands
in order — synth re-does only the changed clips, and a stale transcript fails
loudly instead of misaligning.

An unresolvable anchor error names the scene and transcript window — fix the
phrase, never the numbers. **Stop here. No render in this phase.**

## RULES THAT NO OTHER DOC WILL TEACH YOU

Discovered by real pilot builds that passed every static check and still
produced broken videos. None are optional.

### 1. The build loop — plan first, TTS only when the plan is clean

If two scenes point at the same `compositions/<name>.html`, **every scene that
shares a template renders completely blank** — background and footer only, no
heading, no content. On one pilot that was 18 of 21 scenes. `build_index.py`
clones shared templates into per-scene files itself — which is one more reason
`index.html` is never hand-authored: a hand-written file skips the cloning.

```bash
python3 ../../render-qa/src/build_index.py .                 # scenes.json -> index.html (+ per-scene template clones)
python3 ../../render-qa/src/preflight.py . --static          # plan gates: variety, copy, slots, text, stem — seconds per loop
# iterate on scenes.json until --static exits 0, ONLY THEN spend TTS:
../../../../scripts/with-secrets.sh python3 ../../render-qa/src/synth_narration.py .
python3 ../../render-qa/src/compile_timeline.py . --apply
python3 ../../render-qa/src/preflight.py .
npm run check
```

Re-run `build_index.py` after ANY `scenes.json` edit — the compiled
`index.html` and its clones are artifacts, never edited directly.

### 2. Every slot is authored copy or an explicit "" — nothing in between

Each template declares its variables in a JSON schema block at the top of
`compositions/<name>.html`. Slot defaults are `[[slot-name]]` placeholders: a
slot you leave out of a scene's variables in `scenes.json` renders its
placeholder ON SCREEN, and `preflight.py` (`check_slots.py`) fails the build for it — as it
also fails any slot whose value still IS placeholder text (`[[...]]`, `...`,
`TODO`).

Before authoring a scene, read the schema block at the top of its template
(the first ~15 lines — not the whole file) and enumerate its slots. Every
content slot gets either copy authored from YOUR SCRIPT, or `""` to hide it.
`sceneDuration`, every `*Cues` slot, and the title card's `meta` are
compiler-owned: pre-declare them (empty or placeholder value) and never type
their content yourself.

### 3. On-screen copy must trace to the narration

Headings, labels and points may compress or excerpt the scene's own narration
— they must never introduce facts, counts, or sequence claims the narration
does not say ("two more ways", "step 3 of 5", a stat). When unsure, use the
narration's own words. Never reuse wording from THIS document or from any
template's schema block: those are instructions to you, not lesson content.

### 4. No dead air — an event at least every ~3 seconds

After a scene's entrance settles (~1.2s), something visible must keep
happening on what the narration is saying: the next cued item, a `subBeats`
live line, an illustration beat. `preflight.py` FAILS any event gap over 4.0s
and warns over 3.0s. If the narration for a scene has a long span with
nothing to cue, split the scene at a sentence end or add `subBeats` — never
stretch a heading over silence.

### 5. Title card and outro are DERIVED — never invent them

`eyebrow` = the program display name from tokens.yml's `programs:` map ("Title card & outro
sources" table. `title` = the stem's title segment, hyphens to spaces,
sentence case — never the opening narration sentence, never a paraphrase.
`preflight.py` fails both. Outro: `next` may quote the closing narration;
`cta` is a short imperative pulled from it; they must not restate each other.

### 6. Headings stand alone — never a fragment completed by chips or points

A heading must read as a complete phrase by itself ("Where people look for the
answer"), never a sentence fragment that later chips finish ("The right" +
chips "The right job / The right major" — a real pilot defect that read as
truncated text on screen). Same for morph/step card titles. If a card or
scene would show a title plus a large empty area at its midpoint, give it a
sub-line or tighten the scene.

### 7. Enumerated set spread across the lesson -> `scla-condition`, NOT `scla-steps`

`scla-steps` renders nodes `1..N` where N = the count of non-empty step slots,
and activates them in sequence **within one scene**. It has no notion of "this
scene is step 3 of 4." So if you give one steps scene a single step, it renders
a lone node numbered "1" on an empty four-node rail — even when the scene is
labelled STEP TWO. The pilot did this four times.

Choose by how the narration delivers the set:

- **All items spoken together, one passage** -> ONE `scla-steps` scene with
  every step slot filled and one `stepCues` entry per step.
- **Items introduced one at a time, separated by other scenes** ->
  `scla-condition` per item (number badge + "N of M" progress dots), which is
  exactly what design-contract.md prescribes: *"Split an enumerated set into one of these
  per item, not a timed 5-row list."*

Same rule for `scla-loop` (it shares the steps contract).

## Report exactly these five fields, no prose

```
workspace: <path>
scenes:    <n>
theme:     <summit|horizon|cadence>
gates:     static=<exit> synth=<exit> compile=<exit> preflight=<exit> check=<exit>
status:    <one line>
```

## Hard rules

- **Never type a timing number.** The compiler owns every number.
- **Never fabricate SCLA content.** Work only from the refined script.
- **No FERPA/PII** in any prompt sent to an AI tool.
- Never call `synth_narration.py` bare — only via `scripts/with-secrets.sh`
  (the ambient `HEYGEN_API_KEY` is stale and returns 403).
- Do **not** run `npm run render`. The orchestrator ships.
