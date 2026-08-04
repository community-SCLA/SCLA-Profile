#!/usr/bin/env bash
# lint-refs.sh — repo health linter for the SCLA knowledge base.
# Run from anywhere; no dependencies beyond coreutils + grep.
# Exit 0 = healthy, exit 1 = at least one warning.

set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"

WARNINGS=0
warn() { echo "WARN: $*"; WARNINGS=$((WARNINGS + 1)); }
ok()   { echo "  ok: $*"; }

# Directories/files never linted: archives, local session memory, git internals.
EXCLUDES=(--exclude-dir=_archive --exclude-dir=.git --exclude-dir=.remember --exclude-dir=node_modules)
# docs/_archive is nested; filter it from grep output instead.
filter_archives() { grep -v "^\./docs/_archive/" | grep -v "^docs/_archive/"; }

# ── 1. Backtick path references in root governance files exist on disk ──────
echo "[1/14] Backtick path references resolve"
# Intentional non-paths (_archive/ is named by CLAUDE.md's ban rule; no root _archive exists)
SKIP_PATHS="_archive/ scheduled-tasks/ .claude/agents/ notes/ misc/ tmp/ .env .env.example inbox/ .remember/ decisions-log.md"
REF_FAIL=0
for f in CLAUDE.md; do
  while IFS= read -r ref; do
    path="${ref%%#*}"          # drop anchor fragments
    path="${path%/}"           # tolerate trailing slash
    [ -z "$path" ] && continue
    case " $SKIP_PATHS " in *" $path "* | *" $path/ "*) continue ;; esac
    if [ ! -e "$path" ]; then
      warn "$f references missing path: $ref"
      REF_FAIL=1
    fi
  done < <(grep -o '`[^`]*`' "$f" 2>/dev/null | tr -d '\`' |
           grep -E '^[A-Za-z_.][A-Za-z0-9_./-]*$' | grep -E '/|\.(md|sh|yml|yaml|json|py|svg|mjs)$' || true)
done
[ "$REF_FAIL" -eq 0 ] && ok "all backtick paths in CLAUDE.md exist"

# ── 2. Word budgets ──────────────────────────────────────────────────────────
echo "[2/14] Root word budgets (CLAUDE<=600)"
check_budget() {
  local file=$1 limit=$2 words
  words=$(wc -w < "$file")
  if [ "$words" -gt "$limit" ]; then warn "$file is $words words (budget $limit)"; else ok "$file: $words/$limit words"; fi
}
check_budget CLAUDE.md 600

# ── 3. No stale decisions-log paths ──────────────────────────────────────────
echo "[3/14] No references to old decisions-log path"
# decisions/log.md is excluded: its migration entry legitimately records the old path.
HITS=$(grep -rn "${EXCLUDES[@]}" -e "source-of-truth/decisions-log" -e "](\./decisions-log" . 2>/dev/null |
       filter_archives | grep -v "scripts/lint-refs.sh" | grep -v "decisions/log.md" || true)
if [ -n "$HITS" ]; then warn "stale decisions-log references:"$'\n'"$HITS"; else ok "none found"; fi

# ── 4. No template placeholders ──────────────────────────────────────────────
echo "[4/14] No unfilled template placeholders"
# .claude/skills excluded: the onboard/ingest wizards use placeholder strings as instructions.
HITS=$(grep -rn "${EXCLUDES[@]}" --exclude-dir=.claude -e "\[YOUR_" -e "\[project-1\]" -e "\[DATE\]" . 2>/dev/null |
       filter_archives | grep -v "scripts/lint-refs.sh" || true)
if [ -n "$HITS" ]; then warn "template placeholders found:"$'\n'"$HITS"; else ok "none found"; fi

# ── 5. Critical files exist ──────────────────────────────────────────────────
echo "[5/14] Critical files present"
CRITICAL="CLAUDE.md config/endpoints.json scla.config.yml sync.sh .gitignore
context/me.md decisions/log.md
brand/visual-identity.md brand/voice-and-tone.md
member-support/faqs.md"
MISSING=0
for f in $CRITICAL; do
  if [ ! -f "$f" ]; then warn "critical file missing: $f"; MISSING=1; fi
done
[ "$MISSING" -eq 0 ] && ok "all critical files present"

# ── 6. Stale brand hex values ────────────────────────────────────────────────
echo "[6/14] No stray legacy hex values outside flagged locations"
# Intent: catch legacy hex hardcoded in docs, not in the actual art. Allowed:
# .svg files (the logo source art legitimately carries these colors),
# assets/README.md (describes the SVG file contents), and projects/video-production/
# (carries a TODO [TEAM DECISION] flag until the team picks the canonical set).
HITS=$(grep -rni "${EXCLUDES[@]}" -e "#F1B32E" -e "#55A4DD" . 2>/dev/null | filter_archives |
       grep -v '\.svg:' | grep -v "brand/assets/README.md" |
       grep -v "projects/video-production/" | grep -v "scripts/lint-refs.sh" || true)
if [ -n "$HITS" ]; then warn "legacy hex values found:"$'\n'"$HITS"; else ok "none found"; fi

# ── 7. No archive routing pointers ───────────────────────────────────────────
echo "[7/14] No '_archive/source-of-truth/' routing pointers in live KB"
# Rule: _archive/ is read-only provenance, never a canonical owner / routing target.
# Flag backtick-quoted `_archive/source-of-truth/...` pointers in the routing/governance
# files and the live KB. Allowed and NOT flagged:
#   - `source:` / `Source:` provenance citation lines (traceability)
#   - `_archive/source-dumps/` paths (raw Drive exports, reached via citations)
#   - decisions/log.md (its history legitimately cites old/archived paths)
#   - scripts/lint-refs.sh (this file)
HITS=$(grep -rn "${EXCLUDES[@]}" -e '`_archive/source-of-truth/' \
         CLAUDE.md brand member-support partnerships projects context 2>/dev/null |
       filter_archives |
       grep -v "scripts/lint-refs.sh" | grep -v "decisions/log.md" |
       grep -viE '^[^:]*:[0-9]+:[[:space:]]*source:' || true)
if [ -n "$HITS" ]; then warn "archive routing pointers found (route to live owner instead):"$'\n'"$HITS"; else ok "none found"; fi

# ── 8. No retired scla/ paths ────────────────────────────────────────────────
echo "[8/14] No retired scla/ path references in live files"
# Knowledge folders were un-nested from scla/ to root on 2026-07-03. Allowed:
# decisions/log.md and audits/ (historical records), _archive/ (provenance).
HITS=$(grep -rn "${EXCLUDES[@]}" --exclude-dir=audits -e 'scla/' . 2>/dev/null |
       filter_archives | grep -v "decisions/log.md" |
       grep -v "scripts/lint-refs.sh" | grep -v "hooks/governance-check.sh" || true)
if [ -n "$HITS" ]; then warn "retired scla/ paths found (un-nested layout is canonical):"$'\n'"$HITS"; else ok "none found"; fi

# (Former check 9 — hooks/skill-rules.json registry — retired 2026-07-28 with
#  the hand-maintained skill list itself, R11. Skills are auto-discovered from
#  .claude/skills/; no registry to cross-check.)

# ── 9. Endpoints registry parses, matches schema, carries no secrets ─────────
echo "[9/14] config/endpoints.json valid (schema + no secret material)"
REG_OUT=$(python3 - <<'PYEOF' 2>&1
import json, re
d = json.load(open('config/endpoints.json'))
assert isinstance(d, dict) and d, 'top level must be a non-empty object'
for svc, entries in d.items():
    if svc == '_meta':
        continue
    assert isinstance(entries, list) and entries, f'{svc}: must be a non-empty list'
    for e in entries:
        assert isinstance(e, dict), f'{svc}: entries must be objects'
        for k in ('name', 'type'):
            assert isinstance(e.get(k), str) and e[k], f'{svc}: entry missing {k}'
        for k in ('id', 'url', 'used_by', 'verified', 'notes'):
            assert k in e, f"{svc}/{e['name']}: missing key {k}"
text = json.dumps(d)
for pat in (r'[A-Za-z0-9_\-]{40,}', r'sk-[A-Za-z0-9]{20}', r'eyJ[A-Za-z0-9_\-]{20,}\.'):
    m = re.search(pat, text)
    assert not m, f'possible secret material: {m.group(0)[:12]}…'
print('valid')
PYEOF
)
if [ "$REG_OUT" = "valid" ]; then
  ok "config/endpoints.json parses, matches schema, no secret material"
else
  warn "config/endpoints.json: $REG_OUT"
fi

echo "[10/14] STD-35: no doc claims a mechanism that does not exist"
# The Repo Structure Playbook v1.1, STD-35 — a written rule is a request; only
# a mechanism is a guarantee. This cannot make prose enforceable; it makes prose
# unable to LIE about being enforced. Hard-fails only on a broken claim (a doc
# naming a checker that is missing or that nothing invokes). The unbacked-rule
# gap inventory is reported, not enforced, per STD-38 ("non-blocking at first,
# so it teaches instead of nags") and the playbook's own warning that hardening
# a guideline into a hard rule is itself a defect. Added 2026-07-28.
ENF_OUT="$(python3 "$(dirname "$0")/check-enforcement.py" 2>&1)"
if [ $? -eq 0 ]; then
  ok "$(printf '%s' "$ENF_OUT" | head -1)"
else
  warn "$(printf '%s' "$ENF_OUT" | sed -n '1,8p')"
fi

echo "[11/14] No workspace carries an AGENTS.md"
# The vendor's generic 95-line skill router. `hyperframes init` writes it beside
# CLAUDE.md, and batch-prepare.sh neutralized only CLAUDE.md, so it sat in every
# workspace — committed 15 times over — telling cold build subagents to
# hand-edit index.html and route to skills this repo deleted. Nothing reads it:
# a build subagent is handed _run/BUILD-KIT.md by path, and anyone opening a
# workspace inherits projects/video-production/CLAUDE.md from the parent tree.
# It was pure active misdirection sitting in the working directory.
# Deleting the copies fixed the instance; this check is what stops it returning
# the next time the vendor CLI is upgraded and someone re-runs init.
# design-system/AGENTS.md is deliberately NOT in scope: it is a hand-written
# SCLA project doc that design-contract.md cites by name, not vendor litter.
VP="$(dirname "$0")/../projects/video-production"
STRAY_AGENTS="$(find "$VP/renders-hyperframes" "$VP/experiments" -name 'AGENTS.md' \
  -not -path '*/_archive/*' 2>/dev/null || true)"
TRACKED_AGENTS="$(git -C "$(dirname "$0")/.." ls-files \
  '*renders-hyperframes/*AGENTS.md' '*experiments/*AGENTS.md' 2>/dev/null || true)"
# The mechanism itself, not just today's result: if this line is ever dropped
# from batch-prepare.sh the litter comes straight back on the next prepare.
# `grep -c` PRINTS 0 and EXITS 1 on no-match, so `|| echo 0` appended a second
# 0 and `[ "00" -eq 0 ]` died with "integer expression expected" — leaving the
# mechanism half of this check permanently unevaluated. Caught by running the
# failure case instead of trusting the success case.
PREPARE_PURGES="$(grep -c 'scaffold/AGENTS.md' "$(dirname "$0")/batch-prepare.sh" \
  2>/dev/null || true)"
if [ -n "$STRAY_AGENTS$TRACKED_AGENTS" ]; then
  warn "vendor AGENTS.md present (delete it — a workspace carries no agent
instructions of its own):
$STRAY_AGENTS$TRACKED_AGENTS"
elif [ "$PREPARE_PURGES" -eq 0 ]; then
  warn "batch-prepare.sh no longer deletes scaffold/AGENTS.md — the next
prepared workspace will carry the vendor router again"
else
  ok "no workspace AGENTS.md; batch-prepare.sh still deletes the scaffold copy"
fi

echo "[12/14] render-qa test suite"
# The render-qa test suite actually runs. Until 2026-07-29 the tests
# existed and nothing executed them: not CI, not run_tests.py (which only ran
# its own cases and silently skipped its five sibling test_*.py files). The
# thresholds pinned in test_variety.py and test_gates.py are what stop a future
# session from "fixing" a gate by loosening it until the rejected build passes,
# so they have to be enforced, not merely present.
RQ_TESTS="$(dirname "$0")/../projects/video-production/render-qa/tests/run_tests.py"
if [ -f "$RQ_TESTS" ]; then
  if TEST_OUT="$(python3 "$RQ_TESTS" 2>&1)"; then
    ok "render-qa suite: $(printf '%s' "$TEST_OUT" | grep -c '  ok ') assertions pass"
  else
    warn "render-qa suite FAILED:
$(printf '%s' "$TEST_OUT" | grep -E 'FAIL|failed' | head -8)"
  fi
else
  warn "render-qa test suite missing at $RQ_TESTS"
fi

echo "[13/14] Lesson-script layout: the folder name is the stage name"
# The pipeline has no database — the folders ARE the state. That only works
# while the folders say what they mean, and on 2026-08-04 one of them did not:
# `rendered/` had meant *published* for a week, which produced a
# self-contradiction inside render-lessons/SKILL.md and four disagreeing status
# narratives. Renaming fixed the instance. This check is what stops the next
# one, and it also holds the owner's standing rule that a RAW script gets its
# own folder and is never dumped at a program root.
LAYOUT_FAIL=0
LS_ROOT="projects/video-production/lesson-scripts"
for prog in "$LS_ROOT"/*/; do
  [ -d "$prog" ] || continue
  slug="$(basename "$prog")"
  # A loose .txt at the program root: raw scripts live in inbox/.
  STRAY="$(find "$prog" -maxdepth 1 -name '*.txt' 2>/dev/null || true)"
  if [ -n "$STRAY" ]; then
    warn "raw script(s) at the root of lesson-scripts/$slug — raw goes in inbox/:
$(printf '%s' "$STRAY" | sed 's|^|  |')
  fix: git mv <file> $LS_ROOT/$slug/inbox/"
    LAYOUT_FAIL=1
  fi
  # Retired stage names. Keeping them would mean two vocabularies at once,
  # which is the condition this whole rename existed to end.
  for dead in refined rendered avatar; do
    if [ -d "$prog$dead" ]; then
      warn "lesson-scripts/$slug/$dead/ is a retired stage name (2026-08-04).
  inbox/ -> ready/ -> published/ are the only three; avatar/ was deleted with
  the avatar lane."
      LAYOUT_FAIL=1
    fi
  done
  for stage in inbox ready published; do
    if [ ! -d "$prog$stage" ]; then
      warn "lesson-scripts/$slug/ has no $stage/ — every program carries all
  three stage folders, so nothing has to remember to create one mid-flight."
      LAYOUT_FAIL=1
    fi
  done
done
[ "$LAYOUT_FAIL" -eq 0 ] && ok "every program has inbox/ ready/ published/ and nothing loose at its root"

echo "[14/14] PIPELINE-STATUS.md matches a fresh regeneration"
# The status doc is generated, and its whole value is that it cannot go stale.
# It went stale anyway (23/12 in the doc, 21/14 on disk) because nothing on the
# BUILD side regenerated it — only publish did. build-claim.sh, build-gate.sh
# and build-release.sh now do too; this check is what proves the wiring is
# still connected rather than assuming it.
#
# renders-hyperframes/ is gitignored, so CI has no workspaces and this check has
# nothing to compare — it prints why it skipped rather than passing silently.
WS_DIR="projects/video-production/renders-hyperframes"
STATUS_DOC="projects/video-production/PIPELINE-STATUS.md"
LIVE_WS="$(find "$WS_DIR" -mindepth 1 -maxdepth 1 -type d \
  -not -name '_*' -not -name '.*' 2>/dev/null | head -1 || true)"
if [ -z "$LIVE_WS" ]; then
  ok "no build workspaces on this machine — nothing to compare (CI always lands here)"
elif [ ! -f "$STATUS_DOC" ]; then
  warn "PIPELINE-STATUS.md is missing while build workspaces exist —
  regenerate it: bash scripts/batch-status.sh --write"
else
  FRESH="$(mktemp)"
  if bash scripts/batch-status.sh --write "$FRESH" >/dev/null 2>&1 \
     && diff -q "$FRESH" "$STATUS_DOC" >/dev/null 2>&1; then
    ok "PIPELINE-STATUS.md is current"
  else
    warn "PIPELINE-STATUS.md has drifted from what the folders say.
  A build ran without regenerating it, or someone hand-edited a generated file.
  Fix: bash scripts/batch-status.sh --write
$(diff "$STATUS_DOC" "$FRESH" 2>/dev/null | head -12 | sed 's|^|  |')"
  fi
  rm -f "$FRESH"
fi

echo
if [ "$WARNINGS" -gt 0 ]; then
  echo "lint-refs: $WARNINGS warning(s)"
  exit 1
fi
echo "lint-refs: healthy"
exit 0
