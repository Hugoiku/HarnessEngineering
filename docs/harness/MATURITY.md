# Harness 成熟度等级

| 等级 | 含义 | 要求 |
|------|------|------|
| 0 | 空仓库 | — |
| 1 | Agent 可读 | scaffold、agents_map、docs_base、cursor_rules |
| 2 | 有约束 | + architecture、quality_gates |
| 3 | 可运行 | + platform_ready（router、run、registry、create-skill、compose）+ workflow_skills_ready（verify、self-review） |
| 4 | 可扩展知识 | + knowledge_skills_ready（archive、doc-garden、gc）+ ≥1 个已登记 team skill |

检查命令：`bash scripts/harness/assess.sh` 或见 README 中的 Python 脚本。
