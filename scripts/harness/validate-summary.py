#!/usr/bin/env python3
"""Validate evidence/summary.md or knowledge entry summary quality."""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

from run_common import load_run_config


def extract_summary_text(path: pathlib.Path) -> str:
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        sm = re.search(r"^summary:\s*(.+)$", text, re.M)
        if sm:
            return sm.group(1).strip().strip('"')
        m = re.match(r"^---\n.*?\n---\n(.*)$", text, re.S)
        if m:
            return m.group(1).strip()
    return text.strip()


def validate_summary_text(text: str, cfg: dict | None = None) -> list[str]:
    cfg = cfg or load_run_config()
    errors: list[str] = []
    cleaned = text.strip()
    if not cleaned:
        errors.append("summary 为空")
        return errors
    min_chars = int(cfg.get("min_chars", 20))
    if len(cleaned) < min_chars:
        errors.append(f"summary 过短（{len(cleaned)} < {min_chars} 字符）")
    lower = cleaned.lower()
    for bad in cfg.get("forbidden_substrings") or []:
        if bad.lower() in lower:
            errors.append(f"summary 含占位/禁用词: {bad}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate summary quality.")
    parser.add_argument("path", help="summary.md or knowledge entry .md")
    args = parser.parse_args()
    path = pathlib.Path(args.path)
    if not path.is_file():
        print(f"ERROR: 文件不存在: {path}", file=sys.stderr)
        sys.exit(1)
    body = extract_summary_text(path)
    errors = validate_summary_text(body)
    if errors:
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"OK: summary valid ({len(body)} chars)")


if __name__ == "__main__":
    main()
