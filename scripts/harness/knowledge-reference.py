#!/usr/bin/env python3
"""Record Layer C knowledge references (last_referenced, reference_count, distinct_runs)."""
from __future__ import annotations

import argparse
import pathlib
import sys

from knowledge_common import ROOT, bump_evidence, find_entry_by_id


def main() -> None:
    parser = argparse.ArgumentParser(description="Bump knowledge entry reference counters.")
    parser.add_argument("paths", nargs="*", help="C-layer entry .md paths")
    parser.add_argument("--id", action="append", dest="ids", default=[], help="Entry id (PK-*, BK-*, TK-*)")
    parser.add_argument("--run-id", default=None, help="Harness run directory or id (for distinct_runs)")
    args = parser.parse_args()

    targets: list[pathlib.Path] = [pathlib.Path(p) for p in args.paths]
    for entry_id in args.ids:
        found = find_entry_by_id(entry_id)
        if found is None:
            print(f"ERROR: entry not found: {entry_id}", file=sys.stderr)
            sys.exit(1)
        targets.append(found)

    if not targets:
        parser.print_help()
        sys.exit(1)

    seen: set[pathlib.Path] = set()
    for path in targets:
        path = path.resolve()
        if path in seen or not path.is_file():
            continue
        seen.add(path)
        row = bump_evidence(path, args.run_id)
        runs = len(row.get("distinct_runs") or [])
        print(
            f"OK: {row['id']} reference_count={row['reference_count']} "
            f"distinct_runs={runs} last_referenced={row['last_referenced']}"
        )


if __name__ == "__main__":
    main()
