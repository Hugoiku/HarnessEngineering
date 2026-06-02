#!/usr/bin/env python3
"""Ingest PDF files as Layer C test knowledge entries under docs/knowledge/project/."""
from __future__ import annotations

import argparse
import pathlib
import re
import shutil
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
PROJECT = ROOT / "docs/knowledge/project"
SOURCES = ROOT / "docs/knowledge/test-corpus/sources"
KNOWLEDGE_CONFIG = ROOT / "docs/knowledge/.knowledge-config.yaml"

sys.path.insert(0, str(ROOT / "scripts/harness"))
from knowledge_common import append_log, run_catalog_aggregate, split_frontmatter, upsert_catalog_row  # noqa: E402


def load_summary_limits() -> tuple[int, int]:
    defaults = (60, 120)
    if not KNOWLEDGE_CONFIG.is_file():
        return defaults
    try:
        cfg = yaml.safe_load(KNOWLEDGE_CONFIG.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return defaults
    summary = cfg.get("summary") or {}
    return int(summary.get("max_chars_zh", defaults[0])), int(summary.get("max_chars_en", defaults[1]))


def extract_pdf_text(path: pathlib.Path) -> tuple[int, str]:
    import PyPDF2

    reader = PyPDF2.PdfReader(str(path))
    pages = [(page.extract_text() or "") for page in reader.pages]
    return len(reader.pages), "\n\n".join(pages).strip()


def next_test_id() -> str:
    ids: list[int] = []
    for p in PROJECT.glob("PK-TEST-*.md"):
        m = re.search(r"PK-TEST-(\d+)", p.stem)
        if m:
            ids.append(int(m.group(1)))
    return f"PK-TEST-{max(ids, default=0) + 1:03d}"


def _cjk_ratio(text: str) -> float:
    if not text:
        return 0.0
    cjk = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
    return cjk / len(text)


def _clean_line(line: str) -> str:
    s = re.sub(r"\s+", " ", line).strip()
    s = re.sub(r"^\W+|\W+$", "", s)
    return s


def _first_sentence(text: str, min_len: int = 12) -> str:
    for raw in text.splitlines():
        s = _clean_line(raw)
        if len(s) < min_len:
            continue
        if re.match(r"^(第\s*\d+\s*页|page\s+\d+|-- \d+ of \d+ --)$", s, re.I):
            continue
        parts = re.split(r"(?<=[。！？.!?])\s*", s, maxsplit=1)
        return parts[0].strip()
    return ""


def infer_title(pdf: pathlib.Path, body: str, override: str = "") -> str:
    if override.strip():
        return override.strip()
    stem = pdf.stem
    name_lower = stem.lower()
    if "harness" in name_lower or "知识" in stem:
        return "Harness 知识沉淀实践（AI 工程交付）"
    if "dalio" in name_lower or "worldorder" in name_lower:
        return "Dalio 变化中的世界秩序（图表集）"
    if _cjk_ratio(stem) > 0.3:
        return stem[:40]
    return stem.replace("_", " ")[:60]


def infer_summary(title: str, body: str, pdf: pathlib.Path) -> str:
    max_zh, max_en = load_summary_limits()
    name_lower = pdf.stem.lower()

    if "harness" in name_lower or "知识才是护城河" in pdf.stem:
        s = "AI 工程交付团队知识沉淀：Harness 非目的，知识才是护城河，含实践与反模式"
        return s[:max_zh]

    if "dalio" in name_lower or "worldorder" in name_lower:
        s = "达里奥《变化中的世界秩序》图表与原则摘要（英文 PDF，宏观周期）"
        return s[:max_zh]

    if _cjk_ratio(body[:2000]) > 0.2:
        sent = _first_sentence(body)
        base = f"{title}：{sent}" if sent else title
        return base[:max_zh]

    sent = _first_sentence(body)
    base = f"{title}: {sent}" if sent else title
    return base[:max_en]


def infer_tags(title: str, body: str, pdf: pathlib.Path) -> list[str]:
    name_lower = pdf.stem.lower()
    tags: list[str] = ["pdf-import", "test-corpus"]

    if "harness" in name_lower or "知识" in pdf.stem:
        tags.extend(["harness", "knowledge-management", "ai-engineering", "zh"])
    elif "dalio" in name_lower or "worldorder" in name_lower:
        tags.extend(["dalio", "world-order", "macro", "charts", "economics", "en"])
    else:
        tags.append("zh" if _cjk_ratio(body[:1500]) > 0.2 else "en")

    # dedupe preserve order
    seen: set[str] = set()
    out: list[str] = []
    for t in tags:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def yaml_quote(value: str) -> str:
    if re.search(r'[:#\[\]{}|>&*!%@`",]', value) or value.strip() != value:
        return '"' + value.replace('"', '\\"') + '"'
    return value


def read_existing_evidence(entry_path: pathlib.Path) -> str:
    if not entry_path.is_file():
        return """evidence:
  contributors: []
  last_referenced: null
  reference_count: 0
  distinct_runs: []"""
    fm, fm_block, _ = split_frontmatter(entry_path.read_text(encoding="utf-8"))
    m = re.search(r"(evidence:\s*\n(?:\s+.+\n)+)", fm_block)
    if m:
        return m.group(1).rstrip()
    return """evidence:
  contributors: []
  last_referenced: null
  reference_count: 0
  distinct_runs: []"""


def ingest(
    pdf: pathlib.Path,
    title: str = "",
    entry_id: str = "",
) -> pathlib.Path:
    if not pdf.is_file():
        raise FileNotFoundError(pdf)
    page_count, body = extract_pdf_text(pdf)
    if not body:
        raise ValueError(f"no extractable text: {pdf}")

    entry_id = entry_id.strip() or next_test_id()
    title = infer_title(pdf, body, override=title)
    summary = infer_summary(title, body, pdf)
    tags = infer_tags(title, body, pdf)
    tags_yaml = ", ".join(tags)

    SOURCES.mkdir(parents=True, exist_ok=True)
    dest_pdf = SOURCES / pdf.name
    if pdf.resolve() != dest_pdf.resolve():
        shutil.copy2(pdf, dest_pdf)

    entry_path = PROJECT / f"{entry_id}.md"
    evidence_block = read_existing_evidence(entry_path)

    content = f"""---
id: {entry_id}
title: {yaml_quote(title)}
type: guideline
polarity: recommend
maturity: draft
layer: project
domain: test-corpus
tags: [{tags_yaml}]
applicable_phases: [orient, analyze]
source_references: []
{evidence_block}
summary: {yaml_quote(summary)}
---

# {title}

- 来源 PDF: `docs/knowledge/test-corpus/sources/{pdf.name}`
- 页数: {page_count}
- 字符数: {len(body):,}

## 正文（PDF 提取）

{body}
"""
    entry_path.write_text(content, encoding="utf-8")
    upsert_catalog_row(entry_path)
    append_log("ingest-pdf", entry_id, f"refresh {pdf.name} title={title[:20]}…")
    return entry_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest PDFs into test knowledge corpus.")
    parser.add_argument("pdfs", nargs="+", help="PDF file paths")
    parser.add_argument("--title", action="append", default=[], help="Optional title per PDF")
    parser.add_argument("--entry-id", action="append", default=[], help="Optional PK-TEST-xxx per PDF (update in place)")
    args = parser.parse_args()

    created: list[pathlib.Path] = []
    for i, pdf_str in enumerate(args.pdfs):
        pdf = pathlib.Path(pdf_str)
        title = args.title[i] if i < len(args.title) else ""
        eid = args.entry_id[i] if i < len(args.entry_id) else ""
        path = ingest(pdf, title=title, entry_id=eid)
        created.append(path)
        print(f"OK: {path.relative_to(ROOT)} ({path.stat().st_size:,} bytes)")

    run_catalog_aggregate()
    print(f"OK: ingested {len(created)} entries; sources -> {SOURCES.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
