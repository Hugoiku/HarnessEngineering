#!/usr/bin/env python3
"""Validate registry paths exist."""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
REG = ROOT / "docs/harness/skills.registry.yaml"


def main() -> None:
    if not REG.is_file():
        sys.exit("missing registry")
    text = REG.read_text(encoding="utf-8")
    paths = re.findall(r"path:\s*(.+)", text)
    for p in paths:
        p = p.strip()
        if not (ROOT / p).is_dir():
            sys.exit(f"registry path missing: {p}")
    print("registry OK,", len(paths), "team skill path(s)")


if __name__ == "__main__":
    main()
