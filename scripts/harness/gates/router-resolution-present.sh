#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
RUN_DIR="${RUN_DIR:-docs/harness/runs/latest}"

# 优先校验结构化 JSON（新格式）
if [[ -f "$RUN_DIR/evidence/router-resolution.json" ]]; then
  python3 "$ROOT/scripts/harness/gates/validate-router-resolution.py" "$RUN_DIR"
  exit $?
fi

# 兼容旧 txt 格式（降级：存在且非空即通过，并发出警告）
if [[ -f "$RUN_DIR/evidence/router-resolution.txt" ]]; then
  if [[ -s "$RUN_DIR/evidence/router-resolution.txt" ]]; then
    echo "WARN: 使用旧版 router-resolution.txt，建议迁移到 router-resolution.json"
    exit 0
  fi
  echo "FAIL: router-resolution.txt 为空" >&2
  exit 1
fi

echo "FAIL: 缺少 router-resolution.json（须 write-router-resolution.py 写入路由决策）" >&2
exit 1
