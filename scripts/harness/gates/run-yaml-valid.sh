#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
RUN_DIR="${1:-docs/harness/runs/latest}"

[[ -f "$RUN_DIR/run.yaml" ]] || { echo "FAIL: run.yaml 不存在" >&2; exit 1; }
grep -Eq "status: (COMPLETED|FAILED)" "$RUN_DIR/run.yaml" || { echo "FAIL: run.yaml status 须为 COMPLETED 或 FAILED" >&2; exit 1; }

if grep -q "status: COMPLETED" "$RUN_DIR/run.yaml"; then
  # summary 质量门禁
  python3 "$ROOT/scripts/harness/gates/run-summary-valid.py" "$RUN_DIR"
  # 步骤追踪门禁
  python3 "$ROOT/scripts/harness/gates/check-step-progress.py" "$RUN_DIR"
fi
