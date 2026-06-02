#!/usr/bin/env python3
"""Validate skill directory has SKILL.md and contract.yaml with minimum fields."""
from __future__ import annotations

import pathlib
import sys

import yaml

# 必须存在且非空（空列表不可接受）
REQUIRED_NONEMPTY = ["name", "steps", "outputs"]
# 必须存在，但允许空列表（Skill 可以没有 preconditions / postconditions）
REQUIRED_PRESENT = ["preconditions", "postconditions"]


def main() -> None:
    skill_dir = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")

    if not (skill_dir / "SKILL.md").is_file():
        sys.exit(f"missing SKILL.md in {skill_dir}")

    contract = skill_dir / "contract.yaml"
    if not contract.is_file():
        sys.exit(f"missing contract.yaml in {skill_dir}")

    try:
        data = yaml.safe_load(contract.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        sys.exit(f"contract.yaml YAML parse error: {exc}")

    for key in REQUIRED_NONEMPTY:
        val = data.get(key)
        if val is None:
            sys.exit(f"contract missing required field: {key}")
        if isinstance(val, (list, dict)) and not val:
            sys.exit(f"contract field '{key}' must not be empty")

    for key in REQUIRED_PRESENT:
        if key not in data:
            sys.exit(f"contract missing field: {key}")

    print("OK:", skill_dir.name)


if __name__ == "__main__":
    main()
