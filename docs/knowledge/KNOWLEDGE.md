# 知识架构

整合设计：**五层存储 × 五类知识 × 三级成熟度 × 三级索引 × 查询预算**。

## 存储层

| 层 | 路径 | 范围 |
|----|------|------|
| 0-P | `~/.cursor/skills/local-*` | 个人（不进仓库） |
| 0-T | `team-conventions/` | 团队公约 |
| 1 | `tech-wiki/` | 跨项目技术 |
| 2 | `biz-wiki/{domain}/` | 业务领域 |
| 3 | `project/` | 仅本仓库 |

## 类型（每条仅一种）

`model` | `decision` | `guideline` | `pitfall` | `process`

## 三级索引

| 层级 | 文件 | 内容 |
|------|------|------|
| A | `catalog.md` | 约 50 行，统计 + 路由 |
| B | `*/catalog.md` | 每条条目一行（派生） |
| C | `PK-*` / `BK-*` / `TK-*` | 全文 + frontmatter 中的 `summary` |

## 成熟度（晋升 + 衰减）

统一配置：`docs/knowledge/.knowledge-config.yaml` → `maturity.promotion` / `maturity.decay`（结构对称，按当前 maturity 键名）。

### 晋升

| 当前 | 条件 | 动作 |
|------|------|------|
| draft | `reference_count ≥ 1` | → verified |
| verified | `reference_count ≥ 2` 且 `distinct_runs ≥ 2` | → proven |

### 衰减

| 当前 | 条件 | 动作 |
|------|------|------|
| proven | 12 个月未引用 | → verified |
| verified | 6 个月未引用 | → draft |
| draft | 6 个月 stale | 归档至 `archive/` |

### 执行

```bash
python scripts/harness/knowledge-maturity.py --dry-run          # 晋升+衰减预览
python scripts/harness/knowledge-maturity.py --apply            # 应用
python scripts/harness/knowledge-maturity.py --apply --promote-only
python scripts/harness/knowledge-maturity.py --dry-run --decay-only
```

`knowledge-decay.py` 为兼容别名。定期经 **harness-doc-garden** 调用；CI 做 dry-run。

**引用追踪**：`harness-run` 读 Layer C 后：

```bash
python scripts/harness/knowledge-reference.py --id PK-xxx --run-id <run-dir>
```

更新 `reference_count`、`last_referenced`、`distinct_runs`（供晋升判定）。

## 摘要生成

1. **C 层 `summary`**：Agent 在 **harness-archive** 时写入（长度限制见 config）。
2. **B 层行**：`bash scripts/harness/catalog-line.sh <entry.md>` — 禁止手写 B 层摘要。
3. **A 层**：`bash scripts/harness/catalog-aggregate.sh`（Windows 用 `catalog-aggregate.py`）— 仅统计。

## 查询预算

配置于 `.knowledge-config.yaml` → `query_budget.profiles` 与 `phases`。

评分权重见 `scoring` 段。**harness-run** 在 orient/analyze/summarize 步骤执行。

## 生命周期

```text
harness-run (+ reference) → runs/evidence → harness-archive → docs/knowledge → doc-garden (decay + lint)
```

本框架无 git commit 步骤。
