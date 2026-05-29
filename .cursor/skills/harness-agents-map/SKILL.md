---
name: harness-agents-map
description: 维护约 100 行的 AGENTS.md 作为目录，指向 docs/knowledge/catalog.md、Harness Skill 与深度文档。用于初始化或刷新 Agent 入口地图。
---

# Harness Agent 地图（Agents Map）

## 规则

- AGENTS.md 控制在约 100 行以内
- 不写入完整知识条目，仅指针
- 章节：Harness、Knowledge（Layer A）、Team Skill 表、Core 工作流 Skill、深度文档、查询预算摘要

## 步骤

1. 读取当前 `docs/harness/skills.registry.yaml` 获取 Team Skill 列表。
2. 按 registry 重写 AGENTS.md 团队 Skill 表。
3. 确保 Knowledge 章节指向 `docs/knowledge/catalog.md` 与 `.knowledge-config.yaml`。
