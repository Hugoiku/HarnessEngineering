#!/usr/bin/env python3
"""Helpers for docs/harness/runs run.yaml lifecycle."""
from __future__ import annotations

import pathlib
import re
from datetime import date, datetime, timezone

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
RUNS_DIR = ROOT / "docs/harness/runs"
RUN_CONFIG = ROOT / "docs/harness/.run-config.yaml"

_RUN_YAML_KEYS = {
    "skill", "profile", "status", "started_at",
    "last_activity_at", "current_step", "archived_to_knowledge",
}


def _safe_load(path: pathlib.Path) -> dict:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return {}


def load_run_config() -> dict:
    defaults: dict = {"stale_after_days": 14, "min_chars": 20, "forbidden_substrings": []}
    if not RUN_CONFIG.is_file():
        return defaults
    raw = _safe_load(RUN_CONFIG)
    run_sec = raw.get("run") or {}
    summary_sec = run_sec.get("summary") or {}
    return {
        "stale_after_days": float(run_sec.get("stale_after_days", defaults["stale_after_days"])),
        "min_chars": int(summary_sec.get("min_chars", defaults["min_chars"])),
        "forbidden_substrings": list(summary_sec.get("forbidden_substrings") or []),
    }


def read_run_fields(run_dir: pathlib.Path) -> dict[str, str]:
    run_yaml = run_dir / "run.yaml"
    if not run_yaml.is_file():
        return {}
    raw = _safe_load(run_yaml)
    return {k: str(v) for k, v in raw.items() if k in _RUN_YAML_KEYS and v is not None}


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
