# The SCLA lesson-video pipeline — owner's manual

*Written 2026-07-28, the day the plan-first rewire landed. This file explains
the system; it does not govern it. The governing artifacts are the skills
(`.claude/skills/render-lessons`, `refine-scripts`, `produce-video`), the rules
(`.claude/rules/video-production.md`), and the checkers under `render-qa/` —
if this manual ever disagrees with them, they win and this file needs a fix.*

---

## 1. The idea in one paragraph

Agent judgment is confined to exactly two artifacts: the **refined script**
(what is said) and the **`scenes.json` plan** (what is shown — beats, template
per beat, on-frame copy, cue anchor phrases, icons). Everything else is
compiled or gated by machines: a compiler emits the HTML, a compiler owns every
timing number, checkers enforce your standing preferences at the moment the
plan is written, snapshots are vision-reviewed *before* a render is spent, and
a verifier hashes what actually rendered before anything is published. You
stand at **one gate**: previewing a batch's pilot. Everything downstream of
your approval is exit codes.

## 2. The whole flow

```
                        THE MACHINE                                   YOU
  ┌─────────────────────────────────────────────────────┐   ┌──────────────────┐
  │                                                     │   │                  │
  │  raw script (.txt)                                  │   │  drop scripts at │
  │  lesson-scripts/<program>/            ◄─────────────┼───┤  program root;   │
  │        │                                            │   │  edit any time   │
  │        ▼  /refine-scripts  (qa-facts pass — no      │   │                  │
  │        │                    fabrication survives)   │   │                  │
  │  refined script                                     │   │  open review     │
  │  lesson-scripts/<program>/refined/    ◄─────────────┼───┤  buffer: edit or │
  │        │                                            │   │  veto any script │
  │        ▼  /render-lessons BUILD  (cold subagent)    │   │  before build    │
  │        │                                            │   │                  │
  │   ┌────┴──────────── the authoring loop ─────────┐  │   │                  │
  │   │  agent authors scenes.json   [ONLY judgment] │  │   │                  │
  │   │      │                ▲                      │  │   │                  │
  │   │      ▼                │ fix plan (seconds)   │  │   │                  │
  │   │  build_index.py ──► index.html  [COMPILED]   │  │   │                  │
  │   │  preflight --static  [GATES: variety, copy,  │  │   │                  │
  │   │      │                slots, text, stem]     │  │   │                  │
  │   └──────┼── exit 0 ──────────────────────────────┘ │   │                  │
  │          ▼                                          │   │                  │
  │   synth_narration.py    [HeyGen TTS, cached,        │   │                  │
  │          │               silence-capped]            │   │                  │
  │   compile_timeline.py   [owns EVERY number]         │   │                  │
  │   preflight.py (full)   [+ script-vs-transcript]    │   │                  │
  │   npm run check         [lint + validate]           │   │                  │
  │          │                                          │   │                  │
  │   batch-precheck.sh     [1 snapshot per scene,      │   │                  │
  │          │               blank-scene flags,         │   │                  │
  │          │               vision review of pixels    │   │                  │
  │          │               — BEFORE the render spend] │   │                  │
  │          ▼                                          │   │                  │
  │  built workspace                                    │   │                  │
  │  renders-hyperframes/<stem>/  ══════════════════════╪═══╡ ★ PILOT GATE ★  │
  │          │                                          │   │ preview.sh, then │
  │          │  "ship <stem>" unlocks ▼                 │   │ "ship <stem>"    │
  │          ▼                                          │   │ (one approval    │
  │   batch-ship.sh: render (~7 min) ─► verify_render   │   │  covers the      │
  │          │        [duration ±0.15s, 1920×1080,      │   │  whole batch)    │
  │          │         presence check, sha-256 marker]  │   │                  │
  │          ▼        ─► encode spot-check (vision)     │   │                  │
  │   --publish: file MP4 ─► Wistia upload ─►           │   │                  │
  │   published.tsv row + ledger row ─► script moves    │   │                  │
  │   refined/ → rendered/ ─► commit ─► prune workspace │   │  Wistia URL      │
  │          │                                          │   │  reported to you │
  │          ▼                                          │   │  as confirmation │
  │   next video in the queue (fail = quarantine that   │   │                  │
  │   ONE video; the batch never stops for it)          │   │                  │
  └─────────────────────────────────────────────────────┘   └──────────────────┘
```

## 3. What you invoke, and when

| You want | You say / run |
|---|---|
| A video (or many) produced end to end | `/produce-video` — refines whatever is raw, builds, stops at the pilot gate |
| Just refine raw scripts | `/refine-scripts` — drains program-root `.txt`s into `refined/` |
| Just build from refined scripts | `/render-lessons` — BUILD is the default; a queue >1 runs AUTO-BATCH (pilot first) |
| Approve the pilot / a one-off | watch `bash scripts/preview.sh <stem>`, then reply **`ship <stem>`** |
| See what's outstanding | `bash scripts/batch-status.sh` |
| Resume an interrupted batch | `bash scripts/batch-status.sh` — then tell the agent to continue; state is on disk, no session memory needed |
| Deep-audit a suspicious cut | `/adversarial-qa` (escalation only — not part of the normal run) |
| Retire a shipped workspace to `_archive/` | your call only, `bash scripts/archive-lesson.sh <stem>` — never automated |

**Your two writing surfaces:** drop raw scripts at
`lesson-scripts/<program-slug>/` root (intake), and edit/veto anything in
`refined/` any time before it builds (the open review buffer). Nothing else in
the pipeline is hand-edited — `index.html` is a build artifact, timing numbers
are compiler-owned, and a preference you state becomes a checker, not a memo.

## 4. Your gates — exactly one, plus one standing right

- **★ PILOT GATE (blocking).** A batch builds ONE pilot, stops, and you
  preview it. `ship <stem>` authorizes the *entire batch* — every remaining
  video then runs build → precheck → render → verify → publish unattended,
  each protected by the mechanized guards. A failing pilot stops the run.
  For a single one-off video, the pilot *is* that video.
- **Standing right, not a gate:** `refined/` is yours to edit or veto at any
  moment before build. After your pilot approval there is no second look —
  that's deliberate (the per-video human eye was replaced 2026-07-28 by the
  guard chain below, `decisions/log.md`).

## 5. What protects every video when you're not looking

Any one of these failing **quarantines that video** (built, unpublished,
logged in `render-qa/quarantine.log`) and the batch moves on:

1. `preflight.py` exit 0 before render — script-vs-transcript diff, coverage,
   pacing, text floors, title card, variety, copy, stem, silence caps.
2. `batch-precheck.sh` before render — re-runs preflight itself (subagent
   claims are never trusted), snapshots every scene, flags blank scenes
   deterministically, and a vision subagent reviews the real pixels.
3. `verify_render.py` after render — stream durations vs declared ±0.15s,
   exact 1920×1080, presence/stagnation check, then writes the sha-256
   `qa/VERIFIED` marker naming the exact MP4.
4. Publish refuses to run without a fresh `VERIFIED` marker, re-hashes the
   MP4 against it, and refuses any stem already in `published.tsv` — so
   re-running is always safe, and nothing ships twice.
5. Your taste, mechanized: Title Case headings, no one-item lists, "and/or"
   before final list items, max 2 consecutive same-template scenes, ≥5 content
   forms, no form >40%, artwork coverage, canvas-monotony cap, two-region
   minimum — all calibrated against your reference video
   (`what-makes-for-a-dream-job`), and the calibration itself is pinned by
   tests: **a gate that rejects the reference is a broken gate.**

## 6. Where things live (state IS the folder — nothing narrates it)

```
lesson-scripts/<program>/*.txt        raw — waiting to be refined
lesson-scripts/<program>/refined/     refined — YOUR review buffer, BUILD's queue
lesson-scripts/<program>/refined/avatar/   HeyGen avatar queue (different pipeline)
renders-hyperframes/<stem>/           built — waiting at the pilot gate
lesson-scripts/<program>/rendered/    published (or publishing) — moved at publish
renders-mp4/<program>/hyperframes/    local MP4 staging (gitignored, pre-Wistia)
lesson-scripts/published.tsv          THE machine truth: a stem is done iff it has a row
lesson-scripts/refinement-log.md      your human-facing ledger (Wistia URLs)
render-qa/quarantine.log              videos a guard pulled out of a batch
render-qa/logs/snag-log.md                 latest entry only: session trail + your open items
```

**"What's outstanding?" = `bash scripts/batch-status.sh`.** It rebuilds the
queue in priority order from the folders + tsv + quarantine log alone, and
flags anything in `rendered/` without a published row as **STRANDED** — the
bucket that catches an interrupted run. Anything needing *your* eyes lives in
the snag log's latest **Open** list, and the session is required to ask you
about those directly at close-out — you should never have to go dig.

**Naming:** a stem is `<title>_<program>_<YYYY-MM-DD>` and the date always
means *the most recent action* (refine, build, render) — it moves at every
transition, so identity is the base without the date. `stem.py` owns this;
nothing hand-slices dates.

## 7. Capabilities and costs, plainly

- **Batch scale:** yes — invoke on a whole queue (`/produce-video` or
  `/render-lessons`). AUTO-BATCH drains program by program in priority order,
  one pilot approval total, each video published and committed before the next
  starts, so an interruption strands nothing. No batch cap.
- **Cheap failure:** a variety/copy mistake now costs a 30-line JSON edit
  caught in milliseconds — not a re-authored video (minutes), a re-synth
  (TTS credits), or a re-render (7 minutes). Gates fire on every save of
  `scenes.json` via a hook; the agent literally cannot write a bad plan
  without being told immediately.
- **TTS spend** happens once per changed scene (per-scene cache); the voice is
  pinned (Oxana) with no fallback — a credential failure stops loudly rather
  than shipping a wrong voice.
- **Render spend** is ~7 min/video, only after pixels were already reviewed.
- **Changing the system:** state a preference once and it must land as a
  checker (or be honestly labeled a Convention) — that's enforced by CI
  (`check-enforcement.py`): a doc cannot *claim* a mechanism that doesn't
  exist. Prose can't guard your pipeline; it also can't lie about guarding it.

## 8. Current state as of this writing

- Rebuilt pilot `better-decisions-come-from-better-criteria_early-career-boost_2026-07-28`
  is gate-clean (25 scenes, 7 forms, all guards green) and **waiting at the
  pilot gate**: `bash scripts/preview.sh better-decisions-come-from-better-criteria_early-career-boost_2026-07-28`
- Approval authorizes the ~29-video queue (`batch-status.sh` for the live list).
- Your open items ride the snag log's latest entry (2 mid-career scripts with
  TODOs; one superseded Wistia copy to archive; confirm the "Career
  Accelerator" eyebrow at preview).
