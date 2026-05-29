---
name: harness-router
description: 评估 Harness 成熟度，匹配 Team Skill，并自动判断续跑已有 run 或新建工作记忆，推荐 harness-run 命令。用于任务路由、进度查看或「下一步做什么」。
---

# Harness 路由（Router）

## 步骤

1. 在仓库根目录执行 `bash scripts/harness/assess.sh`（Windows 可参考 README 使用 Python 脚本）。
2. 读取 `docs/harness/STATUS.yaml` 与 `docs/harness/skills.registry.yaml`。
3. **工作记忆判定**（必做）— 脚本会先 `run-stale.py --apply` 标记超时 RUNNING，再解析续跑/新建：
   ```bash
   python scripts/harness/router-resolve.py "<用户最新一条消息>"
   ```
   Windows 同上；可加 `--json` 便于解析。
4. 解析输出并写入 recommendation：
   - `action: resume` → 推荐 **同一** `run_dir`，`harness-run <skill> --run-id <run_dir>`
   - `action: new` → 推荐新建 `docs/harness/runs/<timestamp>-<skill>/`
   - `action: none` → 无 Skill 命中，按成熟度走 create-skill 或 core skill
5. 与 `team[].triggers` 做不区分大小写子串匹配（脚本已含，可交叉验证）。
6. 汇总输出：
   - 成熟度等级与标志位
   - **工作记忆决策**（action、run_dir、reason、sync_work_memory）
   - 推荐 `command`（完整 harness-run 命令）
   - 若无匹配且 Level ≥ 3 → `harness-create-skill`
   - 若 Level < 3 → assess 推荐的下一个 Core Skill
7. 若用户指定 workflow → `harness-run workflow <name>`。

## 工作记忆判定规则（router-resolve）

| 条件 | 决策 |
|------|------|
| 用户说「新任务 / 重新开始 / new run」 | **new** — 强制新建 run |
| 存在 `status: RUNNING` 的 run，且 skill 与意图一致 | **resume** — 续跑同一目录 |
| 用户说「继续 / 接着 / resume」且有 RUNNING run | **resume** |
| 仅有一个 RUNNING run，且用户未要求新任务 | **resume** |
| RUNNING run 的 skill 与意图不一致 | **new** — 为新 skill 建 run |
| RUNNING 超过 14 天无 activity | 标 **STALE**，**禁止 resume**，须 new |
| 无 RUNNING run | **new** |

续跑时须告知执行器：**每完成 contract step 更新同一 `run_dir` 下 evidence 与 run.yaml**，勿只写在聊天里。

## 知识路由

知识密集型任务指向 Layer A：`docs/knowledge/catalog.md` 及 catalog 中的阶段提示。

## 产出

- recommendation 文本（含 action、run_dir、command、理由）
- 可选更新 `docs/harness/STATUS.yaml`（与 assess 不一致时）

## 不在范围内

- 直接执行 Skill（请用 harness-run）
- Git 提交或 PR
