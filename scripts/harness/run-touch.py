#!/usr/bin/env python3
"""Update run.yaml last_activity_at."""
from __future__ import annotations

import argparse
import pathlib
import sys

from run_common import touch_activity


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", help="Path to run directory")
    args = parser.parse_args()
    run_dir = pathlib.Path(args.run_dir)
    if not (run_dir / "run.yaml").is_file():
        print(f"ERROR: missing run.yaml in {run_dir}", file=sys.stderr)
        sys.exit(1)
    ts = touch_activity(run_dir.resolve())
    print(f"OK: last_activity_at={ts}")


if __name__ == "__main__":
    main()
