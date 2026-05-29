#!/usr/bin/env bash
# Gate: SKILL_NAME env or arg names an existing skill dir
set -euo pipefail
NAME="${SKILL_NAME:-${1:-}}"
[[ -n "$NAME" ]] || { echo "skill-exists: 须设置 SKILL_NAME"; exit 1; }
[[ -d ".cursor/skills/$NAME" ]] || [[ -d ".cursor/skills/team/$NAME" ]] || { echo "未找到 Skill: $NAME"; exit 1; }
