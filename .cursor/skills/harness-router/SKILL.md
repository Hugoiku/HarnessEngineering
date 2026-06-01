---
name: harness-router
description: 评估 Harness 成熟度，语义匹配 Team Skill，并判断续跑已有 run 或新建工作记忆，推荐 harness-run 命令。用于任务路由、进度查看或「下一步做什么」。
---

# Harness 路由（Router）

## 步骤

1. 在仓库根目录执行成熟度评估：
   ```bash
   bash scripts/harness/assess.sh
   ```

2. 读取状态数据（脚本负责标记 STALE、收集运行状态）：
   ```bash
   python scripts/harness/router-resolve.py --data
   ```
   输出 JSON 包含：
   - `running[]` — 正在进行的 run（含 skill、description、age_days）
   - `recent_completed[]` — 最近完成的 run（供上下文参考）
   - `team_skills[]` — 已注册 Team Skill（含 description、triggers）
   - `core_skills[]` — 16 个 Core Skill（含 description）

3. **语义路由决策**（你作为 Agent 来判断，不依赖正则）：

   ### ① 意图 → resume 还是 new？

   将用户消息与 `running[]` 中每个 run 的 `skill` 和 `description` 做语义对比：

   | 判断依据 | 决策 |
   |---------|------|
   | 用户意图与某个 running run 的任务在语义上是**同一件事** | **resume** 该 run |
   | 用户意图明显是**全新任务**，与所有 running run 无关 | **new** |
   | 用户明确说「新任务 / 重新开始 / new」| **new**（用户明示） |
   | 用户明确说「继续 / 接着 / resume」且有 running run | **resume** 最近那个 |
   | running run 已是 STALE（age_days 超阈值）| **禁止 resume**，必须 new |
   | 无 running run | **new** |

   > 语义判断示例：用户说「帮我检查一下知识库质量」→ 若有 skill=harness-gc 的 RUNNING run，应 resume；
   > 用户说「我要写一个新的分析报告」→ 即使有 running run，也应 new。

   ### ② 意图 → 目标 Skill？

   将用户消息与 `team_skills[].description`、`team_skills[].triggers`、`core_skills[].description` 做语义对比，选最匹配的一个：

   - **Team Skill 优先**（更具体）
   - 无 Team Skill 匹配 → 从 Core Skill 中选
   - 完全无匹配且 Level ≥ 3 → 推荐 `harness-create-skill`
   - Level < 3 → 推荐 assess 指示的下一个 Core Skill

4. 汇总输出，格式如下：
   ```
   action: resume | new | none
   skill:  <skill-name>
   run_id: <run-dir> | -
   reason: <一句话说明语义判断依据>
   command: harness-run <skill> [--run-id <run-dir>]
   ```

5. 若用户指定 workflow → `harness-run workflow <name>`。

## 知识路由

知识密集型任务指向 Layer A：`docs/knowledge/catalog.md`，按阶段提示选 Layer B/C。

## 产出

- 路由决策（action、run_dir、command、reason）
- 可选更新 `docs/harness/STATUS.yaml`

## 不在范围内

- 直接执行 Skill（请用 harness-run）
- Git 提交或 PR
