#!/usr/bin/env bash
# Assess harness maturity and print recommendations.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

check() { [[ -e "$1" ]]; }

score=0
declare -A flags
flags[scaffold]=false
flags[agents_map]=false
flags[docs_base]=false
flags[cursor_rules]=false
flags[architecture]=false
flags[quality_gates]=false
flags[platform_ready]=false
flags[workflow_skills_ready]=false
flags[knowledge_skills_ready]=false

if check docs/harness/STATUS.yaml && check scripts/harness/assess.sh; then flags[scaffold]=true; fi
if check AGENTS.md; then flags[agents_map]=true; fi
if check docs/knowledge/catalog.md && check docs/knowledge/.knowledge-config.yaml; then flags[docs_base]=true; fi
if compgen -G ".cursor/rules/*.mdc" > /dev/null; then flags[cursor_rules]=true; fi
if check docs/design-docs/layering.md || check ARCHITECTURE.md; then flags[architecture]=true; fi
if check scripts/harness/validate-skill.sh && check docs/harness/golden-principles.md; then flags[quality_gates]=true; fi

platform_skills=(harness-router harness-run harness-registry harness-create-skill harness-compose)
workflow_skills=(harness-verify harness-self-review)
knowledge_skills=(harness-archive harness-doc-garden harness-gc)

platform_ok=true
for s in "${platform_skills[@]}"; do
  [[ -d ".cursor/skills/$s" ]] || platform_ok=false
done
$platform_ok && flags[platform_ready]=true

workflow_ok=true
for s in "${workflow_skills[@]}"; do
  [[ -d ".cursor/skills/$s" ]] || workflow_ok=false
done
$workflow_ok && flags[workflow_skills_ready]=true

know_ok=true
for s in "${knowledge_skills[@]}"; do
  [[ -d ".cursor/skills/$s" ]] || know_ok=false
done
$know_ok && flags[knowledge_skills_ready]=true

level=0
${flags[scaffold]} && ${flags[agents_map]} && ${flags[docs_base]} && ${flags[cursor_rules]} && level=1
[[ $level -ge 1 ]] && ${flags[architecture]} && ${flags[quality_gates]} && level=2
[[ $level -ge 2 ]] && ${flags[platform_ready]} && ${flags[workflow_skills_ready]} && level=3
team_count=0
if check docs/harness/skills.registry.yaml; then
  team_count=$(grep -c "^  - name: team-" docs/harness/skills.registry.yaml 2>/dev/null || true)
fi
[[ $level -ge 3 ]] && ${flags[knowledge_skills_ready]} && [[ "$team_count" -ge 1 ]] && level=4

echo "Harness 成熟度等级: $level"
echo "检查项:"
for k in scaffold agents_map docs_base cursor_rules architecture quality_gates platform_ready workflow_skills_ready knowledge_skills_ready; do
  echo "  $k: ${flags[$k]}"
done
echo "已登记 Team Skill 数量: $team_count"

case $level in
  0) echo "建议下一步: harness-scaffold" ;;
  1) echo "建议下一步: harness-architecture 或 harness-quality-gates" ;;
  2) echo "建议下一步: harness-router（批量补齐平台 Skill）" ;;
  3)
    if [[ "$team_count" -lt 1 ]]; then
      echo "建议下一步: harness-create-skill + harness-registry"
    else
      echo "建议下一步: harness-run <team-skill> 或 harness-doc-garden"
    fi
    ;;
  4) echo "已成熟。任务路由请用 harness-router。" ;;
esac
