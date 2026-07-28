# Repo Audit Brief — 2026-07-28

**This is an execution document, not a report. If you are a fresh session: go to §0.0 and follow it.**

**State, 2026-07-28:** Step 0, the owner directive, and A6 are executed (`7bcb2f9`). All seven original open questions are closed. All four P-items are approved. **The only decisions left are five R-items: R4, R6, R7, R10, R11.**

*Item IDs: **S**-numbers = approved hygiene items (§1) · **R**-numbers = items needing a yes/no (§2) · **P**-numbers = the four structural replacements (§0.5) · **A**-numbers = owner answers (§0.6) · **Q**-numbers = the original open questions, all closed (§0.6) · **STD**-numbers = rules quoted from the official Claude Code docs, held in `audits/2026-07-28-repo-audit-redteam.md`'s companion file `audits/2026-07-28-repo-standard.md` (filed there at STEP 2).*

*Pruned 2026-07-28: the pre-directive diagnosis, the teaching section, the inlined copy of the standard, the superseded order, the closed-questions table, and the glossary were deleted — superseded, duplicated elsewhere, or written for a first-time human reader who has now read them. They are in git history and in `audits/2026-07-28-repo-audit-redteam.md`. Red-team verdict 🟡 after 17 repairs; that report holds the receipts.*

---

## §0.0 COLD START — read this, then go to §0.7 and execute

**You are a fresh session with no context. This section is your whole briefing. Follow it literally.**

### What to read

1. **This section (§0.0)** — the protocol and the ledger.
2. **§0.7** — the step list. Find the first unchecked step in the ledger below and execute *only that step*.
3. **§0.1** (owner policy, 3 lines) — the standing rules behind every decision here.

**Do NOT read §1, §2 or §3 end-to-end.** They are lookup tables. When a step names an item, read *that row only* — "S13" → the S13 row in §1; "R7" → the R7 row in §2. §3 is the target state, useful at the end, not during.

**Total required reading before you start work: §0.0, §0.1, and your one step in §0.7.** Everything else is on demand.

### The three rules that override everything

1. **`.agents/` is untouchable until STEP 13.** It is the live primary skill store: 10 of the 16 entries in `.claude/skills/` are symlinks into it, and `render-qa/synth_narration.py` + `design-system/frame.md` hardcode paths into it. Deleting, moving, or "tidying" it before STEP 13 kills 10 skills and the TTS step of every video build.
2. **One step per pass. Never two structural items in one commit.** STEP 11 (R7) and STEP 12 (R10) run alone, full stop.
3. **Deletion is the default disposition, not archiving** (§0.1). Git history is the archive. Do not create `_archive/` folders.

### Execution protocol — repeat per step

```
1. Read the ledger → find the first unchecked step.
2. If it is marked ⚠️ GATE, STOP and ask the human for a yes/no. Do not proceed on assumption.
3. Read ONLY the files that step names. Verify each claim before editing —
   this brief has been wrong before (see "If a step's premise turns out to be false").
4. Make the edits.
5. Verify:  bash scripts/lint-refs.sh     → must print "lint-refs: healthy"
            git status --short            → only expected paths
   Plus any step-specific check listed in §0.7.
6. Commit. One commit per step:
      refactor(step-N): <what changed>
      <why, in one or two lines>
      Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
7. Tick the step in the ledger below and record anything surprising in §0.2.
8. Stop and report to the human. Do not silently chain into the next step.
```

### If a step's premise turns out to be false

Say so, do not execute it, and correct this brief. Precedent: R8's "byte-identical duplicate skills" was verified-and-false, and executing it as written would have broken the video pipeline. **A step description is a claim, not a fact.**

### Ledger — the live state of the refactor

| Step | Item | Status |
|---|---|---|
| 0 | S14, S15 — credential shield + ignore fix | ☑ **done** 2026-07-28 (`7bcb2f9`) |
| — | Owner directive: delete dead governance, remove Drive mirror | ☑ **done** 2026-07-28 (`7bcb2f9`) |
| — | A6 — retire `postCreate.sh`, fold in brand safeguard | ☑ **done** 2026-07-28 (`7bcb2f9`) |
| 1 | S13, S16, S3 — settings & hook hygiene | ◐ **partial** 2026-07-28 — dotfiles copy done (S13 + S3); project `.claude/settings.json` edit **blocked by the permission classifier** (Claude cannot modify its own settings file, even to tighten it). Intended content ready for a human paste — see §0.2 note. S16 note: the render-retro hook already had an anchored matcher; only the Wistia hook was substring-matched |
| 2 | S8, S9, S11, S7-rem, A5 — mechanical hygiene | ☑ **done** 2026-07-28 — S9 note: the skill's whole mechanics were fictional (`scripts/ingest.py` AND `_templates/` don't exist); rewritten against the real `templates/` scaffolds. S11 note: only ONE citation needed fixing (log.md:311) — line 124 cites the already-date-first file |
| 3 | S5 + A7, R9/A3 — factory docs tell the truth | ☑ **done** 2026-07-28 — template count fixed to 12 (they live in `compositions/`, not `templates/`); lesson-scripts README rebuilt without a program table; voice-auditions/ deleted, Ann purged; bonus: design-system/CLAUDE.md's stale "two human checkpoints / MP4 review" QA line corrected |
| 4 | P2 — `endpoints.md` → `config/endpoints.json` | ☐ |
| 5 | S12 — lint-refs.sh into CI | ☐ |
| 6 | R2/A1 — delete the hourly schedule | ☐ |
| 7 | P1 — `.claude/rules/` replaces prose governance | ☐ |
| 8 | P3, R11 — retire dead governance machinery | ☐ ⚠️ GATE (R11) |
| 9 | R4, R6 — import pattern; align the lesson | ☐ ⚠️ GATE |
| 10 | R5/A2 — canonise `preview.sh`, delete `review.py` | ☐ |
| 11 | R7 — reshape `render-qa/` | ☐ ⚠️ GATE · alone |
| 12 | R10 — arm the remaining hooks | ☐ ⚠️ GATE · alone · optional |
| 13 | P4 — unwind `.agents/` | ☐ **last, on purpose** |
| 14 | R12-later/A4 — dotfiles split | ☐ at leisure |
| 15 | File this brief into `audits/` + repoint CLAUDE.md | ☐ **only after 1–13 are done** |

**Approved without further sign-off:** every step except the four marked ⚠️ GATE. Those five items (R4, R6, R7, R10, R11) need an explicit human yes or no first.

### Why this file is still at root

[`CLAUDE.md`](CLAUDE.md) routes `Refactor — plan, status, structural change` here by root-relative path. **This brief must stay at the repo root until STEP 15**, or a fresh session loses its own instructions mid-refactor. STEP 2 files the *other two* briefs into `audits/`; this one moves last, and CLAUDE.md's routing row is updated in the same commit.

---

## §0. OWNER DIRECTIVE + LIVE PLAN — 2026-07-28

**This file is the single source of truth for the refactor.** §1–§3 are lookup tables serving this section; where they conflict with it, this section wins. Executed items are recorded as done, not proposed.

### §0.1 The owner's standing policy (governs all remaining work)

1. **Markdown is not enforceable and does not govern.** Root-level markdown "rulebooks" and "atlases" (GOVERNANCE.md, MAP.md) drift into fiction and are deleted, not corrected. Do not spend effort updating any file that is destined for deletion.
2. **Rules the AI must follow live in `.claude/rules/` (native, discovered, path-scopable — STD-19/STD-20); rules that must *hold* live in hooks and settings (STD-8–STD-11).** Prose is a request; config is enforcement.
3. **Machine-first registries.** Data that scripts and AI consume (endpoints, IDs, integration facts) belongs in JSON/YAML config validated by the linter — not in human-facing markdown that must be hand-corrected in multiple places. The human should never *need* to read it.

### §0.2 Executed 2026-07-28 (this session — all recoverable from git history)

**Deleted outright** (owner order; the "archive-never-delete" convention is explicitly overridden for these): `_heygen-test-preview/`, `operations/`, `programs/`, `references/`, `GOVERNANCE.md`, `MAP.md`, `context/goals.md`.

**Google Drive mirror sync removed entirely** (owner: "not needed, remove all reference"): `.github/workflows/drive-sync.yml` (the only workflow — `.github/workflows/` is now empty), `scripts/build-docx.sh` (existed solely to feed the mirror), `references/google-drive-api.md` (went with `references/`), the Google Drive section + Notes line in `endpoints.md`, and the Drive example in `.claude/skills/kb-audit/SKILL.md`. **Scope note:** `sync.sh` is a *git* sync (pull/commit/push + workspace submodule pointer), not the Drive mirror — it stays. The Drive mentions in `member-support/*` (planned faqs.json publishing), `projects/drive-review-brief.md`, and `scripts/drive-refactor/` concern the team's Google Drive content, not the mirror — untouched. Historical records (`audits/`, `decisions/log.md`, build/snag logs) keep their mentions; history is not rewritten.

**Root `CLAUDE.md` updated:** dropped the six routing rows that pointed at deleted files (goals, team roster, both programs rows, MAP.md, GOVERNANCE.md), removed the GOVERNANCE.md rulebook pointer from Hard Rules (the `_archive/` ban survives as the one hard rule), and softened the false "every multi-file folder has a README hub" promise (closes **S10**).

**`scripts/lint-refs.sh` updated and passing:** now lints `CLAUDE.md` only (checks 1/2/7), critical-files list pruned of deleted paths, `_archive/` added to intentional non-paths. Run 2026-07-28: `lint-refs: healthy` — meaning **S12** (wire it into CI) is unblocked *today*; its old R3 dependency is gone.

**S14 + S15 executed (second pass, 2026-07-28 — the credential shield is now up):** `.gitignore` gained the Claude Code credential/session block — `.claude/.credentials.json`, `.claude/projects/`, `.claude/shell-snapshots/`, `.claude/file-history/`, `.claude/backups/`, `.claude/sessions/`, `.claude/statsig/`, `.claude/todos/`, `.claude/history.jsonl` — so no clone of this repo (including the dotfiles clone holding the live token) can commit it. The dead negation was fixed the same pass: `.vscode/` → `.vscode/*` + `!.vscode/tasks.json`, which now actually re-includes the task file. Verified after the edit: `git check-ignore` matches **no tracked file** (`.vscode/tasks.json`, `.claude/settings*.json`, and every `.claude/skills/**` entry stay tracked). The `.s3_setup_*` rule's false "root-owned, 0600, not readable" comment was corrected to the red team's verified facts. **Step 0 is closed.**

**Root now holds 25 items** (`ls -A` minus `.git`). `.github/` is gone entirely, not just emptied — S12 recreates it.

**STEP 1 surprise (2026-07-28, fourth pass):** the Claude Code permission classifier blocks the AI from editing the project's own `.claude/settings.json` (both Edit and Write), even when the change only *removes* permissions. The dotfiles clone's copy was editable and got S13 (allow-list slimmed to `git/mkdir/ls/cp/python3/./sync.sh`, colon syntax normalized) and S3 (both duplicate reminder hooks removed — working-tree only, deliberately uncommitted in that clone, temporary until A4's dotfiles split). The project copy still needs a **human** to apply S13 + S16; the exact intended file content was staged at the session scratchpad as `settings.json.step1-intended`. S16's real target is only the Wistia-upload hook (bare `grep -q "wistia-upload.sh"` substring — the one that misfired); the render-retro hook already matches anchored invocations.

**A6 executed (third pass, 2026-07-28) — `.devcontainer/postCreate.sh` retired, safeguard preserved.** The container now has exactly one setup path. The brand anti-fabrication safeguard (re-materialize `brand/` in a sparse checkout — the fix for the 2026-07-22 incident where cold subagents fabricated `brand/voice-and-tone.md` into member-facing videos) was folded into `devcontainer.json`'s `postCreateCommand`, which was then validated as both parseable JSON and valid shell before the script was `git rm`'d. Two deliberate omissions, documented in the file: **`scripts/setup.sh` was NOT folded in** — it copies `hooks/` into `~/.claude` and runs `merge-settings.py` to register them globally, which would silently re-arm the hooks that were unplugged on purpose (R10) and re-duplicate the reminder hooks into the dotfiles clone (S3); and **hyperframes is no longer installed globally** — verified that every real invocation goes through `npx` (the only bare `hyperframes …` strings in the repo are prose in logs, docstrings, and comments). *Side benefit: `postCreate.sh` was the only automated caller of `setup.sh`, so S3's fix is now durable rather than something a container rebuild could undo.*

### §0.3 Item status after the directive

| Item | Status now |
|---|---|
| S2 (fix GOVERNANCE.md), S4 (rewrite MAP.md) | **Moot** — files deleted |
| S5 (stale factory docs) | **Open** — template-count fixes and remaining "PUBLISH" phase mentions (e.g. `endpoints.md` Wistia rows) still pending; folded into P2 for endpoints |
| S7 (front door) | **Partially superseded** — `_heygen-test-preview/` deleted rather than archived; filing the audit briefs into `audits/` still open |
| S10 (README-hub promise) | **Done** (§0.2) |
| S12 (linter in CI) | **Unblocked** — linter is green; wire it up any time (it recreates `.github/`, now gone entirely) |
| S14, S15 (credential shield) | **DONE 2026-07-28**, second pass (§0.2) — **Step 0 is closed** |
| S16, S3, S8, S9, S11, S13 | **Unchanged — the remaining to-do list.** All safe-list: reversible, no sign-off needed |
| R1 (Drive mirror) | **Resolved by removal** — no mirror, no alarm needed |
| R3 (archive rules) | **Mostly moot** — GOVERNANCE/MAP gone; CLAUDE.md keeps the `_archive/` ban; only the nested-archive convention question remains, folded into P1 |
| R4, R6, R7 | **Unchanged** |
| R2 (scheduled run) | **ANSWERED → simplified to a deletion.** Owner 2026-07-28: the hourly run is no longer wanted — delete the schedule outright. No pause, no alarm, no revival plan (§0.6 A1) |
| R5 (review tool) | **ANSWERED → re-scoped.** The owner's actual gate tool is `bash scripts/preview.sh <stem>`; the real defect is that it doesn't reliably surface a clickable forwarded URL (§0.6 A2) |
| R9 (voice auditions) | **ANSWERED → cleared to run.** Oxana is final; scope widened to purging every "Ann" reference (§0.6 A3) |
| R12 (dotfiles/credentials) | **ANSWERED → target architecture set.** All secrets in Infisical; the Infisical machine-identity credentials in the Codespaces secret vault (§0.6 A4) |
| R10 (arm hooks/) | **Reframed by P1** — `hooks/governance-check.sh` guards two deleted files and a stale root list; **P3 deletes it** rather than arming it |
| R11 (retire skill-rules.json) | **Unchanged** — coordinated three-file change stands |
| R8 / Q6 (`.agents/`) | **Answered (§0.4) and resolved by P4**, approved 2026-07-28 |
| **P1, P2, P3, P4** | **ALL FOUR APPROVED** by the owner, 2026-07-28 — see §0.5 |
| Q5 (`.s3_setup_*`) | **ANSWERED** — delete the file (§0.6 A5) |
| Q7 (`postCreate.sh`) | **DONE 2026-07-28** — safeguard folded into `devcontainer.json`, script retired (§0.2, §0.6 A6) |
| Q4 (unverified 07-27 claims) | **CLOSED 2026-07-28** — claim 1 verified TRUE and worse than described (folded into S5); claim 2 unrecoverable and already covered by R7 + S11 (§0.6 A7) |
| S5 (stale factory docs) — scope grew | `lesson-scripts/README.md` is the worst offender in the repo: **3 of its 4 real program folders are missing from its own table, and 2 of the 3 it lists don't exist** (§0.6 A7) |

### §0.4 Why `.agents/` lives at root (owner asked; verified this session)

`.agents/` is the **primary skill store**, not a leftover: 10 of the 16 entries in `.claude/skills/` are **symlinks into `.agents/skills/`** (all seven `hyperframes*` skills, `media-use`, `skill-creator` — verified `ls -l` 2026-07-28), and `render-qa/synth_narration.py` + `design-system/frame.md` reference it directly. Deleting or moving it today would kill 10 skills and the TTS step of every build. It cannot be removed until it is unwound. **Proposed unwind (P4):** materialize the 10 symlinks into real directories under `.claude/skills/` (the standard, auto-discovered location — STD-14/STD-15), repoint the two hardcoded references, then delete `.agents/`. **P4 was approved by the owner on 2026-07-28** — so `.agents/` stays only until its step in the execution order (§0.7) comes up, and nothing may touch it before then.

### §0.5 THE FOUR P-ITEMS — **ALL APPROVED 2026-07-28** (enforcement-first replacements; the part the old plan was missing)

> **Approval, stated once and unambiguously: the owner approved P1, P2, P3 and P4 on 2026-07-28.** All four are execution items, not proposals. No further sign-off is required for any of them. The only remaining sign-offs in this brief are the surviving R-items (R4, R6, R7, R10, R11) at the §2 gate.

**P1 — `.claude/rules/` replaces prose governance.**
Create `.claude/rules/` (natively discovered, recursively, per STD-19; path-scoped via `paths` frontmatter per STD-20):
- `rules/repo-hygiene.md` (unconditional): no new root files outside the approved set; archives are read-only, never routing targets; no corrections to files slated for deletion.
- `rules/video-production.md` (`paths: projects/video-production/**`): the always-true video-pipeline constraints currently living in nested CLAUDE.md prose that every session must obey.
- Root `CLAUDE.md` shrinks to: boot line + routing table + tool discipline. Everything else moves to rules (always-load conventions) or skills (procedures) — per STD-1/STD-3.
- **Every MUST gets a mechanism or it isn't a MUST:** each rule that must *hold* is paired with a `PreToolUse` hook or a settings permission entry (STD-8/STD-10/STD-11). A rule with no mechanism is written as a convention, not a guarantee — the false-"live enforcement" failure mode of GOVERNANCE.md must not be recreated in rules files.

**P2 — `endpoints.md` → `config/endpoints.json` (machine-readable, validated, single-write).**
- Schema: top-level object keyed by service (`wistia`, `heygen`, `infisical`, `notion`, `github`, `routines`), each holding entries of `{ name, type, id, url, used_by, verified, notes }`. Non-secret IDs only; secrets stay exclusively in Infisical (unchanged).
- Consumers: scripts read it with `jq`/`python -c` instead of parsing markdown; AI sessions get one routing row (`Integrations, endpoint IDs → config/endpoints.json`); no human ever needs to open it.
- Enforcement (what markdown could never have): lint-refs.sh gains a check that the JSON parses, matches the schema, and contains no obvious secret material (deterministic, CI-able via S12). Rotation = edit one field in one file.
- The narrative history currently in endpoints.md (token-scope probes, key-rotation stories) moves to `decisions/log.md` where history belongs; the registry holds only current facts + `verified` dates. `endpoints.md` is then **deleted** — same policy as GOVERNANCE/MAP.
- **Closed question (was carried from R12, answered 2026-07-28):** the Infisical `identityId`/`clientId` currently published in `endpoints.md` do **not** move into `config/endpoints.json`. Target architecture, owner's words: *all secrets live in Infisical, and the Infisical machine-identity credentials live in the Codespaces secret vault.* So both IDs move to Codespaces secrets (`INFISICAL_CLIENT_ID`, `INFISICAL_IDENTITY_ID`), `scripts/with-secrets.sh` reads them from the environment, and the registry carries only a pointer (`"auth": "codespaces-secret:INFISICAL_CLIENT_ID"`) — never the value. The linter's no-secret-material check enforces it from then on.

**P3 — retire the dead governance machinery.**
`hooks/governance-check.sh` guards two deleted files and a stale hardcoded root list — delete it rather than repair it (supersedes the "fix the gate script" half of R10). The remaining hooks/ scripts stay under R10's one-at-a-time review. R11 (skill-rules.json + skill-eval.sh + the linter/merge-settings references) proceeds as the coordinated change already specified.

**P4 — unwind `.agents/`** as specified in §0.4 (materialize symlinks → repoint 2 references → delete). This closes R8 with a concrete plan replacing the voided one. **Approved 2026-07-28.**

### §0.6 OWNER ANSWERS — round 2, 2026-07-28 (these closed every remaining open question)

| # | Question | Owner's answer | What it changes in the plan |
|---|---|---|---|
| **A1** | Q1 — where the hourly `/produce-video` schedule lives (blocked R2) | *"I'm not sure where this is either, but go ahead and just delete the schedule — we no longer need this hourly scheduled item."* | **R2 collapses from "pause + alarm + revival plan" to "find it once and delete it."** Locating it is now a 2-minute chore, not a blocker: claude.ai → profile/settings → **Scheduled tasks** (routines) → delete anything naming produce-video or SCLA lessons. Nothing needs to survive it, so no alarm step and no revival design. If nothing is found there, the fallback is a `CronList` check in an interactive session. Record the deletion in `decisions/log.md`. **R2 is no longer blocked by anything.** |
| **A2** | Q2 — which review tool is actually used at the preview gate (blocked R5) | *"Usually I just run `bash scripts/preview.sh <stem>` in terminal and hope it opens a browser tab in a port."* — flagged as **an ongoing pain point** | **R5 stops being "pick one of three" and becomes "canonise one and fix it."** Verified this session: `preview.sh` = single-stem previewer, the human's real tool. `review.sh` = multi-build dashboard + preflight gate, wired to the VS Code task "🎬 Review lesson videos" and named in `.devcontainer/devcontainer.json`'s port comment. `review.py` = a rival single-page dashboard wired to **nothing** (its own docstring claims `review.sh` launches it — `review.sh` does not; verified). **Resolution: `preview.sh` is canonical and gets the reliability fix (print the Codespaces forwarded `https://` URL, wait for the port to actually answer, fail loudly if it doesn't — "and hope" must stop being part of the workflow). `review.py` is deleted as an unwired duplicate. `review.sh` is kept only because the VS Code task and devcontainer comment reference it; if the owner never uses that task, delete it and its two tasks.json entries in the same pass.** |
| **A3** | R9 — is the voice choice final (blocked archiving the auditions) | *"Yes — the voice we're going with is Oxana, not Ann. Remove all reference of Ann."* | **R9 is cleared to run, with widened scope.** Per §0.1 policy the 3.2 MB of `design-system/voice-auditions/` is **deleted, not archived** (Kokoro samples are regenerable). "Remove all reference of Ann" hits 2 live files, verified this session: `design-system/frame.md:57` and `design-system/CLAUDE.md:59` (both read "it replaced Ann — Professional"). Oxana's ID `442360a3e0894fbd85024ff64cc2b928` stays pinned in `frame.md:62`, `design-system/CLAUDE.md:57` and `render-qa/synth_narration.py:92` — unchanged. Also drop the two pointers at `design-system/CLAUDE.md` lines 26 and 70. **Not touched:** `decisions/log.md`, `render-qa/snag-log.md` and the one refined lesson script that happens to contain the word — history is not rewritten and lesson prose is not a voice reference. |
| **A4** | R12 / P2 — Infisical IDs, and the broader dotfiles split | *"In a perfect world all secrets would be stored in Infisical, and in Infisical, machine-identity credentials are in the Codespaces secret vault."* | **Target architecture is now stated, so R12 splits into a do-now half and a do-later half.** Do now: move `identityId`/`clientId` to Codespaces secrets, leave only a pointer in `config/endpoints.json` (see P2), untrack `.claude/settings.local.json`, drop the `git push` pre-approval. Do later, at leisure: the dotfiles split. The split is now clearly *desirable* under this architecture — a dotfiles repo that every future Codespace inherits should carry machine setup, not a knowledge base — but with S14's shields up it is no longer urgent. |
| **A5** | Q5 — keep or delete `.s3_setup_FVC8bRn6m` | *"I don't know what this is, so it's probably not important."* | **Delete it.** It is a leftover package listing (user-owned, readable, gitignored, referenced by nothing — red-team verified). The `.s3_setup_*` ignore rule stays so a regenerated one is never committed; its false "root-owned, 0600" comment was corrected during Step 0. |
| **A6** ✅ **EXECUTED** | Q7 — revive or retire `.devcontainer/postCreate.sh` | *"I don't know what this is — make the logical choice according to best practices."* → then, on review: *"you can retire postCreate.sh."* | **DONE 2026-07-28 — see §0.2 for what was actually executed.** Decision was **fold, then retire — one file ends up holding container setup.** Verified: `postCreate.sh` (26 lines, dead code) and `devcontainer.json`'s inline `postCreateCommand` both install ffmpeg + Infisical, so only two things in the script are *not* live: (a) the **brand anti-fabrication safeguard** — re-materializing `brand/` in a sparse checkout, added after the 2026-07-22 incident where cold subagents fabricated `brand/voice-and-tone.md` because it wasn't on disk; (b) `npm i -g hyperframes` + `bash scripts/setup.sh`. Best practice is one setup path, not two that drift: move the safeguard (and the hyperframes install) into the inline `postCreateCommand`, then delete `postCreate.sh`. Rationale — the safeguard guards against *silent fabrication of brand voice in member-facing videos*; it cannot live in the branch that never runs. **Do not simply retire it: that ships the repo with a known incident's fix removed.** |

| **A7** | Q4 — are yesterday's two un-re-verified claims accurate (owner asked what was needed to check them) | Nothing was needed — **verified directly against the repo, 2026-07-28** | **First, the bad news about the source:** `repo-audit-brief-2026-07-27.md` **no longer exists and is unrecoverable** — it was never committed (`git log --all` and a full `rev-list --objects` scan both find nothing), and it has since been removed from root. The two claims survive only as this brief's one-line paraphrase of them. Both were checkable from that paraphrase anyway: **① "lesson-scripts README program tables" — CONFIRMED, and materially worse than described.** `projects/video-production/lesson-scripts/README.md`'s "Live programs" table lists `early-career-boost`, `career-readiness-accelerator`, `scla-leadership-program`. On disk there are four program folders: `career-transitions`, `early-career-boost`, `entrepreneur-accelerator`, `mid-career-momentum`. So **two of the three listed programs do not exist**, and **three of the four that do exist are absent from the table** — only `early-career-boost` is right. Its "Older programs" note repeats both phantom slugs. The same file also links to `programs/` and `GOVERNANCE.md` (**both deleted in §0.2**), routes to `endpoints.md` (deleted by P2), and still documents the retired **PUBLISH** phase and an "MP4 review" gate removed 2026-07-22. **Folded into S5 and scheduled at §0.7 STEP 3.** **② "folder-skeleton variance" — unrecoverable, and already covered.** The specifics died with the source document; the general claim (folders don't share a consistent shape) is exactly what **R7** (render-qa's flat heap) and **S11** (audits' two naming styles) already address. Nothing further to chase. |

**Nothing is open after this round.** Both former open questions are closed:
- **Q3** — whether the `rclone` Drive credential is valid. **Permanently moot:** the mirror was deleted entirely (§0.2), so there is nothing to revive.
- **Q4** — closed by **A7** above: claim ① confirmed and folded into S5, claim ② unrecoverable and already covered by R7 + S11.

**The only decisions left in this entire brief are the five §2-gate R-items: R4, R6, R7, R10, R11.**

### §0.7 EXECUTION ORDER — the live plan

Every step below is approved. `⚠️` marks the five items still needing a yes/no at the §2 gate; everything else runs without further sign-off.

**Execution contract (from §0.0):** one step per pass · read only the files the step names · verify every claim before editing · `bash scripts/lint-refs.sh` must print `lint-refs: healthy` after every step · one commit per step (`refactor(step-N): …`) · tick the §0.0 ledger · stop and report. **Do not chain steps.**

**Per-step verification commands** (run in addition to the linter):

| Step | Verify with |
|---|---|
| 1 | `python3 -c "import json;[json.load(open(p)) for p in ['.claude/settings.json','.claude/settings.local.json']]"` then confirm `rm`/`find`/`cat`/`head`/`tail` are absent from both allow-lists |
| 2 | `git log --oneline -1 -- audits/` shows the moves; `git ls-files scripts/__pycache__` returns empty; `ls .s3_setup_* 2>&1` says "No such file" |
| 3 | `grep -rn "nine templates" projects/` returns nothing; `grep -rniI "\bAnn\b" projects/video-production/design-system/` returns nothing; the program table in `lesson-scripts/README.md` matches `ls projects/video-production/lesson-scripts/` |
| 4 | `python3 -c "import json;json.load(open('config/endpoints.json'))"`; `grep -rn "endpoints.md" --include='*.md' --include='*.sh' --include='*.py' .` returns nothing outside history files |
| 5 | the workflow file parses and the job passes on a test push |
| 6 | the schedule is gone from claude.ai → Scheduled tasks; the deletion is logged in `decisions/log.md` |
| 7 | `.claude/rules/*.md` load in a fresh session; every MUST in them names its hook or settings entry |
| 8 | `bash scripts/lint-refs.sh` still healthy **after** the coordinated three-file R11 edit — this is the step most likely to turn the linter permanently red |
| 10 | `bash scripts/preview.sh <stem>` prints a working forwarded URL and fails loudly when the port doesn't answer |
| 11 | every positional path still resolves — re-run a full build before committing |
| 13 | all 16 skills resolve in a fresh session **and** one TTS run succeeds, *before* `.agents/` is deleted |

```
STEP 0  ✅ DONE  S14, S15 ─ credential shield + dead ignore rule ─────────── executed 2026-07-28
   │             .gitignore now blocks .claude/.credentials.json + session state
   │             in every clone; .vscode/* negation actually works
   ▼
STEP 1  S13, S16, S3 ─ settings & hook hygiene ──────────────── ~30 min ── no risk
   │  · S13: drop rm / find / cat / head / tail from BOTH settings files'
   │         allow-lists (project + the dotfiles clone's copy); normalize the
   │         mixed Bash(x *) / Bash(x:*) syntax; kill the doubled cp entry
   │  · S16: tighten both reminder hooks to match real invocations, not any
   │         command containing the substring (one misfired this session and
   │         urged a purge script after a read-only search)
   │  · S3:  de-duplicate the 2 reminder hooks out of the dotfiles clone's
   │         settings (temporary until A4's dotfiles split; note it as such)
   ▼
STEP 2  S8, S9, S11, S7-rem, A5 ─ mechanical hygiene ─────────── ~35 min ── no risk
   │  · S8:  untrack scripts/__pycache__/
   │  · S9:  add the missing frontmatter label to new-from-template, and fix
   │         its dead `scripts/ingest.py` instruction
   │  · S11: rename audits/ to one date-first style + fix the 2 citations in
   │         decisions/log.md (lines 124, 311)
   │  · S7-rem: file TWO briefs into audits/ — repo-audit-redteam-2026-07-28.md
   │         and repo-standard-2026-07-28.md. NOT this one: CLAUDE.md routes to
   │         it by root path and a fresh session would lose its instructions
   │         mid-refactor. This brief moves at STEP 15. (All three are already
   │         committed as of 7bcb2f9, so every move is undoable.)
   │  · A5:  delete .s3_setup_FVC8bRn6m
   ▼
STEP 3  S5, R9(A3) ─ factory docs tell the truth ─────────────── ~45 min ── no risk
   │  · S5:  "nine templates" → 12 in projects/video-production/CLAUDE.md,
   │         design-system/CLAUDE.md, design-system/AGENTS.md, frame.md
   │  · S5+ (A7): REBUILD lesson-scripts/README.md — it is the repo's most
   │         wrong live doc. Its "Live programs" table names 2 folders that
   │         don't exist (career-readiness-accelerator, scla-leadership-program)
   │         and omits 3 that do (career-transitions, entrepreneur-accelerator,
   │         mid-career-momentum); the "Older programs" note repeats both
   │         phantoms; it links to programs/ and GOVERNANCE.md (both DELETED);
   │         it documents the retired PUBLISH phase and the MP4-review gate
   │         removed 2026-07-22. Consider dropping the program table entirely
   │         rather than re-hand-maintaining it — `ls` already answers it
   │         (STD-22: don't write down what the file tree shows)
   │         (its endpoints.md link dies with that file in STEP 4)
   │  · A3:  delete voice-auditions/ (3.2 MB); purge "Ann" from frame.md:57 and
   │         design-system/CLAUDE.md:59; drop the pointers at CLAUDE.md 26 + 70
   ▼
STEP 4  P2 ─ endpoints.md → config/endpoints.json ────────────── ~1 h ──── the machine-first turn
   │  · write config/endpoints.json (schema in §0.5); move the narrative
   │    history to decisions/log.md; move the Infisical IDs to Codespaces
   │    secrets per A4 and leave only a pointer; repoint scripts to jq;
   │    swap CLAUDE.md's routing row; DELETE endpoints.md
   │  · extend lint-refs.sh: JSON parses + matches schema + no secret material
   ▼
STEP 5  S12 ─ wire lint-refs.sh into CI ──────────────────────── ~20 min ── additive
   │  · recreates .github/workflows/ (the dir is gone); non-blocking on push;
   │    linter is green today, so it starts green — the whole point
   ▼
STEP 6  R2(A1) ─ delete the hourly schedule ──────────────────── ~10 min ── ⚠️ live config
   │  · A1: find and DELETE the hourly /produce-video schedule; log it in
   │        decisions/log.md. claude.ai → Scheduled tasks; fallback CronList
   │  · A6 ✅ ALREADY DONE 2026-07-28 — postCreate.sh retired, brand safeguard
   │        folded into devcontainer.json, setup.sh deliberately NOT folded (§0.2)
   ▼
STEP 7  P1 ─ .claude/rules/ replaces prose governance ────────── ~1 h ──── the enforcement turn
   │  · rules/repo-hygiene.md (unconditional) + rules/video-production.md
   │    (paths: projects/video-production/**); CLAUDE.md shrinks to boot line +
   │    routing table + tool discipline
   │  · EVERY "must" gets a PreToolUse hook or a settings entry, or it is
   │    written as a convention — do not recreate GOVERNANCE.md's false
   │    "live enforcement" in a new file
   ▼
STEP 8  P3, R11 ⚠️ ─ retire dead governance machinery ────────── ~40 min ── ⚠️
   │  · P3: delete hooks/governance-check.sh outright
   │  · R11 ⚠️: retire skill-eval.sh + skill-rules.json as ONE coordinated
   │            three-file change (also edit lint-refs.sh lines 69/115 and
   │            scripts/merge-settings.py) or the linter goes red forever
   ▼
 ╔═══ REMAINING SIGN-OFF GATE — R4, R6, R7, R10, R11 only (§2) ═══╗
   ▼
STEP 9  R4 ⚠️, R6 ⚠️ ─ import pattern; align the lesson ──────── ~45 min ── ⚠️ member content
   │  · R4: CLAUDE.md imports AGENTS.md (STD-31), not the reverse
   │  · R6: mid-career-momentum's "Rebuild" is canonical; fix career-transitions
   ▼
STEP 10 R5(A2) ─ canonise preview.sh, delete review.py ───────── ~30 min
   │  · make preview.sh print the forwarded https:// URL, wait for the port to
   │    answer, and fail loudly — end "and hope it opens a tab"
   ▼
STEP 11 R7 ⚠️ ─ reshape render-qa/ ───────────────────────────── ~1 h ──── ⚠️ pipeline paths
   │  · scripts compute the repo root POSITIONALLY (synth_narration.py uses
   │    parents[3]) — any depth change silently breaks path resolution.
   │    Check every reference. Add a log-rotation policy (snag-log.md = 502 KB).
   │    Window is open now: renders-hyperframes/ is empty.
   ▼
STEP 12 R10 ⚠️ ─ arm the remaining hooks, ONE at a time ──────── ⚠️ your call, optional
   │  · they were deliberately unplugged once; pre-tool.sh once killed video
   │    builds mid-render. Generous budget, individual review, never as a pack.
   ▼
STEP 13 P4 ─ unwind .agents/ ─────────────────────────────────── ~1 h ──── LAST, on purpose
   │  · materialize the 10 symlinks into real dirs under .claude/skills/
   │  · repoint render-qa/synth_narration.py and design-system/frame.md
   │  · verify all 16 skills still resolve + one TTS run succeeds
   │  · THEN delete .agents/  (618 files, 72% of the repo)
   ▼
STEP 14 R12-later(A4) ─ dotfiles split ───────────────────────── at leisure
   │             · desirable under A4's architecture, no longer urgent (S14 is up)
   ▼
STEP 15 CLOSE OUT ─ file this brief, restore the routing ─────── ~10 min
                 · git mv repo-audit-brief-2026-07-28.md audits/
                 · update CLAUDE.md's "Refactor" routing row to the new path,
                   or delete the row if the refactor is finished — SAME commit
                 · record the refactor's completion in decisions/log.md
                 · ONLY after steps 1-13 are ticked in the §0.0 ledger
```

**Two ordering rules that are not negotiable:** P4 runs **last** (until then, nothing touches `.agents/` — it is the live skill store for 10 of 16 skills and every build's TTS step), and R7 + R10 run **alone**, never two structural items in one pass.

---

## §1. ITEM DETAIL — approved, no sign-off needed


Reversible, touch nothing that's running, approved. Look up a row when a §0.7 step names it. *(The original S1 and S6 did not survive this bar — they are R10 and R11 in §2.)*

> **Post-directive status (§0.3 is authoritative):** **S14 and S15 are DONE** (executed 2026-07-28 — see §0.2). **S2 and S4 are moot** (GOVERNANCE.md and MAP.md were deleted, not corrected). **S10 is done.** **S12's "sequenced after R3" caveat is void** — R3 is moot and the linter already reports `lint-refs: healthy`, so S12 can be wired today and starts green. **S7 is partially superseded** — `_heygen-test-preview/` was deleted rather than archived; what remains is filing the other two root briefs into `audits/` (this one moves at STEP 15). Still to do: **S3, S5, S8, S9, S11, S12, S13, S16.** Where a row below describes archiving, §0.1 has since replaced that with deletion — git history is the archive.
>
> **S5's scope grew (A7, verified 2026-07-28).** Beyond the template count, `projects/video-production/lesson-scripts/README.md` is now the most wrong live document in the repo: its "Live programs" table names **two programs that don't exist** and **omits three that do**, and it links to `programs/` and `GOVERNANCE.md`, both deleted. Details in §0.6 A7; fix scheduled at §0.7 STEP 3.

| ID | What changes, in plain words | So what — what improves for you | Which STD-n it closes | Why it's safe |
|---|---|---|---|---|
| S2 | Correct GOVERNANCE.md's false claims: protections are NOT live, force-push is NOT blocked (the deny-list is empty — verified), the settings file carries two hooks not one, and the approved-root list gains its 5 missing real items by name (`.agents`, `.github`, `.vscode`, `skills-lock.json`, `repo-standard-2026-07-28.md`) and drops the deleted `_archive` entry. Caution: GOVERNANCE.md sits at 996 of its 1000-word budget — trim as you add | The rulebook stops promising protections you don't have — false safety is worse than none. (Note: the *enforced* copy of the approved-root list is hardcoded in `hooks/governance-check.sh`; R10 must fix that too if the hooks are ever armed) | STD-22, STD-11 | Words-only edits |
| S3 | Remove the duplicate copy of the 2 video-reminder hooks from the global settings file — which the red team found is actually the tracked settings file of a **second clone of this same repo** (this repo doubles as the machine's dotfiles). The project copy stays | Each reminder currently fires twice. Honest caveat: an edit in that second clone is temporary — a dotfiles re-sync can restore it. The durable fix is R12's decision about the dotfiles arrangement | STD-21 | Behavior in this repo unchanged; revert = paste back |
| S4 | Rewrite MAP.md to match reality — verified false today: says the agents folder doesn't exist (it does, 4 files), lists 2 of 16 skills, misplaces `kb-integration-plan.md`, omits half of `scripts/` and `references/`, and claims an @-import that isn't in CLAUDE.md. (Its `_archive/` routing lines are carved out of this item — they belong to the R3 decision, not to housekeeping) | The repo's atlas stops sending readers to places that don't exist | STD-22, STD-23 | Words-only edits |
| S5 | Fix stale factory docs: "nine templates" (real count: 12, counted) in the 4 files that say it — `projects/video-production/CLAUDE.md`, `design-system/CLAUDE.md`, `design-system/AGENTS.md`, `design-system/frame.md` — and the retired "PUBLISH" phase still named in `endpoints.md` and `lesson-scripts/README.md` | The AI stops planning around a phase and a template count that changed weeks ago | STD-22 | Words-only edits |
| S7 | Clean the front door: commit-then-file yesterday's `repo-audit-brief-2026-07-27.md` into `audits/` (it's currently untracked, so committing first is what makes the move undoable), file THIS brief and the red-team report there too once acted on, and archive `_heygen-test-preview/` (2.0 MB, referenced by nothing) into a recreated root `_archive/` — the same convention the still-living nested `_archive/` folders use. R3 owns the rule governing that folder | The root shows only real entry points | no citation — general hygiene | Moves and archives only, never deletes |
| S8 | Stop tracking `scripts/__pycache__/` (one machine-generated cache file is committed, contradicting the ignore list — verified) | No junk churn in future commits | no citation — general hygiene | The file regenerates automatically |
| S9 | Add the missing label header to the `new-from-template` skill (the only one of 16 without it — verified; its menu entry currently reads as a filename) — and fix or remove the dead command inside it: its body tells the AI to run `scripts/ingest.py`, which does not exist | The AI can pick that skill reliably — and no longer picks a skill whose first instruction is broken | STD-16 | Two small edits to one file |
| S10 | Fix root CLAUDE.md's promise that "every multi-file folder has a README hub" — `brand/`, `audits/`, `hooks/`, and `scripts/` have 3+ files and no hub (verified). Decision made: **soften the claim now** (one line); adding the 4 hubs is optional follow-up work, not part of this item | The AI stops hunting for guide files that don't exist, on every session | STD-22 | One-line edit |
| S11 | Rename the 3 dated files in `audits/` to one date-first naming style (`confidence-levels.md` is undated and stays as-is) — **and update the two places that cite the old names**: `decisions/log.md` lines 124 and 311 (the original "nothing references these" claim was false) | Audit history reads in order at a glance, and no historical citation breaks | no citation — general hygiene | Renames plus two citation edits, all in one commit |
| S12 | Make the repo's own health-checker (`scripts/lint-refs.sh`) run automatically on every push, non-blocking. **Sequenced AFTER R3**: today the linter exits 1 with 8 warnings, every one an `_archive/` reference that only R3's rewrite can clear — added earlier, the check would be red on every push from day one, which teaches everyone to ignore it | Doc drift gets caught the week it happens, not at the next big audit | no citation — general hygiene (the same request-vs-guarantee *principle* as STD-8, which itself is about AI hooks, not CI) | Additive check; runs after pushes, can't block them (no branch protection currently requires it) |
| S13 | Remove `rm` (delete), plus `cat`/`head`/`tail`/`find`, from the pre-approved command lists in both settings files (project, and the second clone's copy — see S3). CLAUDE.md's own rules ban those commands while settings pre-approve them; settings win (verified in both files). While in there, normalize the mixed `Bash(x *)` / `Bash(x:*)` syntax and the doubled `cp` entry | The AI can no longer delete files without asking you first | STD-11 | One-line edits. Honest worst case: an *unattended* run that needed one of these commands fails instead of prompting — acceptable because R2 pauses the only unattended routine, and the pipeline's skills don't use bare `rm` (verified) |
| S14 | **Do this first, today (~10 min):** add ignore rules for the AI's credential and session files — `.claude/.credentials.json`, `.claude/projects/`, `.claude/shell-snapshots/`, `.claude/file-history/`, `.claude/backups/`, `.claude/sessions/` — so no clone of this repo can ever accidentally commit a live login token. A live token sits unignored in the dotfiles clone right now, with publish commands pre-approved | Closes the single worst outcome this repo could produce | no citation — security hygiene | Ignore rules only; touches no tracked content |
| S15 | Fix the dead `.gitignore` rule: `!.vscode/tasks.json` can never work while `.vscode/` itself is excluded (git can't re-include inside an excluded directory — the file is only tracked today because it was force-added). Fix: `.vscode/*` + `!.vscode/tasks.json` | The ignore file stops lying about what it protects | no citation — general hygiene | Pattern fix only; tracking state unchanged |
| S16 | Tighten the two reminder hooks' triggers: both fire on a bare substring match — one fired on a read-only search this session and asserted "a Wistia upload just ran", urging the AI to run the archive/purge script. Match on actual invocation, not on any command containing the text | A misfiring reminder that urges a destructive cleanup is a booby trap for future AI sessions | STD-9 (make the trigger deterministic) | Matcher-only edit in the hook definitions; same commands, stricter trigger |

---

## §2. ITEM DETAIL — the five that still need a yes/no


Each needs an explicit yes or no before its ⚠️ GATE step runs. "No" is a valid answer — nothing else in the plan depends on these unless a row says so.

> **Post-directive status (§0.3 is authoritative).** Seven of the twelve are settled: **R1 resolved by removal** · **R3 mostly moot** · **R8 answered and superseded by P4 (approved)** · **R2, R5, R9, R12 answered 2026-07-28 — see §0.6, and the ✅ notes in their rows below.** **Only five still want a yes/no from you: R4, R6, R7, R10, R11.**

About the recorded confirmations: yesterday's brief and this one record owner decisions dated 2026-07-28 on **six** items (R1, R2, R3, R4, R6, R8). The red team could not verify those conversationally-recorded confirmations from the filesystem — and found that **R8's was given against a false premise and is void** (see its row) and R4's supporting claim is contradicted by repo evidence. Treat each ⚠️ GATE step as where the owner *confirms or vetoes*, including the pre-recorded ones; the recorded answers are listed so nobody starts from zero.

| ID | What changes | Which STD-n it closes | What breaks if this goes wrong | How I'd undo it | My recommendation |
|---|---|---|---|---|---|
| R1 | **Stop the failing Drive mirror**: disable `.github/workflows/drive-sync.yml`, or finish its setup (the `GDRIVE_TARGET` variable was never set — verified from the failure logs; last 100 runs: 100 failures, 0 successes — the run dies before copying anything) | no citation — general hygiene (silent failure) | Disabling shelves a feature the team once decided on; finishing it would suddenly publish the whole knowledge base to Drive in one shot — pause on whether that's wanted | Re-enable the workflow file (one line) | ✅ recorded 2026-07-28: disable, and add an alarm step before it's ever revived |
| R2 | **Pause the scheduled `/produce-video` run** until its missing credentials/tools are installed — it has fired 24+ times, roughly hourly, every run ending at the same wall (verified via commit history and its own log). **Depends on Q1**: we don't yet know where this schedule is configured, so "pause" can't be executed until Q1 is answered | no citation — general hygiene (silent failure) | If the blocker clears while paused, new scripts sit unprocessed until someone notices | Un-pause the schedule | ✅ **SETTLED 2026-07-28 — simpler than proposed: DELETE it, don't pause it.** Owner: *"we no longer need this hourly scheduled item."* No alarm, no revival design, no Q1 blocker — just locate and remove (§0.6 A1), then log it. §0.7 STEP 6 |
| R3 | **Rewrite the archive rules to match reality**: CLAUDE.md's #1 hard rule, five GOVERNANCE.md passages, and MAP.md all govern the root `_archive/`, deleted 2026-07-23 (commit `bed5ff7`, verified) with no log entry. The rewrite must decide the go-forward convention, because archives aren't dead here: `projects/video-production/_archive/` is still tracked (and stale), `renders-hyperframes/_archive/` is where the pipeline's own hooks file retired work, and S7 recreates root `_archive/` as the destination for archived items. Also update the hardcoded `APPROVED_ROOT` list in `hooks/governance-check.sh` (it still approves the deleted folder) so R10 doesn't arm a stale gate. This item is also what clears the doc-linter's 8 warnings, unblocking S12 | STD-22 (aspirational rules) | If that deletion was actually an accident, rewriting the rules ratifies a mistake — restoring from git history is the alternative | Git history still holds the deleted folder; rules can be reverted | ✅ recorded 2026-07-28: the deletion was intentional; proceed with one coherent edit |
| R4 | **Unify the two AI instruction files** in `design-system/` (CLAUDE.md, 80 lines + AGENTS.md, 89 lines — both exist, both stale on the template count). The official docs (STD-31) endorse the *reverse* of the original plan: keep `AGENTS.md` and have `CLAUDE.md` import it, so other tools keep their entry point. That matters here: the recorded confirmation said "nothing else reads AGENTS.md", but repo evidence contradicts it — `.agents/skills/hyperframes-core/references/subagent-dispatch.md:30` shows a non-Claude tool's standing grant living in the workspace AGENTS.md, and `render-qa/BUILD-LOG.md:552` lists it as a maintained doc | STD-31 | Merging *into* CLAUDE.md and stubbing AGENTS.md could sever a non-Claude tool's entry point | Both files stay in git; the import line is one edit | ✅ do it — but via the STD-31 import pattern (CLAUDE.md imports AGENTS.md), which makes the "who else reads it" question moot |
| R5 | **Pick one review tool**: `scripts/review.sh` and `scripts/review.py` are two implementations of the same job; the editor task list (`.vscode/tasks.json`) wires the `.sh` (verified). Red team adds a third candidate: `scripts/preview.sh`, which the pipeline's own snag log tells humans to run | no citation — duplicates | Repointing to the wrong one breaks the preview step a human uses at the video gate | All stay in git; repoint is one line | ✅ **SETTLED 2026-07-28 — and re-scoped.** The owner's real tool is `bash scripts/preview.sh <stem>`, *"and hope it opens a browser tab in a port"* — that hope is the actual defect. **`preview.sh` is canonical and gets the reliability fix; `review.py` is deleted (wired to nothing — verified); `review.sh` survives only on the VS Code task's account.** §0.6 A2, §0.7 STEP 10 |
| R6 | **Fix the contradictory lesson**: two programs ship "Four Kinds of Career Transition" with incompatible definitions — in `career-transitions/`, "Rebuild" = forced AND dramatic; in `mid-career-momentum/`, "Rebuild" = forced but near your field (verified by reading both scripts) | no citation — member-facing content integrity | Standardizing on the wrong framework publishes wrong teaching to members | Old script text stays in git | ✅ recorded 2026-07-28: mid-career-momentum's version is canonical; align `career-transitions/` before either renders |
| R7 | **Reshape `render-qa/`**: 15 items — 10 top-level code files (13 counting `tests/`), two giant append-only logs (`snag-log.md` alone is 502 KB), and docs — in one flat folder. Red team caution: these scripts compute the repo root positionally (e.g. `synth_narration.py` uses `parents[3]`), so ANY depth change silently breaks path resolution — every reference must be checked. Include a rotation policy for the logs. Timing note: `renders-hyperframes/` is currently empty, so the "between build cycles" window is open right now | no citation — folder-shape hygiene | The video pipeline's scripts and hooks reference these paths; a careless move breaks the factory | Moves tracked in git; revert restores paths | ⏸️ wait — do it alone, checking every reference, ideally soon while no build is in flight |
| R8 | **Resolve the skill-store layout — RE-PLANNED, original version was wrong and dangerous.** The original brief called `.agents/` a "duplicate pack" with "10 files byte-identical to `.claude/skills/`" and recorded a confirmation to archive it. The red team found those 10 entries are **symlinks** — `.agents/` is the *primary* store (618 files; 22 skills, of which 10 are linked into `.claude/skills/` and 12 aren't), and `render-qa/synth_narration.py` plus `design-system/frame.md` reference it directly. **Archiving it would have killed 10 of 16 skills and the TTS step of every build.** The recorded confirmation is void — it answered a false question. Real options: (a) keep `.agents/` as canonical and document it as intentional, or (b) materialize the 10 symlinks into real files under `.claude/skills/`, repoint the two hardcoded references, and only then archive what remains | STD-14, STD-15 | Option (b) done carelessly breaks skill discovery and the render pipeline | Archive-never-delete still applies; symlinks are restorable from git | ⏸️ wait — needs a fresh decision on the true question (see Q6). Do nothing to `.agents/` until then |
| R9 | **Archive 3.2 MB of voice-audition audio** in `design-system/voice-auditions/` (size verified) — including editing the two places `design-system/CLAUDE.md` (lines 26 and 70) points readers at it | no citation — bloat | If the voice choice ever reopens, auditions must be regenerated | Archive, never delete | ✅ **SETTLED 2026-07-28 — cleared, and widened.** Owner: *"the voice we're going with is Oxana, not Ann. Remove all reference of Ann."* Per §0.1 the auditions are **deleted, not archived** (Kokoro samples regenerate). Plus: purge the two live "Ann" lines (`frame.md:57`, `design-system/CLAUDE.md:59`) and the two pointers (`design-system/CLAUDE.md` 26, 70). Oxana's ID stays pinned in all three places. History files keep their mentions. §0.6 A3, §0.7 STEP 3 |
| R10 | **(was S1 — red team reclassified.) Arm the protection scripts in `hooks/`** by registering them in the project settings file. Why this is not safe housekeeping: (a) they were armed once and **deliberately unplugged** (commits `bc1dbde` → `32ce4d0`) — arming reverses a recorded decision; (b) `pre-tool.sh` hard-blocks sessions at a tool-call budget, and its earlier version "killed video sessions mid-build" (decisions/log.md line 172) — a mid-render block would sever the render→upload pass; (c) the gate script's hardcoded approved-root list is stale (still approves the deleted `_archive`, omits `.github`/`.vscode`/`.agents`) and would block legitimate new files including S12's own workflow; (d) "tested" was never demonstrated — no run logs exist; (e) two of the candidates aren't protections at all: `doctor.sh` is a manual utility, and `cleanup-worktrees.sh` force-deletes git worktrees on every session end | STD-8 (mechanism), STD-9, STD-21 | A bad hook blocks the video factory or legitimate work, silently | Registration is a one-file edit; unregistering restores today's state | ⏸️ your call — if yes: fix the gate script's list first (with R3), set the budget generously, review each of the 7 scripts individually, and arm them one at a time, not as a pack |
| R11 | **(was S6 — red team reclassified.) Retire the hand-maintained skill list** (`hooks/skill-eval.sh` + `hooks/skill-rules.json`, which lists 4 of 16 skills). It is NOT "referenced by nothing": the health-checker `scripts/lint-refs.sh` lists `skill-rules.json` as a critical file and parses it (lines 69, 115) — archiving it as-is makes the linter fail forever (and S12's future check with it); `scripts/merge-settings.py` also registers `skill-eval.sh`. Retiring means a coordinated edit to those two scripts in the same change | STD-15, STD-16 | Done as a simple move, the repo's own health check goes permanently red | All files stay in git | ✅ do it — but as the coordinated three-file change, not a move |
| R12 | **(new — red team.) Decide the dotfiles/credentials architecture.** This repo doubles as the machine's Codespaces dotfiles repo (a second clone at the persisted-dotfiles path is what `~/.claude` points into). Consequences to decide on: every future Codespace for ANY repo inherits this whole knowledge base and its permissive settings; the tracked `.claude/settings.local.json` (which should be personal/untracked) pre-approves `git push` and auto-enables all project MCP servers; and `endpoints.md` publishes an Infisical clientId + identityId (half of a credential pair). Options: keep the arrangement knowingly (with S14's shields in place), or split dotfiles into their own repo; either way, un-track `settings.local.json` and drop the push pre-approval | STD-11 | Status quo leaves publish-capable pre-approvals pointed at a tree containing live credentials | Settings edits are one-line reverts; the dotfiles split is a new repo, not a deletion | ✅ **SETTLED 2026-07-28 — target architecture stated.** Owner: *"in a perfect world all secrets would be stored in Infisical, and in Infisical machine-identity credentials are in the Codespaces secret vault."* So: the `identityId`/`clientId` **move to Codespaces secrets** and `config/endpoints.json` carries only a pointer (P2, §0.7 STEP 4); untrack `settings.local.json` + drop the push pre-approval in the same pass. The dotfiles split is now clearly desirable under that architecture but is **not urgent** with S14's shields up — §0.7 STEP 14, at leisure. §0.6 A4 |

---

## §3. TARGET STATE — what "done" looks like

**AFTER — once §0.7 is executed (21 root items; ⚠️ = only if that R-item clears its gate):**

```
SCLA-Profile/
├── CLAUDE.md ..................... ✅🤖 boot line + routing table + tool discipline, nothing else (P1)
├── skills-lock.json .............. ✅📋 unchanged
├── scla.config.yml / sync.sh ..... ✅ unchanged
├── .gitignore .................... ✅⚙️ DONE — credential shield up, negation fixed (S14, S15)
├── .mcp.json ..................... ✅⚙️ unchanged
├── config/
│   └── endpoints.json ............ ✅⚙️📋 machine-first registry: schema-validated, linter-checked, no human reads it (P2)
│                                      Infisical IDs are NOT here — a pointer to the Codespaces secret, per A4
├── .claude/
│   ├── rules/                        ⭐ NEW — where rules the AI must follow actually live (P1)
│   │   ├── repo-hygiene.md ....... ✅🤖 unconditional; every MUST paired with a hook or a settings entry
│   │   └── video-production.md ... ✅🤖 paths: projects/video-production/** — loads only in the factory (STD-20)
│   ├── settings.json ............. ✅⚙️ rm/find/cat/head/tail ask first (S13); hook matchers tightened (S16)
│   ├── settings.local.json ....... ✅⚙️ UNTRACKED; no git-push pre-approval (R12/A4)
│   ├── skills/  (16 real dirs) ... ✅🤖 all real directories, no symlinks, all labelled (S9 + P4)
│   └── agents/  (4 QA agents) .... ✅🤖 unchanged
├── .agents/ ...................... ⛔ DELETED — 618 files unwound into .claude/skills/, 2 references repointed (P4)
├── .devcontainer/ ................ ✅⚙️ ONE setup path; the brand anti-fabrication safeguard lives in it (A6)
├── .vscode/ ...................... ✅⚙️ tasks point only at tools that exist and are used (A2)
├── .github/workflows/ ............ ✅⚙️ RECREATED for one job: lint-refs.sh on push, non-blocking, green from day one (S12)
├── hooks/ ........................ ✅⚙️ governance-check.sh gone (P3); skill-eval pair retired as a coordinated
│                                      3-file change (R11 ⚠️); survivors armed one at a time or not at all (R10 ⚠️)
├── audits/ ....................... ✅📋 one date-first naming style (S11) + all three briefs filed here (S7-rem, STEP 15)
├── brand/ context/ decisions/ .... ✅ unchanged — decisions/log.md gains endpoints' narrative history (P2),
│                                      the schedule deletion (A1), and the citation fixes (S11)
├── member-support/ partnerships/ templates/ ✅ unchanged
├── scripts/ ...................... ✅ preview.sh is canonical AND reliable — prints the forwarded URL, waits for the
│                                      port, fails loudly (A2); review.py deleted; __pycache__ untracked (S8);
│                                      lint-refs.sh also validates config/endpoints.json (P2)
└── projects/video-production/ .... ✅ the factory, honest docs
    ├── design-system/ ............ ✅ CLAUDE.md imports AGENTS.md (R4 ⚠️, STD-31); "12 templates" everywhere (S5);
    │                                 zero "Ann" references; voice-auditions/ deleted (A3)
    ├── lesson-scripts/ ........... ✅ one "Rebuild" definition — mid-career-momentum's (R6 ⚠️)
    ├── _archive/ ................. ✅ governed by rules/repo-hygiene.md: read-only, never a routing target (P1)
    └── render-qa/ ................ 🔄 code / logs / docs separated, every positional path re-verified,
                                       logs on a rotation policy (R7 ⚠️)
```

Legend: ✅ done · ⚠️ only if that R-item clears its gate · 🔄 reshaped · ⛔ deleted · ⭐ new · 🤖 read by the AI · 👤 read by humans · ⚙️ read by machinery (git, CI, the editor) · 📋 a log or registry.

*The current-state tree was deleted in the 2026-07-28 prune: it would have been false the moment STEP 1 ran, which is exactly the drift §0.1 exists to prevent. `ls` and `git status` are the live tree. This one is the target.*

| | Now | After | Why that matters |
|---|---|---|---|
| Top-level items | 25 | 21 — all three briefs filed into `audits/`, `.s3` junk and `.agents/` gone, `endpoints.md` replaced by `config/`, `.github/` back | The front door shows only real entry points |
| Files that can go false | `endpoints.md` + 4 stale factory docs + a hand-maintained skill list | 0 — the registry is JSON the linter validates on every push; the rest is deleted or corrected | Nobody hand-corrects the same fact in four places again |
| Rules that actually hold | 0 enforced; prose only | Every MUST in `.claude/rules/` paired with a hook or a settings entry — or written as a convention and labelled one | The GOVERNANCE.md failure mode (fictional "live enforcement") cannot recur by construction |
| Credential exposure | **0 — shielded 2026-07-28 (S14)**; publish pre-approvals still live | 0, plus: no `rm`/push pre-approval (S13, R12), IDs in the Codespaces vault, `settings.local.json` untracked | The worst outcome this repo could produce is off the table |
| Skill store | 22 skills across a nonstandard `.agents/` reached by 10 symlinks | 16 real directories in `.claude/skills/`, auto-discovered (STD-14/15) | Skills resolve the way the docs say they do; no symlink can dangle |
| Silent automations | 1 hourly schedule firing into a wall | 0 — deleted (A1) | Nothing runs unattended that nobody is watching |

---
