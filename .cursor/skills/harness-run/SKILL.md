---
name: harness-run
description: 对任意 harness 或 team Skill 的受约束执行器。须先 router-resolve，写入工作记忆，COMPLETED 前 summary 质量门禁。执行 harness-* 或 team-* Skill 时必须使用本 Skill。
---

# Harness 受约束执行（Run）

## 调用方式

```text
harness-run <skill-name> [--profile standard|strict|draft] [--run-id <run-dir>]
```

**个人流程（必须）**：

1. 获取工作记忆状态并做**语义路由**（由你作为 Agent 判断，非正则）：
   ```bash
   python scripts/harness/router-resolve.py --data
   ```
   读取输出中的 `running[]`、`team_skills[]`、`core_skills[]`，
   语义判断 resume/new 及目标 skill（见 harness-router/SKILL.md 决策规则）。
2. 设置环境变量并执行本 Skill：
   ```bash
   export HARNESS_USER_MESSAGE="<用户最新消息>"
   export RUN_DIR=docs/harness/runs/<timestamp>-<skill>   # 或 resume 时的已有目录
   ```

## 初始化

**新建 run**：创建 `RUN_DIR`，写入 `run.yaml`（`status: RUNNING`，含 `last_activity_at`）。

**续跑**：`--run-id` 指向已有目录；**禁止**续跑 `STALE` run（须说「新任务」）。

## Contract 步骤摘要

**每完成一个步骤，必须立即用 `run_common.write_run_field` 更新 `current_step`，退出门禁会校验。**

| 步骤 | 完成后写入 current_step | 作用 |
|------|------------------------|------|
| init-run-dir | `init-run-dir` | 创建/打开 run 目录 |
| record-router-resolution | `record-router-resolution` | 调用 `write-router-resolution.py` 写入结构化路由决策 JSON |
| execute-steps | `execute-steps` | 按目标 Skill 的 contract 执行 |
| touch-activity | `touch-activity` | 更新 `last_activity_at` |
| postconditions | `postconditions` | 终态 + summary 质量（COMPLETED 时） |

### 写入路由决策（record-router-resolution 步骤必须做）

```bash
python scripts/harness/write-router-resolution.py \
  --run-dir "$RUN_DIR" \
  --action new \          # new | resume | none
  --skill <skill-name> \
  --reason "语义判断：<一句话说明为何选择此 skill 和 action>"
```

### 更新 current_step 示例

```bash
python scripts/harness/run-touch.py "$RUN_DIR"  # 同时 touch activity
# 在 run.yaml 写入 current_step: execute-steps
python -c "
import sys; sys.path.insert(0,'scripts/harness')
from run_common import write_run_field
from pathlib import Path
write_run_field(Path('$RUN_DIR'), 'current_step', 'execute-steps')
"
```

## COMPLETED 硬门禁

- 必须存在 `evidence/summary.md`
- 必须通过 `python scripts/harness/validate-summary.py evidence/summary.md`
- `current_step` 须已到达 `execute-steps` 或更晚（防跳步）
- `evidence/router-resolution.json` 须通过内容校验

## 知识查询（orient / analyze / summarize）

见 `.knowledge-config.yaml`；每打开 Layer C：

```bash
python scripts/harness/knowledge-reference.py --id <entry-id> --run-id "$RUN_DIR"
```

## 任务完成后

```bash
# 1. 标 COMPLETED（postcondition 会校验 summary）
# 2. 个人跨会话记忆（可选但推荐）：
export RUN_DIR=...
harness-run harness-archive
```

## 不在范围内

- Git 操作
- 绕过 router-resolution 直接执行（contract 会失败）
