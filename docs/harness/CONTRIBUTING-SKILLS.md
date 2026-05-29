# 贡献 Team Skill

## 命名

- **Core（底层平台）**：`harness-*`，由框架维护，项目 fork 勿改。
- **Team Skill**：`team-<主题>`，尽量 **1 个英文短词**；省略与领域重复的 action（如用 `team-excel` 而非 `team-excel-analyze`）。
- **Workflow**：`skills.registry.yaml` 中 **单个英文短词**（如 `persist`），描述「做什么」写在 description，不堆进名称。
- **个人 Skill**：`local-*`，位于 `~/.cursor/skills/`（不写入 registry）

### 示例

| 任务 | 推荐 | 避免 |
|------|------|------|
| Excel 分析 | `team-excel` | `team-excel-analyze` |
| Text to SQL | `team-sql` | `team-text-to-sql` |
| 分析后归档流水线 | workflow `persist` | `insight-persist` |

## 必需文件

```text
.cursor/skills/team-sql/
├── SKILL.md
├── contract.yaml
└── scripts/gates/   （推荐）
```

## contract.yaml 最低要求

- `preconditions`（≥1）
- `steps`，关键步骤 `required: true`
- `postconditions`（≥1）
- `outputs`
- `on_failure: stop`

## 登记

1. 运行 **harness-registry**，写入 `docs/harness/skills.registry.yaml`
2. 更新 **AGENTS.md** 团队 Skill 表（registry Skill 负责）
3. CI：`python scripts/harness/validate-skill.py` + `validate-registry.py`

## 禁止

- 在项目 fork 中修改 `harness-*` Core Skill
- 省略 contract.yaml
- 在 Skill 或知识条目中存放密钥

参见：`docs/harness/golden-principles.md`
