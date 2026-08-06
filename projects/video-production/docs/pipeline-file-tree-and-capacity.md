# SCLA Video Pipeline: Annotated File Tree and Capacity Review

**Snapshot:** 2026-08-05, based on the live working tree and
`run.sh status --json`. Historical `_archive/` contents are intentionally not
inspected or treated as pipeline inputs.

## What changed

The factory now treats authoring, narration, rendering, and publishing as four
different capacity stages. Isolated Codex Cloud tasks can author six lesson
workspaces at once without using HeyGen or Codespace render capacity. Narration
is admitted through a machine-wide two-slot queue, cloud rendering starts at
two and can unlock four after three verified clean renders, and publishing stays
serial.

A normal lesson no longer sends one HeyGen request per beat. Its narration is
combined into one request below a 4,800-character safety ceiling, then split
locally back into the beat WAVs and word timings expected by timing and QA. A
longer script is split into the smallest number of whole-beat chunks. This
replaces the old ten-minute stagger with an enforced capacity limit.

## Production cycle

```text
[0] select scope and persist run state
       ↓
[1] inbox script → fact-checked refinement → ready script
       ↓
[2] prepare one shared scaffold and compact builder kit
       ↓
[3] plan two visual lenses and select one concept
       ↓
[4] claim one stem → author HTML → synthesize audio → compute timing
       ↓
[5] deterministic gate → combined visual/taste review for every selected workspace
       ↓
[5a] owner reviews the complete set → one batch approval
       ↓
[6] cloud/local render → MP4 verification → temporary encode review
       ↓
[7] serial Wistia publish → ledgers → script to published → prune workspace
       ↓
[8] status is reconstructed from disk; failures resume from receipts
```

## Annotated file tree

Phase numbers in brackets correspond to the cycle above. Generated or repeated
items are shown as patterns rather than listing every lesson and every QA test.

```text
SCLA-Profile/
├── AGENTS.md                                      [0]
│   Repository task router. Sends video work to the factory's authoritative
│   instructions and prevents human overview documents from becoming commands.
│
├── .claude/
│   ├── rules/video-production.md                  [all]
│   │   Standing lifecycle and safety rules: scope, content fidelity, leases,
│   │   voice pinning, gates, retries, publishing, and archive boundaries.
│   ├── skills/
│   │   ├── produce-video/SKILL.md                 [0]
│   │   │   Selects one explicit stem and stops at its review gate.
│   │   ├── refine-scripts/SKILL.md                [1]
│   │   │   Refines one script without widening scope or starting a build.
│   │   ├── render-lessons/SKILL.md                [2–8]
│   │   │   Orchestrates the four-call flow: concept, build, visual review,
│   │   │   and temporary post-render encode review.
│   │   └── hyperframes-media/                     [4]
│   │       Shared audio engine. Its TTS worker pool defaults to four requests
│   │       per process; this is a per-video limit, not a batch-wide limit.
│   └── agents/qa-facts.md                         [1]
│       Checks a refined narration candidate against its source.
│
├── projects/video-production/
│   ├── CLAUDE.md                                  [0]
│   │   Small agent router for this subtree. Points each kind of work to one
│   │   contract instead of loading the old full production manual.
│   ├── run.sh                                     [0, 5–8]
│   │   The only public control surface. Selects scope, prints isolated cloud
│   │   task prompts, shows stage limits, approves, retries, and invokes ship.
│   ├── PIPELINE-STATUS.md                         [8]
│   │   Generated human view of disk state. Useful to people, but agents read
│   │   live JSON from `run.sh status --json` instead.
│   ├── README.md                                  [human]
│   │   Human overview; not an agent operating source.
│   │
│   ├── contracts/                                 [1, 4, 5]
│   │   ├── script-state.md
│   │   │   Defines inbox → ready → workspace → published as the only lifecycle.
│   │   ├── builder.md
│   │   │   Compact, one-video build contract and exact authoring sequence.
│   │   ├── cloud-author.md
│   │   │   Source-only contract for one isolated Codex Cloud task; forbids
│   │   │   provider calls, rendering, publishing, and shared-state edits.
│   │   └── visual-review.md
│   │       One reviewer returns separate correctness and taste verdicts.
│   │
│   ├── lesson-scripts/                            [1, 7, 8]
│   │   ├── <program>/
│   │   │   ├── inbox/<stem>.txt
│   │   │   │   Raw or blocked narration; not eligible to build.
│   │   │   ├── ready/<stem>.txt
│   │   │   │   Approved narration and the build queue.
│   │   │   └── published/<stem>.txt
│   │   │       Narration record for a video confirmed live on Wistia.
│   │   ├── published.tsv
│   │   │   Machine resume key: stem, program, render date, and Wistia URL.
│   │   ├── refinement-log.md
│   │   │   Human history of refinement and publishing.
│   │   └── README.md
│   │       Human folder guide, not pipeline state.
│   │
│   ├── design-system/                             [2, 4, 5]
│   │   ├── CONTRACT.md
│   │   │   Machine-facing description of what builders may consume.
│   │   ├── config/tokens.yml
│   │   │   Single source for canvas, palette, type, spacing, timing, program
│   │   │   display names, HeyGen provider, Oxana voice ID, and speed.
│   │   ├── assets/
│   │   │   Approved fonts and SCLA brand marks copied into the scaffold.
│   │   ├── compositions/
│   │   │   Shared runtime composition code; new lesson HTML is authored
│   │   │   freeform rather than assembled from the retired template lane.
│   │   ├── hyperframes.json
│   │   ├── package.json
│   │   ├── meta.json
│   │   │   Pinned HyperFrames project/runtime configuration used to prepare
│   │   │   the batch scaffold.
│   │   ├── AGENTS.md / CLAUDE.md
│   │   │   Local design-system routing; `CLAUDE.md` imports `AGENTS.md`.
│   │   ├── docs/ / README.md
│   │   │   Human design commentary and reference material, not build input.
│   │   └── _archive/
│   │       Read-only provenance. Never loaded, routed to, or copied into work.
│   │
│   ├── renders-hyperframes/                       [2–8]
│   │   ├── _run/
│   │   │   ├── run.json
│   │   │   │   Persistent scope, selected items, full-set review approval, backend,
│   │   │   │   stage-specific limits, retry counts, results, and circuit breaker.
│   │   │   ├── RENDER-BACKEND
│   │   │   │   One shared choice: `cloud` or `local`; currently `cloud`.
│   │   │   ├── BUILD-KIT.md
│   │   │   │   Generated copy of `contracts/builder.md` handed to cold builders.
│   │   │   └── scaffold/
│   │   │       Prepared once per run: pinned dependencies, tokens, fonts, and
│   │   │       brand assets. Avoids a network install for every video.
│   │   ├── _concepts/<stem>/                      [3]
│   │   │   Selected visual thesis and the planner's comparison scores.
│   │   ├── _reference/                            [human]
│   │   │   Explicitly sidelined comparison/backup work; underscore folders are
│   │   │   excluded from queue status.
│   │   ├── .build-in-progress/<stem>              [4–7]
│   │   │   One lease file per active stem. The directory arms the write fence;
│   │   │   releasing one stem cannot drop another stem's protection.
│   │   ├── .render.lock                           [6, local only]
│   │   │   Atomic machine-wide lock. Guarantees one local render at a time.
│   │   ├── .publish.lock                          [7]
│   │   │   Atomic lock. Wistia upload, shared ledgers, and git commit serialize.
│   │   └── <stem>/                                [4–8]
│   │       ├── .scla-control-v2
│   │       │   Marks a workspace created under the compact current contract.
│   │       ├── .build-log.tsv
│   │       │   Append-only journal used to resume from the last completed step.
│   │       ├── design.md / CONCEPT.md
│   │       │   Visual plan and chosen concept used by the builder/reviewer.
│   │       ├── audio_request.json
│   │       │   Script-faithful, beat-by-beat request before paid synthesis.
│   │       ├── assets/voice/*.wav
│   │       ├── audio_meta.json
│   │       │   Provider receipt, clip paths, real durations, native word timing,
│   │       │   voice ID, and speed.
│   │       ├── timing.json
│   │       │   Computed timing authority. Builders apply it; they do not tune it.
│   │       ├── index.html
│   │       │   The authored lesson composition and visible on-frame copy.
│   │       ├── tokens.yml / assets/ / package*.json
│   │       │   Frozen local design/runtime inputs copied from the scaffold.
│   │       ├── qa/
│   │       │   ├── PREFLIGHT-OK
│   │       │   │   Durable marker that the deterministic pre-render gate passed.
│   │       │   ├── failure.json
│   │       │   │   Error class, command, exit, attempt, full log, and recovery.
│   │       │   ├── logs/
│   │       │   │   Full timestamped external-command output.
│   │       │   ├── frames/ / presence/
│   │       │   │   Render evidence used for visual and blank-frame checks.
│   │       │   └── VERIFIED
│   │       │       Pins the verified MP4 path and hash; publish accepts only it.
│   │       └── renders/<dated-stem>.mp4
│   │           Render result before it is filed and published.
│   │
│   ├── render-qa/                                 [1, 4–8]
│   │   ├── AGENTS.md
│   │   │   Small route to the approved QA entry points.
│   │   ├── src/
│   │   │   ├── run_state.py
│   │   │   │   Atomically reads/writes `run.json`; owns retry and circuit state.
│   │   │   ├── prepare_audio.py
│   │   │   │   Forces the production provider, voice, and speed into requests
│   │   │   │   and stamps the effective values into the receipt.
│   │   │   ├── plan_timing.py
│   │   │   │   Converts actual audio durations and word timing into timing.json.
│   │   │   ├── continuous_audio.py
│   │   │   │   Combines beat text into minimal provider requests and splits the
│   │   │   │   result locally back into deterministic beat clips and timestamps.
│   │   │   ├── preflight.py
│   │   │   │   Authoritative pre-render gate; coordinates the `check_*.py` rules.
│   │   │   ├── check_*.py
│   │   │   │   Focused checks for claims, copy, layout, ink, motion, timing,
│   │   │   │   brand, presence, pace, and related measurable requirements.
│   │   │   ├── verify_render.py
│   │   │   │   Verifies dimensions, duration, audio/video integrity, and frames;
│   │   │   │   writes `qa/VERIFIED` only on success.
│   │   │   ├── stem.py
│   │   │   │   Single owner of canonical working and dated delivery names.
│   │   │   └── hfp_common.py / tokens.py / textmetrics.py
│   │   │       Shared parsers and measurements used by multiple gates.
│   │   ├── tests/
│   │   │   Standalone QA, control-plane, mutation, and enforcement tests.
│   │   ├── logs/
│   │   │   Rotated factory history; evidence, never instructions.
│   │   ├── quarantine.log
│   │   │   Append-only incident trail used by live status.
│   │   └── docs/ / README.md
│   │       Human handoffs and explanations, not executable state.
│   │
│   ├── renders-mp4/<program>/                     [7]
│   │   Local backup of the exact dated MP4 delivered to Wistia. Gitignored.
│   ├── experiments/                               [outside cycle]
│   │   Trials and prototypes. They do not enter the production queue.
│   ├── script-templates/                          [outside core cycle]
│   │   General/manual script references, including non-factory avatar work.
│   └── docs/                                      [human]
│       Handoffs and this system map; not machine state or agent instructions.
│
└── scripts/
    ├── batch-prepare.sh                           [2]
    │   Builds/reuses `_run/scaffold` and writes the compact build kit once.
    ├── build-claim.sh                             [4]
    │   Atomically claims one undated workspace, arms its lease, starts its
    │   journal, and refreshes status.
    ├── build-session.sh                           [4–7]
    │   Creates, refreshes, reports, and releases per-stem leases; six-hour TTL
    │   is crash recovery, not normal cleanup.
    ├── write-fence.sh                             [4–7]
    │   While any lease is active, blocks builders from changing shared factory
    │   code while leaving their own workspaces writable.
    ├── build-log.sh                               [4–7]
    │   Appends completed steps to a workspace's durable journal.
    ├── video-audio.sh                             [4]
    │   Pins voice settings, enters the shared two-slot TTS queue, requests
    │   continuous narration, splits beat clips, and checks the receipt.
    ├── with-capacity.sh                           [4, 6]
    │   Named machine-wide slot queue. A waiting job sleeps; a crashed process
    │   releases its slot automatically.
    ├── cloud-author.sh                            [4]
    │   Creates one source-only workspace without touching live run state.
    ├── with-secrets.sh                            [4, 6, 7]
    │   Injects Infisical-managed credentials for HeyGen and Wistia calls.
    ├── build-gate.sh                              [5]
    │   Runs preflight and writes/removes `qa/PREFLIGHT-OK` from the real verdict.
    ├── batch-precheck.sh                          [5, compatibility helper]
    │   Dense snapshot and low-ink pre-render evidence tool. It remains tested,
    │   but the new public four-call flow names the combined reviewer directly.
    ├── batch-ship.sh                              [6, 7]
    │   Render mode: gate, cloud/local render, verify, sample. Publish mode:
    │   verify hash, file MP4, upload, write ledgers, commit, and prune.
    ├── wistia-upload.sh                           [7]
    │   Performs the provider upload and returns the permanent media URL.
    ├── archive-lesson.sh                          [7]
    │   Prunes regenerable workspace bulk in place after confirmed delivery.
    ├── batch-status.sh                            [8]
    │   Reconstructs every normal and exception state from folders, receipts,
    │   ledgers, and run state; can emit JSON or regenerate the human board.
    ├── build-release.sh                           [4–7]
    │   Journals close-out, releases only that stem's lease, and refreshes status.
    ├── preview.sh / review.sh                     [5, human]
    │   Serve one or several gate-clean workspaces for browser review.
    └── lint-refs.sh                               [all]
        Repository's only complete lint/test entry point, including factory QA.
```

Existing pre-v2 workspaces may still contain `make_timing.py`, `build_wall.py`,
or similar bespoke helpers. They are resumable legacy artifacts, not the current
contract. New `.scla-control-v2` workspaces must use `plan_timing.py` and shared
scripts instead.

## Capacity: previous versus current

| Constraint | Previous operating model | Current live model | Practical meaning |
| --- | --- | --- | --- |
| Source-authoring lanes | Four mixed-purpose lanes | Six isolated Codex Cloud tasks, or three local workers | Cloud authoring does not consume HeyGen or local render capacity. |
| Ten-minute stagger | Manual operating rule | Replaced by an enforced two-slot global TTS queue | Jobs wait for a slot; no time-based stagger is needed. |
| Codespace render load | Local rendering competed for four CPUs | Cloud rendering skips the local CPU lock and may run in parallel | This is the biggest speed improvement. Local fallback still renders one at a time. |
| Workspace safety | Parallel agents could interfere with a shared sentinel | One lease per stem; atomic workspace claim; release is independent | Four builders can safely own different stems in the same live checkout. |
| Build startup | Each cold builder initialized HyperFrames and recopied assets | One prepared scaffold and compact build kit per run | Less network work and less repeated agent context per lesson. |
| HeyGen voice calls | One call per beat could produce 18–45 calls per lesson | Normally one request per lesson, admitted two lessons at a time | Provider load falls sharply while beat-level output remains unchanged downstream. |
| Cloud rendering | Not the normal path | Starts at two; four unlocks after 3/3 clean verified renders | A cloud failure automatically resets the limit to two. |
| Local rendering | Resource constrained | One render at a time under `.render.lock` | Adding agents cannot accelerate this stage. |
| Publishing | Shared ledgers and git required care | One publisher under `.publish.lock` | Correctly remains serial. |
| Failure handling | Easy to loop or lose the cause | Two attempts per stem/error class; circuit opens after the same class hits two different stems | Parallelism now stops on a likely system-wide failure instead of burning the queue. |

The Codespace currently reports 4 CPUs, 15 GiB RAM, about 9 GiB available RAM,
and 9.2 GiB free workspace disk. Cloud rendering makes those resources adequate
for authoring and coordination, but disk and Node dependencies still make very
high local worker counts unwise.

## Would Codex or Claude agents speed this up?

**Yes—for the agent-bound parts, not for provider-bound parts.** The concept
planner, HTML builder, first-pass fixes, and visual reviewer divide cleanly by
stem. Codex supports parallel tasks in separate cloud sandboxes, and Claude Code
supports parallel subagents/sessions and worktrees. Those capabilities can keep
the configured authoring lanes full.

They do not increase HeyGen voice capacity, make one local render use less CPU,
or allow two publishers to update shared ledgers safely. Remote/isolated agents
also do not automatically share this checkout's `run.json`, per-stem leases,
Infisical credentials, narration cache, or gitignored render artifacts.

The safest split is:

1. Keep one coordinator in the live checkout. It owns `run.sh`, run scope,
   leases, the circuit breaker, full-set review approval, and publishing.
2. Use one Codex or Claude worker per stem for concept planning, HTML authoring,
   and composition revision. Give each worker only its script, selected concept,
   local tokens, and compact builder contract.
3. Keep paid TTS in the live checkout behind the enforced two-slot queue.
4. Keep cloud render at two until three clean renders unlock four. Keep local
   render and all publish work serial.
5. Increase agent lanes only after measuring a representative batch. Without a
   global TTS throttle and clean cloud-render evidence, adding a fifth builder
   increases risk more reliably than throughput.

For external reference, OpenAI describes Codex cloud tasks as isolated sandbox
environments that can run in parallel, while Anthropic distinguishes subagents,
agent teams, and worktree-isolated sessions for parallel work:

- https://openai.com/index/introducing-codex/
- https://code.claude.com/docs/en/agents

## Now what

Run the first measured batch with six source-authoring tasks, two narration
slots, and two cloud renders. After three clean verified cloud renders, use
`run.sh cloud-limit 4`. Record provider failures and end-to-end wall time before
raising any other limit.
