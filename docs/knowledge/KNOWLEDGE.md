# 知识架构

整合设计：**五层存储 × 五类知识 × 动态记忆管理 × 三级索引 × 查询预算**。

## 存储层

| 层 | 路径 | 范围 |
|----|------|------|
| 0-P | `~/.cursor/skills/local-*` | 个人（不进仓库） |
| 0-T | `team-conventions/` | 团队公约 |
| 1 | `tech-wiki/` | 跨项目技术 |
| 2 | `biz-wiki/{domain}/` | 业务领域 |
| 3 | `project/` | 仅本仓库 |

### 五层存储怎么理解

把 `docs/knowledge/` 想象成一座**图书架**：书按「适用范围」分区摆放，Agent 先判断该去哪区找，再按 A/B/C 索引取书，避免一次搬整架书进上下文。

| 层 | 类比 | 放什么 |
|----|------|--------|
| **0-P** | 自家抽屉里的私笔记 | 仅自己用的 Skill/备忘，**不进仓库**，不参与团队书架 |
| **0-T** | 图书馆张贴的借阅规则 | 命名、流程、协作约定等**稳定公约** |
| **1** | 工具书区 | 与具体业务无关的**通用技术**（语言、框架、调试套路） |
| **2** | 业务专区 | 按领域分的**业务知识**（口径、模型、领域坑点） |
| **3** | 本项目专柜 | **当前仓库专属**的经验与决策（archive 默认落此处） |

**查阅顺序**（见 `.knowledge-config.yaml` 的 `layer_preference`）：通常 **project → biz-wiki → tech-wiki → team-conventions**——先找离任务最近的区，再向外扩展。

**与 A/B/C 的关系**：五层是**书放在哪个区**；A/B/C 是**怎么找书**（总目录 → 书脊摘要 → 打开正文）。两层概念正交，一起用来省 Token。

## 类型（每条仅一种）

`model` | `decision` | `guideline` | `pitfall` | `process`

## 三级索引

| 层级 | 文件 | 内容 |
|------|------|------|
| A | `catalog.md` | 约 50 行，统计 + 路由 |
| B | `*/catalog.md` | 每条条目一行（派生） |
| C | `PK-*` / `BK-*` / `TK-*` | 全文 + frontmatter 中的 `summary` |

## 动态记忆管理（晋升 + 衰减）

书架上的书不会永远摆在最顺手的位置：**常被查阅的往前排，长期无人看的往后撤或入库**。条目 frontmatter 里的 `maturity` 字段（`draft` | `verified` | `proven`）表示**当前记忆档位**，由引用情况与时间自动升降——不是静态标签，而是动态管理。

统一配置：`docs/knowledge/.knowledge-config.yaml` → `maturity.promotion` / `maturity.decay`（配置键名保留 `maturity`，语义为记忆档位）。

### 晋升（记忆加强）

被多次、跨任务引用的条目，档位上调，查询时优先推荐：

| 当前档位 | 条件 | 动作 |
|----------|------|------|
| draft | `reference_count ≥ 1` | → verified |
| verified | `reference_count ≥ 2` 且 `distinct_runs ≥ 2` | → proven |

### 衰减（记忆淡化）

长期无人引用的条目，档位下调或移入存档区，避免书架堆满过时内容：

| 当前档位 | 条件 | 动作 |
|----------|------|------|
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

**引用追踪**（晋升判据来源）：`harness-run` 读 Layer C 后：

```bash
python scripts/harness/knowledge-reference.py --id PK-xxx --run-id <run-dir>
```

更新 `reference_count`、`last_referenced`、`distinct_runs`。

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
