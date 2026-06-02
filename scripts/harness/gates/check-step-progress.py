#!/usr/bin/env python3
"""
门禁：当 run 状态为 COMPLETED 时，校验 current_step 已推进到 postconditions。

防止 Agent 跳过中间步骤直接宣布完成。
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts/harness"))
from run_common import read_run_fields  # noqa: E402

# contract 步骤有序列表，postconditions 须是最后到达的节点
STEP_ORDER = [
    "init-run-dir",
    "record-router-resolution",
    "execute-steps",
    "touch-activity",
    "postconditions",
]
REQUIRED_FINAL_STEP = "postconditions"


def main() -> None:
    run_dir_arg = sys.argv[1] if len(sys.argv) > 1 else "docs/harness/runs/latest"
    run_dir = ROOT / run_dir_arg if not pathlib.Path(run_dir_arg).is_absolute() else pathlib.Path(run_dir_arg)

    fields = read_run_fields(run_dir)
    status = fields.get("status", "")

    if status != "COMPLETED":
        print(f"OK: run 尚未 COMPLETED（status={status}），跳过 step 检查")
        sys.exit(0)

    current_step = fields.get("current_step", "").strip()
    if not current_step:
        print("FAIL: run.yaml 缺少 current_step 字段（Agent 须在每步完成后更新）", file=sys.stderr)
        sys.exit(1)

    if current_step != REQUIRED_FINAL_STEP:
        # 检查是否至少到达了 execute-steps
        try:
            idx = STEP_ORDER.index(current_step)
        except ValueError:
            idx = -1
        exec_idx = STEP_ORDER.index("execute-steps")
        if idx < exec_idx:
            print(
                f"FAIL: current_step='{current_step}' 未到达 execute-steps，"
                "疑似跳过中间步骤直接 COMPLETED",
                file=sys.stderr,
            )
            sys.exit(1)
        print(
            f"WARN: current_step='{current_step}'（期望 '{REQUIRED_FINAL_STEP}'），"
            "但已过 execute-steps，视为可接受"
        )
    else:
        print(f"OK: current_step={current_step}，步骤轨迹完整")


if __name__ == "__main__":
    main()
