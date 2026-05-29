#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
RUN_DIR="${RUN_DIR:-docs/harness/runs/latest}"
[[ -f "$RUN_DIR/evidence/router-resolution.txt" ]] || { echo "缺少 evidence/router-resolution.txt（须先 harness-router + router-resolve）"; exit 1; }
[[ -s "$RUN_DIR/evidence/router-resolution.txt" ]] || { echo "router-resolution.txt 为空"; exit 1; }
