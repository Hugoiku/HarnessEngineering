---
name: harness-scaffold
description: 初始化 Harness 框架骨架，含 docs/harness/、scripts/harness/、docs/harness/runs/ 与占位 CI。用于空仓库接入本模板。
---

# Harness 脚手架（Scaffold）

## 创建内容

- `docs/harness/`（STATUS、registry、golden-principles、PROCESS）
- `scripts/harness/`（assess、validate、catalog 脚本）
- `docs/harness/runs/.gitkeep`
- `.github/workflows/harness-validate.yml`（可选 Skill 校验 CI）

## 步骤

1. 从 harness-framework 模板复制结构，或接着执行 harness-docs-base。
2. 执行 `bash scripts/harness/assess.sh`（Windows 见 README）。
3. 设置 `docs/harness/STATUS.yaml` 中 `scaffold: true`。
