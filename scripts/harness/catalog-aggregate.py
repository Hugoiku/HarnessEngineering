#!/usr/bin/env python3
"""Regenerate Layer A aggregate stats in docs/knowledge/catalog.md."""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
CATALOG = ROOT / "docs/knowledge/catalog.md"

SECTIONS = [
    ("team-conventions", "team-conventions/catalog.md"),
    ("tech-wiki", "tech-wiki/catalog.md"),
    ("project", "project/catalog.md"),
]


def main() -> None:
    rows: list[str] = []
    for name, rel in SECTIONS:
        p = ROOT / "docs/knowledge" / rel
        count = proven = verified = draft = 0
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                if not line.startswith("|") or line.startswith("| ID") or line.startswith("|----"):
                    continue
                cols = [c.strip() for c in line.strip("|").split("|")]
                if len(cols) < 4 or not cols[0] or cols[0] in ("Section", name):
                    continue
                count += 1
                mat = cols[3].lower()
                if mat == "proven":
                    proven += 1
                elif mat == "verified":
                    verified += 1
                elif mat == "draft":
                    draft += 1
        rows.append(f"| {name} | {count} | {proven} | {verified} | {draft} | `{rel}` |")

    block = (
        "<!-- AGGREGATE_START -->\n"
        "| Section | Entries | proven | verified | draft | B catalog |\n"
        "|---------|---------|--------|----------|-------|-----------|\n"
        + "\n".join(rows)
        + "\n<!-- AGGREGATE_END -->"
    )
    text = CATALOG.read_text(encoding="utf-8")
    new = re.sub(
        r"<!-- AGGREGATE_START -->.*?<!-- AGGREGATE_END -->",
        block,
        text,
        flags=re.S,
    )
    CATALOG.write_text(new, encoding="utf-8")
    print(f"Updated {CATALOG}")


if __name__ == "__main__":
    main()
