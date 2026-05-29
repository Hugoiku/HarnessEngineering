---
name: harness-registry
description: 在 docs/harness/skills.registry.yaml 与 AGENTS.md 团队索引中登记或更新 Team Skill，并校验路径与 contract。在 harness-create-skill 之后或更新 triggers/元数据时使用。
---

# Harness Skill 登记（Registry）

## 步骤

1. 校验 Skill：`python scripts/harness/validate-skill.py .cursor/skills/<name>`
2. 在 `docs/harness/skills.registry.yaml` 追加或更新条目：
   - name、owner、description、triggers、requires_maturity、min_profile、contract 路径、inputs、outputs
3. 更新 AGENTS.md 团队 Skill 表（每个 Skill 一行）。
4. 执行 `python scripts/harness/validate-registry.py`。

## 条目 schema 示例

```yaml
- name: team-sql
  owner: data-team
  description: ...
  triggers: ["text to sql", "nl2sql"]
  requires_maturity: 3
  min_profile: standard
  contract: .cursor/skills/team-sql/contract.yaml
  path: .cursor/skills/team-sql
  inputs: [question, schema_path]
  outputs: [query_sql, summary]
```
