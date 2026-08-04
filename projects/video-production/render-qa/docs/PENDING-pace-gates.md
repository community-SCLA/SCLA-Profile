# PENDING — the pace gates, and the recalibration the owner verdict forces

**Status:** measured and proven, **not applied** — every edit below lands in
`render-qa/src/` or `.claude/`, which `scripts/write-fence.sh` blocks. Needs a
session that exports `SCLA_SYSTEM_SESSION=1`. Same posture as
`PENDING-write-fence-fix.md`: the code is written and graded against real
builds, so the flagged session applies and commits rather than re-derives.

**Trigger:** owner verdict, 2026-08-04. Two freeform cuts of the same lesson.

| | `…_early-career-boost` (Jul 30–31) | `…_2026-08-04-freeform-backup` (Aug 4) |
| --- | --- | --- |
| Owner | **approved to ship** | **"SO boring"** |
| Gates | **QUARANTINED** by `verify_render` presence | **clean sweep**, preflight exit 0 |

The gate set approved the cut the owner rejected and blocked the cut the owner
approved. That is a calibration failure in both directions at once, and it is
not fixed by loosening — three of the four things that discriminate were not
being measured at all.

---

## 1. What actually separates the two cuts

Both followed the documented freeform sequence (`/render-lessons` → "Freeform
build sequence"). Same lesson, same script, same pinned voice, ~155s each. The
sequence's only quality instruction is step 2's "concept angle, one sentence
naming the single carrying visual idea" — ungraded prose. Both cuts wrote one.
The rejected cut's `design.md` then says out loud that it did not keep it:

> **Stated honestly:** the board is not literally on screen for the whole
> runtime. It is laid down, read twice in place, and then hands off.

Measured, not asserted:

| Metric | APPROVED | REJECTED | Discriminates? |
| --- | ---: | ---: | --- |
| beats | 26 | 17 | |
| **beats per minute** | **10.26** | **6.47** | **yes** |
| **median beat duration** | **5.15s** | **9.12s** | **yes** |
| longest beat | 12.87s | 15.02s | weak |
| **share of runtime in >8s beats** | **45%** | **79%** | **yes** |
| **mean inter-beat churn** | **3.34%** | **10.07%** | **yes — inverted** |
| twin-beat pairs (`check_diversity`) | 2 (8%) | 0 | **inverted** |
| longest static span under speech | 5.5s | ~3.75s | **inverted** |
| tween call sites | 37 | 13 | yes, but trivially gameable |

## 2. The finding that reverses a standing plan

**A prediction was made and refuted, and the refutation is the point.** The
expectation was that the boring cut would fail `check_presence` harder — longer
beats, less motion, therefore longer freezes. It was never rendered, so the
claim was tested directly: 22 stills on a 1.25s grid across its two longest
beats (s07, 15.0s; s15, 12.5s), graded with `check_diversity`'s own
`is_still()`. Its longest static span is **3.75s** — under `STAGNANT_FAIL`, and
shorter than anything the approved cut was quarantined for.

The rejected cut changes something every ~2.5s, draws a brand-new picture every
beat, and has **zero** twin pairs. **By every animacy measure this pipeline
owns, it is the healthier build.** It is boring anyway.

So the model the gate set encodes is wrong. Boring is not "the frame stopped
moving" and not "the beats look alike":

- **Boring is a new picture that then sits for 9–15 seconds.** The idea rate is
  what the viewer feels, and nothing graded it.
- **Good is a persistent system that re-sorts.** The approved cut's *low*
  inter-beat churn (3.34%) is the *signature of the carrying object* — one field
  of 48 marks, arriving in act 2 and thereafter only re-grouped. Its two twin
  pairs and its 5.5s holds are that same object being held still while the
  narration explains it.

**Consequence — `twin-beats` must NOT be armed.** `logs/snag-log.md` (2026-07-31)
has it waiting on "one approved freeform cut nominated as the reference". That
cut now exists, and it scores **worse** on `twin-beats` than the rejected one.
Arming it would push every future build toward the boring one. Retire the rule
on this lane, or invert it; do not pin it. Recorded here because the snag-log
entry reads as ready-to-arm and is not.

## 3. The four edits

### 3a. NEW — `render-qa/src/check_pace.py`

Move `render-qa/docs/check_pace.py` → `render-qa/src/check_pace.py` (its `RQ`
bootstrap already resolves `../src`; drop the two-line shim on the move).

Three rules, each threshold sitting in the gap between the two cuts with margin
on both sides — the calibration idiom `check_diversity` uses for
`FREEZE_MAXDIFF`:

| Rule | Constant | approved → **threshold** → rejected |
| --- | --- | --- |
| `beat-pace` | `MAX_MEDIAN_BEAT = 7.0` | 5.15s → **7.0** → 9.12s |
| `beat-pace` | `MIN_BEATS_PER_MIN = 8.0` | 10.26 → **8.0** → 6.47 |
| `long-beat-share` | `MAX_LONG_BEAT_SHARE = 0.60` | 45% → **60%** → 79% |
| `carrier-drift` | `MAX_MEAN_CHURN = 0.060` | 3.34% → **6.0%** → 10.07% |

`carrier-drift` is a **band**, not a ceiling: `FROZEN_MEAN_CHURN = 0.004` fails
a cut that is not carrying anything, so this file can never be read as licensing
a still image. The floor proper stays `check_presence`'s.

**Proven, not assumed** — run as-is today:

```
APPROVED: 26 beats / 152.11s — 10.26 bpm, median 5.15s, 45% long, churn 3.34%   PACE: PASS  (exit 0)
REJECTED: 17 beats / 157.54s —  6.47 bpm, median 9.12s, 79% long, churn 10.07%  PACE: FAIL (4) (exit 1)
```

All four findings on the rejected cut name the real defect and the real fix.

**Wiring:** `preflight.py`, freeform branch, as its own `pace` section — timing
rules in **`--static`** (the fix is re-splitting `audio_request.json`, which is
free before step 5 synthesis and costs a re-synthesis after), `--stills`
carrier-drift in the full gate beside `check_freeform_ink` over the same
`snapshots/` grid. Blocking, **not** advisory: STD-38's teach-first posture is
for unpinned taste numbers, and these are pinned to an approved build and a
rejected one. Advisory here would reproduce the exact failure — the boring cut
passed everything advisory and shipped to the gate clean.

Add a firing test `render-qa/tests/test_pace.py` (planted timing rows per rule)
and the three rule ids to `test_firing_coverage.py`.

### 3b. RECALIBRATE — `check_presence.STAGNANT_FAIL` 5.0 → 6.0

The quarantine that blocked the approved cut fired on spans of 5.0s, 5.5s and
5.5s. **The owner watched exactly those spans and approved the cut**, so a hard
floor at 5.0s is by definition below the owner's line. 6.0 clears the reference's
worst (5.5s) with 0.5s of margin and still fails the 7s+ dead hold nothing
defends. `STAGNANT_WARN` stays 3.0 — the 3–6s band remains a warning the human
judges.

This does **not** rescue the rejected cut (worst span 3.75s — already under the
old floor), so it cannot be mistaken for a general loosening. It moves one
number to match one owner verdict, and the pace gates in 3a are what replaces
the pressure.

`check_diversity` imports `STAGNANT_FAIL` and derives `MAX_SAMPLE_GAP =
STAGNANT_FAIL / 4.0`, so its grid relaxes 1.25s → 1.5s automatically. Its
calibration comment (lines 76–99) is written against `FAIL = 5.0` and must be
re-stated in the same commit, or it becomes a lie about the current constant.
`test_diversity.py` pins the derived gap — expect it to move.

### 3c. `.claude/skills/render-lessons/SKILL.md` — freeform sequence

The sequence is what both builders followed, so this is where the difference has
to be written down. Steps 2, 3 and 7:

- **Step 2 (`design.md`)** — the concept angle must name the carrying object
  **and the beat range it persists across**, and that range must cover ≥60% of
  the runtime. "Laid down, read twice, then hands off" is the rejected cut and
  is not a concept angle. Add: *if an element cannot be justified as another way
  of reading the same object, it does not exist* — the rejected cut wrote that
  rule in its own `design.md` and then broke it.
- **Step 3 (`audio_request.json`)** — state the pace target where the beats are
  authored: **~10 beats per minute** (a ~150s lesson is ~25 beats, not ~17), and
  run `check_pace.py --static` here, next to the existing `preflight --static`
  advice. This is the step where the fix is free.
- **Step 7 (snapshots)** — unchanged grid (one still per beat midpoint) now also
  feeds `carrier-drift`; say so, since it is currently described as ink-only.

### 3d. `.claude/rules/video-production.md` — mechanism lines

Add under **Motion** or a new **Pace** heading: *A lesson delivers roughly one
idea per six seconds, against a carrying object that persists.* Mechanism:
`render-qa/src/check_pace.py` via `preflight.py` (`--static` and full), pinned by
`render-qa/tests/test_pace.py`, calibrated against the owner-approved cut
`build-direction-before-you-build-a-plan_early-career-boost` (2026-07-31) and
the rejected `…_2026-08-04-freeform-backup`. Update the stagnation claim in
**How a gate must behave** to 6.0s, and the monotony bullet to record that
`twin-beats` is retired on this lane rather than awaiting a pin (§2).
`lint-refs.sh` check 10 audits these claims, so this lands in the same commit.

---

## 4. Shipping the approved cut — one blocker, and it is not a gate

With 3b applied the quarantine clears. Re-run today, the workspace is otherwise
clean: `boundaries`, `text`, `title_card`, `brand`, `forms`, `copy`,
`continuity`, `fit`, `stem` all PASS, and `motion` now passes — its
`/* motion-allow */` for `#bg-glow` existed but sat in a comment **above** the
`tl.fromTo(` call, where `check_motion` cannot see it. Moved inside the call
2026-08-04; it is a JS comment, so no rendered pixel changes and the MP4 stays
valid.

**`script_match` was the one remaining blocker. It is RESOLVED as of 2026-08-04
and needs no owner input.**

The Aug 4 session had edited the refined script to fix the four-question
conjunction run by joining it into one sentence ("engaged, capable, useful, or
proud of the outcome"), diffing the approved cut at 2.93% / longest miss run 4.
This doc previously framed the fix as a two-way owner call: revert to the July
wording, or re-synthesize and re-render.

**Both options were wrong, and the framing hid why.** The July *script* and the
approved *audio* were never the same string. The July build satisfied the
conjunction rule with a one-word edit in its own beat manifest (`Where` → `or`)
and never back-ported it to the script — that is exactly the
`logs/snag-log.md` 2026-07-30 entry "needs back-porting (or veto)". So option 1
would have left `script_match` failing on a different diff, and option 2 would
have re-cut a video the owner had already approved.

**What was actually done: the script was set to what the approved video says.**

> Where did you feel engaged? Where did you feel capable? Where did you feel
> useful, or did you feel proud of the outcome?

That is the back-port the snag log has been asking for since 2026-07-30. It costs
nothing and trades nothing away — measured, not asserted:

```
before:  375 script words vs 386 beat words — 2.93%, longest miss run 4   FAIL
after:   386 script words vs 386 beat words — 0.00%, longest miss run 0   ok
```

`preflight --static` on the workspace is now **PASS on every section**, `COPY`
included: the `or` satisfies the conjunction rule, so the doctrinal objection to
option 1 does not apply here. The MP4 is untouched. **Do not re-render it.**

With 3b applied, Track A is a filed and published lesson — subject only to
`WISTIA_API_TOKEN`, which was probed against the live vault on 2026-08-04 and is
**absent** from the `dev` environment (`with-secrets.sh` resolves `HEYGEN_API_KEY`
and nothing else). That is an infra action, not a code one.
