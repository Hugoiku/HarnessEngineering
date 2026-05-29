# 知识全景目录（Layer A）

> 约 50 行。Agent 入口。勿在此粘贴全文条目。
> 重新生成统计：`scripts/harness/catalog-aggregate.sh`（Windows：`catalog-aggregate.py`）

## 快速开始

1. 读本文件（Layer A）。
2. 打开对应领域的 Layer B `catalog.md`。
3. 评分后仅读取 Top-K 的 Layer C 全文。

## 存储层

| 层 | 路径 | 范围 |
|----|------|------|
| 0-T | `team-conventions/` | 团队规则，稳定 |
| 1 | `tech-wiki/` | 跨项目技术 |
| 2 | `biz-wiki/{domain}/` | 业务领域 |
| 3 | `project/` | 仅本仓库 |

## 索引（自动聚合）

<!-- AGGREGATE_START -->
| Section | Entries | proven | verified | draft | B catalog |
|---------|---------|--------|----------|-------|-----------|
| team-conventions | 0 | 0 | 0 | 0 | `team-conventions/catalog.md` |
| tech-wiki | 0 | 0 | 0 | 0 | `tech-wiki/catalog.md` |
| project | 1 | 0 | 0 | 1 | `project/catalog.md` |
<!-- AGGREGATE_END -->

## 阶段提示

| 阶段 | 先读 | 类型 |
|------|------|------|
| orient | `project/catalog.md` + 领域 B | guideline, process |
| analyze | 领域 B（过滤后） | model, pitfall, guideline |
| summarize | Top-1 C | decision, guideline |
| archive | 仅 A（去重） | — |

## 相关 Skill

- 查询：`harness-run` 的 orient/analyze 步骤
- 写入：`harness-archive`
- 维护：`harness-doc-garden`
