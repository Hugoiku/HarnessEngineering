---
name: harness-create-skill
description: 脚手架生成新的 team-* Skill，含 SKILL.md、contract.yaml、checklist.md 与 scripts/gates/。当无已登记 Skill 匹配用户任务，或团队希望固化可重复工作流时使用。
---

# Harness 创建 Team Skill

## 命名

- **Team Skill**：`team-<主题>` → 目录 `.cursor/skills/team-<主题>/`
- 尽量 **1 个英文短词**；action 写在 SKILL 步骤里，不堆进名称
- 示例：`team-excel`、`team-sql`（非 `team-excel-analyze`、`team-text-to-sql`）
- **Core `harness-*` 勿在此创建** — 仅脚手架 Team 扩展

## 脚手架结构

```text
.cursor/skills/team-sql/
├── SKILL.md
├── contract.yaml      # 参考 templates/team-contract.yaml
├── checklist.md
└── scripts/gates/validate.sh
```

## contract.yaml 最低要求

- preconditions（≥1）、steps、postconditions（≥1）、outputs、`on_failure: stop`

## SKILL.md frontmatter

为 registry 准备 triggers，例如文档中说明：`triggers: ["关键词1", "关键词2"]`

## 创建之后

推荐执行 **harness-registry**，登记到 `docs/harness/skills.registry.yaml`。

## triggers 示例

Excel：`["分析 excel", "analyze excel", "excel 分析"]`
