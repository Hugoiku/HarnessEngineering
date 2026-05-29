---
name: harness-architecture
description: 在 ARCHITECTURE.md 与 docs/design-docs/layering.md 中文档化分层架构与模块边界。用于为 Agent 生成代码建立结构约束。
---

# Harness 架构文档

## 产出

- `ARCHITECTURE.md` — 领域地图
- `docs/design-docs/layering.md` — 依赖方向、Providers 模式

## 步骤

1. 访谈或推断项目领域划分。
2. 编写分层规则（示例：Types→Config→Repo→Service→Runtime→UI）。
3. 注明 enforcement 方式（结构测试 — 经 harness-quality-gates 补充）。
