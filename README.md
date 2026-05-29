# Harness Framework

面向 Cursor 的泛化 Harness 基础框架：**图书架式知识存储 + 省 Token 索引 + contract 流程约束 + run 工作记忆**；Core Skills 可扩展，git 提交前即可归档经验（不含 commit/PR Skill）。

## 快速开始

### 环境

- **Cursor**（Agent 模式）+ 本仓库作为工作区
- **Python 3**（Windows 下直接用 `python`；Linux/macOS 可用 Git Bash 跑 `.sh`）
- 无需额外服务；个人场景不依赖 git 协作即可使用

### 典型流程

```text
1. 在 Cursor 里说清需求（换话题加「新任务」，续接加「继续」）
2. harness-router → router-resolve 判定新建 or 续跑 run
3. harness-run 按 contract 执行，留 evidence
4. 写 evidence/summary.md → 标 COMPLETED
5. （可选）harness-archive 上架到图书架 docs/knowledge/
```

无需记 Skill 名：路由会匹配；框架规则见 `.cursor/rules/harness-process.mdc`。

### 校验命令

```bash
# 评估成熟度（Git Bash / Linux / macOS）
bash scripts/harness/assess.sh

# Windows：catalog / 校验 / 衰减预览
python scripts/harness/catalog-aggregate.py
python scripts/harness/validate-contract.py
python scripts/harness/validate-registry.py
python scripts/harness/knowledge-maturity.py --dry-run
python scripts/harness/run-stale.py --dry-run
python scripts/harness/demo-token-budget.py --synthetic-entries 0   # Token 对比（含测试 PDF 条目时用）
python scripts/harness/demo-token-budget.py --synthetic-entries 30  # Token 对比（模拟书架规模）
```

在 Cursor 中对 Agent 说（任选）：

> 新任务：整理 XX 模块文档  
> 继续上次的数据分析  
> 任务完成，写 summary 并归档

也可先说「按 harness 流程处理」；不必写 `/harness-router` 等 Skill 名称。

## 架构概览

| 层 | 内容 |
|----|------|
| 知识 | `docs/knowledge/` — **图书架**（五层分区 + A/B/C：总目录 → 书脊摘要 → 按需取书） |
| 流程 | `harness-run` + `contract.yaml` + `docs/harness/runs/` |
| 扩展 | `.cursor/skills/team-*` + `docs/harness/skills.registry.yaml` |

## 为什么用这个框架

### 1. 显著节省 Token

Harness Engineering 常见做法是：**多 Agent 编排交接**——每轮路由对话、handoff 摘要、artifacts 在多个会话间传递，再叠加广搜 wiki/代码与全文阅读，**上下文成本随 Agent 数量与轮次叠加**。

本框架面向 **Cursor 单一 Agent 干活**：路由、执行、归档都在**同一会话、同一个 Agent** 内完成，步骤靠 contract 切换而非再起子 Agent；进度与结论写磁盘，**不必在上下文里重复携带多 Agent 交接包**。

在此前提下，用「**渐进式读取 + 磁盘留痕**」控制上下文体积：

| 机制 | 怎么省 Token |
|------|----------------|
| **图书架（A/B/C）** | Layer A 像**总目录**（约 60 行）→ Layer B 像**书脊一行摘要** → Layer C **按需取书**，仅 Top-K 打开全文 |
| **查询预算** | orient/analyze/summarize 各阶段限制 Layer C 条数与行数（见 `.knowledge-config.yaml`） |
| **summary 而非全文** | 知识条目、run 结论写短摘要；对话里用 ID 引用，禁止粘贴整篇知识 |
| **run 工作记忆落盘** | 进度在 `docs/harness/runs/`，续跑读文件而非重讲背景 |
| **路由结果落盘** | `router-resolution.txt` 存决策要点，避免每轮在聊天里重复 RouterInput/Decision 长文 |
| **单一 Agent** | 无多 Agent handoff 链；换 Skill = 换 contract，不换会话；run/路由已落盘，续跑不重载交接上下文 |

**效果**：单一 Agent 完成全流程，上下文里主要是「当前 contract 步骤 + 少量摘要」，而不是多 Agent 往返堆叠的历史输出与全文知识。

#### Token 对比案例（可复现）

场景：**orient 阶段查阅知识库**。对比三种上下文载入方式：

| 路径 | 含义 |
|------|------|
| **A** | 直接对话：读 `docs/knowledge/` 下全部 Markdown |
| **B** | 多 Agent + 全库读 + 5 轮 Router/handoff 留在上下文 |
| **C** | 本框架：`standard` 查询预算（A≤60 行 + B≤250 行 + Top-3 C 各≤200 行）+ 其余仅 summary 引用 + 磁盘 run |

Token 估算：`字符数 ÷ 2`（中英混合粗算）。

**测试知识库（真实 PDF）**：可将 PDF 导入 `docs/knowledge/project/PK-TEST-*.md` 后对比：

```bash
python scripts/harness/ingest-pdf-to-knowledge.py "path/to/file1.pdf" "path/to/file2.pdf"
python scripts/harness/demo-token-budget.py --synthetic-entries 0
```

**实测结果**（2026-05-29，`scripts/harness/demo-token-budget.py`）：

| 案例 | 知识库内容 | A 全库读 | B 多 Agent + 全库 | C 本框架 | C 较 A 减少 |
|------|------------|----------|-------------------|----------|-------------|
| **PDF 实测** | 2 份 PDF（Harness 实践 16 页 + Dalio 图表 112 页）+ 现有目录文件 | ~45,228 | ~46,477 | **~6,475** | **86%** |
| 模拟 0 条目 | 仅仓库原有文件（无 PDF） | ~2,648 | ~3,897 | ~963 | 64% |
| 模拟 +30 条目 | 内存合成 archive 条目 | ~18,777 | ~20,027 | ~2,739 | 86% |
| 模拟 +100 条目 | 内存合成 archive 条目 | ~56,622 | ~57,871 | ~4,490 | 93% |

PDF 案例：全文约 **8.4 万字符**（两篇合计）；本框架 orient 仅载入 **~1.3 万字符**（Top-3 C 各≤200 行 + 目录 + 其余 summary 引用）。C 路径受查询预算封顶；A/B 随书架厚度线性上涨。

> 说明：衡量的是「载入上下文的文本量」，非 Cursor 账单精确值；PDF 正文存于 `docs/knowledge/test-corpus/sources/`，Markdown 条目为 `PK-TEST-*`。

### 2. Contract 流程约束（可验收，不靠自觉）

每个 Skill 有 `contract.yaml`，相当于**带检查项的 SOP**：

```text
preconditions（开工前检查）
  → steps + evidence（逐步执行并留痕）
  → postconditions + gates（收工前脚本验收）
```

| 对比 | Harness Engineering 常见形态 | 本框架 |
|------|------------------------------|--------|
| 步骤定义 | 长文档 + 聊天内 RouterDecision | **contract 清单**，步骤 ID 固定 |
| 是否跳过 | 依赖 Agent 自觉 | **`on_failure: stop`**，standard 下不可豁免 |
| 完成标准 | 口头「做完了」 | **gates 验磁盘**：路由记录、summary 质量、run 状态 |
| 证据位置 | 易留在对话上下文 | **`evidence/` 目录**，聊天只沟通、文件记账 |

无需记 Skill 名称：路由自动匹配，但**执行路径**仍被 contract 锁住。

### 3. 相对 Harness Engineering：在 git 提交**之前**的优势

Harness Engineering 的完整闭环通常包含 **开发 → 审查 → commit/PR → 合并**；本框架**刻意不做 commit/PR Skill**，专注 **git 提交前** 的研发协作阶段，并在该阶段形成差异化：

| 阶段（git 提交前） | Harness Engineering | 本框架 |
|--------------------|---------------------|--------|
| **上下文成本** | **多 Agent** 交接；artifacts 在对话中压缩/膨胀，每多一环多一份 handoff | **Cursor 单一 Agent** + 查询预算 + 磁盘 run；无多 Agent 上下文叠加 |
| **任务连续性** | 依赖 manifest + 会话记忆 | **一事一 run**，`router-resolve` 判 new/resume，跨会话可读 |
| **流程刚性** | 元路由协议强，但多在聊天层 | **contract + gates**，关键节点可脚本验证 |
| **知识沉淀** | 常经 wiki/PR 才进入团队可见 | **`harness-archive` 入图书架**（`docs/knowledge/`），无需等 commit |
| **接入门槛** | 需理解编排链与 git 闭环 | **Cursor 内开箱**，个人独立使用即可 |
| **岗位扩展** | 域 Skill 常与平台捆绑 | **Core 底座 + 空 registry**，各岗自建 `team-*` |

> **分工说明**：Harness Engineering 强在 **git/PR 之后的团队交付与审计**；本框架强在 **提交 git 之前** —— 用更少 Token 完成任务、用 contract 保证步骤不跳、用 archive 先把经验写下来。需要上库时，仍由人工或现有 CI 走常规 git 流程。

**一句话**：**Cursor 单一 Agent** + 更省 Token 的图书架式读法 + 可验收的 contract 流程 + 不绑 git 也能上架经验 —— 适合在 Cursor 中于开发、文档、分析等阶段日常启用；commit 仍走常规 git 规范，框架不替代这一环。

## 文档

- [成熟度](docs/harness/MATURITY.md)
- [流程约束](docs/harness/PROCESS.md)
- [Run 工作记忆](docs/harness/RUN-MEMORY.md)
- [贡献 Team Skill](docs/harness/CONTRIBUTING-SKILLS.md)
- [知识架构](docs/knowledge/KNOWLEDGE.md)
- [知识配置](docs/knowledge/.knowledge-config.yaml)

## 原则

- **知识优先于工作流** — 经验归档到图书架（`docs/knowledge/`），不依赖聊天记忆
- **无 git commit Skill** — 沉淀经 `harness-archive` 写文件
- **查询预算** — 先目录、再书脊、后取书（Layer A → B → C），见 `.knowledge-config.yaml`

## Core Skill（16 个）

`harness-router`、`harness-run`、`harness-registry`、`harness-create-skill`、`harness-compose`、`harness-scaffold`、`harness-docs-base`、`harness-agents-map`、`harness-cursor-rules`、`harness-architecture`、`harness-quality-gates`、`harness-verify`、`harness-self-review`、`harness-archive`、`harness-doc-garden`、`harness-gc`
