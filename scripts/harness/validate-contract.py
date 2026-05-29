#!/usr/bin/env python3
"""Validate all harness-* and team-* skills."""
from __future__ import annotations

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
VALIDATE = ROOT / "scripts/harness/validate-skill.py"
failed = 0
for pattern in ["harness-*", "team-*"]:
    for d in (ROOT / ".cursor/skills").glob(pattern):
        if not (d / "SKILL.md").is_file():
            continue
        r = subprocess.run([sys.executable, str(VALIDATE), str(d)])
        if r.returncode != 0:
            failed = 1
sys.exit(failed)
