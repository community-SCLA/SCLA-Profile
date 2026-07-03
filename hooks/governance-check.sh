#!/usr/bin/env bash
# governance-check.sh — Pre-tool structural governance enforcement.
# Fires before Write and Bash tool calls to block paths that violate GOVERNANCE.md rules.
# Stdin: {"tool_name": "...", "tool_input": {...}, "session_id": "..."}
# Exit 0 = allow. Exit 2 + stdout message = block (message shown to user).

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_name','unknown'))" 2>/dev/null || echo "unknown")

# Skip when the Bash command is running hook scripts themselves (avoids recursive self-checks)
if [[ "$TOOL_NAME" == "Bash" ]]; then
  _CMD=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('command',''))" 2>/dev/null || echo "")
  if [[ "$_CMD" == *"governance-check.sh"* || "$_CMD" == *"pre-tool.sh"* || "$_CMD" == *"post-tool.sh"* || "$_CMD" == *"stop.sh"* ]]; then
    exit 0
  fi
fi

# Repo root: one level up from this script's directory
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

block() {
  echo "GOVERNANCE BLOCK: $*"
  exit 2
}

# ── Extract candidate paths from the tool call ───────────────────────────────
extract_paths() {
  case "$TOOL_NAME" in
    Write|Edit)
      echo "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
p = d.get('tool_input', {}).get('file_path', '')
if p: print(p)
" 2>/dev/null
      ;;
    Bash)
      CMD=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('command',''))" 2>/dev/null || echo "")
      echo "$CMD" | python3 -c "
import sys, re
cmd = sys.stdin.read()
paths = []

# mkdir: capture path arguments (strip flags like -p, -m 755)
for m in re.finditer(r'\bmkdir\b((?:\s+-\S+)*)\s+(\S+)', cmd):
    path = m.group(2)
    if not path.startswith('-'):
        paths.append(path)

# mv / git mv: capture destination (last non-flag arg)
for m in re.finditer(r'\b(?:git\s+)?mv\b(.+)', cmd):
    args = [a for a in m.group(1).split() if not a.startswith('-')]
    if len(args) >= 2:
        paths.append(args[-1])

for p in paths:
    print(p)
" 2>/dev/null
      ;;
  esac
}

# ── Normalise a raw path to an absolute path inside the repo ─────────────────
normalise() {
  local raw="$1"
  local abs
  if [[ "$raw" == /* ]]; then
    abs="$raw"
  else
    abs="$REPO_ROOT/$raw"
  fi
  python3 -c "import os; print(os.path.normpath('$abs'))" 2>/dev/null || echo "$abs"
}

# ── Approved root-level names ─────────────────────────────────────────────────
APPROVED_ROOT=(
  CLAUDE.md MAP.md GOVERNANCE.md connections.md endpoints.md
  scla.config.yml sync.sh .gitignore .mcp.json
  .claude .devcontainer _archive audits brand context decisions hooks
  member-support operations partnerships programs projects
  references scripts templates .remember .env
)

is_approved_root() {
  local item="$1"
  for a in "${APPROVED_ROOT[@]}"; do
    [[ "$item" == "$a" ]] && return 0
  done
  return 1
}

# ── Per-path rule checks ──────────────────────────────────────────────────────
check_path() {
  local raw_path="$1"
  local abs_path rel_path

  abs_path=$(normalise "$raw_path")

  # Only enforce paths inside the repo
  [[ "$abs_path" != "$REPO_ROOT"* ]] && return 0

  rel_path="${abs_path#$REPO_ROOT/}"

  # ── Rule 0: _archive/ is read-only provenance ────────────────────────────
  # Existing archived files must never be edited or overwritten. Adding a NEW
  # file (retiring content into the archive) is allowed.
  if [[ ("$rel_path" == "_archive" || "$rel_path" == _archive/*) && -e "$abs_path" ]]; then
    block "'$rel_path' already exists inside _archive/ — read-only provenance. \
Never edit or overwrite archived files. \
See GOVERNANCE.md — 'Never route to the archive'."
  fi

  # Skip paths that already exist — we only gate creation of new items
  [[ -e "$abs_path" ]] && return 0

  local basename
  basename=$(basename "$rel_path")

  # ── Rule 1: Banned directory names anywhere in the path ──────────────────
  # (notes/, misc/, tmp/, inbox/ are graveyard dirs per GOVERNANCE.md)
  IFS='/' read -ra PARTS <<< "$rel_path"
  for part in "${PARTS[@]}"; do
    case "$part" in
      notes|misc|tmp|inbox)
        block "'$rel_path' contains banned directory name '$part'. \
Graveyard directories are not allowed. Use an existing folder. \
If a new folder is truly needed, log it in decisions/log.md first. \
See GOVERNANCE.md — 'What NOT to add'."
        ;;
    esac
  done

  # ── Rule 2: Every new path must live under an approved root item ─────────
  # Gates root-level additions AND nested paths whose first segment is not an
  # approved directory (e.g. re-creating a retired scla/ tree).
  if ! is_approved_root "${PARTS[0]}"; then
    block "New path '$rel_path' is outside the approved root layout \
(first segment '${PARTS[0]}' not approved). \
Root additions require a decisions/log.md entry first. \
Approved root items: ${APPROVED_ROOT[*]}. \
See GOVERNANCE.md — 'Approved Root Layout'."
  fi

  # ── Rule 3: No parallel decisions log ────────────────────────────────────
  if [[ "$basename" == "decisions-log.md" || "$basename" == "decisions_log.md" ]]; then
    block "Do not create '$rel_path'. The one decisions log lives at decisions/log.md. \
See GOVERNANCE.md — 'Canonical Owners'."
  fi

  # ── Rule 4: CLAUDE.md only at root, inside projects/, or programs/ ──────
  if [[ "$basename" == "CLAUDE.md" && "$rel_path" != "CLAUDE.md" ]]; then
    if [[ "$rel_path" != projects/* && "$rel_path" != programs/* && "$rel_path" != .claude/* ]]; then
      block "A new CLAUDE.md at '$rel_path' is not approved. \
Scoped CLAUDE.md files are only allowed under projects/ and programs/ for major sub-projects. \
See GOVERNANCE.md — 'Growth Guide'."
    fi
  fi

  # ── Rule 5: Future-home placeholders need real content first ─────────────
  # scheduled-tasks/ and sops/ must not be created as empty directories
  for part in "${PARTS[@]}"; do
    case "$part" in
      scheduled-tasks|sops)
        # Allow if this path IS a file (creating content at the same time)
        if [[ "$basename" == "$part" && ! "$rel_path" == */* ]]; then
          block "Directory '$part' is a future-home placeholder. \
Create it only with its first real content file — don't pre-create the empty folder. \
See GOVERNANCE.md — 'Growth Guide'."
        fi
        ;;
    esac
  done

  # ── Rule 6: _archive/ not archive/ (naming discipline) ───────────────────
  if [[ "${PARTS[0]}" == "archive" ]]; then
    block "Use '_archive' (with underscore), not 'archive'. \
See GOVERNANCE.md — 'Approved Root Layout'."
  fi
}

# ── Main ─────────────────────────────────────────────────────────────────────
while IFS= read -r path; do
  [[ -n "$path" ]] && check_path "$path"
done < <(extract_paths)

exit 0
