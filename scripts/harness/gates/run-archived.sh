#!/usr/bin/env bash
set -euo pipefail
RUN_DIR="${RUN_DIR:-docs/harness/runs/latest}"
[[ -f "$RUN_DIR/run.yaml" ]] || exit 1
grep -q "archived_to_knowledge: true" "$RUN_DIR/run.yaml" || { echo "run 未标记 archived_to_knowledge"; exit 1; }
