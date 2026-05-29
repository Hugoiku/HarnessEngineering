#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
RUN_DIR="${RUN_DIR:?set RUN_DIR}"
python3 scripts/harness/archive-from-run.py --run-dir "$RUN_DIR" "$@"
