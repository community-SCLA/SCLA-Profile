#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
case "${1:-test}" in
  test) PYTHONPATH="$PWD/src" python3 -m unittest discover -s tests -v ;;
  *) echo "Supported command: test" >&2; exit 2 ;;
esac
