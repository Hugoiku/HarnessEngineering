#!/usr/bin/env bash
# Validate skills.registry.yaml entries point to existing skill dirs.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
REG="$ROOT/docs/harness/skills.registry.yaml"
[[ -f "$REG" ]] || { echo "missing registry"; exit 1; }

python3 - "$REG" "$ROOT" <<'PY'
import pathlib, re, sys
reg, root = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
text = reg.read_text(encoding="utf-8")
paths = re.findall(r"path:\s*(.+)", text)
for p in paths:
    p = p.strip()
    if not (root / p).is_dir():
        sys.exit(f"registry path missing: {p}")
print("registry OK,", len(paths), "team skill path(s)")
PY
