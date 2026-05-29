---
name: harness-docs-base
description: 搭建 docs/knowledge/ 下五层知识树、Layer A/B catalog、.knowledge-config.yaml 查询预算、log.md 与示例条目模板。用于初始化或重置知识架构。
---

# Harness 知识库骨架（Docs Base）

## 创建内容（若缺失）

```text
docs/knowledge/
├── catalog.md
├── .knowledge-config.yaml
├── log.md
├── team-conventions/catalog.md
├── tech-wiki/catalog.md
├── biz-wiki/{domain}/catalog.md
├── project/catalog.md
└── contributions/{pending,conflicts}/
```

## 步骤

1. 从本模板复制或创建最小 catalog（仅表头）。
2. 确保 `.knowledge-config.yaml` 包含 `query_budget` 的 profiles 与 phases。
3. 仅在为空时添加示例条目 `project/PK-EXAMPLE-001.md`。
4. 执行 `python scripts/harness/catalog-aggregate.py`。
5. 更新 `docs/harness/STATUS.yaml`：`docs_base: true`。

## 摘要生成策略

- **C 层 `summary`**：由 harness-archive 写入（Agent 生成，长度受限）。
- **B 层行**：经 `scripts/harness/catalog-line.sh` **派生**，禁止在 B 层手写摘要正文。
- **A 层**：经 `catalog-aggregate` **聚合**，仅统计与路由，约 50 行。

## 产出

- 完整的知识目录骨架
