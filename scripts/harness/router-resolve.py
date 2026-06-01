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
import re
import subprocess
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[2]
RUNS_DIR = ROOT / "docs/harness/runs"
REGISTRY = ROOT / "docs/harness/skills.registry.yaml"
SKILLS_DIR = ROOT / ".cursor/skills"


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
    text = run_yaml.read_text(encoding="utf-8")

    def field(key: str, default: str = "") -> str:
        m = re.search(rf"^{key}:\s*(.+)$", text, re.M)
        return m.group(1).strip().strip('"') if m else default

    status = field("status", "UNKNOWN")
    skill = field("skill")
    profile = field("profile", "standard")
    started = field("started_at")
    description = field("description")

    mtime = datetime.fromtimestamp(run_yaml.stat().st_mtime, tz=timezone.utc)
    now = datetime.now(tz=timezone.utc)
    age_days = round((now - mtime).total_seconds() / 86400, 1)

    # 若 run.yaml 没有 description，尝试读 evidence/summary.md 首行
    if not description:
        summary_file = run_dir / "evidence" / "summary.md"
        if summary_file.is_file():
            first = summary_file.read_text(encoding="utf-8").splitlines()
            description = next(
                (l.lstrip("#").strip() for l in first if l.strip() and not l.startswith("---")),
                "",
            )

    return {
        "run_id": run_dir.name,
        "run_dir": str(run_dir.relative_to(ROOT)).replace("\\", "/"),
        "skill": skill,
        "status": status,
        "profile": profile,
        "description": description,
        "started_at": started or mtime.isoformat(),
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
    text = REGISTRY.read_text(encoding="utf-8")
    teams: list[dict] = []
    for block in re.finditer(
        r"- name:\s*(\S+)\s*\n(.*?)(?=\n  - name:|\nworkflows:|\Z)",
        text,
        re.S,
    ):
        name = block.group(1)
        body = block.group(2)

        desc_m = re.search(r"description:\s*(.+)", body)
        description = desc_m.group(1).strip().strip('"') if desc_m else ""

        triggers: list[str] = []
        trig_m = re.search(r"triggers:\s*\n((?:\s+-\s+.+\n)+)", body)
        if trig_m:
            triggers = [
                line.strip()[2:].strip().strip('"').strip("'")
                for line in trig_m.group(1).splitlines()
                if line.strip().startswith("-")
            ]

        skill_path_m = re.search(r"skill_path:\s*(.+)", body)
        skill_path = skill_path_m.group(1).strip().strip('"') if skill_path_m else ""

        # 若注册表里 description 为空，尝试从 SKILL.md frontmatter 读
        if not description and skill_path:
            sm = (ROOT / skill_path).expanduser()
            if sm.is_file():
                sm_text = sm.read_text(encoding="utf-8")
                dm = re.search(r"^description:\s*(.+)$", sm_text, re.M)
                if dm:
                    description = dm.group(1).strip().strip('"')

        teams.append({
            "name": name,
            "description": description,
            "triggers": triggers,
        })
    return teams


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
            text = skill_md.read_text(encoding="utf-8")
        except OSError:
            continue
        dm = re.search(r"^description:\s*(.+)$", text, re.M)
        description = dm.group(1).strip().strip('"') if dm else ""
        skills.append({"name": name, "description": description})
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
