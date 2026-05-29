#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
RUN_DIR="${1:-docs/harness/runs/latest}"
[[ -f "$RUN_DIR/run.yaml" ]] || exit 1
grep -Eq "status: (COMPLETED|FAILED)" "$RUN_DIR/run.yaml" || exit 1
if grep -q "status: COMPLETED" "$RUN_DIR/run.yaml"; then
  python3 "$ROOT/scripts/harness/gates/run-summary-valid.py" "$RUN_DIR"
fi
