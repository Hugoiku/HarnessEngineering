#!/usr/bin/env python3
"""
router-resolve: 提供工作记忆状态数据，供 Agent 做语义路由决策。

脚本只负责：
  1. 标记 STALE run（客观事实）
  2. 收集并输出结构化状态 JSON（running runs、team skills、core skills）

语义判断（意图匹配哪个 run、该 resume 还是 new）由 Agent（LLM）完成。

用法：
  python router-resolve.py --data --json   # 推荐：输出状态数据给 Agent 推理
  python router-resolve.py --list-running  # 兼容旧调用：列出 RUNNING runs
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
from datetime import datetime, timezone

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
RUNS_DIR = ROOT / "docs/harness/runs"
REGISTRY = ROOT / "docs/harness/skills.registry.yaml"
SKILLS_DIR = ROOT / ".cursor/skills"

sys.path.insert(0, str(ROOT / "scripts/harness"))
from run_common import read_run_fields  # noqa: E402


def _safe_load(path: pathlib.Path) -> dict:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return {}


def _parse_frontmatter(text: str) -> dict:
    """Extract YAML frontmatter between --- delimiters."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fm_text = text[4:end]
    try:
        return yaml.safe_load(fm_text) or {}
    except yaml.YAMLError:
        return {}


# ---------------------------------------------------------------------------
# STALE 标记（客观判断，保留在脚本）
# ---------------------------------------------------------------------------

def _apply_stale() -> bool:
    stale = ROOT / "scripts/harness/run-stale.py"
    if not stale.is_file():
        return False
    r = subprocess.run(
        [sys.executable, str(stale), "--apply"],
        cwd=ROOT,
        capture_output=True,
    )
    return r.returncode == 0


# ---------------------------------------------------------------------------
# 解析单个 run
# ---------------------------------------------------------------------------

def _parse_run(run_dir: pathlib.Path) -> dict | None:
    run_yaml = run_dir / "run.yaml"
    if not run_yaml.is_file():
        return None

    fields = read_run_fields(run_dir)
    if not fields:
        return None

    mtime = datetime.fromtimestamp(run_yaml.stat().st_mtime, tz=timezone.utc)
    now = datetime.now(tz=timezone.utc)
    age_days = round((now - mtime).total_seconds() / 86400, 1)

    description = fields.get("description", "")
    if not description:
        summary_file = run_dir / "evidence" / "summary.md"
        if summary_file.is_file():
            first = summary_file.read_text(encoding="utf-8").splitlines()
            description = next(
                (ln.lstrip("#").strip() for ln in first if ln.strip() and not ln.startswith("---")),
                "",
            )

    return {
        "run_id": run_dir.name,
        "run_dir": str(run_dir.relative_to(ROOT)).replace("\\", "/"),
        "skill": fields.get("skill", ""),
        "status": fields.get("status", "UNKNOWN"),
        "profile": fields.get("profile", "standard"),
        "description": description,
        "started_at": fields.get("started_at") or mtime.isoformat(),
        "updated_at": mtime.isoformat(),
        "age_days": age_days,
    }


def list_runs(status_filter: str | None = None) -> list[dict]:
    if not RUNS_DIR.is_dir():
        return []
    runs: list[dict] = []
    for d in sorted(RUNS_DIR.iterdir()):
        if not d.is_dir() or d.name.startswith("."):
            continue
        parsed = _parse_run(d)
        if parsed is None:
            continue
        if status_filter and parsed["status"] != status_filter:
            continue
        runs.append(parsed)
    runs.sort(key=lambda r: r["updated_at"], reverse=True)
    return runs


# ---------------------------------------------------------------------------
# 解析 Team Skill 注册表
# ---------------------------------------------------------------------------

def _parse_registry() -> list[dict]:
    if not REGISTRY.is_file():
        return []
    raw = _safe_load(REGISTRY)
    results: list[dict] = []
    for entry in raw.get("team") or []:
        if not isinstance(entry, dict):
            continue
        name = entry.get("name", "")
        description = entry.get("description", "")
        triggers = list(entry.get("triggers") or [])
        skill_path = entry.get("skill_path", "")

        # 注册表无 description 时，从对应 SKILL.md frontmatter 读
        if not description and skill_path:
            sm = ROOT / skill_path
            if sm.is_file():
                fm = _parse_frontmatter(sm.read_text(encoding="utf-8"))
                description = fm.get("description", "")

        results.append({"name": name, "description": description, "triggers": triggers})
    return results


# ---------------------------------------------------------------------------
# 枚举 Core Skill（harness-*）描述
# ---------------------------------------------------------------------------

def _load_core_skills() -> list[dict]:
    skills: list[dict] = []
    if not SKILLS_DIR.is_dir():
        return skills
    for skill_md in sorted(SKILLS_DIR.glob("harness-*/SKILL.md")):
        name = skill_md.parent.name
        try:
            fm = _parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        except OSError:
            continue
        skills.append({"name": name, "description": fm.get("description", "")})
    return skills


# ---------------------------------------------------------------------------
# 主数据载荷（供 Agent 语义推理）
# ---------------------------------------------------------------------------

def build_data_payload() -> dict:
    stale_applied = _apply_stale()

    running = list_runs("RUNNING")
    recent_completed = [r for r in list_runs(None) if r["status"] in ("COMPLETED", "STALE")][:5]
    team_skills = _parse_registry()
    core_skills = _load_core_skills()

    return {
        "stale_applied": stale_applied,
        "running": running,
        "recent_completed": recent_completed,
        "team_skills": team_skills,
        "core_skills": core_skills,
        "_routing_note": (
            "由 Agent（LLM）根据此数据做语义路由决策，"
            "脚本不做 resume/new 判断。"
            "决策维度：① 用户意图与 running[].description/skill 语义相似 → resume；"
            "② 意图明显是全新任务或与 running 无关 → new；"
            "③ 从 team_skills + core_skills 中语义匹配目标 skill。"
        ),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="router-resolve: 输出工作记忆状态数据，供 Agent 语义路由。"
    )
    parser.add_argument(
        "--data",
        action="store_true",
        help="（推荐）输出完整状态 JSON，由 Agent 做语义路由决策",
    )
    parser.add_argument("--json", action="store_true", help="JSON 格式输出（--list-running 专用）")
    parser.add_argument("--list-running", action="store_true", help="仅列出 RUNNING runs（兼容旧调用）")
    args = parser.parse_args()

    if args.list_running:
        _apply_stale()
        runs = list_runs("RUNNING")
        if args.json:
            print(json.dumps(runs, ensure_ascii=False, indent=2))
        else:
            for r in runs:
                print(f"{r['run_dir']}\t{r['skill']}\t{r['status']}")
        return

    # 默认或 --data：输出完整数据载荷
    payload = build_data_payload()
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
