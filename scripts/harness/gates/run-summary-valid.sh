#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
RUN_DIR="${RUN_DIR:-docs/harness/runs/latest}"
python3 "$ROOT/scripts/harness/gates/run-summary-valid.py" "$RUN_DIR"
