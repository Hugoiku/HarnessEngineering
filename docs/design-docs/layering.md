# 分层模型

按项目定义。示例：

```text
Types → Config → Repo → Service → Runtime → UI
横切关注点：Providers（auth、telemetry、feature flags）
```

通过结构测试与自定义 Linter 强制执行（harness-quality-gates）。
