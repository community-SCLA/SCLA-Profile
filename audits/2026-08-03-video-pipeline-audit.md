> **SUPERSEDED 2026-08-04 — historical record. Do not act on the body below.**
> Its state descriptions were true on 2026-08-03 and are now wrong: `refined/`/`rendered/`
> became `inbox/`/`ready/`/`published/`, and the tool blind spots it catalogues are fixed.
> Kept in `audits/` (not archived — see `.claude/rules/repo-hygiene.md`, no new `_archive/`
> folders) because three of its items are still open.
>
> **Verified walk of its recommendations, 2026-08-04** — each checked against live `HEAD`,
> not inherited from the commit messages:
>
> | Recommendation | Status | Evidence |
> |---|---|---|
> | Make `batch-status.sh` freeform-aware | **DONE** | live run emits `(freeform lane)` / `(scaffold lane)` sub-states |
> | Add a stall detector | **DONE** | 13 `STALLED` rows, each with "left off after **&lt;step&gt;**, N ago" |
> | Reclaim rule for the `mkdir` lock | **DONE** | STALLED rows print reclaim-vs-discard, and say which loses work |
> | Scan raws so `BLOCKED` is visible | **DONE** | live run reports `1 raw · 1 NEEDS SCRIPT` |
> | Delete the commented-out block in `refinement-log.md` | **DONE** | no HTML comments remain in the file |
> | Delete the Notion doc's competing status model | **DONE** | `docs/notion-queue.md` is retired down to a links-only copy |
> | Fix the stale `renders-hyperframes/README.md` | **DONE** | re-verified clean 2026-08-04 |
> | Resolve `rendered/` meaning two things | **DONE** | folders renamed; `published/` = live; `lint-refs.sh` check 13 pins the layout |
> | Re-point style rotation at started builds | **DONE** | `theme_for.py` counts live workspaces + published rows |
> | Fix the snag-log path both skills cite | **DONE** | all 3 skills + both scripts now say `render-qa/logs/snag-log.md` |
> | Give priority order one definition | **DONE** | `PRIORITY=` in `batch-status.sh`; the skill's prose rule now defers to it |
> | Owner call — the `..._freeform-backup` reference cut | **DONE** | registered at `renders-hyperframes/_reference/` with a README |
> | Owner call — the HeyGen avatar lane | **DONE** | lane deleted (`2e2cff0`); no `avatar/` directory survives |
> | Clear `quarantine.log` rows on publish | **OPEN** | still 2 rows, both naming lessons that later published |
> | Watchdog on build subagents | **OPEN** | no idle-kill/retry rule in `render-lessons/SKILL.md` |
> | Owner call — `m4_visibility-actions` build-vs-scrap | **OPEN** | workspace still on disk; its raw is still marked SCRIPT PENDING |

1. Lesson script tree — projects/video-production/lesson-scripts/
Four program directories (the ledger also names career-readiness-accelerator and scla-leadership-program as "No scripts yet" — neither directory exists).

Program	raw *.txt at root	refined/	refined/avatar/	rendered/	avatar/
early-career-boost	0	8	—	3	— (no dir)
mid-career-momentum	1	15	1	0 (dir exists)	0 (dir exists)
career-transitions	0	8	—	0 (dir exists)	0 (dir exists)
entrepreneur-accelerator	1	4	—	0 (dir exists)	0 (dir exists)
Raw at root:

/workspaces/SCLA-Profile/projects/video-production/lesson-scripts/entrepreneur-accelerator/m2_why-build-your-own-path.txt — ordinary raw, no markers, awaiting /refine-scripts.
/workspaces/SCLA-Profile/projects/video-production/lesson-scripts/mid-career-momentum/m4_visibility-actions-what-they-are-and-how-to-practice-them.txt — first line: SCRIPT PENDING — do not refine or build. Re-confirmed 2026-07-24 (auto drain): … plus "Owner-actionable: supply real visibility-actions narration."
rendered/ contents (early-career-boost only): better-decisions-come-from-better-criteria_early-career-boost.txt, build-direction-before-you-build-a-plan_early-career-boost.txt, what-makes-for-a-dream-job_early-career-boost.txt — exactly the three rows in published.tsv.

Frontmatter: none anywhere. I checked the top ~12 lines of representative files in each state (raw ×2, refined ×3, rendered ×1, refined/avatar ×1). Every file is plain narration prose from line 1 — no YAML, no ---, no key/value header. The only in-band state signal in the whole tree is the free-text SCRIPT PENDING / TODO: needs input marker convention that batch-status.sh regex-matches. Refined files are pure spoken lines; raws may still carry [On screen: …] / [Graphic: …] cues and Lesson: / Title: lines (e.g. the entrepreneur raw and the mid-career pending raw).

No built/, published/, or done/ subfolders exist. State folders are exactly: program root → refined/ → rendered/, with avatar/ / refined/avatar/ as a parallel HeyGen route.

2. Build output tree
/workspaces/SCLA-Profile/projects/video-production/renders-hyperframes/ — per-lesson build workspaces, gitignored (.gitignore:56-57 ignores everything but README.md; _run/ is force-tracked). 16 lesson folders + _run/ (BUILD-KIT.md + scaffold/ clone source) + README.md.
A template-lane built folder contains: scenes.json, index.html, compositions/scla-*.html, assets/{voice,fonts,brand}, tokens.yml, hyperframes.json, meta.json, package.json, design-contract.md, .pin. 12 of the 16 match this shape and have assets/voice/narration.wav.
A freeform-lane built folder (opt-in lane, render-lessons §"Freeform build sequence", decisions/log.md 2026-07-30) has no scenes.json — instead design.md, audio_request.json, audio_meta.json, timing.json, per-beat assets/voice/s01.wav…. Present in: build-direction-…_early-career-boost (26 wavs, timed index.html), …_2026-08-04-freeform-backup (17 wavs), and two scaffold-stage ones (career-building-is-a-repeatable-process_early-career-boost created 2026-08-04T18:11Z, do-not-just-ask-what-ai-replaces_early-career-boost created 18:27Z — both index.html all data-start="0", assets/voice empty or absent).
No workspace currently has qa/ or renders/ — zero qa/VERIFIED markers, zero in-workspace MP4s.
Delivered MP4s: /workspaces/SCLA-Profile/projects/video-production/renders-mp4/<program>/hyperframes/ (illustrated) and …/avatar/ (HeyGen). Gitignored (.gitignore:59). Only one file on disk: renders-mp4/early-career-boost/hyperframes/build-direction-before-you-build-a-plan_early-career-boost_2026-08-04.mp4.
"Delivered" is distinguished by the date suffix: working artifacts carry no date; only the delivered MP4 carries _<render-date>, frozen at publish. Rule owned by /workspaces/SCLA-Profile/projects/video-production/render-qa/src/stem.py (base() strips trailing date + render-clock segments; delivered() adds one).
design-system/ is template source (compositions/scla-*.html, config/tokens.yml, assets/fonts/), not a build-output dir. experiments/agent-native-m2/ is a reference freeform build.
3. scripts/batch-status.sh (462 lines, bash wrapper around an inline python3 heredoc)
Reads, and only these:

lesson-scripts/<prog>/refined/*.txt — non-recursive glob (deliberately excludes refined/avatar/).
lesson-scripts/<prog>/rendered/*.txt — non-recursive.
renders-hyperframes/*/ — directories not starting with . or _, indexed by stem_base(dirname).
lesson-scripts/published.tsv — primary key (cols: base, program, render_date, wistia_url).
lesson-scripts/refinement-log.md — fallback: any wistia.com/medias/(\w+) plus any <name>_YYYY-MM-DD token on the same line.
render-qa/quarantine.log — TSV, cols[1] = stem, cols[3] = reason.
optionally renders-hyperframes/<ws>/qa/quarantine-reason.txt for gate findings.
Program order: PRIORITY="${VIDEO_PRIORITY:-early-career-boost mid-career-momentum career-transitions entrepreneur-accelerator}", then any remaining program alphabetically.

States it can emit (per refined script, first match wins): published (base in tsv/ledger) → blocked (regex TODO:\s*needs input or SCRIPT PENDING inside the refined file, quoting the marker's paragraph) → workspace exists → ws_state() sub-stages → else queued. Plus a separate rendered_unpublished ("stranded") bucket for rendered/*.txt with no published row.

ws_state() probe order:


no scenes.json                                  -> "no-plan"    (nothing authored yet)
no assets/voice/narration.wav                   -> "planned"
index.html unreadable                           -> "uncompiled"
all data-start values ⊆ {"0"}                   -> "untimed"
qa/VERIFIED exists                              -> "verified"   (MP4 awaiting publish)
otherwise                                       -> "composition"
no-plan|planned|uncompiled|untimed|composition all roll into the composition_only total.

Modes: default ANSI terminal report; --json; --write [path] regenerates projects/video-production/PIPELINE-STATUS.md (self-described "Generated file — do not hand-edit"). batch-ship.sh calls --write on every quarantine (line 85) and every publish (line 327).

Known blind spots (from the code itself):

Raw scripts at program root are never scanned. Both raws in §1 — including the SCRIPT PENDING one — are invisible; the run reports 0 blocked.
refined/avatar/ is never scanned (by design). The single HeyGen script has no state anywhere in the tool.
ws_state() only understands the template lane. A freeform workspace has no scenes.json by design, so any freeform build — at any maturity — reports no-plan, "build folder exists but holds no scene plan — nothing authored yet", next action "restart the build". This is currently mis-describing 2 real workspaces.
The narration.wav probe misses freeform's per-beat s01.wav… layout.
Quarantine lookup keys on the stem only (quarantined.get(stem) or quarantined.get(base_of(stem))), and is only consulted on branches where a workspace exists.
Ledger fallback matching is regex/best-effort and is explicitly documented as such ("rows abbreviate the stem, so that matching is best-effort — the tsv is the contract").
Programs are lessons.iterdir() dirs that have a refined/ subdir; a program with only raws is skipped entirely.
Live run (2026-08-04): 21 to build · 14 composition-only · 0 MP4 ready to publish · 0 quarantined · 0 stranded · 0 blocked · 3 already on Wistia.

4. Other status ledgers
Path	Records	Current?
lesson-scripts/published.tsv	Machine resume key. Header # base<TAB>program<TAB>render_date<TAB>wistia_url + 3 rows (what-makes-for-a-dream-job 2026-07-17, better-decisions 2026-07-29, build-direction 2026-08-04). Appended by batch-ship.sh in the publish pass.	Current; matches rendered/ exactly.
lesson-scripts/refinement-log.md (162 lines, 55 rows)	Human ledger: Created / Refined / Rendered / Notes per script, per program section. Header states "Ledger, not state machine… Never read this table to decide what to refine, build, ship, or publish." Carries Wistia hashedIds, UNPUBLISH events, qa-facts verdicts, owner-actionable notes.	Partly stale. Rows still describe legacy dated stems (..._2026-07-10.txt) and describe scripts as "in rendered/" that are now in refined/ (the 2026-07-29 bulk unpublish). Lines 138–154 are an HTML-commented-out block (<!-- alternate branch removed: older 2026-07-22 mid-career notes -->) containing ~14 mid-career rows — invisible to readers, still regex-visible to batch-status.sh's ledger scan.
projects/video-production/PIPELINE-STATUS.md	Generated view of the above.	Stale vs. disk right now: file says 23 queued / 12 composition-only; a live batch-status.sh run says 21 / 14. The two 2026-08-04 freeform workspaces were created without a --write.
render-qa/quarantine.log	TSV: timestamp, stem, program, reason. 2 rows (2026-07-29 better-decisions frame-review FAIL; 2026-07-31 build-direction verify_render.py non-zero).	Stale as state — both stems have since published; nothing clears rows, and both are now suppressed only because published.tsv wins the branch order.
render-qa/logs/snag-log.md (+ snag-log-archive-001.md, BUILD-LOG-archive-001.md)	Rolling session memory; "Open" list rolls forward. Read rule: latest ## entry only.	Active. Note: both skills reference it as render-qa/snag-log.md; the file is actually at render-qa/logs/snag-log.md.
docs/notion-queue.md	Full Notion DB schema + a 9-status workflow (Requested → … → Delivered) with Priority Rush/High/Normal/Low.	Explicitly retired 2026-07-13 ("Do not work this queue as a request pipeline"), but it still describes a complete competing status model, including a Final video Wistia field and a style-package rotation rule counting delivered MP4s.
render-qa/docs/HANDOFF-*.md, BUILD-PLAN-agent-native-2026-08-04.md, PENDING-pace-gates.md	Design/handoff docs referencing pipeline state.	Dated snapshots.
experiments/agent-native-m2/PIPELINE-IF-ADOPTED.md (+ .v2.md)	Proposed alternate pipeline state model.	Proposal, two versions.
No published.json, manifest.json, STATUS, QUEUE, or ledger.* file exists.

5. Priority / ordering source
Program order lives in exactly one place: scripts/batch-status.sh:28 — VIDEO_PRIORITY env override, default early-career-boost mid-career-momentum career-transitions entrepreneur-accelerator. No other file defines it.
Within a program the order is the sorted glob of refined/*.txt (for f in sorted(refined.glob("*.txt"))) — i.e. alphabetical by stem, which for m<#>_… names coincides with module order and for early-career-boost's undated title stems does not.
render-lessons §A1 says "Priority is the human's call; absent one, use refinement-log.md's published counts" — a third, prose-only rule that disagrees with the hardcoded default.
The retired docs/notion-queue.md defines a Priority select (Rush/High/Normal/Low) + Due date ordering.
Filenames encode module number (m1_…m7_) for mid-career/career-transitions/entrepreneur; early-career-boost stems have no numbering at all.
6. Skills
/workspaces/SCLA-Profile/.claude/skills/produce-video/SKILL.md (30 lines) — dispatcher only. Reads nothing; routes on queue size (1 → BUILD, >1 → AUTO-BATCH). States refined/ → workspace → rendered/, Wistia URL in refinement-log.md = published; points at bash scripts/batch-status.sh for resume.

/workspaces/SCLA-Profile/.claude/skills/refine-scripts/SKILL.md (141 lines)

Work-left detection: non-recursive ls of lesson-scripts/<program-slug>/ root and its avatar/ subfolder; every *.txt in either is raw. Explicitly "not a recursive find (don't re-sweep refined/)".
Skip rule: "any raw script whose ledger row (or filename) carries an open human question is skipped, not refined blind" — a ledger read, contradicting the same file's line 30 ("never read it to decide what to do; the folders decide").
Writes on completion (step 5): git mv/remove the raw original, update the refinement-log.md row, run bash scripts/batch-status.sh --write, stage + commit. Output target mirrors source: root → refined/, avatar/ → refined/avatar/. Runs render-qa/src/check_copy.py on each output (reports, does not block) and a qa-facts subagent pass.
/workspaces/SCLA-Profile/.claude/skills/render-lessons/SKILL.md (556 lines)

Queue (B1): ls …/refined/*.txt root only, never refined/avatar/, never recursive. Guard: if a script in refined/ already has renders-hyperframes/<base>/, skip it — it's at the gate.
Build lock: mkdir renders-hyperframes/<base>. Render lock: renders-hyperframes/.render.lock inside batch-ship.sh (second render exits 2).
Style-package rotation: count(*.txt in lesson-scripts/<program-slug>/rendered/) mod 3, never scanning _archive/.
Gate: orchestrator re-runs render-qa/src/preflight.py <workspace>.
Writes on completion — all via scripts/batch-ship.sh <stem> <program> --publish (lines 185–347 of that script): guard on qa/VERIFIED + sha re-hash → refuse if stem already in published.tsv → cp MP4 to renders-mp4/<program>/hyperframes/<base>_<date>.mp4 → wistia-upload.sh → append published.tsv → rewrite the refinement-log.md row → git mv script refined/ → rendered/ → batch-status.sh --write → git add -A <lesson-scripts> <PIPELINE-STATUS.md> → git commit -m "ship(<program>): <stem> → Wistia" → archive-lesson.sh --in-place prune. Commit failure = quarantine with the URL recorded.
Resume contract (A6): "A stem is done if and only if it has a row in lesson-scripts/published.tsv."
Freeform lane (§267+): --freeform, no scenes.json/compiler, artifacts are design.md, audio_request.json, audio_meta.json, timing.json, per-beat wavs; "never enters AUTO-BATCH", per-video human preview.
Close-out: prepend an entry to the snag log (referenced as render-qa/snag-log.md).
adversarial-qa (87 lines) — on-demand only, reads a cut; writes no state.

7. Inconsistencies found
refined/ → rendered/ moves at two different times, in the same file. render-lessons lines 23–24 and 50 and 55–57 say the move happens when a build is gate-clean ("rendered/ means 'a gate-clean build exists for this script,' not 'published'"); lines 347–350 and 491–493 say the script stays in refined/ until publish. lesson-scripts/README.md and stem.py's docstring both use the gate-clean wording. batch-ship.sh implements the publish-time move. Disk agrees with the code: 12 gate-clean mid-career workspaces exist while all 15 scripts remain in refined/ and mid-career-momentum/rendered/ is empty.
Consequence of (1): style-package rotation is skewed. The rule counts rendered/*.txt, which now only counts published lessons — 3 for early-career-boost, 0 everywhere else — not started builds as the rule's own comment claims.
Two freeform workspaces are invisible/mislabelled. career-building-is-a-repeatable-process_early-career-boost and do-not-just-ask-what-ai-replaces_early-career-boost (both created 2026-08-04) report as no-plan / "nothing authored yet" / "restart the build", because ws_state() requires scenes.json. They are in fact scaffold-stage freeform workspaces.
PIPELINE-STATUS.md is stale (23/12 committed vs 21/14 live) — the generated doc did not get regenerated when those two workspaces appeared, because only batch-ship.sh triggers --write, and a build never does.
The one blocked script is reported as 0 blocked. SCRIPT PENDING is inside a raw at program root; blocked_reason() is only applied to refined/*.txt.
An orphan workspace no key can reach: renders-hyperframes/build-direction-before-you-build-a-plan_early-career-boost_2026-08-04-freeform-backup. stem.base() returns the name unchanged (the trailing segment 2026-08-04-freeform-backup is not a bare date), so it indexes under a base no script will ever match; nothing lists, prunes, or reports it.
Stem present in one place, missing in another: m4_visibility-actions has a complete built workspace (scenes.json + narration.wav) and a refined/m4_visibility-actions.txt, while the differently-named raw m4_visibility-actions-what-they-are-and-how-to-practice-them.txt sits at root marked "do not refine or build". The ledger (line ~150) records that the raw was accidentally drained on 2026-07-24 and the refined copy deleted; a refined/m4_visibility-actions.txt nonetheless exists today and has been built.
Duplicate/competing ledgers: published.tsv (machine, 3 rows) vs refinement-log.md (human, 55 rows, several rows asserting Wistia IDs marked "archived by owner — no longer live"). batch-status.sh unions both for the "published" count (totals["published"] = len(media_ids)), so archived-but-still-in-the-log media IDs would inflate that count; today both sources agree at 3.
render-qa/quarantine.log never clears. Both rows name lessons that later published; they survive only because the published check runs first.
renders-hyperframes/README.md "What lives where" is stale: says the final .mp4 lives in ../lesson-scripts/<program-slug>/ and that QA snapshots go to "the video's Notion page". renders-mp4/README.md and batch-ship.sh say renders-mp4/<program>/hyperframes/; Notion was retired as intake 2026-07-13.
docs/notion-queue.md retains a full second status model (9 statuses, Priority select, Script location/Final video fields, <stem> including a program slug and a date) that conflicts with the current no-date working-artifact rule in stem.py.
Skill path drift: both skills cite render-qa/snag-log.md; the file is at render-qa/logs/snag-log.md.
refined/avatar/ has no state model at all. m0_welcome-to-mid-career-momentum_2026-07-22.txt (a legacy dated stem) is excluded from every scan by design, has no rendered/avatar/ counterpart folder, and the ledger records it as qa-facts FAIL awaiting owner input. Empty avatar/ directories exist under three programs.
Two naming conventions coexist in refined/: early-career-boost uses <title>_<program>; the other three use m<#>_<title> (with m2_four-kinds-of-career-transition_<program> appearing in both career-transitions and mid-career-momentum as distinct lessons that differ only by the program suffix).
The audit is back. Here's the full picture and my proposal.

TL;DR
Your instinct that it's a hot mess is right, but the cure isn't YAML frontmatter or moving folders — the repo already has the right state model ("the folder IS the status"), and it's the one thing that survived every refactor intact. What's broken is that the one tool that reads that state (batch-status.sh) is blind to the new freeform lane, the docs contradict the code about what one folder means, and nothing watches a build agent while it works — which is why a sub-agent could sit idle for 41 minutes and why two dead build folders are now mislabeled "nothing authored yet." I propose: fix the reader, add a stall detector, delete the competing status stories, and put a watchdog on build sub-agents. No new state files, no frontmatter.

What the audit actually found
The B5 stall left physical residue. Two workspaces created 2026-08-04 (career-building-is-a-repeatable-process, do-not-just-ask-what-ai-replaces) hold a scaffold and nothing else. The status tool calls them "build folder exists but holds no scene plan" and tells you to restart the build — but the folder's existence is the build lock, so a naive restart would collide. A dead agent currently strands a lock forever, invisibly.
The status tool only understands the old template lane. It decides "how far along is this build" by looking for scenes.json and narration.wav — files a freeform build (the lane you're now committed to) never creates. So every freeform build, at any stage, reports as "nothing authored yet."
One folder, two contradicting meanings. The docs (and half of the render-lessons skill) say a script moves to rendered/ when a gate-clean build exists; the code moves it only at publish. Disk agrees with the code. Side effect: the style-rotation rule counts the wrong thing.
Four stale or competing status narratives: PIPELINE-STATUS.md (out of date because only publishing regenerates it), refinement-log.md (55 rows, some describing files that moved, plus a commented-out block the status tool still regex-reads), quarantine.log (never clears — both rows name videos that later published), and the retired Notion doc (still describes a full 9-status workflow).
Invisible items: raw scripts at program root are never scanned (so the one genuinely owner-blocked script reports as "0 blocked"), the HeyGen refined/avatar/ lane has no state model at all, and the rejected reference cut (..._2026-08-04-freeform-backup) sits in a folder no tool can list, prune, or report.
Priority order is defined in three places that disagree: hardcoded in batch-status.sh, prose in the render-lessons skill, and the retired Notion doc.
Why not YAML frontmatter (your suggested option)
A status field written into a file is a claim; a folder's contents are a fact. The moment a build dies mid-way, the YAML says "building" while the disk says otherwise — and someone has to notice and fix the lie. This repo already learned this lesson the hard way (it's why prose governance was deleted and why owner preferences became checkers). Also practical: these .txt files are the narration contract — the TTS engine, the script-fidelity diff, and the copy gates all read them as pure spoken text, so a YAML header would have to be stripped in four places or it gets read aloud. Same logic against moving folders around: the folders already move at exactly the right moments (root → refined/ → rendered/); the problem is the reader, not the layout.

The proposed model — one lesson, one derived status
Every lesson lands in exactly one of these states, and every state is computed from files that already exist — nobody ever updates a status field:

Status	Meaning	Derived from
RAW	script exists, not refined	.txt at program root
BLOCKED	waiting on the owner	SCRIPT PENDING/TODO marker — scanned in raw and refined (today: refined only)
QUEUED	refined, ready to build	refined/*.txt, no workspace
BUILDING	workspace in progress	workspace exists; sub-stage read per lane (freeform: scaffolded → designed → voiced → timed → composed, from which of design.md / wavs / timing.json exist)
STALLED (new)	build abandoned mid-way	workspace incomplete and newest file older than ~30 min, with a printed reclaim command
AT PREVIEW GATE	built, waiting for your eyes	freeform build complete, not rendered (the hyperframe gate)
VERIFIED	rendered MP4 passed all gates	qa/VERIFIED marker
PUBLISHED	live on Wistia	row in published.tsv (unchanged — stays the single "done" key)
QUARANTINED / STRANDED / ORPHAN	exception states	quarantine marker / rendered/ script with no publish row / workspace whose name matches no script
One command shows this — bash scripts/batch-status.sh (terminal) or the regenerated PIPELINE-STATUS.md (readable doc) — same as today, just no longer lying.

The stall fix (so 41 idle minutes can't happen again)
Three layers, because the last failure had zero:

Watchdog in the orchestrator. The render-lessons skill gets a hard rule: builder sub-agents run in the background, and the orchestrator checks the workspace every ~5 minutes. No new file written in 15 minutes → kill the agent, log it, retry once with a fresh agent; second failure → stop and report to you. Never wait silently.
Reclaim rule for the lock. A STALLED workspace's printed "next" command becomes: delete the dead scaffold, then rebuild (today it says "restart the build," which would hit the taken lock).
Backstop in status. Even if an orchestrator dies too, the next session's batch-status.sh run flags the stall — nothing depends on the session that failed having cleaned up.
The pipeline, end to end (who does what)
You call /produce-video (or /render-lessons directly). It reads batch-status.sh and takes the top of the queue.
/refine-scripts drains raw scripts → refined/, one cold sub-agent per script, with a qa-facts agent checking every claim against source material. (Unchanged.)
/render-lessons builds one video per cold builder sub-agent (now watchdogged), runs the deterministic gates (preflight.py, now including the new pace gates), and stops at the preview gate for the pilot — that's your one approval per batch. On approval, batch-ship.sh renders → verifies → publishes to Wistia → records published.tsv → moves the script to rendered/ → commits, one video fully finished before the next starts.
adversarial-qa (four reviewer agents) stays on-demand only, for when you reject a cut and want it torn apart.
Single sources of truth: queue order = batch-status.sh (the other two definitions get deleted); done = published.tsv; status = derived from disk; history = refinement-log.md (ledger only, never consulted for decisions).
Cleanup in the same pass
Clear quarantine.log rows on publish; delete the commented-out block in refinement-log.md and the Notion doc's competing status model; fix the stale renders-hyperframes/README.md (still points at Notion); fix the docs-vs-code contradiction by declaring rendered/ = published (what the code does; I recommend keeping code and fixing docs) and re-pointing style rotation to count started builds so the next 12 videos don't all get the same look; fix the wrong snag-log path both skills cite.

Three decisions only you can make
m4_visibility-actions — a fully built workspace exists for a script the ledger says was accidentally refined from a placeholder you marked "do not build." Keep the build or scrap it?
The rejected reference cut (..._freeform-backup folder) — it's calibration evidence for the pace gates but lives where no tool can see it. I'd register it as a named reference in the repo docs and leave it; say if you'd rather delete it.
The HeyGen avatar lane — one script, no state model, no tooling. Fold it into the same status system, or explicitly park it as out-of-scope?
Everything above is one flagged system session of work (SCLA_SYSTEM_SESSION=1, since it edits scripts/ and .claude/ behind the write fence), each piece with a firing test per house rules — then B5 runs under the watchdog: one freeform pilot, built under the new pace gates, stopping at your preview. Say "go" (and answer the three decisions whenever) and I'll write it into an executable plan.