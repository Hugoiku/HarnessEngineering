#!/usr/bin/env python3
"""Helpers for docs/harness/runs run.yaml lifecycle."""
from __future__ import annotations

import pathlib
import re
from datetime import date, datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[2]
RUNS_DIR = ROOT / "docs/harness/runs"
RUN_CONFIG = ROOT / "docs/harness/.run-config.yaml"


def load_run_config() -> dict:
    cfg = {"stale_after_days": 14, "min_chars": 20, "forbidden_substrings": []}
    if not RUN_CONFIG.is_file():
        return cfg
    text = RUN_CONFIG.read_text(encoding="utf-8")
    m = re.search(r"stale_after_days:\s*(\d+)", text)
    if m:
        cfg["stale_after_days"] = int(m.group(1))
    m = re.search(r"min_chars:\s*(\d+)", text)
    if m:
        cfg["min_chars"] = int(m.group(1))
    forbidden: list[str] = []
    in_block = False
    for line in text.splitlines():
        if "forbidden_substrings:" in line:
            in_block = True
            continue
        if in_block:
            if re.match(r"^\S", line) and not line.startswith(" "):
                break
            fm = re.match(r"\s+-\s+(.+)$", line)
            if fm:
                forbidden.append(fm.group(1).strip().strip('"'))
    cfg["forbidden_substrings"] = forbidden
    return cfg


def read_run_fields(run_dir: pathlib.Path) -> dict[str, str]:
    run_yaml = run_dir / "run.yaml"
    if not run_yaml.is_file():
        return {}
    text = run_yaml.read_text(encoding="utf-8")
    fields: dict[str, str] = {}
    for key in (
        "skill",
        "profile",
        "status",
        "started_at",
        "last_activity_at",
        "current_step",
        "archived_to_knowledge",
    ):
        m = re.search(rf"^{key}:\s*(.+)$", text, re.M)
        if m:
            fields[key] = m.group(1).strip().strip('"')
    return fields


def write_run_field(run_dir: pathlib.Path, key: str, value: str) -> None:
    run_yaml = run_dir / "run.yaml"
    if not run_yaml.is_file():
        raise FileNotFoundError(run_yaml)
    text = run_yaml.read_text(encoding="utf-8")
    line = f"{key}: {value}"
    if re.search(rf"^{key}:\s*", text, re.M):
        text = re.sub(rf"^{key}:\s*.+$", line, text, flags=re.M)
    else:
        text = text.rstrip() + f"\n{line}\n"
    run_yaml.write_text(text, encoding="utf-8")


def touch_activity(run_dir: pathlib.Path) -> str:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    write_run_field(run_dir, "last_activity_at", today)
    if not read_run_fields(run_dir).get("started_at") or read_run_fields(run_dir).get("started_at") == "null":
        write_run_field(run_dir, "started_at", today)
    return today


def days_since_activity(run_dir: pathlib.Path) -> float:
    fields = read_run_fields(run_dir)
    ref = fields.get("last_activity_at") or fields.get("started_at")
    if ref and ref != "null":
        try:
            dt = datetime.fromisoformat(ref.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
        except ValueError:
            ref = None
        else:
            return (datetime.now(timezone.utc) - dt).total_seconds() / 86400
    run_yaml = run_dir / "run.yaml"
    mtime = datetime.fromtimestamp(run_yaml.stat().st_mtime, tz=timezone.utc)
    return (datetime.now(timezone.utc) - mtime).total_seconds() / 86400


def iter_run_dirs() -> list[pathlib.Path]:
    if not RUNS_DIR.is_dir():
        return []
    return sorted(
        [p for p in RUNS_DIR.iterdir() if p.is_dir() and not p.name.startswith(".")],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
