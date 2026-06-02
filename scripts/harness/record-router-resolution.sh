#!/usr/bin/env bash
# Agent 应在语义路由决策后调用 write-router-resolution.py 写入结构化 JSON。
# 本脚本仅标记 activity（write-router-resolution.py 已内含 touch）。
# 若 Agent 直接调用 write-router-resolution.py，本脚本可跳过。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
RUN_DIR="${RUN_DIR:?set RUN_DIR}"
python3 scripts/harness/run-stale.py --apply >/dev/null 2>&1 || true
python3 scripts/harness/run-touch.py "$RUN_DIR"
echo "OK: activity touched (use write-router-resolution.py to record routing decision)"
