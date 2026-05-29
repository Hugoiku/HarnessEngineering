#!/usr/bin/env python3
"""Validate skill directory has SKILL.md and contract.yaml with minimum fields."""
from __future__ import annotations

import pathlib
import sys

REQUIRED = ["name:", "preconditions:", "steps:", "postconditions:", "outputs:"]


def main() -> None:
    skill_dir = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    if not (skill_dir / "SKILL.md").is_file():
        sys.exit(f"missing SKILL.md in {skill_dir}")
    contract = skill_dir / "contract.yaml"
    if not contract.is_file():
        sys.exit(f"missing contract.yaml in {skill_dir}")
    text = contract.read_text(encoding="utf-8")
    for key in REQUIRED:
        if key not in text:
            sys.exit(f"contract missing section: {key}")
    print("OK:", skill_dir.name)


if __name__ == "__main__":
    main()
