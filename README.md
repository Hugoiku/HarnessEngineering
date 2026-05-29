# Harness Framework

面向 Cursor 的泛化 Harness 基础框架：**平台 Core Skills + 团队 Team Skills + 知识三级索引 + 流程约束（harness-run）**。

## 快速开始

```bash
# 评估成熟度（Git Bash / Linux / macOS）
bash scripts/harness/assess.sh

# Windows：catalog / 校验 / 衰减预览
python scripts/harness/catalog-aggregate.py
python scripts/harness/validate-contract.py
python scripts/harness/validate-registry.py
python scripts/harness/knowledge-maturity.py --dry-run
python scripts/harness/run-stale.py --dry-run
```

在 Cursor 中对 Agent 说：

> 加载 harness-router，评估本仓库并推荐下一步

## 架构概览

| 层 | 内容 |
|----|------|
| 知识 | `docs/knowledge/` 五层存储 + A/B/C 三级索引 |
| 流程 | `harness-run` + `contract.yaml` + `docs/harness/runs/` |
| 扩展 | `.cursor/skills/team-*` + `docs/harness/skills.registry.yaml` |

## 文档

- [成熟度](docs/harness/MATURITY.md)
- [流程约束](docs/harness/PROCESS.md)
- [Run 工作记忆](docs/harness/RUN-MEMORY.md)
- [贡献 Team Skill](docs/harness/CONTRIBUTING-SKILLS.md)
- [知识架构](docs/knowledge/KNOWLEDGE.md)
- [知识配置](docs/knowledge/.knowledge-config.yaml)

## 原则

- **知识优先于工作流** — 用 archive 沉淀，不依赖聊天记忆
- **无 git commit Skill** — 沉淀经 `harness-archive` 写文件
- **查询预算** — Layer A → B → C，见 `.knowledge-config.yaml`

## Core Skill（16 个）

`harness-router`、`harness-run`、`harness-registry`、`harness-create-skill`、`harness-compose`、`harness-scaffold`、`harness-docs-base`、`harness-agents-map`、`harness-cursor-rules`、`harness-architecture`、`harness-quality-gates`、`harness-verify`、`harness-self-review`、`harness-archive`、`harness-doc-garden`、`harness-gc`
