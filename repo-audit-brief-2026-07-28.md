# Repo Audit Brief — 2026-07-28

`Red-teamed 2026-07-28 — verdict 🟡 after 17 repairs` (5 blockers, 12 repairs; details in `repo-audit-redteam-2026-07-28.md`, edits listed in the Revision log at the end).

~~Planning pass only. Nothing has been fixed.~~ **Superseded 2026-07-28: execution has begun — §0 is the live record and single source of truth for the refactor; read it first.** Every fact in §1–§9 was checked against the files, the git history, or the GitHub API — first by the original audit session, then re-checked by a six-agent red team, which corrected this document where the two disagreed.

**Currency:** reconciled end-to-end on 2026-07-28 after the owner directive (§0) and the round-2 answers (§0.6). **Step 0 and A6 are executed. All seven §8 questions are closed. All four P-items are approved.** The only decisions left in this document are five R-items: **R4, R6, R7, R10, R11.** Read **§0.7** for what to do next; §1–§9 are the reference record behind it.

*Codes like **S2**, **R3**, **STD-1** are item IDs — S-numbers are defined in §5, R-numbers in §6, STD-numbers in §3. Plain-English terms are defined in the glossary, §9 — flip there any time a word is unfamiliar.*

---

## §0. OWNER DIRECTIVE — 2026-07-28 (READ THIS FIRST; SUPERSEDES EVERYTHING BELOW)

**This file is the single source of truth for the refactor.** §1–§9 are the pre-directive audit record, kept for reference and receipts; where they conflict with this section, this section wins. Executed items below are recorded as done, not proposed.

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
| R8 / §8 Q6 (`.agents/`) | **Answered (§0.4) and resolved by P4**, approved 2026-07-28 |
| **P1, P2, P3, P4** | **ALL FOUR APPROVED** by the owner, 2026-07-28 — see §0.5 |
| §8 Q5 (`.s3_setup_*`) | **ANSWERED** — delete the file (§0.6 A5) |
| §8 Q7 (`postCreate.sh`) | **DONE 2026-07-28** — safeguard folded into `devcontainer.json`, script retired (§0.2, §0.6 A6) |
| §8 Q4 (unverified 07-27 claims) | **CLOSED 2026-07-28** — claim 1 verified TRUE and worse than described (folded into S5); claim 2 unrecoverable and already covered by R7 + S11 (§0.6 A7) |
| S5 (stale factory docs) — scope grew | `lesson-scripts/README.md` is the worst offender in the repo: **3 of its 4 real program folders are missing from its own table, and 2 of the 3 it lists don't exist** (§0.6 A7) |

### §0.4 Why `.agents/` lives at root (owner asked; verified this session)

`.agents/` is the **primary skill store**, not a leftover: 10 of the 16 entries in `.claude/skills/` are **symlinks into `.agents/skills/`** (all seven `hyperframes*` skills, `media-use`, `skill-creator` — verified `ls -l` 2026-07-28), and `render-qa/synth_narration.py` + `design-system/frame.md` reference it directly. Deleting or moving it today would kill 10 skills and the TTS step of every build. It cannot be removed until it is unwound. **Proposed unwind (P4):** materialize the 10 symlinks into real directories under `.claude/skills/` (the standard, auto-discovered location — STD-14/STD-15), repoint the two hardcoded references, then delete `.agents/`. **P4 was approved by the owner on 2026-07-28** — so `.agents/` stays only until its step in the execution order (§0.7) comes up, and nothing may touch it before then.

### §0.5 THE FOUR P-ITEMS — **ALL APPROVED 2026-07-28** (enforcement-first replacements; the part the old plan was missing)

> **Approval, stated once and unambiguously: the owner approved P1, P2, P3 and P4 on 2026-07-28.** All four are execution items, not proposals. No further sign-off is required for any of them. The only remaining sign-offs in this brief are the surviving R-items (R4, R6, R7, R10, R11) at the §7 gate.

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

### §0.6 OWNER ANSWERS to §8 — round 2, 2026-07-28 (these close every open question except two)

| # | Question | Owner's answer | What it changes in the plan |
|---|---|---|---|
| **A1** | §8 Q1 — where the hourly `/produce-video` schedule lives (blocked R2) | *"I'm not sure where this is either, but go ahead and just delete the schedule — we no longer need this hourly scheduled item."* | **R2 collapses from "pause + alarm + revival plan" to "find it once and delete it."** Locating it is now a 2-minute chore, not a blocker: claude.ai → profile/settings → **Scheduled tasks** (routines) → delete anything naming produce-video or SCLA lessons. Nothing needs to survive it, so no alarm step and no revival design. If nothing is found there, the fallback is a `CronList` check in an interactive session. Record the deletion in `decisions/log.md`. **R2 is no longer blocked by anything.** |
| **A2** | §8 Q2 — which review tool is actually used at the preview gate (blocked R5) | *"Usually I just run `bash scripts/preview.sh <stem>` in terminal and hope it opens a browser tab in a port."* — flagged as **an ongoing pain point** | **R5 stops being "pick one of three" and becomes "canonise one and fix it."** Verified this session: `preview.sh` = single-stem previewer, the human's real tool. `review.sh` = multi-build dashboard + preflight gate, wired to the VS Code task "🎬 Review lesson videos" and named in `.devcontainer/devcontainer.json`'s port comment. `review.py` = a rival single-page dashboard wired to **nothing** (its own docstring claims `review.sh` launches it — `review.sh` does not; verified). **Resolution: `preview.sh` is canonical and gets the reliability fix (print the Codespaces forwarded `https://` URL, wait for the port to actually answer, fail loudly if it doesn't — "and hope" must stop being part of the workflow). `review.py` is deleted as an unwired duplicate. `review.sh` is kept only because the VS Code task and devcontainer comment reference it; if the owner never uses that task, delete it and its two tasks.json entries in the same pass.** |
| **A3** | R9 — is the voice choice final (blocked archiving the auditions) | *"Yes — the voice we're going with is Oxana, not Ann. Remove all reference of Ann."* | **R9 is cleared to run, with widened scope.** Per §0.1 policy the 3.2 MB of `design-system/voice-auditions/` is **deleted, not archived** (Kokoro samples are regenerable). "Remove all reference of Ann" hits 2 live files, verified this session: `design-system/frame.md:57` and `design-system/CLAUDE.md:59` (both read "it replaced Ann — Professional"). Oxana's ID `442360a3e0894fbd85024ff64cc2b928` stays pinned in `frame.md:62`, `design-system/CLAUDE.md:57` and `render-qa/synth_narration.py:92` — unchanged. Also drop the two pointers at `design-system/CLAUDE.md` lines 26 and 70. **Not touched:** `decisions/log.md`, `render-qa/snag-log.md` and the one refined lesson script that happens to contain the word — history is not rewritten and lesson prose is not a voice reference. |
| **A4** | R12 / P2 — Infisical IDs, and the broader dotfiles split | *"In a perfect world all secrets would be stored in Infisical, and in Infisical, machine-identity credentials are in the Codespaces secret vault."* | **Target architecture is now stated, so R12 splits into a do-now half and a do-later half.** Do now: move `identityId`/`clientId` to Codespaces secrets, leave only a pointer in `config/endpoints.json` (see P2), untrack `.claude/settings.local.json`, drop the `git push` pre-approval. Do later, at leisure: the dotfiles split. The split is now clearly *desirable* under this architecture — a dotfiles repo that every future Codespace inherits should carry machine setup, not a knowledge base — but with S14's shields up it is no longer urgent. |
| **A5** | §8 Q5 — keep or delete `.s3_setup_FVC8bRn6m` | *"I don't know what this is, so it's probably not important."* | **Delete it.** It is a leftover package listing (user-owned, readable, gitignored, referenced by nothing — red-team verified). The `.s3_setup_*` ignore rule stays so a regenerated one is never committed; its false "root-owned, 0600" comment was corrected during Step 0. |
| **A6** ✅ **EXECUTED** | §8 Q7 — revive or retire `.devcontainer/postCreate.sh` | *"I don't know what this is — make the logical choice according to best practices."* → then, on review: *"you can retire postCreate.sh."* | **DONE 2026-07-28 — see §0.2 for what was actually executed.** Decision was **fold, then retire — one file ends up holding container setup.** Verified: `postCreate.sh` (26 lines, dead code) and `devcontainer.json`'s inline `postCreateCommand` both install ffmpeg + Infisical, so only two things in the script are *not* live: (a) the **brand anti-fabrication safeguard** — re-materializing `brand/` in a sparse checkout, added after the 2026-07-22 incident where cold subagents fabricated `brand/voice-and-tone.md` because it wasn't on disk; (b) `npm i -g hyperframes` + `bash scripts/setup.sh`. Best practice is one setup path, not two that drift: move the safeguard (and the hyperframes install) into the inline `postCreateCommand`, then delete `postCreate.sh`. Rationale — the safeguard guards against *silent fabrication of brand voice in member-facing videos*; it cannot live in the branch that never runs. **Do not simply retire it: that ships the repo with a known incident's fix removed.** |

| **A7** | §8 Q4 — are yesterday's two un-re-verified claims accurate (owner asked what was needed to check them) | Nothing was needed — **verified directly against the repo, 2026-07-28** | **First, the bad news about the source:** `repo-audit-brief-2026-07-27.md` **no longer exists and is unrecoverable** — it was never committed (`git log --all` and a full `rev-list --objects` scan both find nothing), and it has since been removed from root. The two claims survive only as this brief's one-line paraphrase of them. Both were checkable from that paraphrase anyway: **① "lesson-scripts README program tables" — CONFIRMED, and materially worse than described.** `projects/video-production/lesson-scripts/README.md`'s "Live programs" table lists `early-career-boost`, `career-readiness-accelerator`, `scla-leadership-program`. On disk there are four program folders: `career-transitions`, `early-career-boost`, `entrepreneur-accelerator`, `mid-career-momentum`. So **two of the three listed programs do not exist**, and **three of the four that do exist are absent from the table** — only `early-career-boost` is right. Its "Older programs" note repeats both phantom slugs. The same file also links to `programs/` and `GOVERNANCE.md` (**both deleted in §0.2**), routes to `endpoints.md` (deleted by P2), and still documents the retired **PUBLISH** phase and an "MP4 review" gate removed 2026-07-22. **Folded into S5 and scheduled at §0.7 STEP 3.** **② "folder-skeleton variance" — unrecoverable, and already covered.** The specifics died with the source document; the general claim (folders don't share a consistent shape) is exactly what **R7** (render-qa's flat heap) and **S11** (audits' two naming styles) already address. Nothing further to chase. |

**Nothing is open after this round.** Both former open questions are closed:
- **§8 Q3** — whether the `rclone` Drive credential is valid. **Permanently moot:** the mirror was deleted entirely (§0.2), so there is nothing to revive.
- **§8 Q4** — closed by **A7** above: claim ① confirmed and folded into S5, claim ② unrecoverable and already covered by R7 + S11.

**The only decisions left in this entire brief are the five §7-gate R-items: R4, R6, R7, R10, R11.**

### §0.7 EXECUTION ORDER — the live plan (supersedes §7)

Every step below is approved. `⚠️` marks the five items still needing a yes/no at the §7 gate; everything else runs without further sign-off.

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
   │  · S7-rem: file all three root briefs into audits/ (this one, the red-team
   │         report, repo-standard-2026-07-28.md) — git-add the untracked ones
   │         FIRST so the move is undoable
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
 ╔═══ REMAINING SIGN-OFF GATE — R4, R6, R7, R10, R11 only (§6) ═══╗
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
                 · desirable under A4's architecture, no longer urgent (S14 is up)
```

**Two ordering rules that are not negotiable:** P4 runs **last** (until then, nothing touches `.agents/` — it is the live skill store for 10 of 16 skills and every build's TTS step), and R7 + R10 run **alone**, never two structural items in one pass.

---

## §1. START HERE — WHAT'S ACTUALLY GOING ON *(pre-directive snapshot — §0 is current)*

> **Read §0 first; this section is the morning's diagnosis, kept for the reasoning.** Three things it describes have since changed: the **Drive mirror is gone entirely** (deleted, not fixed — so "100 of 100 failures" is history), the **credential exposure is closed** (S14 executed — the shield is up), and the **false rulebooks are deleted** rather than corrected (GOVERNANCE.md, MAP.md). What it says about *pre-approved delete commands* is still true and is the next thing to fix (S13, §0.7 STEP 1).


**WHAT** — This repo is your organization's knowledge base plus the video-lesson factory that runs on top of it. The bones are genuinely good: the main instruction file for the AI is small and tidy, and most things live where the official docs say they should. What has drifted is the *paperwork*: several files confidently describe rules, protections, and automations that no longer exist or never worked.

**SO WHAT** — Three problems outrank everything else. First: your two automations are both failing and nothing tells you. The Google Drive mirror has failed on **every one of its last 100 runs** (all that GitHub reports — it dies before copying anything), and a scheduled video-pipeline run has fired **24+ times**, roughly hourly, just to rediscover the same blocker. Second: your rulebook says protections are "live enforcement" — in reality **none of those protections are switched on**, and the AI is even pre-approved to run delete commands without asking. Third — found by the red team, and the most urgent: a second copy of this repo doubles as this machine's startup configuration, and **a live login credential sits unprotected inside it** while the settings pre-approve the commands that could publish it. Fixing that is ten minutes (**S14**) and should happen before anything else.

One reassurance, because it's the question behind all of this: nothing in the git history shows the delete pre-approval was ever used destructively. The only wholesale deletion found is the `_archive/` folder (2026-07-23), which item **R3** addresses.

**NOW WHAT** — The safe fixes are one sitting (about 2 hours). The sign-off items are not just yes/no: two of them ask you to go check something first (§8 explains exactly what and how), and the follow-on work is roughly 3–4 hours spread over a week. The very first steps are **S14/S15** (protect the credential), then reading the scoreboard below, then answering §6. Nothing gets deleted — only moved, archived, or corrected. Every move of a *tracked* file can be undone from git; the one untracked file we move (yesterday's brief) gets committed first so that stays true.

| Area | What's true now | So what — the cost to you | Now what — after the fix |
|---|---|---|---|
| Credential exposure (red-team find) | ❌ live login token unprotected in a second copy of this repo; publish commands pre-approved | One pre-approved command could put a live credential on GitHub | ✅ shielded today — **S14, S15**, then **R12** |
| The AI's instructions (CLAUDE.md) | ⚠️ small, but promises are false | The AI is told its #1 rule guards a folder deleted on July 23, and that every folder has a guide file — many don't; it wastes time and trusts wrong facts | ✅ every line true again — **R3, S10** |
| Docs that tell the truth | ❌ three key files misdescribe reality | Any person or AI reading MAP.md or GOVERNANCE.md gets ~15 false facts (wrong counts, wrong locations, deleted folders) | ✅ docs match the filesystem — **S2, S4, S5** |
| Rules that are actually enforced | ❌ zero of the claimed protections run | "Hook-enforced" and "force-push denied" are written down but not switched on; delete commands are pre-approved | ✅ dangerous pre-approvals off now (**S13**); re-arming the hook scripts is your call (**R10, R11**) — they were unplugged *on purpose* once, and one of them used to kill video builds |
| Top level clutter | ⚠️ 30 items (pre-audit), incl. a 2 MB test dump | The front door is cluttered with leftovers, a junk system file, and yesterday's audit — hard to see what matters | ✅ clean front door — **S7, S8** |
| Folders shaped the same way | ⚠️ one work folder mixes everything | `render-qa/` piles code, logs, and docs in one flat heap; audit files use two naming styles | ✅ consistent shapes — **R7, S11** |
| Automations that can report failure | ❌ both fail silently | 100/100 failed Drive syncs; 24+ blocked scheduled runs; you found out from this audit, not from them | ✅ paused or fixed, with alerts — **R1, R2** |
| Duplicates | ⚠️ two real duplicate sets + one false alarm | Two competing review tools; two lessons teaching **contradictory** definitions. (The "duplicate skill pack" turned out to be one set of files reached two ways — see **R8**) | ✅ one source of truth each — **R5, R6, R8** |
| Naming and depth | ⚠️ 302 over-deep paths, mixed names | Deep vendored paths and unsortable filenames make things hard to find | ✅ predictable names — **S11, R8** |

Legend: ✅ fine · ⚠️ needs a fix · ❌ broken or wrong.

---

## §2. WHAT "GOOD" ACTUALLY LOOKS LIKE (the teaching section)

| # | What good looks like | So what — why the rule exists | Now what — where your repo stands |
|---|---|---|---|
| 1 | The AI's instruction file holds only facts that are true every session; step-by-step procedures live in skills (STD-1, STD-2, STD-3) | The instruction file is re-read constantly — procedures in it cost you on every single message | ✅ mostly right — procedures already live in skills. One false promise and one dead rule remain → **S10, R3** |
| 2 | Keep each instruction file under roughly 200 lines — a target, not a law (STD-4, STD-5, STD-6, STD-7) | Long files load in full anyway, and the AI follows shorter files better | ✅ root file is 46 lines. One nested file — `projects/video-production/avatar-pipeline/CLAUDE.md` — is 215 (barely over a soft target) — noted, no action needed |
| 3 | A rule that must hold every time belongs in a hook or settings, because written instructions are requests, not guarantees (STD-8 mechanism, STD-9, STD-10, STD-11) | The AI can ignore a sentence; it cannot ignore a hook | ❌ every claimed protection is prose-only today. The enforcing scripts exist — but they were armed once and **deliberately unplugged** (recorded in git), and one has a history of breaking video builds. Re-arming is a decision, not housekeeping → **S13** now; **R10, R11** for your call |
| 4 | Big projects use one small root instruction file plus per-folder ones — officially endorsed (STD-12, STD-13) | Sessions load only the rules for the area they're working in | ✅ you already do this — 5 files, right places. Genuinely well done |
| 5 | Skills, subagents, and rules are found automatically from their standard folders — which makes hand-maintained lists redundant (our inference from STD-14 through STD-20) | Hand-maintained lists rot; automatic discovery can't | ⚠️ discovery works, but a dead hand-list lists 4 of 16 skills, one skill lacks its label, and the *primary* skill store lives in a nonstandard folder reached by symlinks → **R11, S9, R8** |
| 6 | Don't write down what the file tree already shows; no changelogs; no rules nobody follows (STD-22, STD-23 — written for CLAUDE.md; we extend the same logic to the other always-loaded docs this repo routes to) | Hand-copied trees drift into lies the moment files move | ❌ MAP.md is a hand-copied tree with at least 7 false claims → **S4, S5** |
| 7 | Know what costs context every message (instruction files) vs. on demand (skills) vs. nothing (hooks — *unless* the hook prints output into the chat, which this repo's two reminder hooks do) (STD-24 through STD-28) | Every always-loaded line is paid for on every message | ✅ your split is right: 46-line always-on file, heavy material in skills |

---

## §3. THE OFFICIAL STANDARD (the receipts)

This is the outside standard this whole brief is graded against. None of it is my opinion — every row is a direct quote you can go check. The red team re-fetched every source page live on 2026-07-28: all quotes confirmed verbatim; two classification labels were corrected and one row (STD-31) added.

Canonical copy: `repo-standard-2026-07-28.md`. If this section and that file ever disagree, that file wins.

| ID | Rule (quoted verbatim) | HARD RULE or GUIDELINE | Source URL |
|---|---|---|---|
| STD-1 | "Keep it to facts Claude should hold in every session: build commands, conventions, project layout, \"always do X\" rules. If an entry is a multi-step procedure or only matters for one part of the codebase, move it to a skill or a path-scoped rule instead." | GUIDELINE | https://code.claude.com/docs/en/memory |
| STD-2 | "Create a skill when you keep pasting the same instructions, checklist, or multi-step procedure into chat, or when a section of CLAUDE.md has grown into a procedure rather than a fact." | GUIDELINE | https://code.claude.com/docs/en/skills |
| STD-3 | "Put it in CLAUDE.md if Claude should always know it: coding conventions, build commands, project structure, \"never do X\" rules." … "Put it in a skill if it's reference material Claude needs sometimes (API docs, style guides) or a workflow you trigger with /\<name\> (deploy, review, release)." | GUIDELINE | https://code.claude.com/docs/en/features-overview |
| STD-4 | "Size: target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence." | GUIDELINE ("target", not a limit) | https://code.claude.com/docs/en/memory |
| STD-5 | "Rule of thumb: Keep CLAUDE.md under 200 lines. If it's growing, move reference content to skills or split into `.claude/rules/` files." | GUIDELINE ("rule of thumb") | https://code.claude.com/docs/en/features-overview |
| STD-6 | "Aim for a file that is short and signal-dense — under roughly 200 lines." | GUIDELINE ("aim", "roughly") | https://support.claude.com/en/articles/14553240-give-claude-context-claude-md-and-better-prompts |
| STD-7 | "CLAUDE.md files are loaded in full regardless of length, though shorter files produce better adherence." | HARD RULE (stated mechanism) | https://code.claude.com/docs/en/memory |
| STD-8 | "Put guardrails in hooks. An instruction like \"never edit `.env`\" in CLAUDE.md or a skill is a request, not a guarantee. A `PreToolUse` hook that blocks the edit is enforcement. If a rule must hold every time, make it a hook rather than a prompt instruction." | HARD RULE (mechanism: request-not-guarantee) + GUIDELINE (practice: put guardrails in hooks) — split corrected by red team 2026-07-28 | https://code.claude.com/docs/en/features-overview |
| STD-9 | "They provide deterministic control over Claude Code's behavior, ensuring certain actions always happen rather than relying on the LLM to choose to run them." | HARD RULE (stated mechanism) | https://code.claude.com/docs/en/hooks-guide |
| STD-10 | "Claude treats them as context, not enforced configuration. To block an action regardless of what Claude decides, use a PreToolUse hook instead." | HARD RULE | https://code.claude.com/docs/en/memory |
| STD-11 | "Settings rules are enforced by the client regardless of what Claude decides to do. CLAUDE.md instructions shape Claude's behavior but are not a hard enforcement layer." | HARD RULE (stated mechanism) | https://code.claude.com/docs/en/memory |
| STD-12 | "Splitting instructions across per-directory files means Claude loads repository-wide rules plus only the conventions for the code you're working in." … "A root file sets repository-wide rules and each subdirectory adds its own." | GUIDELINE (nested CLAUDE.md endorsed for large repos) | https://code.claude.com/docs/en/large-codebases |
| STD-13 | "Claude also discovers `CLAUDE.md` and `CLAUDE.local.md` files in subdirectories under your current working directory. Instead of loading them at launch, they are included when Claude reads files in those subdirectories." | HARD RULE (stated mechanism) | https://code.claude.com/docs/en/memory |
| STD-14 | "Project skills load from `.claude/skills/` in your starting directory and in every parent directory up to the repository root, so starting Claude in a subdirectory still picks up skills defined at the root." (Personal skills path per the same page's table: `~/.claude/skills/<skill-name>/SKILL.md`) | HARD RULE (stated mechanism) | https://code.claude.com/docs/en/skills |
| STD-15 | "Claude Code watches skill directories for file changes. Adding, editing, or removing a skill under `~/.claude/skills/`, the project `.claude/skills/`, or a `.claude/skills/` inside an `--add-dir` directory takes effect within the current session without restarting." | HARD RULE (stated mechanism; "no hand-maintained registry needed" is an inference from it, not doc text — noted by red team 2026-07-28) | https://code.claude.com/docs/en/skills |
| STD-16 | "Claude picks a skill by reading every discovered skill's name and description, and only the chosen skill's full content loads into context." | HARD RULE (stated mechanism) | https://code.claude.com/docs/en/large-codebases |
| STD-17 | "Because the file lives in `~/.claude/agents/`, the subagent is available in every project on your machine. To scope it to one project instead, move it to that project's `.claude/agents/` directory." … "Project subagents are discovered by walking up from the current working directory, so every `.claude/agents/` between there and the repository root is scanned." | HARD RULE (stated mechanism) | https://code.claude.com/docs/en/sub-agents |
| STD-18 | "When Claude encounters a task that matches a subagent's description, it delegates to that subagent, which works independently and returns results." | HARD RULE (stated mechanism) | https://code.claude.com/docs/en/sub-agents |
| STD-19 | "Place markdown files in your project's `.claude/rules/` directory." … "All `.md` files are discovered recursively, so you can organize rules into subdirectories like `frontend/` or `backend/`" … "Personal rules in `~/.claude/rules/` apply to every project on your machine." | HARD RULE (location + native discovery) | https://code.claude.com/docs/en/memory |
| STD-20 | "Rules can be scoped to specific files using YAML frontmatter with the `paths` field. These conditional rules only apply when Claude is working with files matching the specified patterns." … "Rules without a `paths` field are loaded unconditionally and apply to all files." | HARD RULE (stated mechanism) | https://code.claude.com/docs/en/memory |
| STD-21 | "To create a hook, add a `hooks` block to a settings file." … "Confirm the settings file is in the correct location: `.claude/settings.json` for project hooks, `~/.claude/settings.json` for global hooks" | HARD RULE | https://code.claude.com/docs/en/hooks-guide |
| STD-22 | Do not include: "Full API documentation (Claude can read the code directly)." … "Changelogs or history." … "Anything that is already obvious from the file tree." … "Aspirational rules the team does not actually follow." | GUIDELINE | https://support.claude.com/en/articles/14553240-give-claude-context-claude-md-and-better-prompts |
| STD-23 | The `/doctor` trim check "cuts content Claude can derive from the codebase, such as directory layouts, dependency lists, and architecture overviews, and keeps pitfalls, rationale, and conventions that differ from tool defaults." | GUIDELINE | https://code.claude.com/docs/en/memory |
| STD-24 | "CLAUDE.md files are loaded into the context window at the start of every session, consuming tokens alongside your conversation." | HARD RULE (stated mechanism) | https://code.claude.com/docs/en/memory |
| STD-25 | "Every line is loaded into context on every request, so each one should be worth its cost." | HARD RULE (mechanism) + GUIDELINE (cost test) | https://support.claude.com/en/articles/14553240-give-claude-context-claude-md-and-better-prompts |
| STD-26 | "Rules load into context every session or when matching files are opened. For task-specific instructions that don't need to be in context all the time, use skills instead, which only load when you invoke them or when Claude determines they're relevant to your prompt." | GUIDELINE (with stated mechanism) | https://code.claude.com/docs/en/memory |
| STD-27 | "Unlike CLAUDE.md content, a skill's body loads only when it's used, so long reference material costs almost nothing until you need it." … (features-overview adds: "By default, skill descriptions load at session start so Claude can decide when to use them.") | HARD RULE (stated mechanism) | https://code.claude.com/docs/en/skills and https://code.claude.com/docs/en/features-overview |
| STD-28 | Hooks — "What loads: Nothing by default. Hooks execute outside the main conversation." … "Context cost: Zero, unless the hook returns output that gets added as messages to your conversation." | HARD RULE (stated mechanism) | https://code.claude.com/docs/en/features-overview |
| STD-29 | "Each subagent runs in its own context window with a custom system prompt, specific tool access, and independent permissions." | HARD RULE (stated mechanism) | https://code.claude.com/docs/en/sub-agents |
| STD-30 | "Splitting into `@path` imports helps organization but doesn't reduce context, since imported files load at launch." | HARD RULE (stated mechanism) | https://code.claude.com/docs/en/memory |
| STD-31 | "Claude Code reads `CLAUDE.md`, not `AGENTS.md`. If your repository already uses `AGENTS.md` for other coding agents, create a `CLAUDE.md` that imports it so both tools read the same instructions without duplicating them." (The page also offers `ln -s AGENTS.md CLAUDE.md` as an alternative.) | HARD RULE (first sentence: stated mechanism) + GUIDELINE (import/symlink pattern) — added by red team 2026-07-28 | https://code.claude.com/docs/en/memory |

---

## §4. YOUR REPO, BEFORE AND AFTER

*This section was redrawn 2026-07-28 after the owner directive (§0) and the round-2 answers (§0.6). The original pre-directive tree — 30 root items with GOVERNANCE.md, MAP.md, `programs/`, `operations/`, `references/`, `_heygen-test-preview/` and the Drive workflow still in it — is preserved in git history and in `repo-audit-redteam-2026-07-28.md`.*

**NOW — verified current state, post-directive (25 root items; `ls -A` minus `.git`, counted 2026-07-28):**

```
SCLA-Profile/
├── CLAUDE.md ..................... ✅🤖 46 lines; routing pruned, hub promise softened, _archive/ ban is the one hard rule
├── endpoints.md .................. ❌👤 markdown registry — DELETED by P2, do not hand-correct it
├── repo-audit-brief-2026-07-28.md  📋 THIS FILE — the source of truth; belongs in audits/ (S7-rem)
├── repo-audit-redteam-2026-07-28.md 📋 the receipts; belongs in audits/ (S7-rem) — untracked, git-add before moving
├── repo-standard-2026-07-28.md ... 📋 the graded-against rubric; belongs in audits/ (S7-rem) — untracked, git-add first
├── skills-lock.json .............. ✅📋 version-pin list, real and used
├── .s3_setup_FVC8bRn6m ........... ❌ leftover package listing — DELETE (A5); gitignored, referenced by nothing
├── scla.config.yml / sync.sh ..... ✅ small, real, working (sync.sh is the GIT sync, not the dead Drive mirror)
├── .gitignore .................... ✅⚙️ credential + session shield UP (S14 ✅); .vscode/* negation fixed (S15 ✅)
├── .mcp.json ..................... ✅⚙️
├── .devcontainer/ ................ ⚠️⚙️ TWO setup paths: dead postCreate.sh + the live inline command (A6 folds them)
├── .vscode/ ...................... ⚠️⚙️ tasks.json wires review.sh — the tool the owner doesn't use (A2)
├── hooks/  (9 scripts + 1 data file) ❌⚙️ governance-check.sh guards DELETED files → P3 deletes it;
│                                       skill-eval.sh + skill-rules.json → R11; the rest unplugged on purpose (R10)
├── .claude/
│   ├── settings.json ............. ❌⚙️ still pre-approves rm, find, cat, head, tail — S13, NEXT UP
│   ├── settings.local.json ....... ❌⚙️ tracked (should be personal); pre-approves git push (R12/A4)
│   ├── skills/  (16 entries) ..... ⚠️🤖 6 real + 10 symlinks into .agents/; new-from-template lacks its label (S9)
│   └── agents/  (4 QA agents) .... ✅🤖 right place, auto-discovered
├── .agents/  (618 files, 72% of repo) ⚠️📋 the PRIMARY skill store — unwound by P4, LAST. Touch nothing here until then
├── (.github/ ..................... ⛔ GONE entirely — the Drive workflow was its only content; S12 recreates it)
├── brand/ context/ decisions/ .... ✅ knowledge folders, clean
├── member-support/ partnerships/ templates/ ✅ clean
├── audits/  (4 files) ............ ⚠️ two clashing naming styles (S11); 2 citations in decisions/log.md point at them
├── scripts/  (11 items) .......... ⚠️ preview.sh (used) + review.sh (wired, unused) + review.py (wired to nothing → delete);
│                                      __pycache__/ tracked (S8); lint-refs.sh GREEN, ready for CI (S12)
└── projects/video-production/ .... ⚠️ the factory
    ├── design-system/ ............ ⚠️ TWO AI instruction files (CLAUDE.md + AGENTS.md → R4 import pattern);
    │   │                              "nine templates" ×4 — real count is 12 (S5); 2 stale "Ann" lines (A3)
    │   └── voice-auditions/ ...... ❌ 3.2 MB of Kokoro samples — DELETE, voice choice is final (A3)
    ├── lesson-scripts/ ........... ❌ same lesson in 2 programs with CONTRADICTORY "Rebuild" definitions (R6)
    ├── _archive/ ................. ⚠️ nested archive, tracked, stale — convention decided in P1
    └── render-qa/  (15 items) .... ⚠️ code + logs + docs in one flat heap; snag-log.md alone is 502 KB (R7)
```

**AFTER — once §0.7 is executed (21 root items; ⚠️ = only if that R-item clears the §7 gate):**

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
├── audits/ ....................... ✅📋 one date-first naming style (S11) + all THREE root briefs filed here (S7-rem)
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

Legend — NOW tree: ✅ fine · ⚠️ needs a fix · ❌ broken, wrong, or slated for deletion. AFTER tree: ✅ done · ⚠️ only if that R-item clears the gate · 🔄 reshaped · ⛔ deleted · ⭐ new. Both trees: 🤖 read by the AI · 👤 read by humans · ⚙️ read by machinery (git, CI, the editor) · 📋 a log or registry.

*Note the policy change visible in these trees: under §0.1 the answer to dead weight is **delete**, not archive — git history is the archive. `⛔` no longer means "moved to `_archive/`" as it did in the pre-directive draft.*

| | Now | After | Why that matters |
|---|---|---|---|
| Top-level items | 25 | 21 — three briefs filed into `audits/`, `.s3` junk and `.agents/` gone, `endpoints.md` replaced by `config/`, `.github/` back | The front door shows only real entry points |
| Files that can go false | `endpoints.md` + 4 stale factory docs + a hand-maintained skill list | 0 — the registry is JSON the linter validates on every push; the rest is deleted or corrected | Nobody hand-corrects the same fact in four places again |
| Rules that actually hold | 0 enforced; prose only | Every MUST in `.claude/rules/` paired with a hook or a settings entry — or written as a convention and labelled one | The GOVERNANCE.md failure mode (fictional "live enforcement") cannot recur by construction |
| Credential exposure | **0 — shielded 2026-07-28 (S14)**; publish pre-approvals still live | 0, plus: no `rm`/push pre-approval (S13, R12), IDs in the Codespaces vault, `settings.local.json` untracked | The worst outcome this repo could produce is off the table |
| Skill store | 22 skills across a nonstandard `.agents/` reached by 10 symlinks | 16 real directories in `.claude/skills/`, auto-discovered (STD-14/15) | Skills resolve the way the docs say they do; no symlink can dangle |
| Silent automations | 1 hourly schedule firing into a wall | 0 — deleted (A1) | Nothing runs unattended that nobody is watching |

---

## §5. THE SAFE LIST (no sign-off needed)

These are reversible, touch nothing that's running, and I'd do all of them without asking. You don't need to review them individually. *(Red team note: the original S1 and S6 did NOT survive this bar — they are now R10 and R11 in §6. Three new items, S14–S16, were added.)*

> **Post-directive status (§0.3 is authoritative):** **S14 and S15 are DONE** (executed 2026-07-28 — see §0.2). **S2 and S4 are moot** (GOVERNANCE.md and MAP.md were deleted, not corrected). **S10 is done.** **S12's "sequenced after R3" caveat is void** — R3 is moot and the linter already reports `lint-refs: healthy`, so S12 can be wired today and starts green. **S7 is partially superseded** — `_heygen-test-preview/` was deleted rather than archived; what remains is filing the three root briefs into `audits/`. Still to do: **S3, S5, S8, S9, S11, S12, S13, S16.** Where a row below describes archiving, §0.1 has since replaced that with deletion — git history is the archive.
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

## §6. THE RISKY LIST (your call, one by one)

Each of these needs you to say yes or no. Not approving one is a completely valid answer — nothing else in the plan depends on it unless a row says so.

> **Post-directive status (§0.3 is authoritative).** Seven of the twelve are settled: **R1 resolved by removal** · **R3 mostly moot** · **R8 answered and superseded by P4 (approved)** · **R2, R5, R9, R12 answered 2026-07-28 — see §0.6, and the ✅ notes in their rows below.** **Only five still want a yes/no from you: R4, R6, R7, R10, R11.**

About the recorded confirmations: yesterday's brief and this one record owner decisions dated 2026-07-28 on **six** items (R1, R2, R3, R4, R6, R8). The red team could not verify those conversationally-recorded confirmations from the filesystem — and found that **R8's was given against a false premise and is void** (see its row) and R4's supporting claim is contradicted by repo evidence. Treat the §7 gate as where you *confirm or veto* every R-item, including the pre-recorded ones; the recorded answers are listed so you don't start from zero.

| ID | What changes | Which STD-n it closes | What breaks if this goes wrong | How I'd undo it | My recommendation |
|---|---|---|---|---|---|
| R1 | **Stop the failing Drive mirror**: disable `.github/workflows/drive-sync.yml`, or finish its setup (the `GDRIVE_TARGET` variable was never set — verified from the failure logs; last 100 runs: 100 failures, 0 successes — the run dies before copying anything) | no citation — general hygiene (silent failure) | Disabling shelves a feature the team once decided on; finishing it would suddenly publish the whole knowledge base to Drive in one shot — pause on whether that's wanted | Re-enable the workflow file (one line) | ✅ recorded 2026-07-28: disable, and add an alarm step before it's ever revived |
| R2 | **Pause the scheduled `/produce-video` run** until its missing credentials/tools are installed — it has fired 24+ times, roughly hourly, every run ending at the same wall (verified via commit history and its own log). **Depends on §8 Q1**: we don't yet know where this schedule is configured, so "pause" can't be executed until Q1 is answered | no citation — general hygiene (silent failure) | If the blocker clears while paused, new scripts sit unprocessed until someone notices | Un-pause the schedule | ✅ **SETTLED 2026-07-28 — simpler than proposed: DELETE it, don't pause it.** Owner: *"we no longer need this hourly scheduled item."* No alarm, no revival design, no Q1 blocker — just locate and remove (§0.6 A1), then log it. §0.7 STEP 6 |
| R3 | **Rewrite the archive rules to match reality**: CLAUDE.md's #1 hard rule, five GOVERNANCE.md passages, and MAP.md all govern the root `_archive/`, deleted 2026-07-23 (commit `bed5ff7`, verified) with no log entry. The rewrite must decide the go-forward convention, because archives aren't dead here: `projects/video-production/_archive/` is still tracked (and stale), `renders-hyperframes/_archive/` is where the pipeline's own hooks file retired work, and S7 recreates root `_archive/` as the destination for archived items. Also update the hardcoded `APPROVED_ROOT` list in `hooks/governance-check.sh` (it still approves the deleted folder) so R10 doesn't arm a stale gate. This item is also what clears the doc-linter's 8 warnings, unblocking S12 | STD-22 (aspirational rules) | If that deletion was actually an accident, rewriting the rules ratifies a mistake — restoring from git history is the alternative | Git history still holds the deleted folder; rules can be reverted | ✅ recorded 2026-07-28: the deletion was intentional; proceed with one coherent edit |
| R4 | **Unify the two AI instruction files** in `design-system/` (CLAUDE.md, 80 lines + AGENTS.md, 89 lines — both exist, both stale on the template count). The official docs (STD-31) endorse the *reverse* of the original plan: keep `AGENTS.md` and have `CLAUDE.md` import it, so other tools keep their entry point. That matters here: the recorded confirmation said "nothing else reads AGENTS.md", but repo evidence contradicts it — `.agents/skills/hyperframes-core/references/subagent-dispatch.md:30` shows a non-Claude tool's standing grant living in the workspace AGENTS.md, and `render-qa/BUILD-LOG.md:552` lists it as a maintained doc | STD-31 | Merging *into* CLAUDE.md and stubbing AGENTS.md could sever a non-Claude tool's entry point | Both files stay in git; the import line is one edit | ✅ do it — but via the STD-31 import pattern (CLAUDE.md imports AGENTS.md), which makes the "who else reads it" question moot |
| R5 | **Pick one review tool**: `scripts/review.sh` and `scripts/review.py` are two implementations of the same job; the editor task list (`.vscode/tasks.json`) wires the `.sh` (verified). Red team adds a third candidate: `scripts/preview.sh`, which the pipeline's own snag log tells humans to run | no citation — duplicates | Repointing to the wrong one breaks the preview step a human uses at the video gate | All stay in git; repoint is one line | ✅ **SETTLED 2026-07-28 — and re-scoped.** The owner's real tool is `bash scripts/preview.sh <stem>`, *"and hope it opens a browser tab in a port"* — that hope is the actual defect. **`preview.sh` is canonical and gets the reliability fix; `review.py` is deleted (wired to nothing — verified); `review.sh` survives only on the VS Code task's account.** §0.6 A2, §0.7 STEP 10 |
| R6 | **Fix the contradictory lesson**: two programs ship "Four Kinds of Career Transition" with incompatible definitions — in `career-transitions/`, "Rebuild" = forced AND dramatic; in `mid-career-momentum/`, "Rebuild" = forced but near your field (verified by reading both scripts) | no citation — member-facing content integrity | Standardizing on the wrong framework publishes wrong teaching to members | Old script text stays in git | ✅ recorded 2026-07-28: mid-career-momentum's version is canonical; align `career-transitions/` before either renders |
| R7 | **Reshape `render-qa/`**: 15 items — 10 top-level code files (13 counting `tests/`), two giant append-only logs (`snag-log.md` alone is 502 KB), and docs — in one flat folder. Red team caution: these scripts compute the repo root positionally (e.g. `synth_narration.py` uses `parents[3]`), so ANY depth change silently breaks path resolution — every reference must be checked. Include a rotation policy for the logs. Timing note: `renders-hyperframes/` is currently empty, so the "between build cycles" window is open right now | no citation — folder-shape hygiene | The video pipeline's scripts and hooks reference these paths; a careless move breaks the factory | Moves tracked in git; revert restores paths | ⏸️ wait — do it alone, checking every reference, ideally soon while no build is in flight |
| R8 | **Resolve the skill-store layout — RE-PLANNED, original version was wrong and dangerous.** The original brief called `.agents/` a "duplicate pack" with "10 files byte-identical to `.claude/skills/`" and recorded a confirmation to archive it. The red team found those 10 entries are **symlinks** — `.agents/` is the *primary* store (618 files; 22 skills, of which 10 are linked into `.claude/skills/` and 12 aren't), and `render-qa/synth_narration.py` plus `design-system/frame.md` reference it directly. **Archiving it would have killed 10 of 16 skills and the TTS step of every build.** The recorded confirmation is void — it answered a false question. Real options: (a) keep `.agents/` as canonical and document it as intentional, or (b) materialize the 10 symlinks into real files under `.claude/skills/`, repoint the two hardcoded references, and only then archive what remains | STD-14, STD-15 | Option (b) done carelessly breaks skill discovery and the render pipeline | Archive-never-delete still applies; symlinks are restorable from git | ⏸️ wait — needs a fresh decision on the true question (see §8 Q6). Do nothing to `.agents/` until then |
| R9 | **Archive 3.2 MB of voice-audition audio** in `design-system/voice-auditions/` (size verified) — including editing the two places `design-system/CLAUDE.md` (lines 26 and 70) points readers at it | no citation — bloat | If the voice choice ever reopens, auditions must be regenerated | Archive, never delete | ✅ **SETTLED 2026-07-28 — cleared, and widened.** Owner: *"the voice we're going with is Oxana, not Ann. Remove all reference of Ann."* Per §0.1 the auditions are **deleted, not archived** (Kokoro samples regenerate). Plus: purge the two live "Ann" lines (`frame.md:57`, `design-system/CLAUDE.md:59`) and the two pointers (`design-system/CLAUDE.md` 26, 70). Oxana's ID stays pinned in all three places. History files keep their mentions. §0.6 A3, §0.7 STEP 3 |
| R10 | **(was S1 — red team reclassified.) Arm the protection scripts in `hooks/`** by registering them in the project settings file. Why this is not safe housekeeping: (a) they were armed once and **deliberately unplugged** (commits `bc1dbde` → `32ce4d0`) — arming reverses a recorded decision; (b) `pre-tool.sh` hard-blocks sessions at a tool-call budget, and its earlier version "killed video sessions mid-build" (decisions/log.md line 172) — a mid-render block would sever the render→upload pass; (c) the gate script's hardcoded approved-root list is stale (still approves the deleted `_archive`, omits `.github`/`.vscode`/`.agents`) and would block legitimate new files including S12's own workflow; (d) "tested" was never demonstrated — no run logs exist; (e) two of the candidates aren't protections at all: `doctor.sh` is a manual utility, and `cleanup-worktrees.sh` force-deletes git worktrees on every session end | STD-8 (mechanism), STD-9, STD-21 | A bad hook blocks the video factory or legitimate work, silently | Registration is a one-file edit; unregistering restores today's state | ⏸️ your call — if yes: fix the gate script's list first (with R3), set the budget generously, review each of the 7 scripts individually, and arm them one at a time, not as a pack |
| R11 | **(was S6 — red team reclassified.) Retire the hand-maintained skill list** (`hooks/skill-eval.sh` + `hooks/skill-rules.json`, which lists 4 of 16 skills). It is NOT "referenced by nothing": the health-checker `scripts/lint-refs.sh` lists `skill-rules.json` as a critical file and parses it (lines 69, 115) — archiving it as-is makes the linter fail forever (and S12's future check with it); `scripts/merge-settings.py` also registers `skill-eval.sh`. Retiring means a coordinated edit to those two scripts in the same change | STD-15, STD-16 | Done as a simple move, the repo's own health check goes permanently red | All files stay in git | ✅ do it — but as the coordinated three-file change, not a move |
| R12 | **(new — red team.) Decide the dotfiles/credentials architecture.** This repo doubles as the machine's Codespaces dotfiles repo (a second clone at the persisted-dotfiles path is what `~/.claude` points into). Consequences to decide on: every future Codespace for ANY repo inherits this whole knowledge base and its permissive settings; the tracked `.claude/settings.local.json` (which should be personal/untracked) pre-approves `git push` and auto-enables all project MCP servers; and `endpoints.md` publishes an Infisical clientId + identityId (half of a credential pair). Options: keep the arrangement knowingly (with S14's shields in place), or split dotfiles into their own repo; either way, un-track `settings.local.json` and drop the push pre-approval | STD-11 | Status quo leaves publish-capable pre-approvals pointed at a tree containing live credentials | Settings edits are one-line reverts; the dotfiles split is a new repo, not a deletion | ✅ **SETTLED 2026-07-28 — target architecture stated.** Owner: *"in a perfect world all secrets would be stored in Infisical, and in Infisical machine-identity credentials are in the Codespaces secret vault."* So: the `identityId`/`clientId` **move to Codespaces secrets** and `config/endpoints.json` carries only a pointer (P2, §0.7 STEP 4); untrack `settings.local.json` + drop the push pre-approval in the same pass. The dotfiles split is now clearly desirable under that architecture but is **not urgent** with S14's shields up — §0.7 STEP 14, at leisure. §0.6 A4 |

---

## §7. THE ORDER — **SUPERSEDED, see §0.7**

The pre-directive order below is kept only as a record. It sequences items that are now moot (S2, S4, R1, R3, R8) and predates every answer in §0.6. **Execute from §0.7, not from here.**

The one thing this section still contributes is the **sign-off gate**, now much smaller: after §0.7's STEP 8, five items — **R4, R6, R7, R10, R11** — still want an explicit yes or no from you. Everything else in §0.7 is approved and runs unattended.

<details>
<summary>Superseded pre-directive order (2026-07-28, morning)</summary>

```
STEP 0  S14,S15      ─ shield the credential, fix the ignore rules ─ ~10 min ── DO TODAY
   │
STEP 1  S2,S4,S5,S10 ─ make every doc tell the truth ───────── ~45 min ── no risk
   │                    (the _archive/ lines wait for R3)
STEP 2  S7,S8,S11    ─ clean the front door, file the clutter ─ ~25 min ── no risk
   │                    (commit yesterday's brief before moving it)
STEP 3  S3,S9,S13,S16 ─ settings & skill hygiene ────────────── ~40 min ── no risk
   ▼
 ╔══════════ YOU CONFIRM OR VETO EACH R-ITEM HERE (§6, using §8's answers) ══════════╗
   │
STEP 4  R1,R2  ─ stop the two silently failing automations ─── ~15 min ── ⚠️ live automation
   │             (R2 waits on §8 Q1 if still unanswered)
STEP 5  R3     ─ one coherent archive-rule rewrite ──────────── ~40 min ── ⚠️ edits the AI's core rules
   │             + gate-script list fix · then S12 (the linter check, now green)
STEP 6  R4,R6  ─ instruction-file import pattern; align lesson ─ ~45 min ── ⚠️ member content
   │             (R5 only after §8 Q2 is answered)
STEP 7  R7,R9,R10,R11,R12 ─ reshapes, re-arming, architecture ─ ~2 h ──── ⚠️ pipeline paths
   │             ONE item at a time, never two in one pass
STEP 8  R8     ─ skill-store layout ─ ONLY after §8 Q6 gets a fresh answer
```

</details>

---

## §8. WHAT I'M NOT SURE ABOUT — **ALL 7 CLOSED 2026-07-28**

Answers are recorded in full in **§0.6**; this table is the index. Nothing here is open any more.

| # | What I couldn't determine | Status | Resolution |
|---|---|---|---|
| 1 | Where the scheduled `/produce-video` run is configured | ✅ **CLOSED** | Owner: delete the schedule, it's no longer wanted. Location no longer blocks anything — find it and remove it (claude.ai → Scheduled tasks). See **§0.6 A1**, executes at §0.7 STEP 6 |
| 2 | Which review tool is used at the preview gate | ✅ **CLOSED** | `bash scripts/preview.sh <stem>` — with the honest caveat "and hope it opens a tab", which is now the actual fix. See **§0.6 A2**, executes at §0.7 STEP 10 |
| 3 | Whether the Drive `rclone` credential is valid | ✅ **MOOT** | The mirror was deleted outright (§0.2). Nothing to revive, nothing to test |
| 4 | Whether yesterday's brief's two un-re-verified claims hold (its S16: lesson-scripts README program tables; its R8: folder-skeleton variance) | ✅ **CLOSED — verified directly** | The 07-27 brief itself is **gone and unrecoverable** (never committed; not in `git log --all` or a full object scan). Both claims were checkable anyway. ① **TRUE, and worse:** `lesson-scripts/README.md` lists 2 nonexistent programs, omits 3 real ones, and links to two deleted files — **folded into S5**, §0.7 STEP 3. ② **Unrecoverable specifics, already covered** by R7 + S11. See **§0.6 A7** |
| 5 | What to do with `.s3_setup_FVC8bRn6m` | ✅ **CLOSED** | Delete it. See **§0.6 A5**, executes at §0.7 STEP 2 |
| 6 | Whether `.agents/` is intentional or an accident | ✅ **CLOSED** | Intentional *today* (it's the live primary store — §0.4), and being unwound: **P4 approved**. Nothing touches it until §0.7 STEP 13 |
| 7 | Whether `.devcontainer/postCreate.sh` should be revived or retired | ✅ **DONE 2026-07-28** | Retired. Brand safeguard folded into `devcontainer.json`'s `postCreateCommand` (JSON + shell both validated before removal); `setup.sh` deliberately not folded in — it would re-arm the unplugged hooks (R10) and re-duplicate the reminder hooks (S3). See **§0.2** and **§0.6 A6** |

---

## §9. PLAIN-ENGLISH GLOSSARY

- **Archive** — a set-aside folder where retired files are kept instead of deleted, so they can always be brought back. The root `_archive/` was deleted on July 23; the plan recreates it (S7) and R3 rewrites the rules that govern it.
- **CLAUDE.md** — the instruction file the AI assistant automatically reads at the start of every session in this repo.
- **Commit** — one saved snapshot of the repo's files, with a note saying what changed; git keeps every snapshot forever. **Push** — sending your commits up to GitHub, where others (and automations) can see them. **Force-push** — a push that overwrites history on GitHub; the risky variant.
- **Credential / secret / token** — a stored login key that lets software act as you without a password prompt. Publishing one is like publishing a house key.
- **Deny-list / pre-approved commands** — two lists inside the settings file: commands the AI may never run, and commands it may run *without asking you*. This repo's deny-list is empty and its pre-approved list currently includes delete commands (S13).
- **Dotfiles** — a personal setup repo that GitHub Codespaces automatically installs into every new development machine you create. This repo is currently doing double duty as yours (R12).
- **Drive mirror** — the automation meant to copy this repo's documents into Google Drive after every change.
- **Frontmatter / label** — the small header block at the top of a skill file that gives its name and description; it's how the AI recognizes what the skill is for (S9).
- **Git** — the version-control system underneath this repo; it records every change and can restore any past state.
- **GitHub Action / workflow** — an automation that GitHub runs for you (here: the Drive mirror) every time changes are pushed.
- **Hook** — a small script the AI's settings can attach to its actions, so a check runs automatically every time — enforced, not optional.
- **Hub / README** — a short table-of-contents file inside a folder explaining what each file there is for.
- **Linter** — a checker script that scans files for known problems and prints warnings. This repo's is `scripts/lint-refs.sh` (S12).
- **Registry / hand-list** — a hand-maintained list of what exists (the thing automatic discovery makes unnecessary) (R11).
- **Repo (repository)** — this whole project folder, everything in it, plus its full git history.
- **Root** — the top level of the repo; the first thing anyone sees when they open it.
- **Routine** — a task scheduled to run on its own at set times (here: the video-pipeline run firing roughly hourly).
- **Settings file** — the configuration file (`settings.json`) that controls what the AI may do without asking, and which hooks run. There are two: the project's own, and a global one — which here turns out to be the same file in a second clone (S3, R12).
- **Skill** — a packaged, on-demand instruction set the AI loads only when a matching task comes up.
- **Stub / pointer** — a near-empty file left at an old location whose only job is to say "the real content moved to X", so nothing that looks there breaks (R4).
- **Subagent** — a helper AI session that does one focused job and reports back.
- **Symlink** — a filesystem shortcut: a directory entry that *points at* a file living somewhere else rather than containing its own copy. Delete the target and the shortcut dangles. Central to R8.
- **Tokens / context** — the AI's working memory budget. Everything in always-loaded files is paid for out of it on every message; skills and hooks mostly aren't (§2 row 7).
- **Tracked file** — a file git is watching and saving history for (as opposed to ignored, local-only files). Only tracked files can be restored from history.
- **TTS (text-to-speech)** — the software that turns lesson scripts into narration audio; its missing credentials are what blocks the scheduled video routine (R2).
- **Vendored** — copied from an outside source into this repo wholesale, rather than written here.

---

## Revision log (red team, 2026-07-28)

| Finding | Edit applied |
|---|---|
| RT-1 🔴 | R8 rewritten: "byte-identical duplicates" claim replaced with the symlink truth; recorded confirmation voided; new decision routed to §8 Q6. §1 duplicates row, §2 row 5, and both §4 trees corrected to match |
| RT-2 🔴 | S1 removed from the safe list, reissued as R10 with the arming history, the budget-hook incident, the stale gate list, and the two non-protection scripts spelled out. "Written, tested… never plugged in" replaced with the true history everywhere |
| RT-3 🔴 | S6 removed from the safe list, reissued as R11 as a coordinated three-file change; "referenced by nothing" claim replaced with the two real references |
| RT-4 🔴 | S12 re-sequenced after R3 in §5 and §7, with the reason (8 pre-existing warnings only R3 clears); citation downgraded to principle-analogy |
| RT-5 🔴 | Credential exposure added: new §1 row and paragraph, new S14 (ignore shields, Step 0), new R12 (dotfiles architecture, settings.local.json, push pre-approval, Infisical IDs) |
| RT-6 | S3 and S13 rewritten around the second-clone reality; durability and worst-case claims corrected |
| RT-7 | `_archive/` routing carved out of S4 into R3; MAP.md's AFTER line now carries R3 ⚠️ |
| RT-8 | Counts fixed: root 30 (+4 previously omitted entries drawn in BEFORE tree), scripts/ 12, render-qa code files 10 (13 with tests), hooks/ 9+1, cadence "roughly hourly", brand-guide wording, summary arithmetic 32→~29 |
| RT-9 | §8 Q5 rewritten with the true file facts (user-owned, readable, deletable) |
| RT-10 | R4 re-cited to STD-31, flipped to the docs-endorsed import pattern; contradicting repo evidence recorded |
| RT-11 | §3 synced with the corrected standard file (STD-8 split, STD-15 inference note, STD-31 added) |
| RT-12 | §2 rows 5–7 rephrased (inference marked, STD-22/23 scope note, hook-output caveat) |
| RT-13 | §4 trees redrawn: phantom attributions removed (skills-lock now genuinely in S2; .s3 routed to Q5), this brief's own disposition added (S7), S6/R11 effect moved to the hooks/ line, R9 and nested `_archive/` lines added, every conditional line marked with its R-item |
| RT-14 | Archive destination defined (recreated root `_archive/` via S7, rule ownership in R3, nested archives folded into R3's scope); glossary entry updated |
| RT-15 | Confirmation note corrected (six recorded, all confirm-or-veto at the gate); R2↔Q1 dependency flagged in both places; S10's either/or resolved; §1 time framing made honest |
| RT-16 | Glossary pointer added to the header; ~10 missing terms added; R6's second program named; deletion-history reassurance added to §1; legend split per tree; 215-line file identified; hooks arithmetic reconciled (9 scripts + 1 data file; 7 candidates + skill-eval pair + settings' 2 reminders) |
| RT-17 | New S15 (dead ignore negation) and S16 (hook matchers); S7 commit-first note; S9 dead-command fix; S11 citation repointing; R5 third candidate; R7 path-fragility + log rotation + open window; §8 Q7 (postCreate safeguard) added |

## Revision log (owner directive, 2026-07-28)

| Change | Detail |
|---|---|
| §0 added | Brief promoted to single source of truth for the refactor; owner policy recorded (markdown doesn't govern; rules/hooks/config do; machine-first registries) |
| Executed | Deleted `_heygen-test-preview/`, `operations/`, `programs/`, `references/`, `GOVERNANCE.md`, `MAP.md`, `context/goals.md`; removed the entire Drive mirror (workflow, build-docx.sh, docs, endpoints section); updated root CLAUDE.md routing + Hard Rules + hub claim; rewrote lint-refs.sh for the new root — passing healthy |
| Superseded | S2/S4 moot; S7 partially (heygen deleted, not archived); S10 done; S12 unblocked; R1 resolved by removal; R3 mostly moot; R10's gate-script repair replaced by P3 (delete it) |
| Answered | §8 Q6: `.agents/` is the primary skill store reached by 10 symlinks from `.claude/skills/` — unwind plan is P4 |
| Added | P1 `.claude/rules/` proposal; P2 `config/endpoints.json` replacing endpoints.md; P3 retire dead governance machinery; P4 unwind `.agents/`; new execution order |

## Revision log (owner answers round 2 + brief reconciliation, 2026-07-28)

*This pass folded the directive and the round-2 answers through the whole document, so §1–§9 no longer contradict §0.*

| Change | Detail |
|---|---|
| **Executed** | **S14 + S15 done.** `.gitignore` gained the Claude Code credential/session block (9 rules incl. `.claude/.credentials.json`); `.vscode/` → `.vscode/*` so the `!tasks.json` negation works; the `.s3_setup_*` rule's false "root-owned, 0600" comment corrected. Verified `git check-ignore` matches no tracked file. **Step 0 closed** |
| §0.2 | Records the S14/S15 execution, the verification, and the current root count (25); notes `.github/` is gone entirely, not emptied |
| §0.3 | Status table rebuilt: S14/S15 → DONE; R2/R5/R9/R12 → ANSWERED with their new shapes; Q5/Q7 rows added; P1–P4 row added |
| §0.4 | Records that **P4 is approved**, so `.agents/` is on a clock rather than indefinitely deferred |
| §0.5 | Retitled **"ALL APPROVED"** with a one-line unambiguous approval statement covering P1–P4 (the ambiguity the owner flagged). P2's Infisical open question **closed** per A4: IDs move to Codespaces secrets, registry holds a pointer only |
| **§0.6 NEW** | The six round-2 answers recorded verbatim with their plan consequences (A1 delete the schedule · A2 preview.sh canonical + fix the flakiness · A3 Oxana final, purge "Ann" · A4 Infisical/Codespaces architecture · A5 delete `.s3` · A6 fold the brand safeguard, retire postCreate.sh). Q3 closed as moot; Q4 flagged as the only open item |
| **§0.7 NEW** | The live 14-step execution order, replacing the one-line order at the end of §0.5 — every step names its exact file edits, its risk, and which of the five surviving R-items still needs a gate |
| §1 | Banner added: three of its findings are now historical (Drive mirror deleted, credential closed, rulebooks deleted); the delete pre-approval finding still stands |
| §4 | **Both trees redrawn.** BEFORE → "NOW" = verified 25-item post-directive root; AFTER = the 21-item post-execution root, including `config/`, `.claude/rules/`, the recreated `.github/`, and `.agents/` gone. Summary table re-cut on now-vs-after with two new rows (skill store, silent automations). Note added that `⛔` now means deleted, not archived, per §0.1 |
| §5 | Post-directive banner: S14/S15 done, S2/S4/S10 moot-or-done, **S12's "after R3" caveat void** (linter is green today), S7 partially superseded; archive→delete policy noted |
| §6 | Post-directive banner (5 of 12 still need a gate) + four rows rewritten from ⏸️/recorded to ✅ SETTLED with the owner's own words: R2, R5, R9, R12 |
| §7 | Marked **superseded by §0.7**, old order collapsed into a `<details>` block, sign-off gate restated as R4/R6/R7/R10/R11 |
| §8 | Rewritten as a status index: **6 of 7 closed**, each pointing at its §0.6 answer and §0.7 step; Q4 is the lone open item and blocks nothing |
| **Executed (round 3)** | **A6 done: `.devcontainer/postCreate.sh` retired.** Brand anti-fabrication safeguard folded into `devcontainer.json`'s `postCreateCommand`; JSON parse + `bash -n` both validated before `git rm`. `scripts/setup.sh` deliberately not folded (it would re-arm R10's unplugged hooks and re-duplicate S3's reminder hooks); global hyperframes install dropped after verifying every real call uses `npx`. Side benefit recorded: this makes S3's fix durable, since postCreate.sh was setup.sh's only automated caller |
| **§8 Q4 closed (A7)** | Established that `repo-audit-brief-2026-07-27.md` is **gone and unrecoverable** (never committed — absent from `git log --all` and a full `rev-list --objects` scan). Verified both claims from the surviving paraphrase: ① `lesson-scripts/README.md`'s program table is **confirmed wrong and worse than described** — 2 phantom programs listed, 3 real ones omitted, plus links to deleted `programs/` and `GOVERNANCE.md` and the retired PUBLISH/MP4-review gates → **folded into S5**, §0.7 STEP 3, with a recommendation to delete the table rather than re-maintain it (STD-22); ② folder-skeleton variance is unrecoverable and already covered by R7 + S11. **§8 now has zero open items** |
| Verified this session | 25 root items · `.github/` absent · `scripts/` = 11 items · `review.py` referenced by nothing (tasks.json wires `review.sh`; `review.py`'s own docstring claim is false) · two live "Ann" lines at `frame.md:57` and `design-system/CLAUDE.md:59` · `postCreate.sh` vs `devcontainer.json` overlap is ffmpeg+Infisical, leaving the brand safeguard and the hyperframes install as the only unique content · settings.json still allows `rm`/`find`/`cat`/`head`/`tail` |
