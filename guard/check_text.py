#!/usr/bin/env python3
"""Block drafts that break the hard rules in guard/banned.md before they reach the candidate pool.

Exit code 1 means at least one draft was rejected, so this can gate a pipeline step directly.

Usage:
    python3 guard/check_text.py --file data/eval/20261106T-samples/samples.jsonl --log data/eval/20261106T-samples/guard.log
    python3 guard/check_text.py --text "卧槽！外卖备注写了少辣，辣得我哭😱😱"
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

EMOJI = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF]")
URL = re.compile(r"https?://|t\.co/|www\.", re.IGNORECASE)
MENTION = re.compile(r"@[A-Za-z0-9_]{1,15}")

BANNED_PHRASES = [
    # 断言口吻与谣言标记
    "据传", "据悉", "内部消息", "知情人", "实锤", "独家爆料", "已证实",
    "百分百", "100%", "必然", "肯定会",
    # 绝对化与煽动
    "所有人都", "没有一个", "彻底完蛋", "亡国", "灭族", "血洗", "清算",
]
BANNED_CLOSERS = ["综上", "所以", "希望对你有帮助", "以上"]
ALLOWED_MENTIONS = {"@grok"}

MAX_CHARS = 90
MAX_LINES = 6
MAX_EMOJI_KINDS = 1
MAX_EMOJI_REPEAT = 3


def non_empty_lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.strip()]


def emoji_runs(text: str) -> list[tuple[str, int]]:
    """Consecutive identical emoji, e.g. 😱😱 -> ("😱", 2)."""
    runs: list[tuple[str, int]] = []
    for char in text:
        if not EMOJI.match(char):
            continue
        if runs and runs[-1][0] == char:
            runs[-1] = (char, runs[-1][1] + 1)
        else:
            runs.append((char, 1))
    return runs


def check(text: str) -> list[str]:
    problems: list[str] = []

    if len(text) > MAX_CHARS:
        problems.append(f"长度 {len(text)} > {MAX_CHARS}")

    lines = non_empty_lines(text)
    if len(lines) > MAX_LINES:
        problems.append(f"非空行 {len(lines)} > {MAX_LINES}")

    runs = emoji_runs(text)
    kinds = {char for char, _ in runs}
    if len(kinds) > MAX_EMOJI_KINDS:
        problems.append(f"表情种类 {len(kinds)} > {MAX_EMOJI_KINDS}（{''.join(sorted(kinds))}）")
    for char, count in runs:
        if count > MAX_EMOJI_REPEAT:
            problems.append(f"表情连打 {char}×{count} > {MAX_EMOJI_REPEAT}")
    if runs and lines:
        last_line = lines[-1]
        if not EMOJI.search(last_line):
            problems.append("表情不在最后一行")

    for mention in MENTION.findall(text):
        if mention.lower() not in ALLOWED_MENTIONS:
            problems.append(f"不允许的 @ 提及 {mention}")

    if URL.search(text):
        problems.append("含链接")

    for phrase in BANNED_PHRASES:
        if phrase in text:
            problems.append(f"红线词「{phrase}」")

    for closer in BANNED_CLOSERS:
        if closer in text:
            problems.append(f"收尾语「{closer}」")

    return problems


def longest_common_substring(a: str, b: str) -> int:
    """返回两段文本的最长公共子串长度，用于粗查来源标题与正文是否对得上。"""
    best = 0
    for i in range(len(a)):
        for j in range(len(b)):
            k = 0
            while i + k < len(a) and j + k < len(b) and a[i + k] == b[j + k]:
                k += 1
            best = max(best, k)
    return best


def check_source(draft: dict) -> list[str]:
    """断言型内容必须带来源锚点，且正文要与来源标题对得上；提问与观察不需要。"""
    if draft.get("claim") != "assertion":
        return []
    url = (draft.get("source_url") or "").strip()
    if not url:
        return ["断言型内容缺少 source_url"]
    title = (draft.get("source_title") or "").strip()
    if not title:
        return ["断言型内容缺少 source_title（无法核对来源）"]
    text = re.sub(r"[\s\W_]+", "", draft.get("text", ""))
    clean_title = re.sub(r"[\s\W_]+", "", title)
    common = longest_common_substring(text, clean_title)
    if common < 2:
        return [f"来源标题与正文对不上（最长公共片段 {common} 字）"]
    return []


def iter_drafts(args) -> list[dict]:
    if args.text:
        return [{"id": "stdin", "text": args.text}]
    if not args.file:
        raise SystemExit("需要 --file 或 --text")
    raw = args.file.read_text(encoding="utf-8")
    if args.file.suffix == ".jsonl":
        drafts = []
        for line in raw.splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            drafts.append({"id": str(row.get("id", "?")), "text": row.get("text", ""),
                           "claim": row.get("claim"), "source_url": row.get("source_url", ""),
                           "source_title": row.get("source_title", "")})
        return drafts
    return [{"id": f"line{i}", "text": line, "claim": "observation", "source_url": ""}
            for i, line in enumerate(raw.splitlines(), 1) if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=pathlib.Path)
    parser.add_argument("--text")
    parser.add_argument("--log", type=pathlib.Path)
    parser.add_argument("--json", action="store_true", help="输出机器可读结果")
    args = parser.parse_args()

    results = []
    rejected = 0
    for draft in iter_drafts(args):
        problems = check(draft["text"]) + check_source(draft)
        if problems:
            rejected += 1
        results.append({"id": draft["id"], "ok": not problems, "problems": problems})

    if args.json:
        print(json.dumps({"checked": len(results), "rejected": rejected, "results": results},
                         ensure_ascii=False, indent=2))
    else:
        for result in results:
            mark = "OK  " if result["ok"] else "FAIL"
            print(f"{mark} {result['id']}")
            for problem in result["problems"]:
                print(f"     - {problem}")
        print(f"\n检查 {len(results)} 条，拦截 {rejected} 条")

    if args.log:
        args.log.parent.mkdir(parents=True, exist_ok=True)
        with args.log.open("a", encoding="utf-8") as stream:
            for result in results:
                if not result["ok"]:
                    stream.write(json.dumps(result, ensure_ascii=False) + "\n")

    return 1 if rejected else 0


if __name__ == "__main__":
    sys.exit(main())
