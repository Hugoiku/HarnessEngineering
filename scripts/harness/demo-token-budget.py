#!/usr/bin/env python3
"""Demo: compare context size — naive full read vs Harness query budget (+ chat overhead)."""
from __future__ import annotations

import argparse
import pathlib
import random
import re
import textwrap

ROOT = pathlib.Path(__file__).resolve().parents[2]
KNOWLEDGE = ROOT / "docs/knowledge"
KNOWLEDGE_CONFIG = ROOT / "docs/knowledge/.knowledge-config.yaml"


def est_tokens(text: str) -> int:
    """Rough token estimate (mixed zh/en): ~1 token per 2 chars."""
    return max(1, len(text) // 2)


def load_query_budget() -> dict:
    cfg = {
        "layer_a_max_lines": 60,
        "layer_b_max_lines": 250,
        "layer_c_max_entries": 3,
        "layer_c_max_lines_each": 200,
    }
    if KNOWLEDGE_CONFIG.is_file():
        text = KNOWLEDGE_CONFIG.read_text(encoding="utf-8")
        for key in cfg:
            m = re.search(rf"{key}:\s*(\d+)", text)
            if m:
                cfg[key] = int(m.group(1))
    return cfg


def read_file_capped(path: pathlib.Path, max_lines: int | None) -> str:
    if not path.is_file():
        return ""
    lines = path.read_text(encoding="utf-8").splitlines()
    if max_lines is not None:
        lines = lines[:max_lines]
    return "\n".join(lines)


def iter_c_entries(base: pathlib.Path) -> list[pathlib.Path]:
    skip = {"archive", "contributions", "catalog.md", "log.md", "KNOWLEDGE.md"}
    out: list[pathlib.Path] = []
    for p in base.rglob("*.md"):
        parts = set(p.relative_to(base).parts)
        if parts & skip:
            continue
        if p.name == "catalog.md":
            continue
        if re.match(r"^(PK|BK|TK)-", p.stem):
            out.append(p)
    return sorted(out)


def make_synthetic_entry(i: int) -> str:
    """One C-layer entry ~120 lines (typical archived knowledge)."""
    body = textwrap.dedent(
        f"""
        ---
        id: PK-SYN-{i:03d}
        type: guideline
        maturity: verified
        layer: project
        tags: [synthetic, demo]
        summary: 合成条目 {i}：关于模块 {i} 的结论与适用场景摘要（一行）。
        ---

        # 合成知识条目 {i}

        ## 摘要
        模块 {i} 的调试经验：先查日志，再核对配置，最后复现最小用例。

        ## 正文
        """
    ).strip()
    paragraphs = [
        f"第 {j} 段：在场景 {i}-{j} 下，常见问题是边界条件未覆盖，"
        f"建议增加单元测试并记录到 run evidence。"
        for j in range(1, 16)
    ]
    return body + "\n\n" + "\n\n".join(paragraphs)


def scenario_naive_full_read(base: pathlib.Path, synthetic: list[str]) -> dict:
    """Direct chat: read all knowledge markdown under docs/knowledge."""
    chunks: list[str] = []
    for p in sorted(base.rglob("*.md")):
        if "contributions" in p.parts:
            continue
        chunks.append(p.read_text(encoding="utf-8"))
    for s in synthetic:
        chunks.append(s)
    text = "\n\n".join(chunks)
    return {"name": "A. 直接对话：读全库知识文件", "chars": len(text), "tokens": est_tokens(text)}


def scenario_he_multi_agent_chat(base: pathlib.Path, synthetic: list[str], rounds: int = 5) -> dict:
    """Harness Engineering style: full read + repeated router/handoff in context."""
    router_block = textwrap.dedent(
        """
        ### RouterInput
        - user_goal: 完成模块分析与文档更新
        - state:
          - artifacts: [path + 8 bullet summary...]
        ### RouterDecision
        - next_skill: team-*
        - handoff_brief: 400字交接说明...
        """
    ).strip()
    overhead = (router_block + "\n") * rounds
    handoff = "Agent handoff summary: 步骤、结论、未决问题各 8 条要点。\n" * 8
    full_text = "\n\n".join([read_all_text(base, synthetic), overhead, handoff * rounds])
    return {
        "name": f"B. 多 Agent + 全库读取（{rounds} 轮路由/handoff 留上下文）",
        "chars": len(full_text),
        "tokens": est_tokens(full_text),
    }


def read_all_text(base: pathlib.Path, synthetic: list[str]) -> str:
    parts = []
    for p in sorted(base.rglob("*.md")):
        if "contributions" in p.parts:
            continue
        parts.append(p.read_text(encoding="utf-8"))
    parts.extend(synthetic)
    return "\n\n".join(parts)


def scenario_harness_budget(base: pathlib.Path, synthetic: list[str], budget: dict) -> dict:
    """Harness: Layer A + one Layer B + Top-K C (capped lines); summaries only in chat for rest."""
    chunks: list[str] = []

    a = read_file_capped(base / "catalog.md", budget["layer_a_max_lines"])
    chunks.append(f"[Layer A]\n{a}")

    # orient: one B catalog (project first per layer_preference)
    b = read_file_capped(base / "project/catalog.md", budget["layer_b_max_lines"])
    chunks.append(f"[Layer B project]\n{b}")

    # Top-K C from real + synthetic (simulate picking 3 by catalog)
    entries = iter_c_entries(base)
    syn_paths = []  # use synthetic as extra entries
    all_bodies: list[tuple[str, str]] = []
    for p in entries:
        all_bodies.append((p.stem, p.read_text(encoding="utf-8")))
    for i, s in enumerate(synthetic):
        all_bodies.append((f"PK-SYN-{i+1:03d}", s))

    k = budget["layer_c_max_entries"]
    cap = budget["layer_c_max_lines_each"]
    selected = all_bodies[:k]
    for eid, body in selected:
        lines = body.splitlines()[:cap]
        chunks.append(f"[Layer C {eid}]\n" + "\n".join(lines))

    # Remaining entries: ID + summary only (Harness rule: no full paste)
    for eid, body in all_bodies[k:]:
        sm = re.search(r"^summary:\s*(.+)$", body, re.M)
        summary = sm.group(1).strip() if sm else "(无 summary)"
        chunks.append(f"[引用] {eid}: {summary[:80]}")

    # Run memory from disk (not chat): run.yaml + router-resolution + summary excerpt
    run_snippet = textwrap.dedent(
        """
        [run.yaml] status: RUNNING skill: demo
        [router-resolution.txt] action: new | reason: 无 RUNNING run
        [summary.md] 任务进行中（磁盘留痕，不重复聊天历史）
        """
    ).strip()
    chunks.append(run_snippet)

    text = "\n\n".join(chunks)
    return {
        "name": "C. 本框架：查询预算 + 磁盘 run（standard orient/analyze）",
        "chars": len(text),
        "tokens": est_tokens(text),
        "detail": f"A≤{budget['layer_a_max_lines']}行 B≤{budget['layer_b_max_lines']}行 C≤{k}×{cap}行",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Token budget demo case study.")
    parser.add_argument(
        "--synthetic-entries",
        type=int,
        default=30,
        help="Simulate N archived PK entries (typical team bookshelf size)",
    )
    args = parser.parse_args()

    random.seed(42)
    synthetic = [make_synthetic_entry(i + 1) for i in range(args.synthetic_entries)]
    budget = load_query_budget()

    results = [
        scenario_naive_full_read(KNOWLEDGE, synthetic),
        scenario_he_multi_agent_chat(KNOWLEDGE, synthetic, rounds=5),
        scenario_harness_budget(KNOWLEDGE, synthetic, budget),
    ]

    print("# Token 消耗对比案例")
    print(f"# 场景：orient 阶段查阅知识库（模拟 {args.synthetic_entries} 条 project 级条目 + 仓库现有文件）")
    print(f"# Token 估算：字符数 ÷ 2（中英混合粗算）\n")
    print("| 方式 | 上下文字符 | 估算 Token |")
    print("|------|------------|------------|")
    baseline = results[0]["tokens"]
    for r in results:
        pct = "" if r is results[0] else f"（较 A 约 **-{100 - r['tokens'] * 100 // max(baseline, 1)}%**）"
        if r is results[2]:
            extra = r.get("detail", "")
            pct = f"（较 A 约 **-{100 - r['tokens'] * 100 // max(baseline, 1)}%**；{extra}）"
        print(f"| {r['name']} | {r['chars']:,} | ~{r['tokens']:,} |")

    h = results[2]["tokens"]
    print(f"\n结论：本框架路径 C 较全库读取 A 减少约 **{100 - h * 100 // max(baseline, 1)}%** 估算 Token。")
    if results[1]["tokens"] > baseline:
        print(f"      较含多轮 handoff 的 B 减少约 **{100 - h * 100 // max(results[1]['tokens'], 1)}%**。")
    print("\n说明：规模为模拟；条目越多，A/B 增长越快，C 受查询预算封顶，差距越大。")


if __name__ == "__main__":
    main()
