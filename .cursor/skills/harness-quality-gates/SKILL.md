---
name: harness-quality-gates
description: 配置校验脚本、golden-principles.md 与 CI workflow，用于校验 Skill contract 与 registry。在架构文档之后用于机械约束。
---

# Harness 质量门禁（Quality Gates）

## 交付物

- `docs/harness/golden-principles.md`
- `scripts/harness/validate-contract.py`（及 .sh）
- `.github/workflows/harness-validate.yml`

## CI 执行

```bash
python scripts/harness/validate-contract.py
python scripts/harness/validate-registry.py
```

## Lint 错误信息

为项目 Linter 增加带**修复指引**的错误文案，便于 Agent 自修。
