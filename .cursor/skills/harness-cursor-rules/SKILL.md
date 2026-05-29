---
name: harness-cursor-rules
description: 创建或更新 .cursor/rules/harness-process.mdc，强制 harness-run、查询预算与 harness-archive 模式。用于为团队配置 Cursor 规则约束。
---

# Harness Cursor 规则

## 交付物

`.cursor/rules/harness-process.mdc`，且 `alwaysApply: true`

## 必须包含

- 仅通过 harness-run 执行 Skill
- Layer A→B→C 查询预算
- 持久化使用 harness-archive（无 commit 类 Skill）
- contract 门禁失败即停止

## 可选

- 项目专属规则放在独立 `.mdc` 文件；与 harness-process 分开维护
