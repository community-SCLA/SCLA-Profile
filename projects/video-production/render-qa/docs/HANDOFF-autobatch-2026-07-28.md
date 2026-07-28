# HANDOFF — AUTO-BATCH pipeline rebuild + pilot, 2026-07-28

Written for a session starting with **zero context**. Read this whole file
first; it is self-contained. Then run `bash scripts/batch-status.sh`.

---

## 1. What we are trying to achieve

Ship **30 SCLA lesson videos** from refined scripts to Wistia, in one
unattended overnight run, in priority order.

The owner's requirements, decided 2026-07-28 and not up for re-litigation:

1. **One human approval per batch, not per video.** A pilot video is previewed
   and approved; that approval authorizes the rest. The old per-video
   HYPERFRAME GATE made a 30-video queue need 30 approvals and was retired.
2. **Priority-phased, ship-as-you-go.** Order: `early-career-boost` →
   `mid-career-momentum` → `career-transitions` → `entrepreneur-accelerator`.
   Each video is fully published *before* the next starts, so an interrupted
   run never leaves rendered-but-unpublished work.
3. **After a confirmed upload:** delete the local MP4 (Wistia is the delivery
   copy), but **keep the hyperframes workspace** on disk, pruned but editable,
   so any lesson can be revised later without re-synthesizing narration.
4. **Per video: gates + a sampled snapshot vision check BEFORE rendering**, so
   a structural bug is caught in ~1 min rather than after a 7-minute render.

## 2. Current status — READ THIS BEFORE DOING ANYTHING

**The batch has NOT started. Do not start it yet.** The owner's call at the end
of the last session: *"it's clearly not ready to launch the full batch — we
will be perfecting the end and rendering on the pilot before moving on."*

The pilot is `better-decisions-come-from-better-criteria_early-career-boost_2026-07-06`.

| Thing | State |
|---|---|
| Pipeline tooling | **Done and committed** (see §4) |
| Wistia projects for all 4 programs | **Created + registered** in `config/endpoints.json` |
| Pilot workspace | Built, all gates green, 21 scenes, theme `summit` |
| Pilot MP4 | **Rendered and verified PASS** — 19 MB, 162.7s, 1920×1080, 0 presence violations |
| Pilot published to Wistia | **NO — deliberately not published.** Stopped at `AWAITING_VISION` |
| Pilot script | Already moved `refined/` → `rendered/` by the render phase |
| Remaining queue | 29 videos, none built |

The rendered MP4 is at
`renders-hyperframes/better-decisions-come-from-better-criteria_early-career-boost_2026-07-06/renders/*.mp4`.

**To finish the pilot:** review its frames, then
`bash scripts/batch-ship.sh better-decisions-come-from-better-criteria_early-career-boost_2026-07-06 early-career-boost --publish`

That single command files the MP4, uploads to Wistia, records the URL in
`refinement-log.md`, commits, deletes the local MP4, and prunes the workspace
in place. It is the *only* remaining step for the pilot.

## 3. The three bugs we hit — and why they matter for the batch

All three were found because the **owner previewed the pilot and asked whether
what he was seeing was a real glitch**. Every automated gate said the build was
fine. This is the single most important lesson in this document: *the gates
that existed could not see these.*

### Bug 1 — Shared templates render completely blank
Any scene pointing at a `compositions/<x>.html` that another scene also used
rendered **background and footer only** — no heading, no body, no content.
**18 of the pilot's 21 scenes were blank.** The only survivors were the three
scenes using a template no other scene used (`scla-title`, `scla-career-map`,
`scla-outro`).

*Cause:* `instance_templates.py` clones shared templates per scene, but it was
never in the build loop — `preflight.py` ran it only with `--check` and
reported reuse as a **warning**, not a failure.

*Fix:* the build loop is now **five** commands with the clone first. See §5.

### Bug 2 — Omitted template slots FABRICATE on-screen copy
Each template declares its variables in a JSON schema block at the top of
`compositions/<name>.html`, each with a `default`. **A slot left out of a
clip's `data-variable-values` renders that default as real on-screen copy.**

The pilot put **15 fabricated lines** on screen — including four points under a
heading reading "Two more ways pressure shows up", two of them near-duplicates,
none of which the lesson script says.

This is a **fabrication-ban violation** (`.claude/rules/video-production.md`)
and no gate could catch it: `check_text` grades text size and restatement, not
provenance.

*Fix:* new `render-qa/check_slots.py`, wired into `preflight.py` as check 8.
It fails hard and names the exact placeholder text that would have shipped.
The authoring rule: **pass `""` for every slot you do not use.** The templates
document this in their own labels (`"Point 4 (empty to hide)"`).

*Root cause worth remembering:* this was caused by our own scaffold design.
Giving builders a pre-made scaffold removed their reason to open template
files — and the "empty to hide" contract lives only in those files.

### Bug 3 — Wrong template for an enumerated set
`scla-steps` renders nodes `1..N` where N = the count of non-empty step slots,
and activates them **within one scene**. It has no notion of "this scene is
step 3 of 4". Four scenes each carrying one step therefore each rendered a lone
node labelled **"1"** on an empty four-node rail — even the scene labelled
STEP TWO.

*Fix:* converted to `scla-condition`, which `frame.md` already prescribes:
*"One item of an enumerated set the narration introduces one at a time
(condition/principle/pillar N of M): number badge + progress dots."*
Now recorded as BUILD-KIT rule 3.

### Bug 4 (process) — Subagent gate reports are not trustworthy
The pilot's build subagent reported `preflight=0` while preflight was actually
exiting **1**. Do not trust a subagent's self-reported gate exits.
`batch-precheck.sh` and `batch-ship.sh` both re-run preflight themselves and
treat only the process exit code as authoritative. When reading gate output,
**never** conclude success from a `VERDICT: PASS` line inside a sub-section —
that is one sub-check, not the overall result.

## 4. What was built this session

New scripts, all committed:

| Script | Purpose |
|---|---|
| `scripts/batch-prepare.sh` | Generates `renders-hyperframes/_run/` — `BUILD-KIT.md` (the authoring contract) + `scaffold/` (a pre-`init`'d workspace with the progress rail and `<audio>` host wired). Builds **clone the scaffold** instead of running `hyperframes init` 30 times. `_run/` is gitignored and regenerated per run, so it cannot drift. |
| `scripts/batch-precheck.sh` | Re-runs preflight authoritatively, snapshots **one frame per scene at its midpoint**, flags low-ink (likely blank) frames deterministically, and emits a sampled spread + contact sheets for a vision subagent. Run this BEFORE rendering. |
| `scripts/batch-ship.sh` | The deterministic tail in one call. Default mode: preflight → move script to `rendered/` → render → `verify_render.py` → sample frames → `AWAITING_VISION`. `--publish` mode: file MP4 → Wistia → record URL → commit → delete MP4 → prune workspace. **Fails soft** — a guard failure quarantines one video (logged to `render-qa/quarantine.log`) and the batch continues. |
| `scripts/batch-status.sh` | Reconstructs the remaining queue from folders + ledger alone. **The resume key.** |
| `render-qa/check_slots.py` | New hard gate for Bug 2. |

Modified: `archive-lesson.sh` gained `--in-place` (prune without moving to
`_archive/`, since archiving is a human-only call); `with-secrets.sh` is
REST-only (the `infisical` CLI is not installed here and its dead branch printed
a warning on every call); HyperFrames pinned to **0.7.45** everywhere.

Rules/docs updated: `.claude/rules/video-production.md` (PILOT GATE replaces the
per-video gate), `/render-lessons` SKILL (Phase AUTO-BATCH added, ≤3-per-session
cap deleted), `/produce-video`, both `CLAUDE.md`s, `frame.md`, `decisions/log.md`.

**On the ≤3-builds-per-session cap:** it was deleted because it justified itself
with a 500-tool-call budget in `hooks/pre-tool.sh` that **is not armed**
(`~/.claude/settings.json` has no hooks, no `budget.json`). It was guarding a
limit that does not exist. What actually protects the session — one cold
subagent per video — is retained.

## 5. The build loop (five commands, clone first)

Run from inside the workspace:

```bash
python3 ../../render-qa/instance_templates.py .            # clone shared templates — BUG 1
../../../../scripts/with-secrets.sh python3 ../../render-qa/synth_narration.py .
python3 ../../render-qa/compile_timeline.py . --apply      # owns ALL timing numbers
python3 ../../render-qa/preflight.py .                     # incl. check_slots — BUG 2
npm run check
```

`synth_narration.py` must **only** ever run via `scripts/with-secrets.sh` — the
ambient `HEYGEN_API_KEY` is stale and returns 403. There is **no** kokoro
fallback (`kokoro_onnx` is not installed): if HeyGen fails, stop and report.

Never type a timing number; the compiler owns them.

## 6. Environment (verified working 2026-07-28)

The TTS/egress wall recorded in 25 consecutive snag-log entries is **cleared**.
ffmpeg + ffprobe present · node v22.15.0 · `/dev/shm` raised to 2G · npm,
HeyGen, Infisical and Wistia all reachable · `INFISICAL_CLIENT_ID` and
`INFISICAL_SECRET_KEY` both set.

If `/dev/shm` is under 2G after a restart: `sudo mount -o remount,size=2G /dev/shm`.

**There has never been a Gemini API key.** Our tooling passes `--describe false`
to `hyperframes snapshot` so it never probes for one. Remaining `GEMINI_API_KEY`
mentions live only in vendored upstream HyperFrames skill packs
(`.claude/skills/hyperframes-media/`), documenting an optional Lyria BGM
fallback this pipeline does not use. Ignore them.

**Wistia:** all four programs are registered in `config/endpoints.json` and
route to their own project. The token has upload scope but **not**
project-management scope (`POST /v1/projects.json` → `unauthorized_scope`) and
**no delete scope** — so a misfiled video cannot be removed by the pipeline.
New programs need their project created in the Wistia UI by the owner.

## 7. Running the batch, once the pilot is signed off

Per video, in `batch-status.sh` order:

1. **Cold build subagent**, fast model, **paths only** — the stem, its refined
   script, `_run/BUILD-KIT.md`, and the theme (rotate `summit → horizon →
   cadence` by `count(rendered/*.txt) mod 3` per program). Tell it to clone the
   scaffold, never run `hyperframes init`, never run `npm run render`, and to
   report five fields and no prose. Escalate to a strong model only on retry.
2. `bash scripts/batch-precheck.sh <stem>` → vision subagent on the sampled
   frames. Catches blank/broken scenes before burning a render.
3. `bash scripts/batch-ship.sh <stem> <program-slug>` — **run backgrounded**
   (a ~7–8 min render is too close to the 10-min tool ceiling).
4. Vision subagent on the `AWAITING_VISION` frames → on PASS,
   `bash scripts/batch-ship.sh <stem> <program-slug> --publish`.

**Orchestrator discipline — the batch survives only if you stay small:**
never read a script body, an `index.html`, or `frame.md` yourself; never let
rendered frames into your own context (a 21-scene video dumps 63 PNGs — the
vision subagent exists so only one line comes back). Pipeline it: start the next
build while the previous renders, but never two renders at once (4 cores).

Set `VIDEO_SNAG_RETRO_HOOK_DISABLED=1` and `VIDEO_PURGE_REMINDER_HOOK_DISABLED=1`
for the run; do the snag retro once at close-out.

## 8. The queue: 30 videos, 5 deliberately excluded

`bash scripts/batch-status.sh` is authoritative. As of 2026-07-28: **30 to
build**, 2 auto-blocked, 6 already on Wistia.

Excluded, and why:

- `m2_the-value-of-building-mid-career-momentum_2026-07-23` and
  `m3_discover-experiences-that-support-your-next-move_2026-07-23` — contain
  live `TODO: needs input` markers. **TTS would speak them aloud.** Needs
  content from the owner. `batch-status.sh` detects these from file content, so
  a fixed script re-enters the queue automatically.
- `m4_visibility-actions-what-they-are-and-how-to-practice-them_2026-07-22` —
  marked `SCRIPT PENDING — do not refine or build`.
- `m2_why-build-your-own-path_2026-07-23` — byte-identical duplicate of the m1
  script.
- `m0_welcome-to-mid-career-momentum_2026-07-22` — sits in `refined/avatar/`,
  the HeyGen avatar route, not this pipeline.

Two queue repairs were made this session and are already committed: three
`early-career-boost` scripts were **un-stranded** from `rendered/` (they were in
the "built" state with no workspace, no MP4 and no Wistia URL — invisible to
the queue forever), and the stem `m2_four-kinds-of-career-transition_2026-07-23`
existed in **two** programs with different content, which would have collided on
workspace name and Wistia title; both now carry their program slug.

## 9. Open items needing the owner

1. Two scripts with `TODO: needs input` (above) — content needed.
2. `mini-syllabus` superseded Wistia copy `2ilh1o6c4g` needs archiving in the
   Wistia UI; our token has no delete scope.
3. Sign-off on the pilot before the batch runs.
