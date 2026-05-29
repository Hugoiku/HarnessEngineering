#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
FILES="${KNOWLEDGE_FILES:-}"
[[ -n "$FILES" ]] || exit 0
for f in $FILES; do
  python3 "$ROOT/scripts/harness/validate-summary.py" "$f" || exit 1
done