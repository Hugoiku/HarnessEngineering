# AGENTS.md

约 100 行。仅作目录地图，不是百科全书。

## Harness

- 成熟度：`bash scripts/harness/assess.sh`
- 路由：`.cursor/skills/harness-router/SKILL.md`（含工作记忆续跑/新建判定）
- 执行任意 Skill：**harness-run**（唯一推荐入口）
- 状态：`docs/harness/STATUS.yaml`

## 知识库（Layer A 入口）

- 全景目录：`docs/knowledge/catalog.md`
- 配置 / 查询预算：`docs/knowledge/.knowledge-config.yaml`
- 写入沉淀：`harness-archive`
- 索引维护：`harness-doc-garden`（含 `knowledge-maturity.py` 晋升/衰减）

## Team Skill

当前无已登记 Team Skill。新建：`harness-create-skill` → `harness-registry`

完整登记：`docs/harness/skills.registry.yaml`

## Core 工作流 Skill

| Skill | 何时使用 |
|-------|----------|
| harness-verify | 高风险变更前；本地 lint/测试 |
| harness-self-review | 交付或归档前自检 |
| harness-archive | 将 run 结论写入 `docs/knowledge/` |

## 深度文档

| 主题 | 路径 |
|------|------|
| 架构 | `ARCHITECTURE.md`、`docs/design-docs/layering.md` |
| 黄金原则 | `docs/harness/golden-principles.md` |
| 流程约束 | `docs/harness/PROCESS.md` |
| 贡献 Skill | `docs/harness/CONTRIBUTING-SKILLS.md` |
| 知识架构 | `docs/knowledge/KNOWLEDGE.md` |

## 查询预算（摘要）

1. 每个 run 仅读一次 Layer A（`catalog.md`，≤60 行）。
2. 按领域读一个 Layer B catalog（≤250 行）。
3. Layer C 仅打开 Top-K 条目（见 `.knowledge-config.yaml` 的 phases）。

## 规则

- **任何工作事项**须先 **harness-router** → **harness-run**（见 `.cursor/rules/harness-process.mdc`）。
- 不得绕过 harness-run；`COMPLETED` 须有合格 `evidence/summary.md`。
- 不得把完整知识条目粘贴进对话 — 使用 ID 与摘要即可。

## 个人工作记忆

- 配置：`docs/harness/.run-config.yaml`（STALE 天数、summary 最低字数）
- 脚本：`router-resolve.py`、`run-stale.py`、`validate-summary.py`、`archive-from-run.py`
