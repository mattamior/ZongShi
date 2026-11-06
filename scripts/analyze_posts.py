#!/usr/bin/env python3
"""Post-centric statistics for an account's own top-level posts.

The project replicates what the account *publishes*, not how it answers others,
so this script measures structure, openers, topics, cadence and reach, and ignores
replies entirely (the input file must already exclude reply metadata rows).

Usage:
    python3 scripts/analyze_posts.py data/target/posts-merged/posts.jsonl
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

CJK = re.compile(r"[\u4e00-\u9fff]")
EMOJI_RANGES = ((0x1F000, 0x1FAFF), (0x2600, 0x27BF), (0x2B00, 0x2BFF), (0x2190, 0x21FF))
EMOJI_SKIP = {0xFE0F, 0xFE0E, 0x200D}
SKIN_TONES = range(0x1F3FB, 0x1F400)

OPENERS = (
    ("不懂就问", re.compile(r"^不懂就问")),
    ("我很好奇", re.compile(r"^我很好奇")),
    ("卧槽系", re.compile(r"^卧槽")),
    ("说个冷知识/事实", re.compile(r"^说个(冷知识|事实)")),
    ("插播/说句实话", re.compile(r"^(插播|说句实话)")),
    ("话题式（问句开头）", re.compile(r".{0,6}[？?]")),
)

TOPICS = (
    ("时政/社会", re.compile(r"中国|政府|中共|党|天安门|政治|外交|美国|俄罗斯|乌克兰|朝鲜|日本|韩国|香港|台湾|深圳|墙|审查|主席|总统|选举|政策|经济|社保|监控|公安|网警|反腐|判|体制|五中全会|抗美援朝")),
    ("娱乐/八卦", re.compile(r"明星|粉丝|热搜|演唱会|综艺|剧|八卦|网红|瓜|皇马|巴萨|曼联|姆巴佩|球|影|演员|歌手")),
    ("币圈", re.compile(r"BTC|ETH|比特币|以太|加密|币圈|山寨|meme|合约|梭哈|牛回|数字人民币|股市|纳指|道指")),
    ("AI/科技", re.compile(r"AI|模型|grok|GPT|Claude|苹果|华为|小米|手机|算法|提示词|生成|机器人")),
)


def is_emoji(char: str) -> bool:
    code = ord(char)
    if code in EMOJI_SKIP or code in SKIN_TONES:
        return False
    return any(low <= code <= high for low, high in EMOJI_RANGES)


def percentile(values: list, share: float) -> float:
    if not values:
        return 0
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(len(ordered) * share))]


def classify(text: str) -> str:
    for name, pattern in TOPICS:
        if pattern.search(text):
            return name
    return "日常/其他"


def opener_of(text: str) -> str:
    first = text.strip().split("\n")[0]
    for name, pattern in OPENERS:
        if pattern.search(first):
            return name
    return "其他"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("posts_jsonl", type=Path)
    args = parser.parse_args()

    rows = [json.loads(line) for line in args.posts_jsonl.read_text(encoding="utf-8").splitlines() if line.strip()]
    texts = [(row.get("text") or "").strip() for row in rows]
    lengths = [len(text) for text in texts]
    lines = [len([chunk for chunk in text.split("\n") if chunk.strip()]) for text in texts]
    stamps = sorted(int(row["created_timestamp"]) for row in rows if row.get("created_timestamp"))

    days = sorted({datetime.fromtimestamp(stamp, timezone.utc).date().isoformat() for stamp in stamps})
    gaps = [later - earlier for earlier, later in zip(stamps, stamps[1:])]

    emoji_counter = Counter()
    for text in texts:
        emoji_counter.update(char for char in text if is_emoji(char))

    views = sorted(int(row.get("views") or 0) for row in rows)
    likes = sorted(int(row.get("likes") or 0) for row in rows)
    replies = sorted(int(row.get("replies") or 0) for row in rows)

    by_opener = {}
    for row, text, opener in zip(rows, texts, [opener_of(t) for t in texts]):
        bucket = by_opener.setdefault(opener, {"count": 0, "views": [], "likes": []})
        bucket["count"] += 1
        bucket["views"].append(int(row.get("views") or 0))
        bucket["likes"].append(int(row.get("likes") or 0))
    opener_table = [
        {
            "opener": opener,
            "count": data["count"],
            "views_median": percentile(data["views"], 0.5),
            "likes_median": percentile(data["likes"], 0.5),
        }
        for opener, data in sorted(by_opener.items(), key=lambda item: -item[1]["count"])
    ]

    top_posts = sorted(rows, key=lambda row: -int(row.get("views") or 0))[:5]

    report = {
        "input": str(args.posts_jsonl),
        "count": len(rows),
        "window_utc": {
            "first": datetime.fromtimestamp(min(stamps), timezone.utc).isoformat(),
            "last": datetime.fromtimestamp(max(stamps), timezone.utc).isoformat(),
            "days": len(days),
            "per_day": dict(Counter(datetime.fromtimestamp(stamp, timezone.utc).date().isoformat() for stamp in stamps)),
        },
        "structure": {
            "length_codepoints": {"median": percentile(lengths, 0.5), "p90": percentile(lengths, 0.9), "mean": round(sum(lengths) / len(lengths), 1), "max": max(lengths)},
            "lines_median": percentile(lines, 0.5),
            "lines_p90": percentile(lines, 0.9),
            "multi_line_share": round(sum(1 for n in lines if n > 1) / len(rows), 4),
            "blank_line_between_share": round(sum(1 for t in texts if "\n\n" in t) / len(rows), 4),
            "question_share": round(sum(1 for t in texts if "？" in t or "?" in t) / len(rows), 4),
            "grok_tag_share": round(sum(1 for t in texts if "@grok" in t.lower()) / len(rows), 4),
            "emoji_share": round(sum(1 for t in texts if any(is_emoji(ch) for ch in t)) / len(rows), 4),
            "media_share": round(sum(1 for row in rows if row.get("media")) / len(rows), 4),
            "emoji_top": emoji_counter.most_common(8),
        },
        "openers": opener_table,
        "topics_heuristic": dict(Counter(classify(text) for text in texts).most_common()),
        "reach": {
            "views": {"median": percentile(views, 0.5), "p90": percentile(views, 0.9), "max": max(views), "sum": sum(views)},
            "likes": {"median": percentile(likes, 0.5), "p90": percentile(likes, 0.9), "max": max(likes)},
            "replies": {"median": percentile(replies, 0.5), "p90": percentile(replies, 0.9)},
            "top_by_views": [
                {"id": row["id"], "views": row.get("views"), "likes": row.get("likes"), "text": (row.get("text") or "").replace("\n", " / ")[:80]}
                for row in top_posts
            ],
        },
        "cadence": {
            "posts_per_hour": round(len(stamps) / ((stamps[-1] - stamps[0]) / 3600), 2) if len(stamps) > 1 else 0,
            "gap_median_s": percentile(gaps, 0.5),
            "gap_p90_s": percentile(gaps, 0.9),
            "under_10min_share": round(sum(1 for gap in gaps if gap < 600) / len(gaps), 4) if gaps else 0,
        },
        "hour_of_day_utc8": dict(sorted(Counter(datetime.fromtimestamp(stamp, timezone.utc).astimezone().hour for stamp in stamps).items())),
        "notes": [
            "Input must contain own top-level posts only; reply rows and reposts are excluded upstream.",
            "Topic shares use keyword patterns and will double-count/over-assign; treat as directional.",
            "Views/likes are point-in-time values from the capture, not lifetime totals.",
        ],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
