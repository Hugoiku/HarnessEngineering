#!/usr/bin/env bash
# Validate a skill directory has SKILL.md and contract.yaml with minimum fields.
set -euo pipefail
SKILL_DIR="${1:?usage: validate-skill.sh <skill-dir>}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

[[ -f "$SKILL_DIR/SKILL.md" ]] || { echo "missing SKILL.md in $SKILL_DIR"; exit 1; }
[[ -f "$SKILL_DIR/contract.yaml" ]] || { echo "missing contract.yaml in $SKILL_DIR"; exit 1; }

python3 - "$SKILL_DIR/contract.yaml" <<'PY'
import sys, pathlib
try:
    import yaml
except ImportError:
    # minimal parse without pyyaml
    text = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
    for key in ["name:", "preconditions:", "steps:", "postconditions:", "outputs:"]:
        if key not in text:
            sys.exit(f"contract missing section: {key}")
    sys.exit(0)
c = yaml.safe_load(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
for key in ["name", "preconditions", "steps", "postconditions", "outputs"]:
    if key not in c:
        sys.exit(f"contract missing key: {key}")
print("OK:", c.get("name"))
PY
