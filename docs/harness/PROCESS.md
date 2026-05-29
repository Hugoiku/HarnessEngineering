# Harness 流程约束

## 原则

1. 仅通过 **harness-run** 执行 Skill（不要直接按 SKILL.md 自由发挥）。
2. 每个 Skill 必须有 **contract.yaml**（preconditions、steps、postconditions）。
3. 读知识遵守 `docs/knowledge/.knowledge-config.yaml` 中的 **查询预算**。
4. 写知识使用 **harness-archive**（本框架无 git commit 类 Skill）。
5. B 层 catalog 行由 C 层 frontmatter 经 `catalog-line.sh` **派生**，禁止手写 B 层摘要正文。

## Run 生命周期（个人场景）

```text
harness-router (router-resolve.py，含 STALE 标记)
  → harness-run → docs/harness/runs/<timestamp>-<skill>/
  → evidence/router-resolution.txt + evidence/summary.md
  → COMPLETED（summary 须过 validate-summary.py）
  → harness-archive / archive-from-run.py
  → archived_to_knowledge: true

RUNNING 且 idle ≥ stale_after_days → STALE（不可 resume，须 new）
```

详见 [RUN-MEMORY.md](RUN-MEMORY.md) 与 `docs/harness/.run-config.yaml`。

## 知识生命周期

```text
run evidence → harness-archive → docs/knowledge/** → 更新 catalog → log.md
```

## Profile（严格度）

| Profile | 是否允许豁免 | 用途 |
|---------|--------------|------|
| strict | 否 | 类生产交付 |
| standard | 否 | 默认 |
| draft | 有限 | 探索 / Spike |
