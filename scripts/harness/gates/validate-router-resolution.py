#!/usr/bin/env python3
"""
门禁：校验 evidence/router-resolution.json 内容合规。

检查项：
  1. 文件存在且可解析为 JSON
  2. action 字段值为 new / resume / none 之一
  3. skill 字段非空
  4. reason 字段 ≥ 10 字符（不能糊弄）
"""
from __future__ import annotations

import json
import pathlib
import sys

VALID_ACTIONS = {"new", "resume", "none"}
REASON_MIN_CHARS = 10

ROOT = pathlib.Path(__file__).resolve().parents[3]


def main() -> None:
    run_dir_arg = sys.argv[1] if len(sys.argv) > 1 else "docs/harness/runs/latest"
    run_dir = ROOT / run_dir_arg if not pathlib.Path(run_dir_arg).is_absolute() else pathlib.Path(run_dir_arg)
    resolution_file = run_dir / "evidence" / "router-resolution.json"

    if not resolution_file.is_file():
        print(f"FAIL: 缺少 {resolution_file.relative_to(ROOT)}（须 write-router-resolution.py 写入）", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(resolution_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"FAIL: router-resolution.json 解析失败: {exc}", file=sys.stderr)
        sys.exit(1)

    errors: list[str] = []

    action = data.get("action", "")
    if action not in VALID_ACTIONS:
        errors.append(f"action 无效: '{action}'（须为 {VALID_ACTIONS}）")

    skill = (data.get("skill") or "").strip()
    if not skill:
        errors.append("skill 字段为空")

    reason = (data.get("reason") or "").strip()
    if len(reason) < REASON_MIN_CHARS:
        errors.append(f"reason 过短（{len(reason)} < {REASON_MIN_CHARS} 字符）")

    if errors:
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"OK: router-resolution valid (action={action}, skill={skill})")


if __name__ == "__main__":
    main()
