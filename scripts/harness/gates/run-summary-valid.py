#!/usr/bin/env python3
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
RUN_DIR = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "docs/harness/runs/latest")
summary = RUN_DIR / "evidence/summary.md"
if not summary.is_file():
    print(f"missing {summary}", file=sys.stderr)
    sys.exit(1)
import subprocess
r = subprocess.run([sys.executable, str(ROOT / "scripts/harness/validate-summary.py"), str(summary)])
sys.exit(r.returncode)
