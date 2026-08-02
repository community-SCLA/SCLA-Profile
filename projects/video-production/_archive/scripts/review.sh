#!/usr/bin/env bash
# One click: "what do I need to watch, and open it."
#
# Wired to the VS Code task "Review lesson videos" (.vscode/tasks.json), so the
# normal way to run this is the Run Task menu, not typing it.
#
# For every build in renders-hyperframes/ it runs the deterministic gate
# (render-qa/src/preflight.py, ~0.4s each). Gate-clean builds get a preview server
# started on their own port and a clickable link printed. Everything else is
# listed as "not ready" so you know to skip it.
#
# Previews keep running after this exits — the links stay live until the
# Codespace stops or you run "Stop all previews".
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT="$REPO/projects/video-production/renders-hyperframes"
PREFLIGHT="$REPO/projects/video-production/render-qa/src/preflight.py"
PORTS=(3002 3003 3004 3005 3006 3007)
HF="hyperframes@0.7.79"   # single pin, matches design-system/package.json (render-validated)

bold=$'\e[1m'; dim=$'\e[2m'; grn=$'\e[32m'; ylw=$'\e[33m'; off=$'\e[0m'

port_busy() { (exec 3<>"/dev/tcp/127.0.0.1/$1") 2>/dev/null; }

# Which stem is the preview server on $1 serving? Empty if none.
stem_on_port() {
  curl -s --max-time 2 "http://127.0.0.1:$1/api/projects" 2>/dev/null \
    | python3 -c 'import sys,json
try:
    p=json.load(sys.stdin).get("projects") or []
    print(p[0]["id"] if p else "")
except Exception:
    print("")' 2>/dev/null
}

url_for() {
  if [ -n "${CODESPACE_NAME:-}" ] && [ -n "${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-}" ]; then
    echo "https://${CODESPACE_NAME}-$1.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
  else
    echo "http://localhost:$1"
  fi
}

# "m2_four-kinds-of-career-transition_mid-career-momentum_2026-07-25"
#   -> "Four kinds of career transition   (mid career momentum)"
pretty() {
  python3 - "$1" <<'PY'
import re, sys
stem = sys.argv[1]
name = re.sub(r'_\d{4}-\d{2}-\d{2}$', '', stem)
parts = name.rsplit('_', 1)
title = re.sub(r'^m\d+_', '', parts[0]).replace('-', ' ').replace('_', ' ').strip()
program = parts[1].replace('-', ' ') if len(parts) > 1 else ''
print(f"{title[:1].upper()}{title[1:]}" + (f"   ({program})" if program else ""))
PY
}

[ -d "$ROOT" ] || { echo "No renders-hyperframes/ at $ROOT" >&2; exit 1; }

echo ""
echo "${bold}Checking every build against the Motion v2 gate...${off}"
echo ""

READY=(); BLOCKED=(); BLOCKED_WHY=()
for d in "$ROOT"/*/; do
  stem="$(basename "$d")"
  case "$stem" in _*) continue ;; esac
  [ -f "$d/index.html" ] || continue
  if out="$(python3 "$PREFLIGHT" "$d" 2>&1)"; then
    READY+=("$stem")
  else
    BLOCKED+=("$stem")
    why="$(printf '%s\n' "$out" | grep -oE '^\[!! \] [a-z_]+' | awk '{print $3}' | paste -sd, -)"
    BLOCKED_WHY+=("${why:-gate failed}")
  fi
done

# ---- start a preview for each ready build, reusing anything already serving it
LINKS=()
CLAIMED=""   # ports handed out in this run; a just-launched server has not bound
             # yet, so port_busy alone would hand the same port to every build
for stem in "${READY[@]:-}"; do
  [ -z "$stem" ] && continue

  found=""
  for p in "${PORTS[@]}"; do
    if port_busy "$p" && [ "$(stem_on_port "$p")" = "$stem" ]; then found="$p"; break; fi
  done

  if [ -z "$found" ]; then
    for p in "${PORTS[@]}"; do
      case " $CLAIMED " in *" $p "*) continue ;; esac
      port_busy "$p" && continue
      # Fully detached: own session, all three fds off this script's, so the
      # preview outlives this terminal and never holds the task's output open.
      setsid bash -c "cd '$ROOT/$stem' && exec npx --yes '$HF' preview --port $p" \
        </dev/null >/dev/null 2>&1 &
      disown 2>/dev/null || true
      found="$p"; break
    done
  fi

  [ -n "$found" ] && CLAIMED="$CLAIMED $found"

  if [ -z "$found" ]; then
    LINKS+=("!|$stem|no free port")
  else
    LINKS+=("$found|$stem|")
  fi
done

# Give any freshly-launched servers a moment to bind.
if [ ${#LINKS[@]} -gt 0 ]; then
  for _ in $(seq 1 40); do
    pending=0
    for row in "${LINKS[@]}"; do
      p="${row%%|*}"; rest="${row#*|}"; s="${rest%%|*}"
      [ "$p" = "!" ] && continue
      [ "$(stem_on_port "$p")" = "$s" ] || pending=1
    done
    [ "$pending" -eq 0 ] && break
    sleep 1
  done
fi

echo "${bold}${grn}READY FOR YOU — ctrl/cmd-click to watch${off}"
echo ""
if [ ${#READY[@]} -eq 0 ]; then
  echo "  ${dim}Nothing is gate-clean right now.${off}"
else
  for row in "${LINKS[@]}"; do
    p="${row%%|*}"; rest="${row#*|}"; s="${rest%%|*}"; err="${rest#*|}"
    echo "  ${bold}$(pretty "$s")${off}"
    if [ "$p" = "!" ]; then
      echo "    ${ylw}$err — stop a preview and re-run.${off}"
    else
      echo "    $(url_for "$p")/#project/$s"
    fi
    echo ""
  done
fi

if [ ${#BLOCKED[@]} -gt 0 ]; then
  echo "${bold}NOT READY — skip these${off}"
  echo ""
  for i in "${!BLOCKED[@]}"; do
    echo "  $(pretty "${BLOCKED[$i]}")"
    echo "    ${dim}failing: ${BLOCKED_WHY[$i]}${off}"
  done
  echo ""
fi

echo "${dim}Happy with one? Tell Claude:  ship <its folder name>${off}"
echo "${dim}Previews stay up after this window closes.${off}"
echo ""
exit 0
