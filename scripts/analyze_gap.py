#!/usr/bin/env python3
"""Compare generated samples against the target corpus on the distributions P2 cares about.

No KS statistic: it looks only at the single worst point of the length curve, and with 20
samples a couple of edits move it by 0.05, so it gate-kept nothing. Length is compared by
band shares plus p50/p90 instead.

Usage:
    python3 scripts/analyze_gap.py \
        --corpus data/target/posts-merged/posts.jsonl \
        --samples data/eval/20261106T-samples/samples.jsonl \
        --output data/eval/20261106T-samples/gap.json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import statistics

EMOJI = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF]")
TERMINAL_PUNCT = set("。！？!?…~～.，,")
LENGTH_BANDS = [(0, 20), (21, 40), (41, 60), (61, 80), (81, None)]


def load_texts(path: pathlib.Path) -> list[str]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return [row.get("text", "") for row in rows]


def strip_trailing_emoji(text: str) -> str:
    cleaned = text.rstrip()
    while cleaned and EMOJI.match(cleaned[-1]):
        cleaned = cleaned[:-1].rstrip()
    return cleaned


def ends_without_punctuation(text: str) -> bool:
    cleaned = strip_trailing_emoji(text)
    return bool(cleaned) and cleaned[-1] not in TERMINAL_PUNCT


def has_repeated_emoji(text: str) -> bool:
    chars = list(text)
    for index in range(len(chars) - 1):
        if chars[index] == chars[index + 1] and EMOJI.match(chars[index]):
            return True
    return False


def non_empty_lines(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip())


def band_shares(lengths: list[int]) -> dict[str, float]:
    total = len(lengths)
    shares = {}
    for low, high in LENGTH_BANDS:
        count = sum(1 for n in lengths if n >= low and (high is None or n <= high))
        label = f"{low}-{high}" if high is not None else f"{low}+"
        shares[label] = round(count / total, 4)
    return shares


def describe(texts: list[str]) -> dict:
    lengths = [len(t) for t in texts]
    lines = [non_empty_lines(t) for t in texts]
    return {
        "n": len(texts),
        "length_p50": statistics.median(lengths),
        "length_p90": sorted(lengths)[int(len(lengths) * 0.9)],
        "length_mean": round(statistics.mean(lengths), 1),
        "length_bands": band_shares(lengths),
        "no_terminal_punct_share": round(sum(ends_without_punctuation(t) for t in texts) / len(texts), 4),
        "emoji_share": round(sum(1 for t in texts if EMOJI.search(t)) / len(texts), 4),
        "repeated_emoji_share": round(sum(has_repeated_emoji(t) for t in texts) / len(texts), 4),
        "multi_line_share": round(sum(1 for n in lines if n > 1) / len(texts), 4),
        "blank_line_share": round(sum(1 for t in texts if "\n\n" in t) / len(texts), 4),
        "question_share": round(sum(1 for t in texts if ("?" in t or "？" in t)) / len(texts), 4),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=pathlib.Path, required=True)
    parser.add_argument("--samples", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path)
    args = parser.parse_args()

    before = describe(load_texts(args.corpus))
    after = describe(load_texts(args.samples))

    band_deltas = {
        band: round(after["length_bands"][band] - before["length_bands"][band], 4)
        for band in before["length_bands"]
    }
    share_deltas = {
        key: round(after[key] - before[key], 4)
        for key in ("no_terminal_punct_share", "emoji_share", "repeated_emoji_share",
                    "multi_line_share", "blank_line_share", "question_share")
    }

    report = {
        "corpus": str(args.corpus),
        "samples": str(args.samples),
        "corpus_metrics": before,
        "sample_metrics": after,
        "length_band_deltas": band_deltas,
        "share_deltas": share_deltas,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
