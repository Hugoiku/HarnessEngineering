#!/usr/bin/env bash
# Gate: run directory exists and status COMPLETED
set -euo pipefail
RUN_DIR="${1:-}"
[[ -n "$RUN_DIR" && -f "$RUN_DIR/run.yaml" ]] || { echo "archive-pre: 缺少 run 目录"; exit 1; }
grep -q "status: COMPLETED" "$RUN_DIR/run.yaml" || { echo "archive-pre: run 尚未 COMPLETED"; exit 1; }
