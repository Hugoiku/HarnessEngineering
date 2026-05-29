# Run 工作记忆（个人场景）

与 `docs/knowledge/` 长期记忆配合使用。

## 生命周期

```text
router-resolve (new/resume)
  → harness-run (RUNNING, last_activity_at)
  → evidence/summary.md + validate-summary
  → COMPLETED
  → harness-archive / archive-from-run.py
  → archived_to_knowledge: true

RUNNING 且 idle ≥ stale_after_days → STALE（不可 resume）
```

## 脚本

| 脚本 | 用途 |
|------|------|
| `router-resolve.py` | 续跑 vs 新建 |
| `run-stale.py` | 标记 STALE（不删除） |
| `run-touch.py` | 更新 last_activity_at |
| `validate-summary.py` | summary 质量门禁 |
| `archive-from-run.py` | 一键 personal archive |

配置：`docs/harness/.run-config.yaml`
