#!/usr/bin/env python3
"""Apply knowledge maturity promotion and decay from .knowledge-config.yaml."""
from __future__ import annotations

import argparse
import pathlib
import re
from datetime import date

from knowledge_common import (
    KNOWLEDGE_ROOT,
    append_log,
    inner_frontmatter,
    iter_entries,
    load_decay_config,
    load_promotion_config,
    months_since,
    parse_evidence,
    remove_catalog_row,
    run_catalog_aggregate,
    set_maturity,
    split_frontmatter,
)


def _meets_promotion(
    maturity: str,
    evidence: dict,
    rule: dict,
) -> tuple[bool, str]:
    refs = int(evidence.get("reference_count") or 0)
    runs = evidence.get("distinct_runs") or []
    min_refs = int(rule.get("min_reference_count", 0))
    if refs < min_refs:
        return False, f"refs {refs}<{min_refs}"
    min_runs = rule.get("min_distinct_runs")
    if min_runs is not None:
        need = int(min_runs)
        if len(runs) < need:
            return False, f"distinct_runs {len(runs)}<{need}"
    return True, f"refs={refs}, runs={len(runs)}"


def apply_promotion(dry_run: bool) -> list[str]:
    rules = load_promotion_config()
    actions: list[str] = []

    for entry_path in iter_entries(include_archived=False):
        text = entry_path.read_text(encoding="utf-8")
        fm, fm_block, _ = split_frontmatter(text)
        entry_id = fm.get("id", entry_path.stem)
        maturity = fm.get("maturity", "draft")
        if maturity not in rules or maturity == "archived":
            continue

        evidence = parse_evidence(inner_frontmatter(fm_block))
        rule = rules[maturity]
        ok, detail = _meets_promotion(maturity, evidence, rule)
        if not ok:
            continue

        target = rule.get("to", "")
        if not target:
            continue
        msg = (
            f"{'DRY ' if dry_run else ''}UPGRADE {entry_id}: "
            f"{maturity} -> {target} ({detail})"
        )
        actions.append(msg)
        if not dry_run:
            set_maturity(entry_path, target)
            append_log("promote", entry_id, f"{maturity}->{target} {detail}")

    return actions


def archive_entry(entry_path: pathlib.Path, archive_dir_name: str, dry_run: bool) -> str:
    fm, _, _ = split_frontmatter(entry_path.read_text(encoding="utf-8"))
    entry_id = fm["id"]
    rel = entry_path.relative_to(KNOWLEDGE_ROOT)
    dest = KNOWLEDGE_ROOT / archive_dir_name / rel
    if dry_run:
        return f"DRY archive {entry_id}: {rel} -> {dest.relative_to(KNOWLEDGE_ROOT)}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    text = entry_path.read_text(encoding="utf-8")
    text = re.sub(r"^maturity:\s*.+$", "maturity: archived", text, flags=re.M)
    dest.write_text(text, encoding="utf-8")
    remove_catalog_row(entry_path)
    entry_path.unlink()
    append_log("archive", entry_id, f"stale draft moved to {dest.relative_to(KNOWLEDGE_ROOT)}")
    return f"ARCHIVE {entry_id} -> {dest.relative_to(KNOWLEDGE_ROOT)}"


def apply_decay(dry_run: bool, as_of: date) -> list[str]:
    rules = load_decay_config()
    actions: list[str] = []

    for entry_path in iter_entries(include_archived=False):
        text = entry_path.read_text(encoding="utf-8")
        fm, fm_block, _ = split_frontmatter(text)
        entry_id = fm.get("id", entry_path.stem)
        maturity = fm.get("maturity", "draft")
        if maturity == "archived":
            continue

        evidence = parse_evidence(inner_frontmatter(fm_block))
        idle_months = months_since(evidence.get("last_referenced"), entry_path, as_of)

        if maturity == "proven" and "proven" in rules:
            rule = rules["proven"]
            threshold = int(rule.get("unused_months", 12))
            if idle_months >= threshold:
                target = rule.get("to", "verified")
                msg = (
                    f"{'DRY ' if dry_run else ''}DOWNGRADE {entry_id}: "
                    f"proven -> {target} (idle {idle_months:.1f}m >= {threshold}m)"
                )
                actions.append(msg)
                if not dry_run:
                    set_maturity(entry_path, target)
                    append_log("decay", entry_id, f"proven->{target} idle {idle_months:.1f}m")
            continue

        if maturity == "verified" and "verified" in rules:
            rule = rules["verified"]
            threshold = int(rule.get("unused_months", 6))
            if idle_months >= threshold:
                target = rule.get("to", "draft")
                msg = (
                    f"{'DRY ' if dry_run else ''}DOWNGRADE {entry_id}: "
                    f"verified -> {target} (idle {idle_months:.1f}m >= {threshold}m)"
                )
                actions.append(msg)
                if not dry_run:
                    set_maturity(entry_path, target)
                    append_log("decay", entry_id, f"verified->{target} idle {idle_months:.1f}m")
            continue

        if maturity == "draft" and "draft" in rules:
            rule = rules["draft"]
            threshold = int(rule.get("stale_months", 6))
            if idle_months >= threshold:
                archive_dir = rule.get("archive_dir", "archive")
                msg = archive_entry(entry_path, archive_dir, dry_run)
                actions.append(msg)

    return actions


def apply_maturity(
    dry_run: bool,
    as_of: date,
    *,
    promote: bool = True,
    decay: bool = True,
) -> list[str]:
    actions: list[str] = []
    if promote:
        actions.extend(apply_promotion(dry_run))
    if decay:
        actions.extend(apply_decay(dry_run, as_of))
    if not dry_run and actions:
        run_catalog_aggregate()
    return actions


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Apply knowledge maturity promotion and decay."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report actions without modifying files (default unless --apply)",
    )
    parser.add_argument("--apply", action="store_true", help="Apply changes")
    parser.add_argument(
        "--promote-only",
        action="store_true",
        help="Only run promotion rules",
    )
    parser.add_argument(
        "--decay-only",
        action="store_true",
        help="Only run decay rules",
    )
    parser.add_argument(
        "--as-of",
        default=date.today().isoformat(),
        help="Evaluate decay as of YYYY-MM-DD",
    )
    parser.add_argument(
        "--report",
        default=None,
        help="Write report markdown to path",
    )
    args = parser.parse_args()

    if args.promote_only and args.decay_only:
        parser.error("Use at most one of --promote-only and --decay-only")

    dry_run = not args.apply
    as_of = date.fromisoformat(args.as_of[:10])
    promote = not args.decay_only
    decay = not args.promote_only

    actions = apply_maturity(dry_run, as_of, promote=promote, decay=decay)

    mode = "dry-run" if dry_run else "apply"
    scope = "promotion+decay"
    if args.promote_only:
        scope = "promotion"
    elif args.decay_only:
        scope = "decay"
    header = f"# Knowledge maturity ({scope}, {mode}) as-of {as_of.isoformat()}\n\n"
    body = "No maturity actions.\n" if not actions else "\n".join(f"- {line}" for line in actions) + "\n"

    print(header.strip())
    print(body.strip())

    if args.report:
        report_path = pathlib.Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(header + body, encoding="utf-8")


if __name__ == "__main__":
    main()
