#!/usr/bin/env bash
# Validate all harness-* and team-* skill contracts under .cursor/skills
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VALIDATE="$ROOT/scripts/harness/validate-skill.sh"
shopt -s nullglob
failed=0
for dir in "$ROOT/.cursor/skills"/harness-* "$ROOT/.cursor/skills"/team-* "$ROOT/.cursor/skills/team"/*; do
  [[ -d "$dir" ]] || continue
  [[ -f "$dir/SKILL.md" ]] || continue
  if ! bash "$VALIDATE" "$dir"; then failed=1; fi
done
exit $failed
