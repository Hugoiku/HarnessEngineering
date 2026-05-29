#!/usr/bin/env bash
# Gate: a completed harness-verify run exists for current run session (optional marker file).
set -euo pipefail
MARKER="${HARNESS_VERIFY_MARKER:-docs/harness/.verify-passed}"
if [[ -f "$MARKER" ]]; then exit 0; fi
echo "verify-passed 门禁: 未找到标记文件 $MARKER（请先运行 harness-verify 或设置 HARNESS_VERIFY_MARKER）"
exit 1
