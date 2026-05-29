#!/usr/bin/env python3
"""One-step archive: run evidence/summary.md -> docs/knowledge/project/PK-*.md"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys
from datetime import date

ROOT = pathlib.Path(__file__).resolve().parents[2]
KNOWLEDGE_PROJECT = ROOT / "docs/knowledge/project"

from knowledge_common import append_log, run_catalog_aggregate, upsert_catalog_row
from run_common import read_run_fields, write_run_field

# shared validation
import importlib.util

_spec = importlib.util.spec_from_file_location(
    "validate_summary_mod", ROOT / "scripts/harness/validate-summary.py"
)
_vs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_vs)


def next_pk_id() -> str:
    ids: list[int] = []
    for p in KNOWLEDGE_PROJECT.glob("PK-*.md"):
        m = re.search(r"PK-(\d+)", p.stem)
        if m:
            ids.append(int(m.group(1)))
    n = max(ids, default=0) + 1
    return f"PK-{n:03d}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Archive run summary to knowledge project layer.")
    parser.add_argument("--run-dir", required=True, help="docs/harness/runs/<id>")
    parser.add_argument("--title", default="", help="Entry title (default from first line of summary)")
    parser.add_argument("--type", default="guideline", help="model|decision|guideline|pitfall|process")
    parser.add_argument("--tags", default="run-archive", help="Comma-separated tags")
    args = parser.parse_args()

    run_dir = (ROOT / args.run_dir).resolve() if not pathlib.Path(args.run_dir).is_absolute() else pathlib.Path(args.run_dir)
    summary_path = run_dir / "evidence/summary.md"
    if not summary_path.is_file():
        print(f"ERROR: missing {summary_path}", file=sys.stderr)
        sys.exit(1)

    fields = read_run_fields(run_dir)
    if fields.get("status") != "COMPLETED":
        print(f"ERROR: run status 须为 COMPLETED，当前: {fields.get('status')}", file=sys.stderr)
        sys.exit(1)

    summary_text = _vs.extract_summary_text(summary_path)
    errors = _vs.validate_summary_text(summary_text)
    if errors:
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)

    title = args.title.strip() or summary_text.splitlines()[0][:40]
    entry_id = next_pk_id()
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    tags_yaml = ", ".join(tags)

    content = f"""---
id: {entry_id}
type: {args.type}
polarity: recommend
maturity: draft
layer: project
domain: personal
tags: [{tags_yaml}]
applicable_phases: [orient, analyze]
source_references: []
evidence:
  contributors: []
  last_referenced: null
  reference_count: 0
  distinct_runs: [{run_dir.name}]
summary: {summary_text[:120]}
---

# {title}

## 摘要

{summary_text}

## 来源

- run: `{run_dir.relative_to(ROOT).as_posix()}`
- archived: {date.today().isoformat()}

## 适用场景

- （补充）

## 不适用场景

- （补充）
"""
    entry_path = KNOWLEDGE_PROJECT / f"{entry_id}.md"
    entry_path.write_text(content, encoding="utf-8")
    upsert_catalog_row(entry_path)
    append_log("archive", entry_id, f"from run {run_dir.name}")
    run_catalog_aggregate()
    write_run_field(run_dir, "archived_to_knowledge", "true")

    print(f"OK: archived {entry_id} -> {entry_path.relative_to(ROOT)}")
    print(f"OK: run marked archived_to_knowledge=true")


if __name__ == "__main__":
    main()
