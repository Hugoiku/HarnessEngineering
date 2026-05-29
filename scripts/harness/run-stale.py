#!/usr/bin/env python3
"""Mark inactive RUNNING runs as STALE (conservative: never delete)."""
from __future__ import annotations

import argparse
import sys

from run_common import days_since_activity, iter_run_dirs, load_run_config, read_run_fields, write_run_field


def apply_stale(dry_run: bool) -> list[str]:
    cfg = load_run_config()
    threshold = float(cfg["stale_after_days"])
    actions: list[str] = []
    for run_dir in iter_run_dirs():
        fields = read_run_fields(run_dir)
        status = fields.get("status", "")
        if status != "RUNNING":
            continue
        idle = days_since_activity(run_dir)
        if idle < threshold:
            continue
        msg = (
            f"{'DRY ' if dry_run else ''}STALE {run_dir.name}: "
            f"RUNNING idle {idle:.1f}d >= {threshold}d"
        )
        actions.append(msg)
        if not dry_run:
            write_run_field(run_dir, "status", "STALE")
    return actions


def main() -> None:
    parser = argparse.ArgumentParser(description="Mark stale RUNNING runs.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    dry_run = not args.apply
    actions = apply_stale(dry_run=dry_run)
    mode = "dry-run" if dry_run else "apply"
    print(f"# Run stale ({mode})")
    if not actions:
        print("No stale actions.")
        return
    for line in actions:
        print(line)


if __name__ == "__main__":
    main()
