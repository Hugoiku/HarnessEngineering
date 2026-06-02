#!/usr/bin/env python3
"""Shared helpers for knowledge entry frontmatter, catalogs, and maturity rules."""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys
from datetime import date, datetime
from typing import Any

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
KNOWLEDGE_ROOT = ROOT / "docs/knowledge"
CONFIG_PATH = KNOWLEDGE_ROOT / ".knowledge-config.yaml"

ENTRY_GLOBS = ("**/PK-*.md", "**/BK-*.md", "**/TK-*.md")
SKIP_PARTS = {"archive", "contributions"}


def _load_config() -> dict[str, Any]:
    try:
        return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return {}


def load_maturity_rules(section: str) -> dict[str, Any]:
    """Load promotion or decay rules keyed by current maturity level."""
    return _load_config().get("maturity", {}).get(section, {})


def load_decay_config() -> dict[str, Any]:
    return load_maturity_rules("decay")


def load_promotion_config() -> dict[str, Any]:
    return load_maturity_rules("promotion")


def split_frontmatter(text: str) -> tuple[dict[str, str], str, str]:
    m = re.match(r"^(---\n)(.*?)(\n---\n)(.*)$", text, re.S)
    if not m:
        raise ValueError("missing frontmatter")
    prefix, fm_text, suffix, body = m.group(1), m.group(2), m.group(3), m.group(4)
    fm: dict[str, str] = {}
    for line in fm_text.splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm, prefix + fm_text + suffix, body


def inner_frontmatter(fm_block: str) -> str:
    m = re.match(r"^---\n(.*?)\n---\n", fm_block, re.S)
    return m.group(1) if m else fm_block


def _parse_runs(value: str) -> list[str]:
    value = value.strip()
    if not value or value in ("[]", "null"):
        return []
    inner = value.strip("[]")
    if not inner.strip():
        return []
    return [part.strip().strip('"').strip("'") for part in inner.split(",") if part.strip()]


def parse_evidence(fm_text: str) -> dict[str, Any]:
    evidence: dict[str, Any] = {
        "contributors": "[]",
        "last_referenced": None,
        "reference_count": 0,
        "distinct_runs": [],
    }
    in_evidence = False
    for line in fm_text.splitlines():
        if line.strip() == "evidence:":
            in_evidence = True
            continue
        if in_evidence:
            if re.match(r"^  \w", line):
                k, v = line.strip().split(":", 1)
                v = v.strip()
                if k == "reference_count":
                    evidence[k] = int(v)
                elif k == "last_referenced":
                    evidence[k] = None if v in ("null", "~", "") else v.strip('"')
                elif k == "distinct_runs":
                    evidence[k] = _parse_runs(v)
                else:
                    evidence[k] = v
            elif line and not line.startswith(" "):
                break
    return evidence


def render_evidence(evidence: dict[str, Any]) -> list[str]:
    runs = evidence.get("distinct_runs") or []
    runs_body = ", ".join(runs)
    last_ref = evidence.get("last_referenced")
    last_ref_str = last_ref if last_ref else "null"
    return [
        "evidence:",
        f"  contributors: {evidence.get('contributors', '[]')}",
        f"  last_referenced: {last_ref_str}",
        f"  reference_count: {int(evidence.get('reference_count') or 0)}",
        f"  distinct_runs: [{runs_body}]",
    ]


def replace_evidence_block(inner_fm: str, evidence: dict[str, Any]) -> str:
    lines = inner_fm.splitlines()
    out: list[str] = []
    i = 0
    replaced = False
    while i < len(lines):
        if lines[i].strip() == "evidence:":
            out.extend(render_evidence(evidence))
            replaced = True
            i += 1
            while i < len(lines) and re.match(r"^  \w", lines[i]):
                i += 1
            continue
        out.append(lines[i])
        i += 1
    if not replaced:
        insert_at = len(out)
        for j, line in enumerate(out):
            if line.startswith("summary:"):
                insert_at = j
                break
        out[insert_at:insert_at] = render_evidence(evidence)
    return "\n".join(out)


def write_entry_evidence(entry_path: pathlib.Path, evidence: dict[str, Any]) -> None:
    text = entry_path.read_text(encoding="utf-8")
    fm, fm_block, body = split_frontmatter(text)
    inner = inner_frontmatter(fm_block)
    new_inner = replace_evidence_block(inner, evidence)
    entry_path.write_text(f"---\n{new_inner}\n---\n{body}", encoding="utf-8")


def bump_evidence(
    entry_path: pathlib.Path,
    run_id: str | None = None,
) -> dict[str, Any]:
    text = entry_path.read_text(encoding="utf-8")
    fm, fm_block, _ = split_frontmatter(text)
    inner = inner_frontmatter(fm_block)
    evidence = parse_evidence(inner)
    evidence["reference_count"] = int(evidence.get("reference_count") or 0) + 1
    evidence["last_referenced"] = date.today().isoformat()
    if run_id:
        runs = list(evidence.get("distinct_runs") or [])
        if run_id not in runs:
            runs.append(run_id)
        evidence["distinct_runs"] = runs
    write_entry_evidence(entry_path, evidence)
    return {
        "id": fm.get("id", entry_path.stem),
        "reference_count": evidence["reference_count"],
        "last_referenced": evidence["last_referenced"],
        "distinct_runs": evidence["distinct_runs"],
        "run_id": run_id,
    }


def iter_entries(include_archived: bool = False) -> list[pathlib.Path]:
    entries: list[pathlib.Path] = []
    for pattern in ENTRY_GLOBS:
        for path in KNOWLEDGE_ROOT.glob(pattern):
            parts = set(path.relative_to(KNOWLEDGE_ROOT).parts)
            if not include_archived and (parts & SKIP_PARTS):
                continue
            if path.name == "catalog.md":
                continue
            entries.append(path)
    return sorted(entries)


def find_entry_by_id(entry_id: str) -> pathlib.Path | None:
    for path in iter_entries(include_archived=True):
        text = path.read_text(encoding="utf-8")
        if re.search(rf"^id:\s*{re.escape(entry_id)}\s*$", text, re.M):
            return path
    return None


def catalog_for_entry(entry_path: pathlib.Path) -> pathlib.Path | None:
    rel = entry_path.relative_to(KNOWLEDGE_ROOT)
    parts = rel.parts
    if parts[0] == "project":
        return KNOWLEDGE_ROOT / "project/catalog.md"
    if parts[0] == "tech-wiki":
        return KNOWLEDGE_ROOT / "tech-wiki/catalog.md"
    if parts[0] == "biz-wiki" and len(parts) >= 2:
        return KNOWLEDGE_ROOT / parts[0] / parts[1] / "catalog.md"
    if parts[0] == "team-conventions":
        return KNOWLEDGE_ROOT / "team-conventions/catalog.md"
    return None


def catalog_line_for_entry(entry_path: pathlib.Path) -> str:
    return _catalog_line_python(entry_path)


def _catalog_line_python(entry_path: pathlib.Path) -> str:
    text = entry_path.read_text(encoding="utf-8")
    fm, _, _ = split_frontmatter(text)
    tags = fm.get("tags", "[]").strip("[]")
    summary = fm.get("summary", fm.get("title", "")).strip('"')
    return (
        f"| {fm['id']} | {fm.get('title', '').strip('\"')} | {fm['type']} | "
        f"{fm['maturity']} | {tags} | {summary} |"
    )


def _catalog_row_entry_id(line: str) -> str | None:
    if not line.startswith("|"):
        return None
    parts = [p.strip() for p in line.split("|")]
    if len(parts) < 3 or parts[1] in ("ID", ""):
        return None
    if parts[1].startswith("-"):
        return None
    return parts[1]


def upsert_catalog_row(entry_path: pathlib.Path) -> None:
    catalog = catalog_for_entry(entry_path)
    if catalog is None or not catalog.is_file():
        return
    fm, _, _ = split_frontmatter(entry_path.read_text(encoding="utf-8"))
    entry_id = fm["id"]
    new_line = catalog_line_for_entry(entry_path)
    lines = catalog.read_text(encoding="utf-8").splitlines()
    updated = [line for line in lines if _catalog_row_entry_id(line) != entry_id]
    inserted = False
    for i, line in enumerate(updated):
        if line.startswith("|----"):
            updated.insert(i + 1, new_line)
            inserted = True
            break
    if not inserted and new_line:
        updated.append(new_line)
    catalog.write_text("\n".join(updated) + "\n", encoding="utf-8")


def remove_catalog_row(entry_path: pathlib.Path) -> None:
    catalog = catalog_for_entry(entry_path)
    if catalog is None or not catalog.is_file():
        return
    fm, _, _ = split_frontmatter(entry_path.read_text(encoding="utf-8"))
    entry_id = fm["id"]
    lines = [
        line
        for line in catalog.read_text(encoding="utf-8").splitlines()
        if _catalog_row_entry_id(line) != entry_id
    ]
    catalog.write_text("\n".join(lines) + "\n", encoding="utf-8")


def set_maturity(entry_path: pathlib.Path, maturity: str) -> None:
    text = entry_path.read_text(encoding="utf-8")
    m = re.match(r"^(---\n)(.*?)(\n---\n)(.*)$", text, re.S)
    if not m:
        raise ValueError(f"missing frontmatter: {entry_path}")
    fm_text = m.group(2)
    body = m.group(4)
    if re.search(r"^maturity:\s*", fm_text, re.M):
        fm_text = re.sub(r"^maturity:\s*.+$", f"maturity: {maturity}", fm_text, flags=re.M)
    else:
        fm_text += f"\nmaturity: {maturity}"
    entry_path.write_text(f"---\n{fm_text}\n---\n{body}", encoding="utf-8")
    upsert_catalog_row(entry_path)


def months_since(iso_date: str | None, fallback_path: pathlib.Path, as_of: date) -> float:
    if iso_date:
        try:
            ref = datetime.strptime(iso_date[:10], "%Y-%m-%d").date()
        except ValueError:
            ref = datetime.fromtimestamp(fallback_path.stat().st_mtime).date()
    else:
        ref = datetime.fromtimestamp(fallback_path.stat().st_mtime).date()
    return (as_of - ref).days / 30.44


def append_log(action: str, entry_id: str, detail: str) -> None:
    log_path = KNOWLEDGE_ROOT / "log.md"
    today = date.today().isoformat()
    block = f"\n## [{today}] {action} | system | {entry_id} | {detail}\n"
    text = log_path.read_text(encoding="utf-8")
    log_path.write_text(text.rstrip() + block + "\n", encoding="utf-8")


def run_catalog_aggregate() -> None:
    agg = ROOT / "scripts/harness/catalog-aggregate.py"
    subprocess.run([sys.executable, str(agg)], check=True, cwd=ROOT)
