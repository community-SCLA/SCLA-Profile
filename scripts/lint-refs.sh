#!/usr/bin/env bash
# lint-refs.sh — repo health linter for the SCLA knowledge base.
# Run from anywhere; no dependencies beyond coreutils + grep.
# Exit 0 = healthy, exit 1 = at least one warning. See GOVERNANCE.md "Health Checks".

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
echo "[1/9] Backtick path references resolve"
# Documented future homes + intentional non-paths (see GOVERNANCE.md "Future homes" / "What NOT to add")
SKIP_PATHS="references/ scheduled-tasks/ .claude/agents/ operations/sops/ notes/ misc/ tmp/ .env .env.example inbox/ .remember/ decisions-log.md"
REF_FAIL=0
for f in CLAUDE.md MAP.md GOVERNANCE.md; do
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
[ "$REF_FAIL" -eq 0 ] && ok "all backtick paths in CLAUDE.md / MAP.md / GOVERNANCE.md exist"

# ── 2. Word budgets ──────────────────────────────────────────────────────────
echo "[2/9] Root word budgets (CLAUDE<=600 MAP<=700 GOVERNANCE<=1000)"
check_budget() {
  local file=$1 limit=$2 words
  words=$(wc -w < "$file")
  if [ "$words" -gt "$limit" ]; then warn "$file is $words words (budget $limit)"; else ok "$file: $words/$limit words"; fi
}
check_budget CLAUDE.md 600
check_budget MAP.md 700
check_budget GOVERNANCE.md 1000

# ── 3. No stale decisions-log paths ──────────────────────────────────────────
echo "[3/9] No references to old decisions-log path"
# decisions/log.md is excluded: its migration entry legitimately records the old path.
HITS=$(grep -rn "${EXCLUDES[@]}" -e "source-of-truth/decisions-log" -e "](\./decisions-log" . 2>/dev/null |
       filter_archives | grep -v "scripts/lint-refs.sh" | grep -v "decisions/log.md" || true)
if [ -n "$HITS" ]; then warn "stale decisions-log references:"$'\n'"$HITS"; else ok "none found"; fi

# ── 4. No template placeholders ──────────────────────────────────────────────
echo "[4/9] No unfilled template placeholders"
# .claude/skills excluded: the onboard/ingest wizards use placeholder strings as instructions.
HITS=$(grep -rn "${EXCLUDES[@]}" --exclude-dir=.claude -e "\[YOUR_" -e "\[project-1\]" -e "\[DATE\]" . 2>/dev/null |
       filter_archives | grep -v "scripts/lint-refs.sh" || true)
if [ -n "$HITS" ]; then warn "template placeholders found:"$'\n'"$HITS"; else ok "none found"; fi

# ── 5. Critical files exist ──────────────────────────────────────────────────
echo "[5/9] Critical files present"
CRITICAL="CLAUDE.md MAP.md GOVERNANCE.md connections.md endpoints.md scla.config.yml sync.sh .gitignore
context/me.md context/goals.md decisions/log.md
brand/visual-identity.md brand/voice-and-tone.md
operations/team-roster.md member-support/faqs.md hooks/skill-rules.json"
MISSING=0
for f in $CRITICAL; do
  if [ ! -f "$f" ]; then warn "critical file missing: $f"; MISSING=1; fi
done
[ "$MISSING" -eq 0 ] && ok "all critical files present"

# ── 6. Stale brand hex values ────────────────────────────────────────────────
echo "[6/9] No stray legacy hex values outside flagged locations"
# Intent: catch legacy hex hardcoded in docs, not in the actual art. Allowed:
# .svg files (the logo source art legitimately carries these colors),
# assets/README.md (describes the SVG file contents), and projects/video-production/
# (carries a TODO [TEAM DECISION] flag until the team picks the canonical set).
HITS=$(grep -rni "${EXCLUDES[@]}" -e "#F1B32E" -e "#55A4DD" . 2>/dev/null | filter_archives |
       grep -v '\.svg:' | grep -v "brand/assets/README.md" |
       grep -v "projects/video-production/" | grep -v "scripts/lint-refs.sh" || true)
if [ -n "$HITS" ]; then warn "legacy hex values found:"$'\n'"$HITS"; else ok "none found"; fi

# ── 7. No archive routing pointers ───────────────────────────────────────────
echo "[7/9] No '_archive/source-of-truth/' routing pointers in live KB"
# Rule: _archive/ is read-only provenance, never a canonical owner / routing target.
# Flag backtick-quoted `_archive/source-of-truth/...` pointers in the routing/governance
# files and the live KB. Allowed and NOT flagged:
#   - `source:` / `Source:` provenance citation lines (traceability)
#   - `_archive/source-dumps/` paths (raw Drive exports, reached via citations)
#   - decisions/log.md (its history legitimately cites old/archived paths)
#   - scripts/lint-refs.sh (this file)
HITS=$(grep -rn "${EXCLUDES[@]}" -e '`_archive/source-of-truth/' \
         CLAUDE.md MAP.md GOVERNANCE.md brand member-support operations programs partnerships projects context 2>/dev/null |
       filter_archives |
       grep -v "scripts/lint-refs.sh" | grep -v "decisions/log.md" |
       grep -viE '^[^:]*:[0-9]+:[[:space:]]*source:' || true)
if [ -n "$HITS" ]; then warn "archive routing pointers found (route to live owner instead):"$'\n'"$HITS"; else ok "none found"; fi

# ── 8. No retired scla/ paths ────────────────────────────────────────────────
echo "[8/9] No retired scla/ path references in live files"
# Knowledge folders were un-nested from scla/ to root on 2026-07-03. Allowed:
# decisions/log.md and audits/ (historical records), _archive/ (provenance).
HITS=$(grep -rn "${EXCLUDES[@]}" --exclude-dir=audits -e 'scla/' . 2>/dev/null |
       filter_archives | grep -v "decisions/log.md" |
       grep -v "scripts/lint-refs.sh" | grep -v "hooks/governance-check.sh" || true)
if [ -n "$HITS" ]; then warn "retired scla/ paths found (un-nested layout is canonical):"$'\n'"$HITS"; else ok "none found"; fi

# ── 9. Skill registry lists implemented skills only ──────────────────────────
echo "[9/9] hooks/skill-rules.json skills all exist in .claude/skills/"
REG_FAIL=0
for s in $(python3 -c "import json; print(' '.join(json.load(open('hooks/skill-rules.json'))['skills'].keys()))" 2>/dev/null); do
  if [ ! -f ".claude/skills/$s/SKILL.md" ]; then
    warn "skill-rules.json lists unimplemented skill: $s"
    REG_FAIL=1
  fi
done
[ "$REG_FAIL" -eq 0 ] && ok "registry matches implemented skills"

echo
if [ "$WARNINGS" -gt 0 ]; then
  echo "lint-refs: $WARNINGS warning(s)"
  exit 1
fi
echo "lint-refs: healthy"
exit 0
