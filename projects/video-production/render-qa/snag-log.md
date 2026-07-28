# Snag log — rolling render-session memory

**Read rule: ONLY the latest entry** — the first `## ` section below (use Read
with a line limit; never load the whole file). Every entry is self-contained:
its **Open** list carries every unresolved item forward, so the newest entry
is always the complete current state. Everything under it is append-only trail.

**Write rule** (every `/refine-scripts` / `/render-lessons` close-out;
hook-enforced after any render): **prepend** a new dated entry with three parts:

- **Open — owner-actionable only.** An item may roll forward ONLY if it
  genuinely needs the human: a decision, a credential/access, or an action
  outside the agent's reach. Anything the agent could do itself — code, config,
  a retry, filing an upstream bug — it MUST do this session; never roll
  agent-fixable work forward. Copy each still-unresolved owner item from the
  previous entry verbatim (keep its `since YYYY-MM-DD`), plus anything new this
  session hit that only the owner can clear. **If this list is non-empty, the
  session ASKS the human directly at close-out** — present each item as a
  decision (AskUserQuestion when the session is interactive), never as a log
  line the human has to go find. This file is the trail, not the human's inbox;
  the human should never have to open it. An item closes when resolved and then
  simply stops appearing.
- **Fixed this session** — snags hit and resolved, tagged
  `[env]/[tooling]/[authoring]/[upstream]/[defect]`, with resolution + time cost.
- **Promoted to docs** — durable lessons do NOT accumulate here: fix the owning
  doc (the skill's command block, `frame.md`, a preflight/verify check) in the
  same session and note where it went. The doc is the memory; this log is the
  trail that proves the loop ran.

**Rotation policy (2026-07-28, R7):** the live file keeps the newest ~5–10
entries. When it grows past ~100 KB, move everything below the newest 5 entries
to `logs/snag-log-archive-<NNN>.md` (next number; prepend the standard
provenance header). Archives are read-only trail — the read rule above never
changes: only the latest entry in THIS file is current state.

Sibling: `logs/BUILD-LOG.md` (dated build/overhaul/run records; rotated the
same way if it outgrows ~100 KB). Handoff docs live in `docs/`.


## 2026-07-28 ~21:45 UTC · plan-first rewire landed + pilot rebuilt through it

Picked up HANDOFF-deterministic-rewire-2026-07-28.md mid-flight (3 subagents
were cut off). All three had landed; §6 ran green after two fixes below. The
pilot was rebuilt THROUGH the new flow — a cold builder authored `scenes.json`
only, looped `--static` pre-TTS, and the deck went 25 scenes / 7 content forms
/ all gates exit 0 / precheck + vision PASS. Sitting at the PILOT GATE now.
No render ran this session.

**Open — owner-actionable only**

- **2 scripts carry live `TODO: needs input`** *(since 2026-07-23)* —
  `m2_the-value-of-building-mid-career-momentum_2026-07-23`,
  `m3_discover-experiences-that-support-your-next-move_2026-07-23`.
- **`mini-syllabus` superseded Wistia copy `2ilh1o6c4g` still needs archiving**
  *(since 2026-07-21)* — token has no delete scope.
- **Confirm the on-screen program label** *(since 2026-07-28)* — eyebrow is
  now gated to "Career Accelerator" (title_card check verifies it); visible on
  the rebuilt pilot title card at preview. Say so if wrong.
- **Pilot sign-off (rebuilt cut)** — `bash scripts/preview.sh
  better-decisions-come-from-better-criteria_early-career-boost_2026-07-28`;
  approval authorizes the batch. (Replaces the previous entry's _2026-07-06
  preview line — that cut was rejected and has been rebuilt plan-first.)
- **Commit decision** *(new 2026-07-28)* — ~35 files across three sessions
  uncommitted (gates, compiler, skills, rules, tests, logs). Recommendation:
  commit granularly; all suites green.

**Fixed this session**

- `[defect]` **check_variety `family()` missed `__scene_NN` instance suffixes**
  — every hand-named clone counted as its own template family, so run caps,
  canvas caps, and distribution silently undercounted on real workspaces (the
  rejected pilot reported 8 findings; truth was 13, including the 9-scene/78.3s
  light-canvas run the owner rejected). Fix: strip at the first `__`. Tests
  still pin reference-PASS / rejected-FAIL. ~15 min.
- `[tooling]` **Agent A's pinning test was never written** (cut off mid-step) —
  added `tests/test_build_index.py` (26 checks: byte-determinism, round-trip,
  canon head/tail cross-pinned against `batch-prepare.sh`, placeholders,
  `__i2` clone scheme). Via subagent. No defects found in `build_index.py`.
- `[defect]` **Broken STD-35 claim** — `.claude/rules/video-production.md`
  backticked `scenes.json` inside a Mechanism annotation; check-enforcement
  hard-failed it (per-workspace artifact, not a repo file). Reworded; 41
  backed / 0 broken. ~5 min.
- `[env]` **Stale user-level skill copies shadowed the project skills** —
  `/home/codespace/.claude/skills/{render-lessons,refine-scripts,produce-video}/SKILL.md`
  were pre-rewire copies, and the skill loader served the STALE render-lessons
  ("assemble index.html first") over the project's plan-first rewrite. Synced
  all three (verified byte-identical). Durable risk: the sync is manual and
  nothing detects drift — if the duplicate install is deliberate, it deserves
  a checker; if not, the user-level copies should be deleted. ~10 min.
- `[authoring]` 15 unreferenced `__scene_NN` template clones from the rejected
  build pruned from the pilot workspace; preflight re-verified exit 0.

**Promoted to docs**

- decisions/log.md: new top entry — plan-first rewire (builder authors the
  plan; compiler emits the HTML; gates fire at plan stage; doctrine line).
- HANDOFF-deterministic-rewire-2026-07-28.md: pickup banner (what landed,
  what remains) so no future session re-runs its queue.

## 2026-07-28 ~19:10 UTC · pilot certification loop (audit + 3 clean re-runs)

Owner directive: batch may not launch until the pilot rebuilds 3 consecutive
times with zero glitches, pixel-verified. Achieved: horizon, cadence, summit
runs each went build -> 5 gates -> precheck vision -> render -> verify ->
3-lane frame review with ZERO FAILs. Batch is certified pending the PILOT
GATE sign-off on the summit cut.

**Open — owner-actionable only**

- **2 scripts carry live `TODO: needs input`** *(since 2026-07-23)* —
  `m2_the-value-of-building-mid-career-momentum_2026-07-23`,
  `m3_discover-experiences-that-support-your-next-move_2026-07-23`.
- **`mini-syllabus` superseded Wistia copy `2ilh1o6c4g` still needs archiving**
  *(since 2026-07-21)* — token has no delete scope.
- **Confirm the on-screen program label** *(new 2026-07-28)* — frame.md now
  pins early-career-boost's eyebrow to "Career Accelerator" per the 2026-07-21
  ledger note; visible on the pilot title card at preview. Say so if wrong.
- **Pilot sign-off** — `bash scripts/preview.sh better-decisions-come-from-better-criteria_early-career-boost_2026-07-06`;
  approval authorizes the 29-video batch.

**Fixed this session**

- `[defect]` **State machine unsound for unattended runs (5 blockers).** Stems
  vanished from batch-status after the preflight-time script move (interrupted
  runs silently stranded videos); publish could upload a different MP4 than
  verify verified; no publish idempotency; ledger matcher never matched real
  rows (would double-publish); git failures masked with MP4 deleted anyway.
  Fix: qa/VERIFIED sha-256 marker contract, lesson-scripts/published.tsv as
  machine resume key (backfilled 6 rows), STRANDED bucket, script moves at
  publish, unmasked commits, publish lock, disk guard, render timeout, upload
  retries. ~half the session.
- `[defect]` **BUILD-KIT generator dumped the whole SKILL into every builder**
  (unanchored awk end-pattern) — including the orchestrator phases and a
  verbatim quote of the fabricated heading, which the run-0 builder copied
  on screen. Marker-bounded extraction, fails loud, no quotable copy.
- `[defect]` **All 55 realistic template defaults could fabricate content** —
  they were literally this pilot's copy; every other lesson would render it on
  an omitted slot. Now `[[slot]]` placeholders + check_slots fails any
  placeholder that would render (multi-line-safe parse too).
- `[defect]` **check_text never graded chip copy** (`chips` key unmatched,
  comma list diluted overlap) — echo-chips class now trips at 100%.
- `[defect]` **Title card + outro were builder-invented each run** (run 2
  guessed a program name; used narration as title). frame.md display-name
  table + derivation rules; preflight check 7b enforces.
- `[tooling]` **with-secrets curl flag needed curl>=7.71; box has 7.68** —
  login died pre-request, derailing a builder into an unauthorized kokoro
  fallback + pip install. Flag dropped; kokoro uninstalled; BUILD-KIT now
  hard-stops on TTS failure (no fallback voice — pinned-voice rule).
- `[authoring]` **Pacing gate recalibrated** 4.5/3.5 -> 4.0/3.0 with a
  dead-air rule in BUILD-KIT; templates polished (subBeats live-line styling,
  morph content-driven card height + earlier entrance, closing tick square->bar).

**Promoted to docs**

- `.claude/rules/video-production.md` (published.tsv + VERIFIED contract),
  render-lessons SKILL (B3/SHIP/A3/A6 rewritten to the guard chain),
  batch-prepare BUILD-KIT rules 2-6, frame.md "Title card & outro sources",
  preflight 7b, HANDOFF doc replaced. Known accepted characteristic: 3.0-3.5s
  content-bearing holds (gray zone) surface as WARNs and were reviewer-judged
  acceptable; remedy (subBeats/split) documented in BUILD-KIT rule 4.

## 2026-07-28 ~09:50 UTC · /render-lessons AUTO-BATCH (pilot + pipeline rebuild)

First session in 26 firings to actually dispatch a build. The 25-firing
environment blocker is **cleared** — ffmpeg/ffprobe present, node v22.15.0,
/dev/shm raised to 2G, npm/HeyGen/Infisical/Wistia all reachable, Infisical
creds present. Nothing in the env item survives; it stops appearing.

**Open — owner-actionable only**

- **2 scripts carry live `TODO: needs input`** *(since 2026-07-23)* — they
  cannot be built; TTS would speak the marker aloud. Content is needed from the
  owner: `m2_the-value-of-building-mid-career-momentum_2026-07-23`,
  `m3_discover-experiences-that-support-your-next-move_2026-07-23`.
  `batch-status.sh` now detects these from file content, so a fixed script
  re-enters the queue with no bookkeeping.
- **`mini-syllabus` superseded Wistia copy `2ilh1o6c4g` still needs archiving**
  *(since 2026-07-21)* — the WISTIA_API token is read+write, not delete.
- **Wistia token lacks project-management scope** *(new 2026-07-28)* —
  `POST /v1/projects.json` returns `unauthorized_scope`, so the pipeline cannot
  create per-program projects. Owner created the three needed projects in the
  UI this session and they are now registered in `config/endpoints.json`; this
  only recurs when a new program is added.

**Fixed this session**

- `[defect]` **Shared templates render completely blank.** Any scene pointing at
  a `compositions/` file another scene also used rendered background + footer
  only — 18 of the pilot's 21 scenes. The three survivors were the only scenes
  using a template no one else used. Cause: `instance_templates.py` was never in
  the build loop; preflight ran it only with `--check` and reported it as a
  warning. Found by the human previewing the pilot and asking whether it was a
  real glitch — no gate caught it. ~40 min.
- `[defect]` **Omitted template slots fabricate on-screen copy.** Templates
  declare a `default` per slot; a slot left out of `data-variable-values`
  renders that default as real copy. The pilot put 15 such lines on screen,
  including four points under a "Two more ways pressure shows up" heading. This
  is a fabrication-ban violation and no existing gate could catch it —
  `check_text` grades size and restatement, not provenance. ~35 min.
- `[authoring]` **`scla-steps` used for an enumerated set spread across the
  lesson.** It renders nodes `1..N` from the count of non-empty step slots and
  has no notion of "step 3 of 4", so four one-step scenes each rendered a lone
  node labelled "1" — scene 11 is STEP TWO. Converted to `scla-condition`,
  which frame.md already prescribes for this case. ~25 min.
- `[tooling]` **`with-secrets.sh` dead CLI branch removed.** The `infisical`
  CLI is not installed here, so every call printed a "falling back to REST"
  warning — 60+ times across a 30-video batch. REST is now the only path.
- `[tooling]` **Version pin unified at 0.7.45.** `scripts/review.sh` had drifted
  to 0.7.76, which arrived incidentally in a VS Code-task commit and had only
  ever been exercised for *preview*, never render. Pinned down, not up, given
  this repo's history of version bumps breaking rendering.
- `[defect]` **Scaffold defects caught by the pilot** — `data-vars` vs
  `data-variable-values`, missing `data-composition-id`, un-predeclared
  `sceneDuration`, and an `<audio>` tag without `id`/`data-start` that lint
  flags as "audio will be SILENT in renders". All four fixed in the generator.
- `[process]` **Subagent-reported gate exits are not trustworthy.** The pilot
  builder reported `preflight=0` while preflight was exiting 1. Both
  `batch-precheck.sh` and `batch-ship.sh` now re-run preflight themselves and
  treat only the process exit code as authoritative.

**Promoted to docs**

- Build loop is now **five** commands with `instance_templates.py` first —
  `_run/BUILD-KIT.md` (generated by `scripts/batch-prepare.sh`).
- "Blank every unused slot with `""`" and "enumerated set spread across the
  lesson -> `scla-condition`, not `scla-steps`" — BUILD-KIT rules 2 and 3.
- New `render-qa/check_slots.py`, wired into `preflight.py` as check 8 — the
  fabrication class is now mechanized, not a convention.
- Per-video gate is no longer a human eye: PILOT GATE + mechanized guards, in
  `.claude/rules/video-production.md` and `/render-lessons` Phase AUTO-BATCH.
- `frame.md` "Host-root progress rail" now points at the generated scaffold
  instead of claiming no scaffold exists.

## 2026-07-28 06:55 UTC (25th firing) · /produce-video (scheduled routine): BUILD still blocked on TTS/egress wall, unchanged; no renotify

Automated run via `/produce-video`. Refine step: listed each program's root and `avatar/`
non-recursively (`career-transitions`, `early-career-boost`, `entrepreneur-accelerator`,
`mid-career-momentum`). Same two raw `.txt` files present at program roots, unchanged —
`entrepreneur-accelerator/m2_why-build-your-own-path_2026-07-23.txt` (byte-identical duplicate of the
M1 script per the ledger row, confirmed by direct read) and
`mid-career-momentum/m4_visibility-actions-what-they-are-and-how-to-practice-them_2026-07-22.txt`
(`SCRIPT PENDING — do not refine or build` marker confirmed still at file top by direct read) — both
correctly skipped by folder-content alone. No avatar-route raws at any program root. No refine subagent
dispatched — true no-op.

Moved to Phase BUILD context. `refined/` root queue unchanged at 29 scripts (career-transitions 8,
early-career-boost 2, entrepreneur-accelerator 4, mid-career-momentum 15, of which 2 carry live
`TODO: needs input` lines). `renders-hyperframes/` still holds only `README.md` — fresh container, no
partial workspace to resume. Independently re-verified the TTS/egress wall from scratch before selecting
or dispatching any build subagent: no `infisical` on PATH; no `INFISICAL_CLIENT_ID`/
`INFISICAL_SECRET_KEY`/`HEYGEN_API_KEY` in env; `python3 -c "import kokoro_onnx"` →
`ModuleNotFoundError`; no `ffmpeg` on PATH; direct curl to `https://api.heygen.com` and
`https://huggingface.co` both fail (exit 56, `http_code 000`). Identical to every prior firing's
finding. No build subagent dispatched — dispatching one would just fail identically at
`synth_narration.py` and burn tool-call budget for nothing. Batch cap not exercised.

**No push notification this run.** Nothing changed since the already-notified (2026-07-26) blocker: same
wall, same queue, no new raw scripts, no build progress. A 25th identical notification would be noise.

**Open (owner-actionable, unchanged since first flagged 2026-07-23, notified 2026-07-26):**
- **TTS/egress wall:** unchanged — see prior entries for full detail. 29 scripts (27 buildable, 2 blocked
  independently by their own TODO lines) remain queued in `refined/` waiting on this. **Firing cadence:**
  this routine has now fired 25 times across 2026-07-27→28 with zero BUILD progress possible from within
  it. Repeating the same recommendation: the owner may want to widen this routine's interval or pause it
  until the environment is provisioned for TTS (credentials + CLI, or kokoro + ffmpeg + egress), since
  real builds are happening via a different session type (see the 22nd-firing entry's closed
  duplicate-file finding).
- **2 `TODO: needs input` scripts queued in `mid-career-momentum/refined/`** (would be spoken by TTS as
  literal text if built as-is): `m2_the-value-of-building-mid-career-momentum_2026-07-23`,
  `m3_discover-experiences-that-support-your-next-move_2026-07-23`. Blocked behind the TTS/egress wall
  regardless, so not yet a live risk, but flagged so it isn't missed once TTS is unblocked.

**Fixed this session:** none — no code/config issue found that this agent could resolve; the blocker is
environment provisioning (secrets + CLI + egress) outside this session's reach.

**Promoted to docs:** none new this session (already documented in the prior entries' trail).

## 2026-07-28 (24th firing) · /produce-video (scheduled routine): BUILD still blocked on TTS/egress wall, unchanged; no renotify

Automated run via `/produce-video`. Refine step: listed each program's root and `avatar/`
non-recursively (`career-transitions`, `early-career-boost`, `entrepreneur-accelerator`,
`mid-career-momentum`). Same two raw `.txt` files present at program roots, unchanged —
`entrepreneur-accelerator/m2_why-build-your-own-path_2026-07-23.txt` (byte-identical duplicate of the
M1 script per the ledger row, confirmed by direct read) and
`mid-career-momentum/m4_visibility-actions-what-they-are-and-how-to-practice-them_2026-07-22.txt`
(`SCRIPT PENDING — do not refine or build` marker confirmed still at file top by direct read) — both
correctly skipped by folder-content alone. No avatar-route raws at any program root. No refine subagent
dispatched — true no-op.

Moved to Phase BUILD context. `refined/` root queue unchanged at 29 scripts (career-transitions 8,
early-career-boost 2, entrepreneur-accelerator 4, mid-career-momentum 15, of which 2 carry live
`TODO: needs input` lines). `renders-hyperframes/` still holds only `README.md` — fresh container, no
partial workspace to resume. Independently re-verified the TTS/egress wall from scratch before selecting
or dispatching any build subagent: no `infisical` on PATH; no `INFISICAL_CLIENT_ID`/
`INFISICAL_SECRET_KEY`/`HEYGEN_API_KEY` in env; `python3 -c "import kokoro_onnx"` →
`ModuleNotFoundError`; no `ffmpeg` on PATH; direct curl to `https://api.heygen.com` and
`https://huggingface.co` both fail (exit 56, `http_code 000`). Identical to every prior firing's
finding. No build subagent dispatched — dispatching one would just fail identically at
`synth_narration.py` and burn tool-call budget for nothing. Batch cap not exercised.

**No push notification this run.** Nothing changed since the already-notified (2026-07-26) blocker: same
wall, same queue, no new raw scripts, no build progress. A 24th identical notification would be noise.

**Open (owner-actionable, unchanged since first flagged 2026-07-23, notified 2026-07-26):**
- **TTS/egress wall:** unchanged — see prior entries for full detail. 29 scripts (27 buildable, 2 blocked
  independently by their own TODO lines) remain queued in `refined/` waiting on this. **Firing cadence:**
  this routine has now fired 24 times across 2026-07-27→28 with zero BUILD progress possible from within
  it. Repeating the same recommendation: the owner may want to widen this routine's interval or pause it
  until the environment is provisioned for TTS (credentials + CLI, or kokoro + ffmpeg + egress), since
  real builds are happening via a different session type (see the 22nd-firing entry's closed
  duplicate-file finding).
- **2 `TODO: needs input` scripts queued in `mid-career-momentum/refined/`** (would be spoken by TTS as
  literal text if built as-is): `m2_the-value-of-building-mid-career-momentum_2026-07-23`,
  `m3_discover-experiences-that-support-your-next-move_2026-07-23`. Blocked behind the TTS/egress wall
  regardless, so not yet a live risk, but flagged so it isn't missed once TTS is unblocked.

**Fixed this session:** none — no code/config issue found that this agent could resolve; the blocker is
environment provisioning (secrets + CLI + egress) outside this session's reach.

**Promoted to docs:** none new this session (already documented in the prior entries' trail).

## 2026-07-28 01:57 UTC (23rd firing) · /produce-video (scheduled routine): BUILD still blocked on TTS/egress wall, unchanged; no renotify

Automated run via `/produce-video`. Refine step: listed each program's root and `avatar/`
non-recursively (`career-transitions`, `early-career-boost`, `entrepreneur-accelerator`,
`mid-career-momentum`). Same two raw `.txt` files present at program roots, unchanged —
`entrepreneur-accelerator/m2_why-build-your-own-path_2026-07-23.txt` (re-confirmed by direct read + md5
`226e875076a9411a33363895c1ee002c`, matching the known m1-duplicate; still correctly staying raw per the
ledger row) and `mid-career-momentum/m4_visibility-actions-what-they-are-and-how-to-practice-them_2026-07-22.txt`
(`SCRIPT PENDING — do not refine or build` marker confirmed still at file top by direct read) — both
re-confirmed by direct read, correctly skipped by folder-content alone. No avatar-route raws at any
program root. No refine subagent dispatched — true no-op.

Moved to Phase BUILD. `refined/` root queue = 29 scripts (career-transitions 8, early-career-boost 2,
entrepreneur-accelerator 4, mid-career-momentum 15, of which 2 carry live `TODO: needs input` lines),
unchanged from the 22nd firing. `renders-hyperframes/` still holds only `README.md` — no partial
workspace to resume. Selected a 3-build batch under the cap
(`better-decisions-come-from-better-criteria_early-career-boost_2026-07-06`,
`using-the-career-map-tool_early-career-boost_2026-07-10`,
`m2_welcome-and-using-career-transitions-as-leaps-ahead_2026-07-23` — oldest-refined, no ledger
blockers) but independently re-verified the TTS/egress wall from scratch before dispatching any build
subagent: no `infisical` on PATH; no `INFISICAL_CLIENT_ID`/`INFISICAL_SECRET_KEY`/`HEYGEN_API_KEY` in
env; `python3 -c "import kokoro_onnx"` → `ModuleNotFoundError`; no `ffmpeg` on PATH; direct curl to
`https://api.heygen.com` and `https://huggingface.co` both fail (`CONNECT tunnel failed, response 403`,
http_code 000). Identical to every prior firing's finding. No build subagent dispatched — dispatching one
would just fail identically at `synth_narration.py` and burn tool-call budget for nothing. Batch cap not
exercised.

**No push notification this run.** Nothing changed since the already-notified (2026-07-26) blocker: same
wall, same queue, no new raw scripts, no build progress. A 23rd identical notification would be noise.

**Open (owner-actionable, unchanged since first flagged 2026-07-23, notified 2026-07-26):**
- **TTS/egress wall:** unchanged — see prior entries for full detail. 29 scripts (27 buildable, 2 blocked
  independently by their own TODO lines) remain queued in `refined/` waiting on this. **Firing cadence:**
  this routine has now fired 23 times across 2026-07-27→28 with zero BUILD progress possible from within
  it. Repeating the same recommendation: the owner may want to widen this routine's interval or pause it
  until the environment is provisioned for TTS (credentials + CLI, or kokoro + ffmpeg + egress), since
  real builds are happening via a different session type (see the 22nd-firing entry's closed
  duplicate-file finding).
- **2 `TODO: needs input` scripts queued in `mid-career-momentum/refined/`** (would be spoken by TTS as
  literal text if built as-is): `m2_the-value-of-building-mid-career-momentum_2026-07-23`,
  `m3_discover-experiences-that-support-your-next-move_2026-07-23`. Blocked behind the TTS/egress wall
  regardless, so not yet a live risk, but flagged so it isn't missed once TTS is unblocked.

**Fixed this session:** none — no code/config issue found that this agent could resolve; the blocker is
environment provisioning (secrets + CLI + egress) outside this session's reach.

**Promoted to docs:** none new this session (already documented in the prior entries' trail).

## 2026-07-27 23:57 UTC (22nd firing) · /produce-video (scheduled routine): BUILD still blocked on TTS/egress wall; refined×rendered duplicate finding now fully resolved; no renotify

Automated run via `/produce-video`. Refine step: listed each program's root and `avatar/`
non-recursively (`career-transitions`, `early-career-boost`, `entrepreneur-accelerator`,
`mid-career-momentum`). Same two raw `.txt` files present at program roots, unchanged —
`entrepreneur-accelerator/m2_why-build-your-own-path_2026-07-23.txt` (re-confirmed by direct read +
diff against the refined `m1_reframing-entrepreneurship-and-going-solo` body: identical narration
modulo cue-strip/typographic normalization, still correctly staying raw per the ledger row) and
`mid-career-momentum/m4_visibility-actions-what-they-are-and-how-to-practice-them_2026-07-22.txt`
(`SCRIPT PENDING — do not refine or build` marker confirmed still at file top by direct read) — both
re-confirmed by direct read, correctly skipped by folder-content alone. No avatar-route raws at any
program root. No refine subagent dispatched — true no-op.

Moved to Phase BUILD. `refined/` root queue = 29 scripts (career-transitions 8, early-career-boost 2,
entrepreneur-accelerator 4, mid-career-momentum 15), plus 1 separate `refined/avatar/` file (HeyGen
route, not this queue). `renders-hyperframes/` still holds only `README.md` — no partial workspace to
resume. Independently re-verified the TTS/egress wall from scratch (not trusting the prior entry):
`which infisical` → not found; no `INFISICAL_CLIENT_ID`/`INFISICAL_SECRET_KEY`/`HEYGEN_API_KEY` in env;
`python3 -c "import kokoro_onnx"` → `ModuleNotFoundError`; `which ffmpeg` → not found; direct curl to
`https://api.heygen.com` and `https://huggingface.co` both failed (exit 56, http_code 000). Neither the
default HeyGen-starfish TTS path nor the kokoro fallback can run, so no build subagent was dispatched.
`refined/` unchanged by this run; batch cap not exercised.

**Data-integrity finding now CLOSED:** the 5-stem `refined/`×`rendered/` overlap flagged since the
16th-ish firing is gone — `comm -12` on every program's `refined/`×`rendered/` stem lists returns empty
everywhere. `early-career-boost/refined/` shrank from 5 files to 2
(`better-decisions-come-from-better-criteria_..._2026-07-06`, `using-the-career-map-tool_..._2026-07-10`
remain; `build-direction-before-you-build-a-plan`, `how-to-make-strong-career-decisions`,
`skills-for-the-ai-era-future` are gone from `refined/` and exist only in `rendered/` now) —
`git log --oneline -- lesson-scripts/early-career-boost/refined/` shows commit `2630285` "BUILD
gate-clean, horizon theme" for `skills-for-the-ai-era-future`, i.e. a real build ran to completion
outside this routine's blocked firings (working credentials, different session type) and the
bookkeeping cleanup that follows a gate-clean build removed the stale duplicate. `mid-career-momentum`'s
`m2_four-kinds-of-career-transition` no longer overlaps either (`rendered/` is empty for that program;
the stem is only in `refined/`). No action needed from this routine — noting the closure so it isn't
mistakenly re-flagged as open.

The 2 `TODO: needs input` scripts in `mid-career-momentum/refined/`
(`m2_the-value-of-building-mid-career-momentum_2026-07-23`,
`m3_discover-experiences-that-support-your-next-move_2026-07-23`) are unchanged — still carry their TODO
lines (`grep -l` confirms both). Still blocked behind the TTS/egress wall regardless.

**No push notification this run.** The blocker the human was already notified about (2026-07-26, after
3 days silent) is unchanged — still a guaranteed environment-provisioning wall this routine cannot clear
itself. The only change since the 21st firing (duplicate-file cleanup) is positive, already resolved
without needing the human, and not itself an actionable ask — logging it is enough. A 22nd identical
"BUILD is blocked" notification would be pure noise.

**Open (owner-actionable, unchanged since first flagged 2026-07-23, notified 2026-07-26):**
- **TTS/egress wall:** `INFISICAL_CLIENT_ID`/`INFISICAL_SECRET_KEY` (Codespaces repo secrets) and the
  `infisical` CLI are not present in this environment — `with-secrets.sh` hard-fails without them, and
  they're normally installed by the devcontainer's `postCreateCommand`, which doesn't run in this session
  type. No `kokoro_onnx` fallback, no `ffmpeg`, and no network egress reaches `api.heygen.com` or
  `huggingface.co` either. Every BUILD phase in this routine's environment is a guaranteed no-op until
  credentials + CLI are provisioned for this environment type (or the kokoro fallback + ffmpeg + egress
  are). 29 scripts are queued in `refined/` waiting on this. **Firing cadence:** this routine has now
  fired 22 times today with no BUILD progress possible from within it; the owner may want to widen its
  interval or pause it until the environment is provisioned, since builds are in fact happening (see the
  closed duplicate-file finding above) — just via a different session type, not this one.
- **2 `TODO: needs input` scripts queued in `mid-career-momentum/refined/`** (would be spoken by TTS as
  literal text if built as-is): `m2_the-value-of-building-mid-career-momentum_2026-07-23`,
  `m3_discover-experiences-that-support-your-next-move_2026-07-23`. Blocked behind the TTS/egress wall
  regardless, so not yet a live risk, but flagged so it isn't missed once TTS is unblocked.

**Fixed this session:** none — no code/config issue found that this agent could resolve; the blocker is
environment provisioning (secrets + CLI + egress) outside this session's reach.

**Promoted to docs:** none new this session (already documented in the prior entry's trail).

