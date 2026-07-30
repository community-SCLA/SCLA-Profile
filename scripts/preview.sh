#!/usr/bin/env bash
# Preview a built HyperFrames lesson workspace in HeyGen Studio on an
# auto-forwarded port, and print a click-through URL. Removes the "cd into the
# workspace and run it by hand every time" friction — run it from anywhere with
# just the stem.
#
# Usage:  scripts/preview.sh <stem>
# A full or partial path to the workspace also works — anything up to and
# including renders-hyperframes/ is stripped, as is a trailing slash.
# With no argument, lists the available stems.
#
# Ports 3002-3004 auto-forward (.devcontainer/devcontainer.json), so up to three
# workspaces can be previewed side by side; each run takes the lowest free port.
# Pin one with HF_PREVIEW_PORT=3003 to always reclaim the same tab.
# In a Codespace the printed URL is the forwarded https:// one — clickable
# straight from the terminal.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT="$REPO/projects/video-production/renders-hyperframes"
PORTS=(3002 3003 3004)

list_stems() {
  echo "" >&2
  echo "available stems:" >&2
  for d in "$ROOT"/*/; do
    [ -f "$d/index.html" ] && echo "  $(basename "$d")" >&2
  done
}

STEM="${1:-}"
# Accept a pasted path as well as a bare stem.
STEM="${STEM#./}"
STEM="${STEM##*renders-hyperframes/}"
STEM="${STEM%/}"

if [ -z "$STEM" ]; then
  echo "usage: scripts/preview.sh <stem>" >&2
  list_stems
  exit 2
fi

WS="$ROOT/$STEM"
if [ ! -d "$WS" ]; then
  echo "No workspace at $WS — run /render-lessons BUILD for '$STEM' first." >&2
  list_stems
  exit 1
fi

port_busy() { (exec 3<>"/dev/tcp/127.0.0.1/$1") 2>/dev/null; }

if [ -n "${HF_PREVIEW_PORT:-}" ]; then
  PORT="$HF_PREVIEW_PORT"
else
  PORT=""
  for p in "${PORTS[@]}"; do
    port_busy "$p" || { PORT="$p"; break; }
  done
  if [ -z "$PORT" ]; then
    echo "Ports ${PORTS[*]} are all serving previews already." >&2
    echo "Free one (Ctrl-C its terminal, or: pkill -f 'hyperframes[ ]preview')" >&2
    echo "or pin a port: HF_PREVIEW_PORT=3005 scripts/preview.sh $STEM" >&2
    exit 1
  fi
fi

# A stale server on THIS port would shadow the workspace we're opening, so clear
# it — but leave previews on other ports alone so several can run at once. The
# render path does its own blanket sweep at preflight (render-qa/logs/BUILD-LOG.md
# step 0), which is what actually keeps a stale Studio out of a render.
# Bracketed pattern so we never kill this shell (see render-qa/logs/snag-log.md).
pkill -f "[h]yperframes.* preview --port $PORT" 2>/dev/null || true

if [ -n "${CODESPACE_NAME:-}" ] && [ -n "${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-}" ]; then
  URL="https://${CODESPACE_NAME}-${PORT}.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
else
  URL="http://localhost:$PORT"
fi

# Start the server, then WAIT until the port actually answers before printing
# the URL — the URL is only ever shown for a live server, and a dead one fails
# loudly instead of leaving you to "hope it opens a tab" (R5/A2).
cd "$WS"
npm run dev -- --port "$PORT" &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null || true' INT TERM

WAIT_SECS=30
answered=""
for _ in $(seq 1 $((WAIT_SECS * 2))); do
  if port_busy "$PORT"; then answered=1; break; fi
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    echo "" >&2
    echo "FAILED: the preview server exited before serving port $PORT — see npm output above." >&2
    echo "Debug by hand: cd $WS && npm run dev -- --port $PORT" >&2
    exit 1
  fi
  sleep 0.5
done

if [ -z "$answered" ]; then
  kill "$SERVER_PID" 2>/dev/null || true
  echo "" >&2
  echo "FAILED: port $PORT never answered within ${WAIT_SECS}s — no URL to open." >&2
  echo "Debug by hand: cd $WS && npm run dev -- --port $PORT" >&2
  exit 1
fi

echo ""
echo "  $STEM"
echo "  HyperFrames Studio → $URL/#project/$STEM"
echo "  (server is up and answering on port $PORT; ctrl/cmd-click the link, Ctrl-C here to stop)"
echo ""
wait "$SERVER_PID"
