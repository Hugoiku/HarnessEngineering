---
name: harness-self-review
description: 对照验收标准、架构规则与知识缺口进行自检清单，在归档或交付前使用。在 Team Skill 执行完成后、harness-archive 之前使用。
---

# Harness 自检（Self Review）

## 检查清单

- [ ] 任务验收标准已满足
- [ ] 待归档 evidence 中无敏感原始数据
- [ ] run.yaml 已记录 knowledgeReferences
- [ ] 未违反架构 / golden-principles
- [ ] 若无 catalog 条目命中，已标记 knowledge_gap

## 产出

- `evidence/self-review.md`，每项 pass/fail
