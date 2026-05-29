---
name: harness-archive
description: 从 COMPLETED run 的 evidence/summary.md 一键写入 docs/knowledge/（archive-from-run），含 summary 质量检查。个人跨会话记忆，不涉及 git commit。
---

# Harness 知识归档（Archive）

## 前置条件

- run `status: COMPLETED`
- `evidence/summary.md` 已通过 `validate-summary.py`

## 快速归档（推荐）

```bash
export RUN_DIR=docs/harness/runs/<run-id>
python scripts/harness/archive-from-run.py --run-dir "$RUN_DIR"
```

或 **harness-run harness-archive**（contract 调用 `archive-from-run.sh`）。

脚本会：

1. 校验 summary 质量  
2. 创建 `docs/knowledge/project/PK-*.md`（draft）  
3. 更新 B/A catalog、`log.md`  
4. 设置 run `archived_to_knowledge: true`  

## 不在范围内

- git commit / PR
- 归档原始敏感明细
