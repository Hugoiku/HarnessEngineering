---
name: harness-compose
description: 定义并执行 docs/harness/skills.registry.yaml 中带 hard gate 的多 Skill 流水线。用于分析后归档等标准团队流程，不含 git commit 步骤。
---

# Harness 流程组合（Compose）

## Workflow 格式（`skills.registry.yaml`）

登记 Team Skill 后，可定义 workflow，例如：

```yaml
workflows:
  persist:
    profile: standard
    pipeline:
      - skill: team-sql          # 团队自建 Skill
        gate: hard
      - skill: harness-self-review
        gate: hard
      - skill: harness-archive
        gate: hard
```

## 执行方式

对 pipeline 中每一步调用 **harness-run**。若 `gate: hard` 且该步失败，整条流水线终止。

## 允许的终端 Skill

- team-* skills（团队扩展，非框架内置）
- harness-verify、harness-self-review、harness-archive
- **不包含** harness-commit / harness-pr（已从框架移除）

## 产出

- compose 对应 run.yaml 中的合并 evidence 引用
