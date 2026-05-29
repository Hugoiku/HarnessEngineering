---
name: harness-gc
description: 扫描代码库与知识条目是否违反 docs/harness/golden-principles.md，并给出重构建议。质量漂移时按需使用。
---

# Harness 垃圾回收（GC）

## 步骤

1. 阅读 `docs/harness/golden-principles.md`。
2. 扫描反模式（重复 helper、缺失 summary、仅存在于对话的知识等）。
3. 输出 `evidence/gc-report.md`，按优先级列出修复项。
4. 可选：对 recurring pitfalls 经 harness-archive 创建 draft 知识条目。

## 不在范围内

- 未经用户确认自动改代码
- Git commit
