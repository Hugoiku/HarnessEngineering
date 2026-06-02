#!/usr/bin/env python3
"""
Agent 调用此脚本将语义路由决策写入 evidence/router-resolution.json。

用法：
  python write-router-resolution.py \
    --run-dir docs/harness/runs/<id> \
    --action new \
    --skill harness-gc \
    --reason "用户意图与知识库质量检查语义匹配"

可选：
  --run-id <已有 run 目录>（resume 时传入）
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/harness"))
from run_common import touch_activity  # noqa: E402

VALID_ACTIONS = {"new", "resume", "none"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Write structured router resolution.")
    parser.add_argument("--run-dir", required=True, help="RUN_DIR path")
    parser.add_argument("--action", required=True, choices=list(VALID_ACTIONS))
    parser.add_argument("--skill", required=True, help="Target skill name")
    parser.add_argument("--reason", required=True, help="Semantic routing reason (≥10 chars)")
    parser.add_argument("--resumed-run-id", default="", help="Resumed run ID (for resume action)")
    args = parser.parse_args()

    if len(args.reason.strip()) < 10:
        print("ERROR: --reason 至少 10 个字符", file=sys.stderr)
        sys.exit(1)

    run_dir = ROOT / args.run_dir if not pathlib.Path(args.run_dir).is_absolute() else pathlib.Path(args.run_dir)
    evidence_dir = run_dir / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    resolution = {
        "action": args.action,
        "skill": args.skill,
        "reason": args.reason.strip(),
        "resumed_run_id": args.resumed_run_id or None,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }

    out = evidence_dir / "router-resolution.json"
    out.write_text(json.dumps(resolution, ensure_ascii=False, indent=2), encoding="utf-8")
    touch_activity(run_dir)
    print(f"OK: router-resolution recorded -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
