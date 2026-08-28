#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="$PWD/src:$PWD/tests"
case "${1:-test}" in
  test) python3 -m unittest discover -s tests -v ;;
  compile) export NODE_PATH="$PWD/config/node_modules"; python3 -c 'from convert import render, from_notion; from test_convert import api_sample; from cloud_job import validate_mjml; validate_mjml(render(from_notion(api_sample()))["mjml"]); print("Synthetic MJML compiled successfully.")' ;;
  generate) export NODE_PATH="$PWD/config/node_modules"; python3 src/cloud_job.py ;;
  *) echo "Supported commands: test, compile, generate" >&2; exit 2 ;;
esac
