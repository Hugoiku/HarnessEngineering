#!/usr/bin/env python3
"""Resolve harness-run target: resume existing run vs start new (working memory sync)."""
from __future__ import annotations

import argparse
import pathlib
import re
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[2]
RUNS_DIR = ROOT / "docs/harness/runs"
REGISTRY = ROOT / "docs/harness/skills.registry.yaml"

# apply stale marks before resolve
import subprocess

def _apply_stale() -> None:
    stale = ROOT / "scripts/harness/run-stale.py"
    if stale.is_file():
        subprocess.run(
            [sys.executable, str(stale), "--apply"],
            cwd=ROOT,
            capture_output=True,
        )

NEW_TASK_PATTERNS = [
    r"新任务",
    r"重新开始",
    r"重新来",
    r"另起",
    r"新开",
    r"\bnew run\b",
    r"\bnew task\b",
    r"\bstart over\b",
]
RESUME_PATTERNS = [
    r"继续",
    r"接着",
    r"同一任务",
    r"续跑",
    r"\bresume\b",
    r"\bcontinue\b",
]


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
        triggers: list[str] = []
        trig_section = re.search(r"triggers:\s*\n((?:\s+-\s+.+\n)+)", body)
        if trig_section:
            triggers = [
                line.strip()[2:].strip().strip('"').strip("'")
                for line in trig_section.group(1).splitlines()
                if line.strip().startswith("-")
            ]
        teams.append({"name": name, "triggers": triggers})
    return teams


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
    mtime = datetime.fromtimestamp(run_yaml.stat().st_mtime, tz=timezone.utc)
    return {
        "run_id": run_dir.name,
        "run_dir": str(run_dir.relative_to(ROOT)).replace("\\", "/"),
        "skill": skill,
        "status": status,
        "profile": profile,
        "started_at": started or mtime.isoformat(),
        "updated_at": mtime.isoformat(),
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


def match_skill(user_text: str, registry: list[dict]) -> str | None:
    text = user_text.lower()
    best: tuple[int, str] | None = None
    for entry in registry:
        name = entry["name"]
        if name.lower() in text:
            score = len(name) + 100
            if best is None or score > best[0]:
                best = (score, name)
        for trig in entry.get("triggers") or []:
            if trig.lower() in text:
                score = len(trig)
                if best is None or score > best[0]:
                    best = (score, name)
    # harness-* core skills explicit mention
    for m in re.finditer(r"\bharness-[\w-]+\b", user_text, re.I):
        name = m.group(0).lower()
        score = 50 + len(name)
        if best is None or score > best[0]:
            best = (score, name)
    return best[1] if best else None


def wants_new_task(user_text: str) -> bool:
    text = user_text.lower()
    return any(re.search(p, text, re.I) for p in NEW_TASK_PATTERNS)


def wants_resume(user_text: str) -> bool:
    text = user_text.lower()
    return any(re.search(p, text, re.I) for p in RESUME_PATTERNS)


def resolve(user_text: str) -> dict:
    _apply_stale()
    registry = _parse_registry()
    matched_skill = match_skill(user_text, registry)
    running = list_runs("RUNNING")
    all_recent = list_runs(None)

    result: dict = {
        "action": "new",
        "skill": matched_skill,
        "run_id": None,
        "run_dir": None,
        "profile": "standard",
        "sync_work_memory": True,
        "reason": "",
        "command": None,
    }

    if wants_new_task(user_text):
        result["reason"] = "用户明确要求新任务，创建新 run"
        if matched_skill:
            result["command"] = f"harness-run {matched_skill}"
        return result

    # Prefer RUNNING run matching skill
    candidates = running
    if matched_skill:
        skill_runs = [r for r in running if r["skill"] == matched_skill]
        if skill_runs:
            candidates = skill_runs

    if candidates and (wants_resume(user_text) or matched_skill or len(running) == 1):
        pick = candidates[0]
        if matched_skill and pick["skill"] != matched_skill and not wants_resume(user_text):
            result["reason"] = f"进行中的 run 为 {pick['skill']}，与当前意图 {matched_skill} 不一致，建议新 run"
            result["command"] = f"harness-run {matched_skill}"
            return result

        result["action"] = "resume"
        result["skill"] = pick["skill"]
        result["run_id"] = pick["run_id"]
        result["run_dir"] = pick["run_dir"]
        result["profile"] = pick["profile"]
        result["reason"] = (
            f"发现 RUNNING 工作记忆 {pick['run_dir']}（skill={pick['skill']}），"
            "续跑并同步 evidence/run.yaml，勿新建 run"
        )
        result["command"] = f"harness-run {pick['skill']} --run-id {pick['run_dir']}"
        return result

    if matched_skill:
        result["reason"] = "无进行中的 run，创建新工作记忆"
        result["command"] = f"harness-run {matched_skill}"
        return result

    if running:
        pick = running[0]
        result["action"] = "resume"
        result["skill"] = pick["skill"]
        result["run_id"] = pick["run_id"]
        result["run_dir"] = pick["run_dir"]
        result["profile"] = pick["profile"]
        result["reason"] = (
            f"未匹配 Team Skill，但存在 RUNNING run {pick['run_dir']}，"
            "建议续跑以保持工作记忆一致"
        )
        result["command"] = f"harness-run {pick['skill']} --run-id {pick['run_dir']}"
        return result

    result["action"] = "none"
    result["sync_work_memory"] = False
    result["reason"] = "未匹配 Skill 且无 RUNNING run，按成熟度推荐 create-skill 或 core skill"
    return result


def format_output(data: dict, as_json: bool) -> str:
    if as_json:
        import json
        return json.dumps(data, ensure_ascii=False, indent=2)
    lines = [
        f"action: {data['action']}",
        f"skill: {data.get('skill') or '-'}",
        f"run_id: {data.get('run_id') or '-'}",
        f"run_dir: {data.get('run_dir') or '-'}",
        f"sync_work_memory: {data['sync_work_memory']}",
        f"reason: {data['reason']}",
    ]
    if data.get("command"):
        lines.append(f"command: {data['command']}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Router: resume vs new harness run.")
    parser.add_argument("message", nargs="?", default="", help="User intent / latest message")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--list-running", action="store_true", help="List RUNNING runs only")
    args = parser.parse_args()

    if args.list_running:
        runs = list_runs("RUNNING")
        if args.json:
            import json
            print(json.dumps(runs, ensure_ascii=False, indent=2))
        else:
            for r in runs:
                print(f"{r['run_dir']}\t{r['skill']}\t{r['status']}")
        return

    if not args.message.strip():
        parser.print_help()
        sys.exit(1)

    print(format_output(resolve(args.message.strip()), args.json))


if __name__ == "__main__":
    main()
