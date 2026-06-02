#!/usr/bin/env python3
"""Validate evidence/summary.md or knowledge entry summary quality.

两级校验：
  1. 规则层（快速）：字符数 + 禁用词黑名单
  2. 语义层（可选）：调用 Claude Haiku 评审摘要是否表达了明确结论
     - 由 .run-config.yaml 的 run.summary.semantic_gate 控制（默认 false）
     - 需要 ANTHROPIC_API_KEY 环境变量
     - LLM 不可用时降级为规则层（不阻塞流程）
"""
from __future__ import annotations

import argparse
import os
import pathlib
import re
import sys

from run_common import load_run_config

_SEMANTIC_PROMPT = """\
你是一个知识质量评审员。请判断以下「任务摘要」是否合格。

合格标准（全部满足才算 PASS）：
1. 表达了明确的结论、决策或洞察——不是「完成了某任务」这类空话
2. 可以脱离上下文独立理解，读者能知道「学到了什么」或「决定了什么」
3. 有实质信息量，不是占位符

摘要：
{summary}

只回复以下格式之一（不要有其他内容）：
PASS: <一句话说明通过理由>
FAIL: <一句话说明不合格原因>"""


def _semantic_validate(text: str, model: str) -> tuple[bool, str]:
    """调用 LLM 评审摘要质量。返回 (passed, reason)。"""
    try:
        import anthropic  # type: ignore
    except ImportError:
        return True, "anthropic SDK 未安装，跳过语义校验"

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return True, "ANTHROPIC_API_KEY 未设置，跳过语义校验"

    try:
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model=model,
            max_tokens=120,
            messages=[{"role": "user", "content": _SEMANTIC_PROMPT.format(summary=text)}],
        )
        reply = msg.content[0].text.strip()
    except Exception as exc:
        return True, f"LLM 调用失败，跳过语义校验: {exc}"

    upper = reply.upper()
    if upper.startswith("PASS"):
        reason = reply[4:].lstrip(": ").strip()
        return True, reason or "语义合格"
    if upper.startswith("FAIL"):
        reason = reply[4:].lstrip(": ").strip()
        return False, reason or "语义不合格"
    # 格式异常：不阻塞，只告警
    return True, f"LLM 回复格式异常，跳过语义校验（原文：{reply[:60]}）"


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


def validate_summary_text(
    text: str,
    cfg: dict | None = None,
    semantic: bool | None = None,
) -> list[str]:
    """
    semantic=None  → 读 cfg["semantic_gate"] 决定（默认 False）
    semantic=True  → 强制启用语义校验
    semantic=False → 强制跳过语义校验
    """
    cfg = cfg or load_run_config()
    errors: list[str] = []
    cleaned = text.strip()

    if not cleaned:
        errors.append("summary 为空")
        return errors

    # ── 规则层 ───────────────────────────────────────────
    min_chars = int(cfg.get("min_chars", 20))
    if len(cleaned) < min_chars:
        errors.append(f"summary 过短（{len(cleaned)} < {min_chars} 字符）")

    lower = cleaned.lower()
    for bad in cfg.get("forbidden_substrings") or []:
        if bad.lower() in lower:
            errors.append(f"summary 含占位/禁用词: {bad}")

    # 规则层已有错误时不再浪费 LLM 调用
    if errors:
        return errors

    # ── 语义层 ───────────────────────────────────────────
    use_semantic = cfg.get("semantic_gate", False) if semantic is None else semantic
    if use_semantic:
        model = cfg.get("semantic_model", "claude-haiku-4-5")
        passed, reason = _semantic_validate(cleaned, model)
        if not passed:
            errors.append(f"语义质量不合格: {reason}")
        else:
            print(f"  语义校验通过: {reason}")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate summary quality.")
    parser.add_argument("path", help="summary.md or knowledge entry .md")
    parser.add_argument(
        "--semantic",
        action="store_true",
        default=None,
        help="强制启用语义校验（覆盖 config）",
    )
    parser.add_argument(
        "--no-semantic",
        dest="semantic",
        action="store_false",
        help="强制跳过语义校验（覆盖 config）",
    )
    args = parser.parse_args()

    path = pathlib.Path(args.path)
    if not path.is_file():
        print(f"ERROR: 文件不存在: {path}", file=sys.stderr)
        sys.exit(1)

    body = extract_summary_text(path)
    errors = validate_summary_text(body, semantic=args.semantic)
    if errors:
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"OK: summary valid ({len(body)} chars)")


if __name__ == "__main__":
    main()
