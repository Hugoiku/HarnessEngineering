---
name: harness-doc-garden
description: 校验知识索引 B/C 同步，并执行 knowledge-maturity.py 晋升/衰减。定期或发布前使用。
---

# Harness 文档园丁（Doc Garden）

## 检查项

| 检查 | 动作 |
|------|------|
| B 行与 C frontmatter 不一致 | 经 `catalog-line.sh` 重生成行 |
| C 条目未出现在 B catalog | 补行 |
| B 行无对应 C 文件 | 标记 orphan → `contributions/conflicts/` |
| summary 缺失或过长 | Lint 失败；需 harness-archive 修复 |
| 成熟度晋升/衰减 | 运行 `knowledge-maturity.py`（见下） |

## 步骤

1. 扫描 `docs/knowledge/` 下所有 C 层 `*.md`（不含 `archive/`）。
2. 同步 B 层 catalog；写入 `evidence/doc-garden-report.md`。
3. **成熟度维护**（默认先 dry-run，确认后 apply）：
   ```bash
   python scripts/harness/knowledge-maturity.py --dry-run
   python scripts/harness/knowledge-maturity.py --apply --report evidence/maturity-report.md
   ```
4. 执行 `python scripts/harness/catalog-aggregate.py` 刷新 Layer A。

## 规则（对称配置）

见 `docs/knowledge/.knowledge-config.yaml`：

**晋升** `maturity.promotion` — 按引用次数 /  distinct runs  
**衰减** `maturity.decay` — 按 idle 月数 / stale

## 引用计数

`harness-run` 打开 Layer C 后须调用：

```bash
python scripts/harness/knowledge-reference.py --id PK-xxx --run-id <run-dir>
```
