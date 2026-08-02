# HANDOFF — owner review → enforcement architecture, 2026-07-28 (evening)

Written for a session starting with **zero context**. Read this whole file
before touching the video pipeline. Supersedes the status claims in
`HANDOFF-autobatch-2026-07-28.md` (that file said the pilot was certified and
ready to ship; the owner then reviewed it and rejected it — see §2).

**Nothing in this session is committed.** `git status` shows ~20 modified and 7
new files. Decide commit vs. revert before doing anything else.

---

## 1. TL;DR — where things stand

The owner reviewed the certified pilot and rejected it on **naming plus four
quality grounds**. Every complaint traced to the same root cause: **the rules
existed as prose, or were actively contradicted, and nothing enforced them.**

This session did four things:

1. **Fixed the naming** — a stem now carries exactly one date meaning the most
   recent action, owned by a module, enforced at three points.
2. **Turned all four quality complaints into gates** — variety, copy, artwork,
   in-scene silence.
3. **Calibrated those gates against the owner's named reference video** — which
   caught that the first version of the variety gate *would have rejected the
   reference*.
4. **Built the meta-mechanism** (playbook STD-35): a CI check that makes it
   impossible for a doc to claim enforcement it doesn't have.

**The pilot build now FAILS preflight on 11 variety + 30 copy + in-scene-gap
findings.** It cannot ship as-is. It needs a rebuild. That rebuild has not been
started — it is the owner's call.

---

## 2. What the owner said, verbatim in substance

Reviewing `better-decisions-come-from-better-criteria_early-career-boost`:

**Two blocking gate questions asked up front** (with instructions to stop if
either answered "no"):

1. *Does the date in the name reflect when it was actually rendered?* →
   **NO.** The name carried `2026-07-06` (the script's refine date) after a
   `2026-07-28` render, with the HyperFrames CLI's own `_2026-07-28_18-49-26`
   suffix stacked on top of it.
2. *Was it rendered using v2 (the recent design updates)?* → **YES.** Workspace
   scaffolded 2026-07-28 15:55Z, after Motion v2 (`61467a9`, 2026-07-27); all
   twelve templates and `design-contract.md` byte-identical to design-system at HEAD,
   including the four follow-on fixes.

**Then five quality complaints:**

- Lists need "or"/"and" before the final item — *"slides 2 and 10 are good
  examples"* (e.g. "Mentorship? Growth?" → "Mentorship? **Or** growth?").
- Strange sound gaps in scenes 12 and 05, *"primarily between when the
  statement heading is spoken and when points are spoken… a major glitch or
  lag."*
- Slides that render the encircled point when there is only **one** point —
  *"Frame 15 and 11 are examples… you would never just render a single bullet
  point."*
- The encircled bullet is *"used too frequently, surely there are other
  illustrations we can swap in and out like an arrow pointing from one
  statement to another."*
- *"The WPM could increase, ever slightly."*
- Overall: *"still feels a bit boring, doesn't have a lot of visual variety, and
  feels a bit slow."*

**Two further owner directives, which shape everything below:**

- *"I have given preferences that, for whatever reason, have not been recorded
  down and not enforced"* — e.g. **statements should be Title Case**, given
  before and never applied.
- *"README is never used as a reference for the pipeline — that is for my
  reference… The reason is that it is not enforceable."* Then: *"How do we make
  these things enforceable?"*, then the observation that **`CLAUDE.md` and
  `design-contract.md` are equally unenforceable**, then the Repo Structure Playbook v1.1,
  then: *"I want them to be enforceable from the very beginning when the
  hyperframes are actually being rendered."*

Also, mid-session: *"If it fucks up all the scripts, don't worry about it. I'd
rather have things just run as they're supposed to run and forego my naming
convention."* — **This did not prove necessary. See §4.4; nothing broke, and no
`.txt` was renamed.**

---

## 3. Root-cause analysis — why each complaint happened

This is the most important section. Every single complaint was a **prose
failure**, not a capability failure.

| Complaint | Where the rule actually lived | Why it failed |
|---|---|---|
| No visual variety | `decisions/log.md` 2026-07-27 **only** | The Motion v2 variety rule ("max 2 consecutive, ≥5 distinct forms") was written into the decision log and **never reached `design-contract.md` or either skill**. Writing it down was treated as shipping it. |
| Title Case headings | `frame.md` (now `design-contract.md`) said the **opposite** | Line 381 read *"Sentence case for titles and body."* The pipeline was correctly following a rule that contradicted the owner. 0 of 17 headings were Title Case. |
| List conjunctions | `design-contract.md`, as the soft word *"prefer"* | The bullet **already contained the exact mentorship/growth example** the owner complained about. Advisory language, no gate. |
| Single circled point | Nowhere | Not 2 scenes but **5**: 06, 08 (`lines=1`) and 11, 13, 15 (`chips=1`). |
| Sound gaps | Nowhere | Not a pipeline bug — see §3.1. |
| Stale date in name | `lesson-scripts/README.md` | Which the owner had explicitly designated as *their* reference, not a pipeline authority. |

### 3.1 The sound gaps — diagnosed, counter-intuitive

**HeyGen's Oxana voice emits 0.98–1.26 s of real dead air at some in-scene
sentence boundaries, non-deterministically.** Decisive evidence — four
grammatically identical "Ordinal," constructions in one build:

| text | pause |
|---|---|
| `First,` → `define` | 0.480 s |
| `Second,` → `broaden` | 0.380 s |
| `Third,` → `compare` | 0.500 s |
| `Fourth,` → `notice` | **1.140 s** |

**3× variance on identical syntax.** No punctuation or re-wording can control
it. Verified against raw PCM with an independent energy scan (measured runs sit
0.06–0.12 s under the timestamp gaps — the timestamps are accurate; the silence
is genuinely in the provider's render). Across the file, **56.18 s of 159.29 s
(35.3%) is inter-word silence.**

Four hypotheses were tested and three falsified:

- ❌ per-scene lead silence too large — `LEAD` is 0.15 s, 1.3% of scene-12.
- ❌ 0.9 s question rule stacking — the constant is 0.45 s, evaluated once per
  scene on its final character; fired on 2 of 21 scenes, exactly as designed.
- ❌ duration padded to fit cues — boundary math is exact, zero slack.
- ✅ provider pauses — but **not** double-padded; mid-scene the pipeline adds
  precisely 0 ms.

**Why it read as "heading → points":** `compile_timeline.py:366` derives reveal
cues from those same word timestamps, so the pause propagates into the
animation. Picture and sound go dead together.

**Why the gate missed it:** `preflight.check_pacing()` scored scene-05 at 2.89 s
and scene-12 at 2.98 s — both under its 3.0 s WARN. It grades *visual event*
spacing and never opens `narration.words.json`. Nothing in `render-qa/`
inspected in-scene silence.

> ⚠️ **Doc discrepancy found:** `decisions/log.md` (2026-07-13 entry) describes
> silence insertion as *"0.6s air + 0.15s lead, 0.9s after questions."* The
> code, `design-contract.md`, and `render-qa/README.md` all say **0.3 / 0.15 / 0.45**. The
> 0.6/0.9 numbers exist nowhere in the codebase. The log entry is historical and
> was left untouched, but do not trust it.

---

## 4. What changed — complete inventory

### 4.1 New files (7)

| File | What it is |
|---|---|
| `render-qa/src/stem.py` | **Sole owner** of stem naming. `split`/`base`/`date`/`restamp`/`normalize`/`is_canonical`. `restamp` refuses a malformed name; `normalize` is the one lenient path, for renderer output only. |
| `render-qa/src/check_variety.py` | The variety gate. 5 rules — one-item lists, max-consecutive (with exemption), distinct forms, max share, artwork coverage. |
| `render-qa/src/check_copy.py` | The copy gate. Title Case headings, no terminal period, list conjunctions in narration. |
| `render-qa/tests/test_stem.py` | Fixture tests for the one-date rule, incl. the identity invariant `published.tsv` depends on. |
| `render-qa/tests/test_variety.py` | **Calibration tests.** Pins thresholds to the two real videos; asserts reference PASSES, rejected FAILS, exemption is earned. |
| `scripts/check-enforcement.py` | Playbook **STD-35** audit. See §5. |
| `scripts/hyperframe-guard.sh` | Build-time enforcement. Runs the gates on every `index.html` write, via a `PostToolUse` hook. |

### 4.2 Modified files (~17)

**Naming mechanism:**
- `scripts/batch-ship.sh` — `stem_base`/`stem_restamp`/`stem_norm` helpers;
  normalizes `renders/*.mp4` **before** `verify_render.py` pins the path+sha in
  `qa/VERIFIED`; `FILED` via `stem.py` not `${STEM%_*}`; `rendered/` script
  restamped to the render date; `published.tsv` written with **base** in col 1;
  ledger matcher now keys on title prefix **alone** (it matched prefix+date,
  which would have appended a duplicate row on every publish once dates moved).
- `scripts/batch-prepare.sh` — BUILD-KIT now tells builders to name the
  workspace with the **build** date via `stem.py restamp`, and to report the
  workspace stem, not the script stem.
- `scripts/batch-status.sh` — imports `stem.py`; resolves published/workspace
  lookups by base; new `ws_by_base` index (a workspace can no longer be found by
  joining the script's stem to a path).
- `lesson-scripts/published.tsv` — 6 rows migrated, col 1 header `stem` → `base`.
- `render-qa/src/preflight.py` — `locate_script()` now matches by base **(see §4.4 —
  this was a silent-failure bug)**; new sections 10 (variety), 11 (copy), 12
  (stem).

**Audio / narration:**
- `render-qa/src/synth_narration.py` — new `MAX_INSCENE_GAP = 0.5`,
  `INSCENE_FADE = 0.008`, `_fade_edges()`, `compress_gaps()`. Excises the
  **middle** of an over-cap pause (neither word's edge moves), applies an 8 ms
  declick, shifts subsequent timestamps by the cumulative removal. Runs
  **before** `trim_clip`. HeyGen path only (needs word timestamps). New
  `--max-gap`; manifest gains `max_inscene_gap`/`gap_trimmed`. **Speed 0.95 →
  1.0.**
- `render-qa/src/preflight.py` — section 9, `check_inscene_gaps()`,
  `INSCENE_GAP_FAIL = 0.8`. Reads the **whole-file** `narration.words.json`, not
  the per-scene files (those are the provider's untouched response and still
  contain the excised pauses — they'd fail forever). Buckets by
  `scene-times.json` to exclude deliberate boundary air.
- `design-system/docs/design-contract.md` + `AGENTS.md` — `speed: 0.95` → `1.0` in frontmatter
  and prose (kept in sync so a future agent can't pass `--speed 0.95` and undo
  the owner's change).

**Rules and docs:**
- `design-system/docs/design-contract.md` — **"Sentence case for titles and body" removed** and
  replaced with the Title Case rule; new **"Variety contract"** section; list
  conjunction promoted from *prefer* to normative + gated; new in-scene silence
  rule; artwork coverage rule.
- `.claude/rules/video-production.md` — two new rules: the one-date stem rule,
  and the standing-preferences rule (naming its gates and the build-time hook).
- `.claude/rules/repo-hygiene.md` — new **STD-35** rule.
- `.claude/skills/refine-scripts/SKILL.md` — conjunction rule as a MUST; the
  ~14-word sentence rule (decided 2026-07-27, never written down).
- `.claude/skills/render-lessons/SKILL.md` — variety + Title Case brief **inside
  the `BUILD-KIT` markers** (that block is extracted verbatim into
  `_run/BUILD-KIT.md` for cold build subagents — it is the highest-leverage
  place); stem naming in the build sequence.
- `scripts/lint-refs.sh` — renumbered to `/10`, new check 10.
- `.claude/settings.json` — new `Write|Edit` PostToolUse hook.
- `decisions/log.md` — new entry at top (append-at-top is the convention).
- `render-qa/README.md`, `render-qa/tests/run_tests.py` (+32 tests).

### 4.3 On-disk changes (not git-tracked)

- Workspace renamed `..._2026-07-06` → **`..._2026-07-28`**.
- MP4 renamed to `better-decisions-come-from-better-criteria_early-career-boost_2026-07-28.mp4`
  (was `..._2026-07-06_2026-07-28_18-49-26.mp4`).
- `qa/VERIFIED` repointed to the new path; **sha-256 re-verified as matching**.
- **No `.txt` script was renamed.** `git status` on `lesson-scripts/` shows only
  `published.tsv`.

### 4.4 ⚠️ The near-miss you must know about

`preflight.locate_script()` built its filename as `f"{ws.name}.txt"` — an exact
match on the workspace directory name. Once workspaces carry the **build** date
and scripts carry the **refine** date, that lookup returns `None`. And
`check_script_match`'s missing-script branch is a **WARN-and-skip that returns
`pass: True`**.

So the naming change would have **silently disarmed the script-fidelity gate —
the primary mechanism behind the fabrication ban** — on every future build,
while still printing a green preflight. It now resolves by base (exact match
first, then base match). Verified: `script_match` **PASSES** with a `2026-07-28`
workspace against a `2026-07-06` script.

**Generalise this.** Anything that joins a stem to a path is now suspect. Audit
before adding new ones.

### 4.5 Memory (outside the repo)

`~/.claude/projects/-workspaces-SCLA-Profile/memory/` gained
`owner-preferences-must-become-gates.md` and `lesson-stem-one-date-rule.md`,
both indexed in `MEMORY.md`.

---

## 5. The enforcement architecture (playbook STD-35)

The owner supplied **The Repo Structure Playbook v1.1**. STD-35 (MUST):

> A written rule is a request; only a mechanism — a hook, a CI check, a lint,
> branch protection — is a guarantee. **How to check:** list every
> "always/never" sentence; for each, name the mechanism — or the gap.

**The conclusion reached, and worth restating to the owner:** you cannot make a
document enforceable. You can only make it **small** — shrink it until
everything load-bearing has moved into code — and make it **unable to lie**
about being enforced.

Enforcement now exists at three levels:

| Level | Mechanism | Fires when | Blocks? |
|---|---|---|---|
| **Authoring** | `scripts/hyperframe-guard.sh` via `PostToolUse` hook on Write/Edit | the builder writes `index.html` | No — reports (a half-written file mid-authoring is normal) |
| **Pre-render** | `preflight.py` sections 9–12 | before any render | **Yes** — `batch-ship.sh` quarantines |
| **Repo/CI** | `check-enforcement.py` as `lint-refs.sh` check 10 | every push | **Yes** on a broken claim |

`check-enforcement.py` splits findings deliberately:

- **BROKEN CLAIM → exit 1.** A doc names a mechanism that doesn't exist, or a
  checker **nothing invokes**. This is the dangerous case: a reader trusts it and
  skips the manual check. False safety is worse than none.
- **UNBACKED RULE → report only.** A normative sentence with no mechanism and no
  honest `Convention` label. Non-blocking per **STD-38** ("non-blocking at
  first, so it teaches instead of nags") and because the playbook warns that
  hardening a guideline into a hard rule is itself a defect.

**First run found 5 broken claims — four of them written earlier in this same
session** (`*(Gate: rule 1 — hard fail.)*` promised a gate but named no file),
plus a nested-paren bug in its own parser. **Current state: 40 backed, 0 broken,
31 unbacked.**

> **The 31 unbacked rules are a real, honest gap inventory** — e.g. `CLAUDE.md`
> "Never re-read a file already read this session", `design-contract.md` "Boundaries land
> on sentence ends". These are the next candidates for mechanisation, or for
> honest `Convention` labels. Run `python3 scripts/check-enforcement.py --json`
> for the full list. This is a good agenda item for the next session.

---

## 6. The reference video — measured, and it changed the gate

The owner supplied `https://sclc.wistia.com/s/u99h9iia509hd7y` as the look to
recreate. It resolves to **`what-makes-for-a-dream-job_early-career-boost`**
(Wistia `gryylc7qns`, 187.5 s, published 2026-07-17).

Two immediate observations:
- Its published name **already carries the render date** — `batch-ship.sh`'s
  restamp was working correctly at publish. The naming break was only ever
  *upstream* of ship.
- It was rendered **ten days before Motion v2**. The look the owner wants back
  **predates** the overhaul meant to make videos less boring.

Its workspace was pruned post-publish and is gitignored, so the MP4 was
downloaded and 31 frames extracted at 6 s intervals.

> **Ephemeral:** the download and frames live in this session's scratchpad
> (`/tmp/claude-1000/.../scratchpad/dreamjob.mp4`, `ref/f001–f031.jpg`) and
> **will not survive**. Re-fetch via
> `curl -sL https://fast.wistia.net/embed/medias/gryylc7qns.json` → `assets[]`.

### Measured comparison

| | reference (must PASS) | rejected (must FAIL) |
|---|---|---|
| runtime / content scenes | 187.5 s / 14 | 160.4 s / 19 |
| template families | **7** | 4 |
| peak single-form share | **36%** (condition 5/14) | 42% (statement 8/19) |
| scenes carrying artwork | **79%** | 33% |
| distinct artwork assets | ~11 | 6 (compass used twice) |
| longest same-family run | 5 (earns exemption) | 3 (does not) |
| seconds per visual state | 5.1 s | 4.2 s |

### 🔑 Two findings that changed conclusions

**1. The first version of the variety gate would have REJECTED the reference.**
Its best passage is five consecutive `scla-condition` scenes — which works
because each advances a 5-dot stepper, carries its own artwork, and lasts ~6 s.
A gate that rejects the bar is a broken gate. Hence the exemption (§7).

**2. The rejected build is NOT actually slower.** 4.2 s per visual state vs the
reference's 5.1 s — it changes state *more* often. An earlier framing in this
session ("feels slow" = timing) was wrong. It feels slow because **every change
is the same change** — another line of text in the same column of the same
layout — and because ~45% of the canvas is empty on nearly every scene. The
reference changes *what kind of object you are looking at*: a real bar chart
with axes and growing bars, figure glyphs mirrored and recoloured, red
strike-throughs annotating live text, cards that physically demote and slide.

---

## 7. The gates, precisely

### `check_variety.py`

| Rule | Threshold | Notes |
|---|---|---|
| 1 — no one-item list | list slot must be 0 or ≥2 | 0 = correctly blanked (`check_slots.py`'s job) |
| 2 — max consecutive | 2, extendable to **6** | Exemption requires **all three**: advancing progress indicator (`num`/`total`/`step`), distinct artwork per scene (no reuse inside the run), each ≤7 s |
| 3 — distinct forms | ≥4 (<90 s), **≥6** (≥90 s), **≥7** (≥150 s) | raised from 5; reference has 7 |
| 4 — max form share | **40%** | **Do not tighten** — reference peaks at 36% |
| 5 — artwork | ≥60% coverage, ≥5 distinct assets, ≤2 uses each, ≤2 consecutive bare | **New.** Largest measured gap; previously ungated entirely |

Artwork is detected from non-empty `icon`/`icons` slots.

### `check_copy.py`

- Headings (`heading`/`statement`/`title`): Title Case, no terminal period
  (`?`/`!` fine). Acronyms preserved (AI, SCLA); hyphenated compounds
  capitalised per part; minor words lowercase unless first/last.
- Narration enumerations of ≥3 items need `and`/`or` before the final item.
  Two detectors: runs of ≥3 short fragments, and comma lists of ≥3.
  **Tuned to avoid false positives:** the comma detector skips sentences
  containing quotes and any part >6 words — without that, clause commas
  ("someone thinks, "I already put so much time into this, I cannot change
  now," even when…") and quoted speech both tripped it. After tuning it flags
  exactly scenes **2 and 10** — the owner's two named examples.

### Current verdict on the pilot build

`VARIETY: FAIL (11)` · `COPY: FAIL (30)` · `inscene_gaps: FAIL` · everything
else PASS, including `stem` and `script_match`.

---

## 8. Verify everything (copy-paste)

```bash
cd /workspaces/SCLA-Profile
bash scripts/lint-refs.sh                                   # → healthy, check 10 = 0 broken
python3 scripts/check-enforcement.py                        # → 40 backed, 0 broken, 31 unbacked
python3 projects/video-production/render-qa/tests/run_tests.py        # → 65 passed
python3 projects/video-production/render-qa/tests/test_stem.py        # → all pass
python3 projects/video-production/render-qa/tests/test_variety.py     # → reference PASSES, rejected FAILS
python3 projects/video-production/render-qa/tests/test_script_match.py # → 28 passed
bash projects/video-production/render-qa/tests/test_retro_hook.sh     # → 4/4 (run from repo root)
bash scripts/batch-status.sh                                # → 29 to build, 1 built-unpublished, 6 on Wistia

WS=projects/video-production/renders-hyperframes/better-decisions-come-from-better-criteria_early-career-boost_2026-07-28
python3 projects/video-production/render-qa/src/preflight.py $WS   # → FAIL on 9/10/11 only
bash scripts/hyperframe-guard.sh $WS/index.html                # → the build-time view
```

---

## 9. What is NOT done — open items for the next session

1. **The rebuild.** The pilot fails 3 gate families. It needs re-authoring
   against the new contract (more forms, more artwork, Title Case headings,
   conjunctions in scenes 2 and 10, no one-item lists, re-synth for the 0.5 s
   cap + 1.0 speed). **Not started — owner's call.** Note the whole 29-video
   queue sits behind the PILOT GATE.
2. **Nothing is committed.**
3. **The 31 unbacked rules** (§5) — mechanise or honestly label.
4. **Two gates recommended by the frame analysis but NOT built**, because they
   can't be detected reliably from `index.html` alone:
   - **Composition gate** — ≥25% of content scenes should place content in two
     spatially separate regions (reference ~35%; rejected **0%**). This was
     assessed as the single most visible difference. Needs a region model.
   - **Theme-block cap** — ≤6 consecutive scenes / ≤65 s on one background
     canvas. The rejected build runs **9 consecutive light scenes over 78.3 s**.
     Needs a template→canvas map (light vs navy), which is derivable from
     template CSS but was judged too fragile to guess at.
5. **`HANDOFF-autobatch-2026-07-28.md` was stale** — it asserted the pilot was
   certified and ready to ship and pointed at the old workspace path. A
   correction banner was added; the body still describes the pre-review state
   as history.
6. **`decisions/log.md`'s 0.6/0.9 silence numbers are wrong** (§3.1) — left as
   historical record, do not trust.

---

## 10. Doctrine to carry forward

The owner's standing instruction, and the thing most likely to be forgotten:

> **A preference is not real until it is a checker.** If it can be mechanised,
> it goes in `render-qa/` and gets wired into `preflight.py` *and* the authoring
> hook. If it cannot, it gets labelled **Convention** out loud. It never goes in
> `decisions/log.md` alone, never in a README, and never as the word "prefer".

And its corollary, learned the hard way this session: **a gate calibrated
without a reference is a guess.** Every threshold in `check_variety.py` is
pinned by `test_variety.py` to a video the owner actually approved. Change a
threshold, and that test tells you whether you just broke the bar.

## Playbook
## How to read this

**Every rule has a tier:**

| Tier | What it means |
|---|---|
| **MUST** | Always applies. A violation is a finding — no judgment call needed. |
| **SHOULD** | Applies unless the repo records a deliberate reason it doesn't. An undocumented violation is a finding. |
| **TARGET** | A number to aim for, not a law. The audit reports the distance, not a violation. |

An audit (or a red team) may never present a SHOULD or a TARGET as a MUST. Hardening a
guideline into a hard rule is itself a defect.

**Every rule has a stable ID** — STD-1 through STD-43. IDs are never renumbered or
reused; a retired rule keeps its number and gets marked retired. Briefs, red-team
reports, and commit messages all cite these IDs.

**Every rule has a source tag** (key in Appendix 1). `A-*` tags are Anthropic's official
Claude Code docs; `O-*` tags are the AGENTS.md open spec and OpenAI's Codex docs; `UNIV`
means a universal software-craft convention no single page owns. Universal doesn't mean
optional — it means everybody's.

---

## The one-glance picture

What a repo looks like when every rule below is satisfied:

```
your-repo/                          ── root: doors + required files, ≤ 12 items ──
├── README.md ............ 👤 the human's door — what this is, where things live
├── AGENTS.md ............ 🤖 the agent's door — one canonical file, whatever your
│                              tool names it (see the routing table)
├── LICENSE, .gitignore .. ⚙️ standard project files tools expect at root
├── config/ .............. ⚙️ machine-readable settings — the single source of truth
├── docs/ ................ 👤 read-once material: setup notes, design history
├── src/  (or projects/, tasks/) ── the actual work, every unit the same shape:
│   └── one-unit/
│       ├── README.md .... 👤 its human door — always, once it holds 4+ files
│       ├── AGENTS.md .... 🤖 its agent door — only if an agent works here often
│       ├── run.sh ....... ⚙️ its machine door (only if something runs on its own)
│       ├── src/ ......... the code
│       ├── config/ ...... its settings
│       ├── docs/ ........ its read-once notes
│       └── logs/ ........ run output — gitignored, rotated
├── _templates/ .......... 📁 a blank copy of that shape — new work born tidy
├── _archive/ ............ ⛔ retired work — never deleted, never in the way
└── .claude/ · .codex/ ·  ⚙️ your AI tool's own folder — settings, skills, rules,
    .cursor/ · .gemini/       hooks, in its standard locations, discovered
                              natively. One row of the routing table, not all of them.
```

Both doors, at both levels: a unit gets a README once it holds 4+ files or any
subfolder (STD-4), and its own agent file only if an agent regularly works inside it
(STD-4, STD-5). A unit nobody's agent touches needs no agent door.

**And when a unit runs on a schedule** — same shape, plus the four things "unattended"
demands. A scheduled task is where a missing door costs the most, because nobody is
watching when it fails:

```
tasks/nightly-sync/            ── the standard shape, plus what running alone requires ──
├── README.md ......... 👤 what it does, WHEN it runs, and who hears about it breaking
├── AGENTS.md ......... 🤖 only if an agent works in here                      (STD-4)
├── run.sh ............ ⚙️ the ONE machine door — the scheduler calls this,    (STD-6)
│                          never a command pasted into a doc or a crontab line
├── config/
│   ├── schedule.json . ⚙️ when it runs, machine-readable, one copy only  (STD-19/20)
│   └── alerts.json ... ⚙️ where failure goes — the repo's one channel   (STD-36/37)
├── src/ .............. the code the door calls
├── docs/ ............. read-once: design notes, and the runbook for when it breaks
├── state/ ............ last-run marker, cursor, checkpoint — gitignored    (STD-41)
└── logs/ ............. run output — gitignored, rotated                    (STD-41)

  ⚠️ the schedule ALSO lives wherever the scheduler actually reads it — crontab,
     launchd plist, .github/workflows/*.yml, a cloud scheduler. That's the copy that
     runs. The repo's config/ copy must match it, or one of them is lying    (STD-20)
  ⚠️ "it failed at 3am and nobody found out" is not a small problem — it is the
     definition of already broken                                        (STD-36/37)
```

Nothing here is a new rule. It's the same unit shape with the four scheduled-work
answers made visible: what starts it, when it runs, where it keeps state, and who hears
the alarm.

---

## §A — The doors (entry points)

Every folder that matters has an entry point for each kind of visitor: a human door
(README), an agent door (CLAUDE.md / AGENTS.md), and — only where something runs on its
own — a machine door (run.sh). A folder full of loose files with no "start here" isn't
failing you; it has no doors. **When a door is missing, the fix is to create it.**

| ID · Tier | Rule | Why it exists | How to check | Src |
|---|---|---|---|---|
| **STD-1** · MUST | The root has a human door: a `README.md` that says what this repo is, how it's organized, and where to start. | It's the first thing any person sees; without it every visitor starts lost. | Root README exists, is more than a stub, and its claims are true. | O-spec, UNIV |
| **STD-2** · SHOULD | If an AI assistant works in this repo, the root has one agent door: `CLAUDE.md` (Claude Code) or `AGENTS.md` (Codex, Cursor, Gemini CLI, and most others). | It's the one file the agent reads before doing anything; without it every session re-derives the basics. | The file exists at root and its contents follow STD-12 through STD-18. | A-mem, O-spec |
| **STD-3** · MUST | One canonical agent file. If two tool names are needed, one imports or symlinks the other (a `CLAUDE.md` containing `@AGENTS.md`, or a symlink) — never two files maintained by hand. | Two hand-maintained copies always diverge, and each tool then reads a different truth. | If both names exist, one must be an import stub or symlink. Diff them. | A-mem, O-spec |
| **STD-4** · SHOULD | Every unit of work (a project, task, app, or package folder) has the doors its visitors need: a README hub once it holds 4+ files or any subfolder, and its own agent file if an agent regularly works there. Missing doors get created, not wished for. | A folder with twelve loose files and no "start here" makes every visit an excavation. | List unit folders; for each, note which doors exist and which are missing. | UNIV |
| **STD-5** · SHOULD | Big repos layer agent files: a small root file for repo-wide rules, plus per-area files that load only when working in that area. The file nearest the work wins. | One giant root file either costs context on every message or stays too generic to help anyone. | If the root agent file exceeds its target size and carries area-specific detail, layering is overdue. | A-large, O-guide |
| **STD-6** · SHOULD | Anything that runs on its own has one obvious machine door — a `run.sh`, Makefile target, or package script — not a command buried in prose. | "How do I run this" should never require reading a doc. | For each automation, the start command is a file or target, not a sentence. | UNIV |

---

## §B — The root

The top level is the most expensive room in the house: every human scans it every time,
and the agent's root file is read on every message. It holds doors, required files, and
almost nothing else.

| ID · Tier | Rule | Why it exists | How to check | Src |
|---|---|---|---|---|
| **STD-7** · MUST | The root holds only: doors (STD-1/2), standard project files tools require at root (LICENSE, `.gitignore`, dependency manifests, CI and tool configs), and at most 2–3 small repo-wide lookup files. Everything else lives one level down in a named folder. | The root is a map; every extra item is noise on the map. | List every root item; each must fit one of the three categories or get a filing destination. | UNIV |
| **STD-8** · TARGET | 12 or fewer visible items at root (files + folders, dotfiles excluded). Over 20 is failing regardless of what the items are. | A root you can't read in one glance stops being a map. | Count. Don't estimate. | UNIV |
| **STD-9** · MUST | Every root markdown file other than the doors passes all four tests: repo-wide in scope, small, currently true, and actually read by someone or something. Failing any one, it moves — into `docs/`, or into the folder it describes. | Root markdown nobody reads is where drift breeds. A doc about X belongs with X. | For each root `.md`: who or what consumes it? Is it current? Is it repo-wide? | UNIV |
| **STD-10** · SHOULD | Dated output — audit briefs, reports, exports — is filed in its dated home (`audits/`, `reports/`) the day it's made. It never lives loose at root. | Yesterday's report at root is today's clutter and next month's false claim. | Any date-named file sitting at root is a finding. | UNIV |
| **STD-11** · MUST | No junk at root: caches, temp files, test dumps, and tool droppings are gitignored, and removed or archived. | Junk at the front door teaches everyone to stop looking at the front door. | Every root item is either purposeful or a finding. | UNIV |

---

## §C — The agent file (what's inside the agent door)

The agent file is re-read constantly — in most tools, on every message. Every line is
paid for over and over, and every line is trusted completely. So it holds only durable,
true facts; everything else lives elsewhere and gets pointed to.

| ID · Tier | Rule | Why it exists | How to check | Src |
|---|---|---|---|---|
| **STD-12** · SHOULD | Contents are durable facts the agent needs every session: what the repo is, where things live, build/run/test commands, conventions, hard boundaries ("never touch X"), and what "done" means. | This is the expensive real estate; only always-true, always-needed facts earn a spot. | Read each line: is it a fact needed every session? | A-mem, O-best |
| **STD-13** · SHOULD | Multi-step procedures and sometimes-needed reference live outside the agent file — in skills, path-scoped rules, or linked task docs it points to — never inline. | A procedure in the agent file costs context on every message; in a skill it costs nothing until used. | Any numbered how-to inside the agent file is a finding. | A-skill, O-best |
| **STD-14** · TARGET | Keep each agent file short — under roughly 200 lines (Anthropic's target; Codex enforces a hard 32 KiB cap on the combined file chain). Short and accurate beats long and vague. | Long files load in full anyway, and agents follow shorter files better. | `wc -l` on every agent file. | A-mem, O-guide |
| **STD-15** · MUST | The agent file contains no hand-copied directory trees, no changelogs, no full API documentation, and no aspirational rules nobody actually follows. | The file tree already shows the tree; hand copies go stale the day something moves. | Scan for tree diagrams, history sections, and rules contradicted by practice. | A-supp, A-mem |
| **STD-16** · MUST | Every line of every agent file is true right now, and gets re-checked whenever the structure changes. | The agent trusts this file completely; one false line poisons every future session. | Verify each factual claim against the filesystem. | A-supp, UNIV |
| **STD-17** · SHOULD | Grow the agent file incrementally: start minimal, add a rule only after a repeated mistake, and when the agent gets something wrong, fix the file so the correction persists. | Rules added "just in case" are exactly the ones that turn aspirational. | Practice, not filesystem state — advisory. | O-best, O-custom |
| **STD-18** · SHOULD | Skills, rules, subagents, and hooks live in the tool's standard discovery locations (`.claude/skills/`, `.claude/rules/`, `.claude/agents/`, or the tool's equivalent). No hand-maintained list duplicating what the tool discovers on its own. | Hand lists rot; native discovery can't. | Are extensions in standard paths? Does any file list them by hand? | A-skill, A-mem |

---

## §D — Configuration as code

If a machine, a script, or a prompt consumes a value, that value lives in a
machine-readable file — JSON, YAML, or TOML — exactly once. Prose describes; config
defines. A markdown file holding endpoints is a note wearing a config's clothes.

| ID · Tier | Rule | Why it exists | How to check | Src |
|---|---|---|---|---|
| **STD-19** · MUST | Values that machines or prompts consume — endpoints, IDs, schedules, paths, lists, thresholds — live in machine-readable files (JSON, YAML, or TOML), not in prose. | Prose can't be parsed, validated, or trusted by a script; it can only be believed. | Find automations or prompts reading values out of `.md` files or holding them inline. | UNIV |
| **STD-20** · MUST | One source of truth per value. The same endpoint, ID, or list is never maintained in two places; docs point at the config file and never restate its contents. | Two copies of a value will disagree — the only question is when. | Grep a few signature values across the repo; every duplicate is a finding. | UNIV |
| **STD-21** · SHOULD | A constant repeated in two or more scripts is hoisted into one shared config file they all read. | Changing it in three places means forgetting it in one. | Search for repeated literals across scripts. | UNIV |
| **STD-22** · SHOULD | Every config file is consumed by something that would notice if it broke — code loads it, a schema validates it, or a check parses it. A config file nothing reads gets fixed or archived. | An unread config is drift with a `.json` extension. | For each config file, name its consumer. | UNIV |
| **STD-23** · SHOULD | Prose and settings split cleanly: durable guidance lives in the agent file; tool and runtime settings live in the tool's config file (`.claude/settings.json`, `.codex/config.toml`). Neither does the other's job. | Mixing them means neither the human nor the tool can trust either. | Settings values in prose files, or paragraphs of guidance inside settings files. | O-best, A-large |

---

## §E — Docs that stay true

A false doc is worse than no doc, because it's trusted precisely for being written down.
The cure is fewer hand-written claims: generate what's derivable, file what's read-once,
archive what's retired — and verify what remains.

| ID · Tier | Rule | Why it exists | How to check | Src |
|---|---|---|---|---|
| **STD-24** · MUST | Every claim in a hand-written doc is checkable against the filesystem — and currently true. | Readers (human and AI) act on false docs with full confidence. | Verify claims; every false one is a finding. | A-supp, UNIV |
| **STD-25** · SHOULD | Anything derivable from the filesystem — indexes, inventories, file counts, status tables — is generated by a script, or dropped. Never maintained by hand. | Hand-maintained mirrors of reality go false the moment reality moves. | Find docs restating what a command could produce. | A-mem, UNIV |
| **STD-26** · SHOULD | Read-once material — setup notes, design history, how-it-works — lives in a `docs/` folder (the repo's, or the unit's), not at root and not mixed in with code. | Reference material belongs on a shelf, not on the workbench. | `.md` files loose among code files, or piled at root. | UNIV |
| **STD-27** · SHOULD | Retired work is archived to one agreed place (`_archive/` at the root, or per-unit), never hard-deleted — and archives stay out of everyday paths and searches. | Deletion destroys the option to have been wrong; a good archive is a safety net that stays out of the way. | Is there one archive convention? Are stale archives sitting inside working folders? | UNIV |

---

## §F — One shape for every room

Sameness is the entire point. When every unit of work shares one internal shape, opening
any folder means already knowing where to look — and a template means new work is born
tidy instead of fixed later.

| ID · Tier | Rule | Why it exists | How to check | Src |
|---|---|---|---|---|
| **STD-28** · SHOULD | All units of work share one internal shape: doors on top, then code (`src/`), settings (`config/`), read-once docs (`docs/`), and run output (`logs/`) each in their own folder — or your documented equivalent, applied everywhere. | Ten folders in ten shapes is the "I can never find anything" feeling, made of folders. | Compare unit folders; count how many distinct shapes are in use. | UNIV |
| **STD-29** · MUST | Code, config, docs, and logs don't sit mixed in one flat folder once a unit passes ~8 files. | Flat heaps are where logs bury code and docs go to die. | Find flat folders mixing file types. | UNIV |
| **STD-30** · SHOULD | A blank template of the standard shape exists, and new units start as a copy of it. | Tidiness you have to remember is tidiness that decays; a template makes it the default. | Does `_templates/` (or equivalent) exist, and does it match the real convention? | UNIV |

---

## §G — Names and depth

Good names sort themselves, search themselves, and say what a thing is. Good depth means
a path you can say out loud from memory.

| ID · Tier | Rule | Why it exists | How to check | Src |
|---|---|---|---|---|
| **STD-31** · SHOULD | Names are lowercase with hyphens (kebab-case), no spaces — one style per folder, applied consistently. | Mixed styles break sorting, and spaces break scripts. | Look for mixed styles inside one folder. | UNIV |
| **STD-32** · SHOULD | Dated files put the date first — `YYYY-MM-DD` — so they sort themselves in every file browser. | Date-first is the only format that alphabetizes into chronology for free. | Dated files with the date elsewhere, or missing. | UNIV |
| **STD-33** · TARGET | Working files sit within 4 folder levels of the root. Deeper means the structure wants flattening. (Vendored and generated trees are exempt.) | If you can't say the path from memory, neither can anyone else — including the agent. | Find files at depth 5+, excluding vendored paths. | UNIV |
| **STD-34** · SHOULD | A name says what the thing is, specifically enough to search for: no `final-v2`, no `misc`, no `untitled`, no `new-new`. | A name you can't grep for is a file you'll re-create instead of find. | Scan for filler names. | UNIV |

---

## §H — Locks, not notes (enforcement & automation health)

A written rule is a request. Only a mechanism — a hook, a CI check, branch protection —
is a guarantee. And anything that runs unattended must be able to tell a human it broke,
or it's already broken.

| ID · Tier | Rule | Why it exists | How to check | Src |
|---|---|---|---|---|
| **STD-35** · MUST | A written rule is a request; only a mechanism — a hook, a CI check, a lint, branch protection — is a guarantee. Any rule that must hold every single time is enforced by a mechanism, not a sentence. | A sentence can be missed, forgotten, or skipped. A lock can't be talked past. | List every "always/never" sentence; for each, name the mechanism — or the gap. | A-feat, A-hook |
| **STD-36** · MUST | Every automation that runs unattended can report its own failure to a human. If it failed right now and nobody would find out, it is already broken. | Silent failure means the audit finds out months later — instead of you, the same day. | For each scheduled thing: how would a human learn of failure, and how fast? | UNIV |
| **STD-37** · SHOULD | All failure alerts funnel to one channel — and the alarm has been tested at least once by breaking something on purpose. | Alerts scattered across three apps get ignored in all three; an alarm never heard firing is a hope. | Count alert destinations; ask when the alarm last actually fired. | UNIV |
| **STD-38** · SHOULD | The repo runs a recurring drift check — links resolve, doc claims match the filesystem, configs parse — non-blocking at first, so it teaches instead of nags. | Drift caught the week it happens is a one-line fix; caught at the next audit, it's a project. | Does such a check exist, and does it actually run? | UNIV |
| **STD-39** · MUST | Agent permission settings never pre-approve destructive or publishing commands — delete, force-push, deploy. Those always ask a human first. And any protection a doc claims ("force-push is blocked") actually exists in the settings. | A pre-approved delete plus one confused session is how repos lose things. False safety is worse than none. | Read the agent's settings allow/deny lists; compare against what the docs claim. | A-mem, UNIV |

---

## §I — Git and secrets

Version control is the safety net every other rule leans on — "reversible" means "git
can undo it." And a credential in a tracked file is a house key taped to the front door.

| ID · Tier | Rule | Why it exists | How to check | Src |
|---|---|---|---|---|
| **STD-40** · MUST | The repo is under version control, and changes land as small, labeled commits — so any single step can be undone without undoing the rest. | One giant commit means undo-everything or undo-nothing. | Is it a git repo? Is recent history granular? | UNIV |
| **STD-41** · MUST | Generated files, caches, logs, and local scratch are gitignored and untracked. Ignore rules are verified, not assumed — a `!` re-include inside an excluded directory silently does nothing. | Tracked junk churns every commit, and a broken ignore rule protects nothing while claiming to. | Check for tracked cache/log files; test suspicious ignore patterns. | UNIV |
| **STD-42** · MUST | Secrets and credentials never live in tracked files. They come from env vars or a secret manager, and ignore rules shield credential paths — including AI-tool session and credential directories (`.claude/.credentials.json` and friends). | Publishing a credential is publishing a house key — and one pre-approved push is all it takes. | Scan tracked files for tokens and keys; confirm the shield patterns exist. | UNIV |
| **STD-43** · SHOULD | Personal settings stay untracked (`settings.local.json`, `CLAUDE.local.md`); team settings are tracked. And one repo serves one purpose — a project repo doesn't double as a machine's dotfiles. | Tracked personal settings leak one person's pre-approvals to everyone; a double-duty repo spreads them to every machine. | Look for tracked local-settings files, and for a repo doing double duty. | A-mem, A-large |

---

## Appendix 1 — Source key

Every `A-*` and `O-*` rule was distilled from these official pages (verified live
2026-07-28). The rules are paraphrased for checkability; the pages are the receipts.

| Key | Source |
|---|---|
| A-mem | https://code.claude.com/docs/en/memory |
| A-feat | https://code.claude.com/docs/en/features-overview |
| A-large | https://code.claude.com/docs/en/large-codebases |
| A-skill | https://code.claude.com/docs/en/skills |
| A-hook | https://code.claude.com/docs/en/hooks-guide |
| A-supp | https://support.claude.com/en/articles/14553240-give-claude-context-claude-md-and-better-prompts |
| O-spec | https://agents.md (the AGENTS.md open spec — Linux Foundation / Agentic AI Foundation) |
| O-guide | https://developers.openai.com/codex/guides/agents-md |
| O-best | https://developers.openai.com/codex/learn/best-practices |
| O-custom | https://developers.openai.com/codex/concepts/customization |
| UNIV | Universal software-craft convention — no single page owns it; every style guide assumes it. |
