#!/usr/bin/env bash
# Record router-resolve output into run evidence (after init-run-dir).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
RUN_DIR="${RUN_DIR:?set RUN_DIR}"
MSG="${HARNESS_USER_MESSAGE:?set HARNESS_USER_MESSAGE}"
mkdir -p "$RUN_DIR/evidence"
python3 scripts/harness/run-stale.py --apply >/dev/null 2>&1 || true
python3 scripts/harness/router-resolve.py "$MSG" > "$RUN_DIR/evidence/router-resolution.txt"
python3 scripts/harness/run-touch.py "$RUN_DIR"
echo "OK: router-resolution recorded"
