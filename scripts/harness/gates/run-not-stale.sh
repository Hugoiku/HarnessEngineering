#!/usr/bin/env bash
set -euo pipefail
RUN_DIR="${RUN_DIR:-docs/harness/runs/latest}"
[[ -f "$RUN_DIR/run.yaml" ]] || exit 0
grep -q "status: STALE" "$RUN_DIR/run.yaml" && { echo "run 已为 STALE，请新建 run（说「新任务」）"; exit 1; }
