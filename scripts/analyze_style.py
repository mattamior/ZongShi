#!/usr/bin/env python3
"""Deterministic style statistics for a captured timeline.

Prints one JSON object so STYLE.md numbers can be recomputed and compared.
Reads `authored.jsonl` / `replies.jsonl` / `originals.jsonl` from a capture directory.

Usage:
    python3 scripts/analyze_style.py data/target/<ts>
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

MENTION_PREFIX = re.compile(r"^(?:@[A-Za-z0-9_]+[\s\u200b,，:：]*)+")
CJK = re.compile(r"[\u4e00-\u9fff]")

# Wide, explicitly bounded ranges. Skin-tone modifiers and the emoji selector are
# excluded so "👍🏼" counts once; this is a heuristic, not a Unicode emoji property.
EMOJI_RANGES = (
    (0x1F000, 0x1FAFF),
    (0x2600, 0x27BF),
    (0x2B00, 0x2BFF),
    (0x2190, 0x21FF),
)
EMOJI_SKIP = {0xFE0F, 0xFE0E, 0x200D}
SKIN_TONES = range(0x1F3FB, 0x1F400)

REGISTERS = (
    ("ack", re.compile(r"^(是的|对的|可以|牛|牛逼|NB|真的|必须的|好的|是|行|有道理|够了|没问题|不错|太|确实)")),
    ("laugh", re.compile(r"(哈|笑死|没绷住|绷不住|😂|🤣|😆)")),
    ("shock", re.compile(r"(卧槽|我草|操|天塌|吓|离谱|夸张|😱|我去)")),
    ("question", re.compile(r"(？|\?|咋|怎么|为什么|是不是|多少|啥|呢)")),
)


def is_emoji(char: str) -> bool:
    code = ord(char)
    if code in EMOJI_SKIP or code in SKIN_TONES:
        return False
    return any(low <= code <= high for low, high in EMOJI_RANGES)


def body_of(text: str) -> str:
    return MENTION_PREFIX.sub("", text or "").strip()


def percentile(values: list, share: float) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(len(ordered) * share))]


def load_jsonl(path: Path) -> list:
    rows = []
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def describe_texts(rows: list) -> dict:
    bodies = [body_of(row.get("text")) for row in rows]
    lengths = [len(body) for body in bodies]
    counts = Counter(bodies)

    no_punct = question = exclamation = other_punct = 0
    with_emoji = at_end = emoji_only = multi_line = 0
    emoji_counter = Counter()
    repeat_runs = 0
    for body in bodies:
        stripped = body.rstrip()
        if not stripped:
            continue
        if "\n" in stripped:
            multi_line += 1
        last = stripped[-1]
        if last in "？?":
            question += 1
        elif last in "！!":
            exclamation += 1
        elif last in "。.，,…~～":
            other_punct += 1
        else:
            no_punct += 1
        chars = [char for char in stripped if is_emoji(char)]
        if chars:
            with_emoji += 1
            emoji_counter.update(chars)
            if is_emoji(last):
                at_end += 1
            if not CJK.search(stripped) and not re.search(r"[A-Za-z]", stripped):
                emoji_only += 1
        if re.search(r"([\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF])\1{1,}", stripped):
            repeat_runs += 1

    total = len(bodies)
    return {
        "count": total,
        "starts_with_mention": {
            "count": sum(1 for row in rows if (row.get("text") or "").startswith("@")),
            "share": round(sum(1 for row in rows if (row.get("text") or "").startswith("@")) / total, 4) if total else 0,
        },
        "body_length": {
            "median": percentile(lengths, 0.5),
            "p90": percentile(lengths, 0.9),
            "mean": round(sum(lengths) / total, 2) if total else 0,
            "max": max(lengths) if lengths else 0,
        },
        "terminal_punctuation": {
            "none": no_punct,
            "share_none": round(no_punct / total, 4) if total else 0,
            "question": question,
            "exclamation": exclamation,
            "period_or_tilde": other_punct,
        },
        "emoji": {
            "with_emoji": with_emoji,
            "share": round(with_emoji / total, 4) if total else 0,
            "at_line_end": at_end,
            "emoji_only_body": emoji_only,
            "repeat_runs": repeat_runs,
            "top": emoji_counter.most_common(10),
        },
        "multi_line": {"count": multi_line, "share": round(multi_line / total, 4) if total else 0},
        "distinct_bodies": len(counts),
        "top_bodies": [[body, count] for body, count in counts.most_common(8)],
    }


def registers(rows: list) -> dict:
    tally = Counter()
    for row in rows:
        body = body_of(row.get("text"))
        if not body:
            tally["empty"] += 1
            continue
        if not CJK.search(body) and not re.search(r"[A-Za-z]", body):
            tally["emoji_only"] += 1
            continue
        for name, pattern in REGISTERS:
            if pattern.search(body):
                tally[name] += 1
                break
        else:
            tally["other"] += 1
    return dict(tally)


def cadence(rows: list) -> dict:
    stamps = sorted(int(row["created_timestamp"]) for row in rows if row.get("created_timestamp"))
    if len(stamps) < 2:
        return {}
    gaps = [later - earlier for earlier, later in zip(stamps, stamps[1:])]
    bursts = []
    current = 1
    for gap in gaps:
        if gap > 120:
            bursts.append(current)
            current = 1
        else:
            current += 1
    bursts.append(current)
    span_hours = (stamps[-1] - stamps[0]) / 3600
    return {
        "gaps_median_s": percentile(gaps, 0.5),
        "gaps_p90_s": percentile(gaps, 0.9),
        "gaps_mean_s": round(sum(gaps) / len(gaps), 1),
        "under_60s_share": round(sum(1 for gap in gaps if gap < 60) / len(gaps), 4),
        "over_2h": sum(1 for gap in gaps if gap > 7200),
        "bursts": len(bursts),
        "burst_size_max": max(bursts),
        "burst_size_median": percentile(bursts, 0.5),
        "posts_per_hour": round(len(stamps) / span_hours, 2) if span_hours else 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture_dir", type=Path)
    args = parser.parse_args()
    root: Path = args.capture_dir

    replies = load_jsonl(root / "replies.jsonl") if (root / "replies.jsonl").exists() else []
    originals = load_jsonl(root / "originals.jsonl") if (root / "originals.jsonl").exists() else []
    # Posts with reply metadata missing but a leading @mention are replies whose parent
    # context the provider dropped; keeping them in "originals" would skew original shape.
    strict_originals = [row for row in originals if not (row.get("text") or "").startswith("@")]
    mention_led = len(originals) - len(strict_originals)
    authored = replies + originals
    if not authored:
        raise SystemExit(f"No authored statuses found in {root}")

    stamps = [int(row["created_timestamp"]) for row in authored if row.get("created_timestamp")]
    targets = Counter(
        (row.get("replying_to") or {}).get("screen_name") for row in replies if (row.get("replying_to") or {}).get("screen_name")
    )
    languages = Counter(str(row.get("lang")) for row in authored)

    report = {
        "input": {
            "capture_dir": str(root),
            "authored": len(authored),
            "replies": len(replies),
            "originals": len(strict_originals),
            "collection": json.loads((root / "collection.json").read_text(encoding="utf-8")).get("collection", {})
            if (root / "collection.json").exists()
            else {},
        },
        "time_range_utc": {
            "oldest": datetime.fromtimestamp(min(stamps), timezone.utc).isoformat() if stamps else None,
            "newest": datetime.fromtimestamp(max(stamps), timezone.utc).isoformat() if stamps else None,
        },
        "reply_share": round(len(replies) / len(authored), 4),
        "replies": describe_texts(replies),
        "originals": describe_texts(strict_originals),
        "mention_led_without_reply_metadata": mention_led,
        "reply_registers_heuristic": registers(replies),
        "original_openers": Counter(
            (row.get("text") or "").strip().split("\n")[0][:20] for row in strict_originals
        ).most_common(12),
        "original_shape": {
            "question_share": round(sum(1 for row in strict_originals if "？" in (row.get("text") or "") or "?" in (row.get("text") or "")) / len(strict_originals), 4) if strict_originals else 0,
            "grok_share": round(sum(1 for row in strict_originals if "@grok" in (row.get("text") or "").lower()) / len(strict_originals), 4) if strict_originals else 0,
            "line_count_median": percentile([len((row.get("text") or "").split("\n")) for row in strict_originals], 0.5),
        },
        "reply_targets_top": targets.most_common(15),
        "languages": languages.most_common(),
        "cadence_all": cadence(authored),
        "notes": [
            "Body length strips leading @mentions only; it measures Unicode code points, not visual width.",
            "Emoji detection uses bounded code-point ranges and excludes skin-tone modifiers; it is a heuristic.",
            "Register labels are regex heuristics, not linguistic classification; check the counts against samples.",
            "API `lang` tags are noisy (Chinese is often tagged `ja`); do not use them as a language split.",
        ],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
