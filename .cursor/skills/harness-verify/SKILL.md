---
name: harness-verify
description: 在交付或归档前运行项目本地 lint、测试与构建；成功时写入 docs/harness/.verify-passed 标记。用于 risky 变更前或 strict 流程中的 harness-archive 之前。
---

# Harness 本地验证（Verify）

## 步骤

1. 识别技术栈（package.json、pyproject.toml、Makefile 等）。
2. 运行项目标准命令（首次运行后记录在 SKILL 或 AGENTS.md）。
3. 成功时写入标记：
   ```bash
   date -Iseconds > docs/harness/.verify-passed
   ```
4. 在当前 run 的 evidence 中记录命令与输出摘要。

## 模板仓库默认

若无应用栈：至少运行 `python scripts/harness/validate-contract.py` 作为最小 verify。

## 产出

- verify 报告
- 可选 `.verify-passed` 标记文件
