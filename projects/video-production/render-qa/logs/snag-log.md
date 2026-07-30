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


## 2026-07-30 (latest) · carry-forward-inventory BUILD — the two rolled-forward gate items, closed

Owner asked for one illustrated lesson video (`m4_building-your-carry-forward-inventory`,
career-transitions, theme summit) matching the `better-decisions` reference. The
refined script already existed and was byte-identical to the script supplied in
the request, so `/refine-scripts` was a no-op and this was a pure BUILD.

**The plan is gate-clean and there is no video.** `preflight.py --static` exits 0
(re-run independently, not taken from the builder's report): 16 scenes, 14
content scenes, 6 distinct forms, largest share 28.6%, artwork 14/14, longest
same-family run 2. Narration verified verbatim against the refined script — 338
words in, 338 out, exact match. TTS and render were never attempted, because
this environment's network policy answers **403 on CONNECT** for
`api.heygen.com`, `app.infisical.com` AND `cdn.jsdelivr.net` (GSAP, which every
composition loads). No narration means no word timestamps, and every timing
number derives from those. Per the standing rule the wall was reported, not
worked around: no provider swap, no local TTS, no vendored GSAP. `main`'s HEAD
commit records the same wall on the sixteenth run of the day, so the diagnosis
cost minutes rather than the ~40 it cost on 2026-07-29 — the probe was run
before dispatching the builder, and the builder was told the finding up front.

The previous entry's two "Promoted to docs" items were explicitly recorded as
that session's own output and left for the next session. Both are now done, so
neither was eligible to roll forward as an owner item.

**Open — owner-actionable only**

- **Egress policy blocks the whole render path** *(new)* — `api.heygen.com`,
  `app.infisical.com`, `cdn.jsdelivr.net` all 403 on CONNECT. The pipeline can
  author but can never ship from this environment. This is the same wall the
  last ~17 runs hit and it is the single thing standing between a gate-clean
  plan and a published video. Only the owner can change the environment policy.
- **2 scripts carry live `TODO: needs input`** *(since 2026-07-23)* —
  `m2_the-value-of-building-mid-career-momentum`,
  `m3_discover-experiences-that-support-your-next-move`. Still blocking; they
  cannot enter the pipeline.
- **`mini-syllabus` superseded Wistia copy `2ilh1o6c4g` still needs archiving**
  *(since 2026-07-21)* — token has no delete scope.
- **Pilot sign-off (2026-07-29 rebuild #3)** *(since 2026-07-29)* —
  `bash scripts/preview.sh better-decisions-come-from-better-criteria_early-career-boost`.
  Rendered and verified, NOT published.
- **Pilot sign-off (mid-career-momentum)** *(since 2026-07-29)* —
  `bash scripts/preview.sh m2_mid-career-mindsets-and-limiting-beliefs` is the
  only gate-clean lesson of the 13. Nothing in this program can render until a
  human approves a pilot.
- **"Career Accelerator" appears in APPROVED SCRIPT BODY** *(since 2026-07-29)* —
  `m1_mini-syllabus` narrates "your broader Career Accelerator journey". The
  owner rejected that name on the banner on 2026-07-29 and the `programs:` map
  was reverted. Whether the name is retired repo-wide or only as a program
  label is a decision only the owner can make; the script was left untouched.
- **Scene-12 (career map) holds ~3s pixel-static mid-scene** *(since
  2026-07-29)* — advisory, in `check_presence`'s 3–5s gray zone. The fix is
  authoring and changes the scene's rhythm — worth a decision.
- **`m4_building-your-carry-forward-inventory` scene-02 is one 38-word
  sentence** *(new)* — ~14.1s against the 12.5s cap, so the new static pacing
  gate WARNs and the post-synth gate will likely FAIL. There is no legal split
  inside the scene plan: every split point leaves the next scene opening
  mid-clause, which `check_continuity` hard-fails. The fix is one sentence in
  the refined script — replacing ", and the tool that answers it is" with a full
  stop plus "The tool that answers it is" yields 9 + 29 words, both under cap
  with a legal opener. Left to the owner because the script text was supplied
  verbatim in the request; changing their copy is their call, not the agent's.

**Fixed this session**

- [tooling] **`pacing` now fires at `--static`** — the previous entry's item 1.
  It was the only owner-facing gate that could not run before TTS was spent
  (12 of 13 lessons on 2026-07-29 learned it after 258 clips). `check_pacing_static()`
  estimates duration from narration word count and locates cue anchors by word
  offset. Rates are **measured, not guessed**: 249 real content scenes across 14
  built lessons give words/sec of `data-duration` at median 2.71, p95 3.72.
  `WPS_TYPICAL` drives a WARN band; `WPS_FAST` is a one-sided certainty bound
  above every observed rate, so a static FAIL can only mean the copy genuinely
  cannot fit. Validated against all 14 builds — the owner's reference passes,
  and the one hard FAIL (`m5_skills-for-the-ai-era` scene-13) really does run
  14.9s. It then earned itself immediately: it caught this lesson's scene-02
  during a JSON edit, which is exactly the class that used to cost a re-synth.
- [defect] **`scla-stat` has a cue-able beat** — the previous entry's item 2.
  Its meters all land in the entrance, so entrance + closing beat were the only
  events and any stat scene over ~5.7s could not pass pacing, while BUILD-KIT
  went on recommending the template. New `contextCue` holds the context sentence
  until the narration reaches it: ceiling ~5.7s → **~9.7s**, above the ~8s median
  content scene. Absent the variable the behaviour is unchanged, so existing
  builds are unaffected. Verified by executing the timeline against a GSAP stub
  (default 0.8s / cued honoured / clamped to `sdur−1.4` / junk falls back),
  because `npm run check`'s Runtime pass cannot execute here.
- [tooling] **`render-qa/snag-log.md` did not exist** — the real path is
  `logs/snag-log.md`, and a session following its own documented snag memory got
  a read error. Repointed in both pipeline skills, `adversarial-qa`, the rules
  file, the `settings.json` hook text, `PIPELINE-MANUAL.md`, the autobatch
  handoff, `preview.sh` and `wistia-upload.sh`. `decisions/log.md` and `audits/`
  keep the old path as historical record.
- [env] **`ffprobe` was absent**, so `run_tests.py` crashed with a bare
  `FileNotFoundError` and check 11 could not grade anything. Confirmed
  pre-existing by re-running the suite on stashed HEAD before blaming the edit.
  Installed ffmpeg via apt (`--no-install-recommends`; the plain install 404s on
  stale driver debs). Suite then 83 assertions green.

**Promoted to docs**

- `design-contract.md`'s `scla-stat` row and the `/render-lessons` BUILD-KIT
  block both now state the template's cue slot and its ~9.7s ceiling. BUILD-KIT
  had been recommending a template the pacing gate then failed; per STD-35 the
  constraint belongs where the recommendation lives, and `batch-prepare.sh`
  regenerates `_run/BUILD-KIT.md` from that block so the fix propagates.
- Two repo-vs-doc gaps found and recorded here rather than silently tolerated,
  both agent-fixable only in part because the right fix is a policy call:
  1. **`build_index.py --extract` is lossy and writes in place.** Pointed at
     `m5_skills-for-the-ai-era` to learn the manifest shape, it round-tripped
     that committed plan and silently dropped every `theme` var (plus altered
     `meta` and apostrophes). Reverted. It is a live footgun for any builder
     told to learn the format that way — BUILD-KIT and this SKILL both suggest
     it. It should write to stdout, or refuse a workspace it was not given.
  2. **`renders-hyperframes/` and `_run/` are fully tracked in git**, though
     `projects/video-production/CLAUDE.md` and the AUTO-BATCH section both call
     them gitignored. There are no matching `.gitignore` rules at all, so every
     workspace is committed. The doc and the repo disagree; which one is wrong
     is a decision, so it is named here instead of guessed at.

## 2026-07-29 · mid-career-momentum batch — parallelism applied to the one stage that measures as serial

Owner asked for all 15 mid-career-momentum lessons rendered in parallel inside
30 minutes. 13 were buildable. **Zero rendered.** The 30-minute target was not
reachable for renders under any schedule (one render at a time, machine-wide,
~7 min each), and saying so up front would have been worth more than the two
status updates that implied builds might still make it.

The session's real cost was self-inflicted: 13 build subagents were dispatched
at once, each running `TTS_WORKERS=3`, into a provider that
`synth_narration.py:96-100` already documents as tolerating ~3 concurrent calls
**in total** — the worker count had been dialled 5 → 3 on 2026-07-27 after a
21-scene build lost 16 clips. Every build failed at TTS with
`HeyGen request/transcode error`. Four subagents independently diagnosed it as
backend flakiness or a `with-secrets.sh` credential fault (the 2026-07-28
precedent), which is the wrong repair and would have escalated to the owner.
The orchestrator had verified the credential path before dispatch, so the
concurrency reading was available; it was not applied until three builds had
burned ~25 minutes. **`TTS_WORKERS=1` on a quiet machine: 0 errors across 258
clips.** The parallelism that WAS safe — authoring — produced 13 usable plans.

**Open — owner-actionable only**

- **2 scripts carry live `TODO: needs input`** *(since 2026-07-23)* —
  `m2_the-value-of-building-mid-career-momentum`,
  `m3_discover-experiences-that-support-your-next-move`. Still blocking; they
  cannot enter the pipeline.
- **`mini-syllabus` superseded Wistia copy `2ilh1o6c4g` still needs archiving**
  *(since 2026-07-21)* — token has no delete scope.
- **Pilot sign-off (2026-07-29 rebuild #3)** *(since 2026-07-29)* —
  `bash scripts/preview.sh better-decisions-come-from-better-criteria_early-career-boost`.
  Rendered and verified, NOT published.
- **Pilot sign-off (mid-career-momentum)** *(new)* —
  `bash scripts/preview.sh m2_mid-career-mindsets-and-limiting-beliefs` is the
  only gate-clean lesson of the 13. Nothing in this program can render until a
  human approves a pilot.
- **"Career Accelerator" appears in APPROVED SCRIPT BODY** *(new)* —
  `m1_mini-syllabus` narrates "your broader Career Accelerator journey". The
  owner rejected that name on the banner on 2026-07-29 and the `programs:` map
  was reverted. Whether the name is retired repo-wide or only as a program
  label is a decision only the owner can make; the script was left untouched.
- **Scene-12 (career map) holds ~3s pixel-static mid-scene** *(since
  2026-07-29)* — advisory, in `check_presence`'s 3–5s gray zone. The fix is
  authoring and changes the scene's rhythm — worth a decision.

**Fixed this session**

- [env] **HeyGen TTS concurrency** — root-caused to fan-out, not the provider.
  Serialized to one workspace at a time at `TTS_WORKERS=1`; all 13 lessons
  synthesized clean (258 clips). ~40 min lost before the diagnosis landed.
- [defect] **`scla-chips` `subBeats` renders outside the safe area** — the
  `#cc-subbeat-proto` prototype sits at `y=-222` whenever `subBeats` is
  populated at all. Two independent build agents hit it; `check_geometry.py`
  caught it both times, so the gate works — the template does not. Worked
  around by using delayed `iconCue` anchors instead. **Not yet fixed at the
  template**, which is where it belongs (see Promoted).
- [authoring] **Anchor phrases inside em-dash compounds** — 13 cue-resolution
  failures across 3 lessons, all the documented `word—word` single-token class.
  Fixed by quoting the compound verbatim or clearing it. All 13 lessons now
  compile.
- [authoring] **Two conjunction-rule defects in `m6_youve-built-momentum`'s
  refined script** — fixed by joining the lists into one sentence ("...and
  results", "...and compounding"), the sanctioned form, not a bolted-on word.
  Verified against `check_copy.py --script`.

**Promoted to docs**

- Nothing yet — see the two items below, both of which are agent-fixable and
  therefore MUST NOT roll forward as Open items. They are the session's real
  output and are recorded here so the next session finishes them:
  1. **The pacing gate must fire at `--static`.** 12 of 13 lessons, authored
     independently by 12 agents all following BUILD-KIT, failed `pacing` the
     same way — 4–10s stretches with no visual event, plus 2–5 scenes over the
     12.5s cap each. It is the only owner-facing gate that cannot fire before
     TTS is spent, so today it was learned after 258 clips instead of during a
     JSON edit. Every other rule in this repo fires at plan stage. A
     words-per-second estimate from the refined script is enough to grade both
     the cap and cue density statically.
  2. **`scla-stat` has no cue mechanism.** Verified against the template source
     by two agents: entrance + closing beat only, no `*Cues`/`iconCue` slot. Any
     `scla-stat` scene longer than ~5.7s therefore CANNOT pass pacing, and the
     only fix is to abandon the template. BUILD-KIT actively tells builders to
     spend `scla-stat` because it "goes untouched build after build" — the
     variety contract and the pacing gate are in direct conflict, and the
     template loses. Either give it a cue slot or stop recommending it.

## 2026-07-29 · owner review of rebuild #2 — five notes, four of them a gate that was never armed

Owner reviewed the 2026-07-29 cut and named five things. The headline is the
banner: an Early Career Boost lesson titled **"Career Accelerator"** — *"a MUST
… a hard rule that must be enforced."* It had a gate. `preflight.py` check 7b
compared the eyebrow to `tokens.yml`'s `programs:` map and passed, because the
map itself carried the alias. **Grading a value against an unchecked table is
not enforcement — it relocates where a wrong value is allowed to sit.** Same
shape as the last three sessions, one level further out.

**Open — owner-actionable only**

- **2 scripts carry live `TODO: needs input`** *(since 2026-07-23)* —
  `m2_the-value-of-building-mid-career-momentum_2026-07-23`,
  `m3_discover-experiences-that-support-your-next-move_2026-07-23`.
- **`mini-syllabus` superseded Wistia copy `2ilh1o6c4g` still needs archiving**
  *(since 2026-07-21)* — token has no delete scope.
- **Pilot sign-off (2026-07-29 rebuild #3)** — `bash scripts/preview.sh
  better-decisions-come-from-better-criteria_early-career-boost_2026-07-29`,
  or the MP4 in `renders/`. Rendered and verified, NOT published.
- **16/32 refined scripts flag the *conjunction* check** — reported, not
  blocked; a minority are rhetoric or definitions rather than lists.
- **Scene-12 (career map) holds ~3s pixel-static mid-scene** — advisory, in
  `check_presence`'s 3–5s gray zone, and it is the dead stretch the deleted
  ripple used to paper over. The contract's fix is authoring (cue the route
  earlier, or reveal each path card on its own spoken phrase), which changes
  the scene's rhythm — worth a decision rather than a silent rewrite.

("Confirm the on-screen program label", open since 2026-07-28, is closed: the
owner confirmed it by rejecting it.)

**Fixed this session**

- [defect] **The banner did not name the program** — `programs:` map reverted
  (`early-career-boost` → "Early Career Boost"), and the map is now graded:
  a display name must slugify back to its own key (`tokens.programs_problems()`
  → check 7b, full + `--static`), plus `tests/test_programs.py` in CI, which
  also fails a `lesson-scripts/` folder with no banner. ~35 min.
- [defect] **`scripts/hyperframe-guard.sh` had been dead since 2026-07-28** —
  its `RQ` still pointed at `render-qa/`, which the layout refactor emptied into
  `render-qa/src/`. Every PostToolUse firing printed `can't open file` instead of
  a verdict; it read as alive because it produced output, and the jq shape
  contract could not see it (no interpreter ran to emit a payload). Found by
  editing a `scenes.json`. `test_guard_contract.py` now resolves the guard's own
  `RQ` and asserts both entry points exist. ~15 min.
- [authoring] **scla-loop sub-beats moved into the header panel** — under the
  heading, not under the illustration, so a line like "Same four steps, every
  time" reads as a subheading of the statement rather than a caption on a
  three-node diagram. Owner's call, and it also retires the seam that produced
  last session's text-on-text.
- [defect] **Career-map cards were spaced for the copy, not for the slot** —
  74px between one pair and 26px between the other, because top-anchored cards
  grow downward when copy wraps. Fixed slots sized for the widest legal card
  (48px gutters), stage/viewBox made 1:1 so a coordinate is a frame pixel, and
  cards widened 360 → 440 so a 427px phrase stops taking two lines. New
  `card-gutter` rule in `check_geometry.py` (layout boxes, not ink) against a
  new `spacing.card-gutter` token. ~50 min, most of it narrowing the rule until
  it stopped firing on decorative concentric ghost rings.
- [defect] **`icons: "…,map,…"` on `scla-points` drew nothing, silently** —
  `map` existed in `scla-statement`/`scla-steps` and not in `scla-points`;
  `ICONS[name]` returning undefined is a typo no browser reports. New
  `unknown-icon` rule in `check_slots.py` reading the library it actually calls;
  the four libraries re-synced. (The row icons themselves are gone from this
  build at the owner's request — the bullets carry it.)
- [authoring] **Final-slide audio** — `FINAL_HOLD` 1.1 → 1.8s and
  `MIN_FINAL_HOLD` 1.0 → 1.5 together. Worth stating plainly: the release WAS
  in the file (1.34s of trailing audio past the last word timestamp), so this
  is not last session's clipped-tail defect recurring — a lesson ending just
  needs longer to land than a scene boundary does.
- [tooling] **`run_tests.py` asserted the number, not the behaviour** — it
  hard-coded `1.1` and went red the moment the hold changed. Now reads
  `synth_narration.FINAL_HOLD`; a separate assertion pins the producer above its
  own floor.
- [tooling] **A mutation whose defect the design eliminated** — the loop
  text-collision mutant fired capacity rules once the sub-beat moved. Retargeted
  at the seam the NEW layout still has (a heading wrapping into the sub-beat
  below it), not re-pointed at whatever the mutant happened to trip.

**Promoted to docs**

- `.claude/rules/video-production.md` — four new rules: the banner is the
  program folder's name; a hook that crashes is a gate that is off; even spacing
  is a property of the slots; an unknown icon name draws nothing. The trailing-
  hold rule extended with the 1.8s number and why.
- `design-system/docs/design-contract.md` — title-card sources rewritten (the
  2026-07-21 "Career Accelerator" rebrand note deleted, replaced with the
  slug round-trip and its mechanism); the icon-library divergence documented
  under "Living icon library".
- `decisions/log.md` — the banner reversal and the dead guard, with why a green
  gate certified both.
- Templates carry their own budgets in comments beside the CSS that creates
  them (`scla-career-map` slot budget, `scla-loop` header budget).

## 2026-07-29 (later) · owner rejected the rebuilt cut again — three gates that could not fail

Owner sent a screenshot of scene-19 with text printed through text, reported
scene-02's audio as "didn't sound like she completed the sentence… almost like
she ended on a question mark", and said again that there should be an
enforceable minimum text size. All three already had a gate. **None of the
three gates was capable of failing:**

- **min text size** — floor 32px, smallest body rule in the system 32px. Armed,
  wired, run every build, structurally inert. The caption they objected to was
  exactly compliant.
- **overlap** — `check_layout.py` ran the real browser inspector at 60 sample
  points and returned PASS with *zero* findings, not even advisory:
  `hyperframes inspect` grades text against its own container, so two
  absolutely-positioned siblings on the same pixels is not a case it models.
  `check_capacity.py` never graded that slot at all — it infers slot bindings
  from `getElementById(...).textContent = vars.x`, and `scla-loop` binds its
  four captions in a `forEach`.
- **conjunction** — the rule was *satisfied* by the copy that caused the bad
  audio. "…The right city. Or the right path." passes; it also reads as an
  unfinished sentence.

Lesson, sharper than 2026-07-28's: **a written, wired, executing gate still
does not hold if its threshold, its input, or its model makes failure
unreachable.** Coverage ≠ capability.

**Open — owner-actionable only**

- **2 scripts carry live `TODO: needs input`** *(since 2026-07-23)* —
  `m2_the-value-of-building-mid-career-momentum_2026-07-23`,
  `m3_discover-experiences-that-support-your-next-move_2026-07-23`.
- **`mini-syllabus` superseded Wistia copy `2ilh1o6c4g` still needs archiving**
  *(since 2026-07-21)* — token has no delete scope.
- **Confirm the on-screen program label** *(since 2026-07-28)* — eyebrow gated
  to "Career Accelerator"; visible on the rebuilt title card at preview.
- **Pilot sign-off (2026-07-29 rebuild #2)** — `bash scripts/preview.sh
  better-decisions-come-from-better-criteria_early-career-boost_2026-07-29`.
- **16/32 refined scripts flag the *conjunction* check** — reported, not
  blocked; a minority are rhetoric or definitions rather than lists. (The new
  *dangling-fragment* check is separate and clean: 3 flags across 32 scripts,
  all real, now 0.)

**Fixed this session**

- [defect] **Body floor was the smallest size in use** — `frame.md`
  `typography.min-size.body` 32 → 40px (loaded, so one edit moves every gate);
  12 template rules raised; `.kp-num` correctly re-classed as an exempt marker
  numeral. Fallout was exactly one card over budget, named at plan stage by
  `check_capacity`. ~25 min.
- [defect] **No gate owned text-on-text collision** — new `boxmodel.py`
  (absolute + block-flow + flex row/column + grid-centre + vertical
  writing-mode, ink boxes not layout boxes) and `check_geometry.py`
  (text-collision / footer-breach / safe-area-breach), wired into `preflight.py`
  in BOTH full and `--static` mode. Reproduced the owner's screenshot exactly
  (260×31px) before the fix and clears after. ~90 min — the long pole, and most
  of it was killing false positives, which was the point: a gate that cries
  wolf gets switched off.
- [tooling] **Templates now declare what the gate used to guess** — `data-slot`
  and `data-present-if` on `scla-loop`; empty geometry prototypes for the
  run-time-created sub-beat lines in `scla-loop`/`chips`/`points`/`steps`.
  `check_capacity` prefers declared bindings over the JS regex. ~20 min.
- [defect] **`boxmodel` parser ate its own tree** — `</circle>` popped elements
  never pushed (paired void tags), orphaning everything after `scla-stat`'s ring
  SVG; the gate reported that template clean having graded **0** boxes. Fixed to
  pop-to-match, and `nothing-graded` is now itself a failure. ~15 min.
- [defect] **`scla-points` rail label breached the safe area** — `right:44px`
  put a vertical label's outer edge at x=1876, 28px inside the declared 72px
  keep-out, since the system was built. Nothing had ever modelled vertical text.
  Rail + label moved inboard. Found by the new gate, unprompted. ~10 min.
- [defect] **Conjunction satisfied by a dangling fragment** — `check_copy.py`
  rule (c). Discriminators earned one at a time against the 32-script library:
  terminal mark (question lists must keep rising), length + finite verb ("But
  titles are only labels." is a sentence), and position (only the LAST fragment
  can dangle — mid-paragraph the next sentence completes it). 3 flags/32, all
  real. The `test_gates.py` fixture pinning the bolted-on form as CORRECT was
  inverted. ~35 min.
- [authoring] **scene-02 went under the 4.5s beat floor after the copy fix** —
  comma-joining removed three full-stop pauses (4.57 → 4.28s). Did NOT weaken
  the floor; re-cut the line to keep the script's staccato and join only the
  final pair ("…The right city, or the right path."), which restores the pauses
  and closes the list. Back to 4.571s. ~10 min.
- [defect] **`scla-loop` was half-empty for half its runtime** — caught on the
  precheck contact sheet, not by any checker: at scene-19's midpoint the ring
  was bare because every node waited for its spoken cue and this narration names
  the steps only in its second half. Empty numbered rings now enter with the
  track; gold fill + caption still land on the cue. ~15 min.

**Promoted to docs**

- `.claude/rules/video-production.md` — three new standing rules (geometry, the
  real text floor, join-don't-bolt), each naming its mechanism.
- `decisions/log.md` — "A gate must be able to fail."
- `frame.md` — `typography.min-size.body` 40 + the scale band, with the reason
  the old number was inert written next to it.
- `scla-loop.html` — the vertical geometry budget written as a comment beside
  the numbers it constrains, so the next editor sees why they are what they are.

**Standing gap left open (deliberate, not forgotten):** `check_geometry` reports
2 unplaced elements per build (a flex-row logo `<img>` sized only by height
makes its siblings' x unknowable). Reported, never guessed. Chips pills are also
not modelled. Both are visible in the gate's own output rather than silent.

## 2026-07-29 · owner rejection of `better-decisions` → five gates, and the cut rebuilt through them

Owner rejected the 2026-07-28 cut over six defects, several raised before. The
finding that reframed the session: **this was mostly not a missing-rules
problem.** Three of the five classes were already visible to tooling the
pipeline ran and passed, lost to a scope, a sampling and a severity error.
Worst of them, the conjunction rule was *disabled by the defect beside it* — a
seven-item list split across three scenes leaves runs of 2/2/2, never reaching
the >=3 threshold `check_copy` grades, so the rule the owner has given more
often than any other never fired. The missing "or" was also **already in the
approved script**; the renderer faithfully spoke bad copy.

The cut was rebuilt plan-first: 25 scenes -> 20, every gate green, rendered.

**Open — owner-actionable only**

- **2 scripts carry live `TODO: needs input`** *(since 2026-07-23)* —
  `m2_the-value-of-building-mid-career-momentum_2026-07-23`,
  `m3_discover-experiences-that-support-your-next-move_2026-07-23`.
- **`mini-syllabus` superseded Wistia copy `2ilh1o6c4g` still needs archiving**
  *(since 2026-07-21)* — token has no delete scope.
- **Confirm the on-screen program label** *(since 2026-07-28)* — eyebrow gated
  to "Career Accelerator"; visible on the rebuilt title card at preview.
- **Pilot sign-off (2026-07-29 cut)** — `bash scripts/preview.sh
  better-decisions-come-from-better-criteria_early-career-boost_2026-07-29`.
  Replaces the _2026-07-28 preview line; that cut was rejected and rebuilt.
- **16/32 refined scripts flag the conjunction check** — reported, not blocked,
  because a minority are rhetoric or definitions rather than lists. Worth a
  pass when there is appetite; each finding needs a human judgement.

**Fixed this session**

- [defect] **Conjunction rule graded per scene** — moved to the joined
  narration stream, attributed to the scene owning the final item. This alone
  was why "Mentorship? Growth?" shipped. ~20 min.
- [defect] **No gate on scene content weight** — new `check_continuity.py`:
  4.5s beat floor, split-sentence detection, enumerations spanning scenes.
  Calibrated on owner judgement (they rejected a 9-word "But…" clause and said
  nothing about a 24-word one, so length discriminates tail from beat). ~40 min.
- [defect] **Layout inspector sampled 9 points across the whole runtime and its
  `content_overlap` finding was severity `info`** — new `check_layout.py`
  samples every scene plus transition seams and treats overlap as fatal. Both
  owner layout complaints reproduce and now block. ~35 min.
- [defect] **No gate on copy fitting its box** — `check_capacity.py` +
  `textmetrics.py` measure real rendered width against committed font metrics
  (`assets/fonts/metrics.json`, <0.05px vs PIL). ~45 min.
- [defect] **Final narration clip got `gap = 0.0`** where every other scene got
  0.3s, so `narration.wav` ended 5ms after the last word's decay while the
  video held 1.1s past it — the owner heard the word cut off. Final clip is no
  longer tail-trimmed and gets `FINAL_HOLD`; `check_boundaries` gained
  `audio-tail-clipped`. Verified on the rebuild: 1.100s trailing, last 50ms
  peak 0. ~30 min.
- [tooling] **`frame.md` was 675 lines nothing read** — one regex-scraped table
  was its only parsed content; every normative number was hand-copied into
  Python under "keep in sync". `tokens.py` makes the frontmatter loaded truth
  and adds enforced `safe-area` / `footer-reserve` / `content-bottom`. ~25 min.
- [tooling] **Nothing ran the test suite** — not CI, and not `run_tests.py`,
  which ran its own 65 cases and silently skipped five sibling suites including
  the one pinning the variety thresholds. One command runs all 138 now;
  `lint-refs.sh` check 11 runs that command. ~15 min.
- [upstream] **CLI pin 34 versions stale** — bumped 0.7.45 -> 0.7.79 and
  validated with `npm run check`. Kept the pin deliberately: unpinned lets a
  batch start on one version and finish on another. ~10 min.
- [authoring] **Continuity and variety pulled against each other** — variety
  graded a form's share by scene COUNT, so a continuity merge looked like a
  regression. Share is graded in SECONDS now, making merges share-neutral by
  construction. Reference video still passes. ~15 min.
- [authoring] **No `map` icon existed** — owner asked for one on the compare
  beat; the canonical set had only `examine` (magnifier). Added to the ICONS
  map and both mirrors, plus `frame.md`. ~10 min.
- [authoring] **My own career-map fix violated the type floor** — dropped
  `.cm-role` to 30px against a 32px body floor; `check_text` caught it inside a
  minute. Widened the node to 360px at 34px instead. The guard hook also caught
  three real defects in my first scene plan (9-scene canvas run, a chip
  restating its heading, three icons past the reuse cap). ~15 min.

**Promoted to docs**

- `.claude/rules/video-production.md` — nine new standing rules, each naming its
  mechanism; STD-35 audit went 41 -> 59 backed claims, 0 broken.
- `.claude/skills/refine-scripts/SKILL.md` — new **step 3b**: the refiner now
  RUNS `check_copy.py` on its own output. The conjunction rule was already in
  that file as prose and was violated anyway; owner directive this session was
  to prevent upstream rather than catch downstream.
- `decisions/log.md` — 2026-07-29 entry on scope/sampling/severity, and on why
  the pin stays.
- `design-system/frame.md` — `spacing` block is now loaded, not quoted; `map`
  icon documented.

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
- New `render-qa/src/check_slots.py`, wired into `preflight.py` as check 8 — the
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

